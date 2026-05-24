"""
bias_correction.py — Monthly-Stratified Empirical Quantile Mapping (EQM)
=========================================================================
ARICE Project — FuXi-S2S Calibration against PAGASA Station Data

Architecture
------------
EQMModel              : Single fitted CDF-mapping (one variable, one stratum).
EQMVariableCorrector  : Holds 12 monthly EQMModels + 1 all-year fallback
                        for a single variable.  Dispatches predict() calls
                        by extracting the month from a datetime array.
BiasCorrector         : Top-level class.  One EQMVariableCorrector per variable.
                        fit() / transform() / save() / load() public API.
evaluate_correction() : Module-level function.  Prints RMSE / MAE / MBE table.

Why monthly stratification?
---------------------------
The Philippines has a pronounced monsoon cycle.  A single all-year CDF
conflates the dry-season (Nov–Apr) and wet-season (May–Oct) distributions,
producing a mean that is accurate for neither.  Fitting separate quantile
curves for each calendar month lets the correction respond to intra-annual
shifts in rainfall intensity, temperature range, and wind patterns.

Fallback rule
-------------
If a month has fewer than MIN_SAMPLES_PER_MONTH (default 30) valid training
pairs, the all-year model is used instead.  This prevents the CDF from being
built on a handful of unrepresentative points.
"""

from __future__ import annotations

import pickle
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

# Minimum paired samples required to train a monthly model.
# Months below this count fall back to the all-year curve.
MIN_SAMPLES_PER_MONTH: int = 30


# ---------------------------------------------------------------------------
# EQMModel — single distribution mapping
# ---------------------------------------------------------------------------

@dataclass
class EQMModel:
    """
    Stores an empirical quantile mapping for one variable / one stratum.

    The core mapping is:
        x_corrected = F_obs^{-1}( F_model( x ) )

    For zero-inflated variables (rainfall) a two-stage algorithm is used:
        1. Compute p = F_model(x)  (what quantile does the raw value sit at?)
        2. If p <= dry_day_threshold  →  output = 0.0  (preserve dry-day freq.)
        3. Else                       →  apply wet-only EQM.
    """

    forecast_quantiles: np.ndarray      # sorted FuXi training values (knots)
    obs_quantiles: np.ndarray           # sorted PAGASA training values (knots)
    obs_min: float                      # hard floor for extrapolation
    obs_max: float
    dry_day_threshold: Optional[float] = None   # probability in [0,1]; None = not zero-inflated
    wet_forecast_quantiles: Optional[np.ndarray] = None
    wet_obs_quantiles: Optional[np.ndarray] = None
    variable_name: str = "unknown"
    month: Optional[int] = None         # 1–12, or None for all-year model

    # scipy interp1d objects — rebuilt after unpickling, never serialised
    _full_interp: Optional[interp1d] = field(default=None, repr=False)
    _wet_interp: Optional[interp1d] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self._build_interpolators()

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_full_interp"] = None
        state["_wet_interp"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._build_interpolators()

    # ------------------------------------------------------------------

    def _build_interpolators(self) -> None:
        def _make(x_knots: np.ndarray, y_knots: np.ndarray) -> interp1d:
            _, idx = np.unique(x_knots, return_index=True)
            xu, yu = x_knots[idx], y_knots[idx]
            if xu.size < 2:
                xu = np.array([xu[0] - 1e-6, xu[0] + 1e-6])
                yu = np.array([yu[0], yu[0]])
            return interp1d(xu, yu, kind="linear",
                            fill_value="extrapolate", bounds_error=False)

        self._full_interp = _make(self.forecast_quantiles, self.obs_quantiles)

        if (self.wet_forecast_quantiles is not None
                and self.wet_obs_quantiles is not None
                and self.wet_forecast_quantiles.size >= 2):
            self._wet_interp = _make(self.wet_forecast_quantiles,
                                     self.wet_obs_quantiles)
        else:
            self._wet_interp = None

    # ------------------------------------------------------------------

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Apply EQM mapping to a 1-D array of raw forecast values."""
        x = np.asarray(x, dtype=float)
        out = np.empty_like(x)

        if self.dry_day_threshold is not None and self._wet_interp is not None:
            # Compute empirical quantile rank of each raw value
            p = np.interp(
                x,
                self.forecast_quantiles,
                np.linspace(0, 1, len(self.forecast_quantiles)),
            )
            dry_mask = p <= self.dry_day_threshold
            out[dry_mask] = 0.0

            wet_mask = ~dry_mask
            if wet_mask.any():
                mapped = self._wet_interp(x[wet_mask])
                out[wet_mask] = np.maximum(mapped, self.obs_min)
        else:
            out = np.maximum(self._full_interp(x), self.obs_min)

        return out


# ---------------------------------------------------------------------------
# _fit_eqm_model — internal factory
# ---------------------------------------------------------------------------

def _fit_eqm_model(
    x: np.ndarray,
    y: np.ndarray,
    n_quantiles: int,
    zero_inflated: bool,
    variable_name: str,
    month: Optional[int] = None,
) -> EQMModel:
    """
    Build one EQMModel from aligned (forecast, observation) arrays.
    Raises ValueError if fewer than 10 valid finite pairs exist.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    if x.size < 10:
        raise ValueError(
            f"[{variable_name}] month={month}: only {x.size} valid samples (need ≥10)."
        )

    n_q = min(n_quantiles, x.size)
    levels = np.linspace(0, 100, n_q + 1)
    fcast_knots = np.percentile(x, levels)
    obs_knots = np.percentile(y, levels)
    obs_min, obs_max = float(y.min()), float(y.max())

    dry_day_threshold = None
    wet_fcast_knots = None
    wet_obs_knots = None

    if zero_inflated:
        p0 = float(np.sum(y == 0.0)) / x.size   # fraction of dry days in obs

        if p0 >= 1.0:
            warnings.warn(f"[{variable_name}] month={month}: all obs are 0; forcing dry.", RuntimeWarning)
            dry_day_threshold = 1.0
        else:
            dry_day_threshold = p0
            x_wet = x[y > 0.0]
            y_wet = y[y > 0.0]
            if x_wet.size >= 10:
                n_qw = min(n_quantiles, x_wet.size)
                wl = np.linspace(0, 100, n_qw + 1)
                wet_fcast_knots = np.percentile(x_wet, wl)
                wet_obs_knots = np.percentile(y_wet, wl)
            else:
                warnings.warn(
                    f"[{variable_name}] month={month}: <10 wet-day samples; "
                    "dry-day threshold disabled.", RuntimeWarning,
                )
                dry_day_threshold = None

    return EQMModel(
        forecast_quantiles=fcast_knots,
        obs_quantiles=obs_knots,
        obs_min=obs_min,
        obs_max=obs_max,
        dry_day_threshold=dry_day_threshold,
        wet_forecast_quantiles=wet_fcast_knots,
        wet_obs_quantiles=wet_obs_knots,
        variable_name=variable_name,
        month=month,
    )


# ---------------------------------------------------------------------------
# EQMVariableCorrector — monthly stratification for one variable
# ---------------------------------------------------------------------------

class EQMVariableCorrector:
    """
    Manages 12 monthly EQMModels + 1 all-year fallback for a single variable.

    Fitting
    -------
    1. An all-year model is always fitted first from the full training set.
    2. The data is then grouped by calendar month (1–12).
    3. If a month has >= MIN_SAMPLES_PER_MONTH valid pairs, a dedicated monthly
       model is fitted.  Otherwise, that month's slot is left as None and the
       all-year model is used at prediction time.

    Prediction
    ----------
    Given an array of (values, months), each value is routed to its
    month-specific model (or the all-year fallback).
    """

    def __init__(self, variable_name: str, obs_col: str) -> None:
        self.variable_name = variable_name
        self.obs_col = obs_col
        self.all_year_model: Optional[EQMModel] = None
        # Keys 1–12; value is None when the month uses the all-year fallback
        self.monthly_models: Dict[int, Optional[EQMModel]] = {m: None for m in range(1, 13)}
        self.fallback_months: List[int] = []   # months that fell back to all-year

    # ------------------------------------------------------------------

    def fit(
        self,
        x: np.ndarray,
        y: np.ndarray,
        months: np.ndarray,
        n_quantiles: int,
        zero_inflated: bool,
    ) -> "EQMVariableCorrector":
        """
        Fit all-year model, then attempt monthly models.

        Parameters
        ----------
        x       : Raw FuXi forecast values (all training rows).
        y       : Corresponding PAGASA observations.
        months  : Integer month array (1–12), same length as x and y.
        """
        # --- All-year model (always fitted; used as fallback) ---
        self.all_year_model = _fit_eqm_model(
            x, y, n_quantiles, zero_inflated,
            variable_name=self.variable_name, month=None,
        )

        # --- Monthly models ---
        self.fallback_months = []
        for m in range(1, 13):
            mask = months == m
            n_m = int(mask.sum())

            if n_m < MIN_SAMPLES_PER_MONTH:
                # Not enough data — will use all-year model at predict time
                self.monthly_models[m] = None
                self.fallback_months.append(m)
                continue

            try:
                self.monthly_models[m] = _fit_eqm_model(
                    x[mask], y[mask], n_quantiles, zero_inflated,
                    variable_name=self.variable_name, month=m,
                )
            except ValueError as e:
                warnings.warn(str(e), UserWarning)
                self.monthly_models[m] = None
                self.fallback_months.append(m)

        return self

    # ------------------------------------------------------------------

    def predict(self, x: np.ndarray, months: np.ndarray) -> np.ndarray:
        """
        Correct raw forecast values using the appropriate monthly model.

        Parameters
        ----------
        x      : Raw forecast values.
        months : Integer months (1–12) corresponding to each element of x.
        """
        x = np.asarray(x, dtype=float)
        months = np.asarray(months, dtype=int)
        out = np.empty_like(x)

        for m in range(1, 13):
            mask = months == m
            if not mask.any():
                continue

            model = self.monthly_models.get(m) or self.all_year_model
            if model is None:
                raise RuntimeError(
                    f"[{self.variable_name}] No model available for month {m}."
                )

            finite = mask & np.isfinite(x)
            nan_in_month = mask & ~np.isfinite(x)

            out[nan_in_month] = np.nan
            if finite.any():
                out[finite] = model.predict(x[finite])

        return out

    # ------------------------------------------------------------------

    def summary_rows(self) -> List[dict]:
        """Return one dict per month (plus all-year) for diagnostics."""
        rows = []
        ay = self.all_year_model
        rows.append({
            "variable": self.variable_name,
            "month": "all-year",
            "source": "fitted",
            "obs_min": ay.obs_min if ay else None,
            "obs_max": ay.obs_max if ay else None,
            "dry_day_p0": ay.dry_day_threshold if ay else None,
            "n_knots": len(ay.forecast_quantiles) if ay else None,
        })
        for m in range(1, 13):
            mod = self.monthly_models[m]
            is_fallback = m in self.fallback_months
            rows.append({
                "variable": self.variable_name,
                "month": m,
                "source": "fallback→all-year" if is_fallback else "fitted",
                "obs_min": mod.obs_min if mod else ay.obs_min if ay else None,
                "obs_max": mod.obs_max if mod else ay.obs_max if ay else None,
                "dry_day_p0": mod.dry_day_threshold if mod else (ay.dry_day_threshold if ay else None),
                "n_knots": len(mod.forecast_quantiles) if mod else None,
            })
        return rows


# ---------------------------------------------------------------------------
# BiasCorrector — top-level class (drop-in compatible API)
# ---------------------------------------------------------------------------

class BiasCorrector:
    """
    Monthly-stratified EQM bias corrector for FuXi-S2S / ARICE.

    Usage
    -----
    corrector = BiasCorrector().fit(training_df, mapping, datetime_col='valid_time')
    corrected  = corrector.transform(forecast_df, datetime_col='valid_time')
    corrector.save('artifacts/bias_correction_params.pkl')
    corrector  = BiasCorrector.load('artifacts/bias_correction_params.pkl')

    The `datetime_col` argument (default: 'valid_time') must point to a column
    that is already a pandas datetime dtype or is parseable by pd.to_datetime().
    The month integer is extracted from it to route each row to the correct
    monthly EQM curve.
    """

    DEFAULT_MAPPING: Dict[str, str] = {
        "t2m_celsius": "TMAX",
        "tp":          "RAINFALL",
        "wind_speed":  "WINDSPEED",
    }
    DEFAULT_ZERO_INFLATED: frozenset = frozenset({"tp"})

    def __init__(
        self,
        n_quantiles: int = 100,
        zero_inflated_vars: Optional[frozenset] = None,
    ) -> None:
        self.n_quantiles = n_quantiles
        self.zero_inflated_vars: frozenset = (
            zero_inflated_vars
            if zero_inflated_vars is not None
            else self.DEFAULT_ZERO_INFLATED
        )
        # variable_name → EQMVariableCorrector
        self.correctors: Dict[str, EQMVariableCorrector] = {}
        self.is_fitted: bool = False

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(
        self,
        training_df: pd.DataFrame,
        mapping: Optional[Dict[str, str]] = None,
        datetime_col: str = "valid_time",
    ) -> "BiasCorrector":
        """
        Fit monthly-stratified EQM models from paired training data.

        Parameters
        ----------
        training_df  : DataFrame with forecast columns, obs columns, and a
                       datetime column (datetime_col).
        mapping      : {forecast_col: obs_col}.  Defaults to DEFAULT_MAPPING.
        datetime_col : Name of the column holding forecast valid datetimes.
                       Used to extract calendar month (1–12) for stratification.
        """
        if mapping is None:
            mapping = self.DEFAULT_MAPPING

        # Extract and validate the month array
        if datetime_col not in training_df.columns:
            raise KeyError(
                f"datetime_col '{datetime_col}' not found in training_df. "
                f"Available columns: {list(training_df.columns)}"
            )
        dt_series = pd.to_datetime(training_df[datetime_col], errors="coerce")
        if dt_series.isna().all():
            raise ValueError(f"Column '{datetime_col}' could not be parsed as datetime.")

        months = dt_series.dt.month.to_numpy(dtype=float)

        self.correctors = {}

        for forecast_col, obs_col in mapping.items():
            missing = [c for c in (forecast_col, obs_col) if c not in training_df.columns]
            if missing:
                warnings.warn(
                    f"Skipping '{forecast_col}→{obs_col}': column(s) {missing} not found.",
                    UserWarning,
                )
                continue

            x = training_df[forecast_col].to_numpy(dtype=float)
            y = training_df[obs_col].to_numpy(dtype=float)

            # Align months — drop rows where month is NaT
            valid_month_mask = np.isfinite(months)
            x_v = x[valid_month_mask]
            y_v = y[valid_month_mask]
            m_v = months[valid_month_mask].astype(int)

            is_zi = forecast_col in self.zero_inflated_vars

            try:
                vc = EQMVariableCorrector(
                    variable_name=forecast_col, obs_col=obs_col
                ).fit(
                    x=x_v, y=y_v, months=m_v,
                    n_quantiles=self.n_quantiles,
                    zero_inflated=is_zi,
                )
                self.correctors[forecast_col] = vc

                zi_tag = " [zero-inflated]" if is_zi else ""
                fb_tag = (
                    f"  fallback months: {vc.fallback_months}"
                    if vc.fallback_months else "  all months fitted"
                )
                print(
                    f"  ✓ EQM fitted: {forecast_col} → {obs_col}{zi_tag}\n"
                    f"    obs range (all-year): "
                    f"[{vc.all_year_model.obs_min:.2f}, {vc.all_year_model.obs_max:.2f}]\n"
                    f"{fb_tag}"
                )

            except ValueError as e:
                warnings.warn(f"Could not fit EQM for '{forecast_col}': {e}", UserWarning)

        if not self.correctors:
            raise ValueError("No EQM models were fitted.  Check column names in training_df.")

        self.is_fitted = True
        return self

    # ------------------------------------------------------------------
    # transform
    # ------------------------------------------------------------------

    def transform(
        self,
        df: pd.DataFrame,
        datetime_col: str = "valid_time",
    ) -> pd.DataFrame:
        """
        Apply monthly-stratified EQM corrections to a forecast DataFrame.

        Returns a copy of df with <forecast_col>_corrected columns appended.

        Parameters
        ----------
        df           : DataFrame with forecast columns and a datetime column.
        datetime_col : Same column used during fit().
        """
        if not self.is_fitted:
            raise RuntimeError("BiasCorrector is not fitted.  Call .fit() first.")

        if datetime_col not in df.columns:
            raise KeyError(
                f"datetime_col '{datetime_col}' not found in DataFrame."
            )

        months = pd.to_datetime(df[datetime_col], errors="coerce").dt.month.to_numpy(dtype=float)

        out = df.copy()

        for forecast_col, vc in self.correctors.items():
            if forecast_col not in out.columns:
                warnings.warn(f"'{forecast_col}' not in DataFrame; skipping.", UserWarning)
                continue

            x = out[forecast_col].to_numpy(dtype=float)
            corrected = np.full_like(x, fill_value=np.nan)

            # Only process rows where both value and month are finite
            ok = np.isfinite(x) & np.isfinite(months)
            if ok.any():
                corrected[ok] = vc.predict(x[ok], months[ok].astype(int))

            out[f"{forecast_col}_corrected"] = corrected

        return out

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: "str | Path") -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "correctors":         self.correctors,
            "n_quantiles":        self.n_quantiles,
            "zero_inflated_vars": self.zero_inflated_vars,
        }
        with path.open("wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"  ✓ BiasCorrector saved → {path}")
        return str(path)

    @classmethod
    def load(cls, path: "str | Path") -> "BiasCorrector":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"BiasCorrector file not found: {path}")
        with path.open("rb") as f:
            payload = pickle.load(f)
        obj = cls(
            n_quantiles=payload.get("n_quantiles", 100),
            zero_inflated_vars=payload.get("zero_inflated_vars"),
        )
        obj.correctors = payload.get("correctors", {})
        obj.is_fitted = bool(obj.correctors)
        return obj

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def summary(self) -> pd.DataFrame:
        """
        Return a tidy DataFrame with one row per (variable, month) stratum.
        'source' column shows 'fitted' or 'fallback→all-year'.
        """
        if not self.is_fitted:
            raise RuntimeError("BiasCorrector is not fitted.")
        rows: List[dict] = []
        for vc in self.correctors.values():
            rows.extend(vc.summary_rows())
        return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# evaluate_correction — standalone metrics function
# ---------------------------------------------------------------------------

def evaluate_correction(
    eval_df: pd.DataFrame,
    mapping: Dict[str, str],
    corrected_suffix: str = "_corrected",
    display_table: bool = True,
) -> pd.DataFrame:
    """
    Compare raw FuXi vs. EQM-calibrated values against PAGASA observations.

    Computes RMSE, MAE, and Mean Bias Error (MBE) for both raw and corrected
    forecasts, then prints a formatted comparison table.

    Parameters
    ----------
    eval_df          : DataFrame containing:
                         - Raw forecast columns  (e.g. 'tp')
                         - Corrected columns     (e.g. 'tp_corrected')
                         - Observation columns   (e.g. 'RAINFALL')
    mapping          : {forecast_col: obs_col} — same dict used during fit().
    corrected_suffix : Suffix appended to forecast columns after transform().
    display_table    : If True, print a formatted table to stdout.

    Returns
    -------
    pd.DataFrame
        Metrics table with columns:
        [variable, obs_col, metric, raw, calibrated, improvement_%]
    """

    def _rmse(pred: np.ndarray, obs: np.ndarray) -> float:
        m = np.isfinite(pred) & np.isfinite(obs)
        return float(np.sqrt(np.mean((pred[m] - obs[m]) ** 2))) if m.sum() else np.nan

    def _mae(pred: np.ndarray, obs: np.ndarray) -> float:
        m = np.isfinite(pred) & np.isfinite(obs)
        return float(np.mean(np.abs(pred[m] - obs[m]))) if m.sum() else np.nan

    def _mbe(pred: np.ndarray, obs: np.ndarray) -> float:
        """Mean Bias Error: positive = model over-predicts."""
        m = np.isfinite(pred) & np.isfinite(obs)
        return float(np.mean(pred[m] - obs[m])) if m.sum() else np.nan

    rows: List[dict] = []

    for forecast_col, obs_col in mapping.items():
        corrected_col = f"{forecast_col}{corrected_suffix}"

        missing = [c for c in (forecast_col, obs_col, corrected_col) if c not in eval_df.columns]
        if missing:
            warnings.warn(
                f"evaluate_correction: skipping '{forecast_col}' — missing columns {missing}.",
                UserWarning,
            )
            continue

        raw = eval_df[forecast_col].to_numpy(dtype=float)
        cor = eval_df[corrected_col].to_numpy(dtype=float)
        obs = eval_df[obs_col].to_numpy(dtype=float)

        for metric_name, fn in [("RMSE", _rmse), ("MAE", _mae), ("MBE", _mbe)]:
            raw_val = fn(raw, obs)
            cor_val = fn(cor, obs)

            # Improvement: reduction in absolute error magnitude (positive = better)
            if np.isfinite(raw_val) and raw_val != 0:
                improvement = (abs(raw_val) - abs(cor_val)) / abs(raw_val) * 100.0
            else:
                improvement = np.nan

            rows.append({
                "variable":      forecast_col,
                "obs_col":       obs_col,
                "metric":        metric_name,
                "raw":           raw_val,
                "calibrated":    cor_val,
                "improvement_%": improvement,
            })

    results = pd.DataFrame(rows)

    if display_table and not results.empty:
        print("\n" + "=" * 72)
        print("  BIAS CORRECTION EVALUATION — Raw vs. EQM Calibrated")
        print("=" * 72)
        header = f"{'Variable':<14} {'Obs Col':<12} {'Metric':<6} {'Raw':>10} {'Calibrated':>12} {'Improvement':>12}"
        print(header)
        print("-" * 72)
        for _, r in results.iterrows():
            imp = f"{r['improvement_%']:+.1f}%" if np.isfinite(r["improvement_%"]) else "   N/A"
            print(
                f"{r['variable']:<14} {r['obs_col']:<12} {r['metric']:<6} "
                f"{r['raw']:>10.3f} {r['calibrated']:>12.3f} {imp:>12}"
            )
        print("=" * 72)
        print("  Improvement% = reduction in |error| relative to raw forecast.\n"
              "  Positive = calibration improved the forecast.\n")

    return results


# ---------------------------------------------------------------------------
# Module-level helpers (unchanged from previous version)
# ---------------------------------------------------------------------------

def _list_csv_files(root: "str | Path") -> List[Path]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*.csv") if p.is_file()])


def load_training_data(compare_result_dir: "str | Path") -> Optional[pd.DataFrame]:
    """Load comparison CSVs from compare_result_dir and concatenate them."""
    files = _list_csv_files(compare_result_dir)
    if not files:
        return None
    dfs = []
    for p in files:
        try:
            dfs.append(pd.read_csv(p))
        except Exception:
            continue
    return pd.concat(dfs, ignore_index=True) if dfs else None


def train_and_save_corrector(
    training_df: pd.DataFrame,
    output_path: "str | Path" = "bias_correction_params.pkl",
    mapping: Optional[Dict[str, str]] = None,
    datetime_col: str = "valid_time",
    n_quantiles: int = 100,
    zero_inflated_vars: Optional[frozenset] = None,
) -> Tuple["BiasCorrector", str]:
    """Convenience: fit a BiasCorrector and save it in one call."""
    corrector = BiasCorrector(
        n_quantiles=n_quantiles,
        zero_inflated_vars=zero_inflated_vars,
    ).fit(training_df, mapping=mapping, datetime_col=datetime_col)
    saved_path = corrector.save(output_path)
    return corrector, saved_path
