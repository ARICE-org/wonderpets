#!/bin/bash
# ==============================================================================
# FuXi-S2S Model Service Entrypoint
# ==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  FuXi-S2S Model Service               ${NC}"
echo -e "${CYAN}========================================${NC}"

# ==============================================================================
# Normalize environment variables
# ==============================================================================
normalize_env() {
    if [[ -z "${MONGO_DB_URI:-}" && -n "${MONGO_URI:-}" ]]; then
        export MONGO_DB_URI="$MONGO_URI"
    fi
    if [[ -z "${MONGO_URI:-}" && -n "${MONGO_DB_URI:-}" ]]; then
        export MONGO_URI="$MONGO_DB_URI"
    fi
}

# ==============================================================================
# Setup CDS API credentials
# ==============================================================================
setup_cds_credentials() {
    # Remove if it's a directory (bad mount)
    if [[ -d /root/.cdsapirc ]]; then
        rm -rf /root/.cdsapirc
    fi
    
    if [[ -f /root/.cdsapirc ]]; then
        echo -e "${GREEN}[Setup] Using mounted CDS API credentials${NC}"
    elif [[ -n "$CDS_API_KEY" && -n "$CDS_API_URL" ]]; then
        echo -e "${GREEN}[Setup] Configuring CDS API from environment${NC}"
        cat > /root/.cdsapirc << EOF
url: $CDS_API_URL
key: $CDS_API_KEY
EOF
    else
        echo -e "${YELLOW}[Warning] No CDS API credentials found${NC}"
    fi
}

# ==============================================================================
# Check GPU
# ==============================================================================
check_gpu() {
    echo -e "${CYAN}[GPU] Checking NVIDIA GPU...${NC}"
    python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')" 2>/dev/null || echo "GPU check failed"
}

# ==============================================================================
# Show help
# ==============================================================================
show_help() {
    echo ""
    echo -e "${GREEN}FuXi-S2S Model Service Commands:${NC}"
    echo ""
    echo "  ${CYAN}serve${NC}     - Start FastAPI server (default)"
    echo "  ${CYAN}pipeline${NC}  - Run full forecast pipeline"
    echo "  ${CYAN}download${NC}  - Download ERA5 data"
    echo "  ${CYAN}inference${NC} - Run model inference"
    echo "  ${CYAN}store${NC}     - Store forecasts to MongoDB"
    echo "  ${CYAN}shell${NC}     - Interactive shell"
    echo ""
}

# ==============================================================================
# Main
# ==============================================================================
normalize_env
setup_cds_credentials

case "${1:-serve}" in
    serve)
        check_gpu
        echo -e "${GREEN}[Server] Starting FastAPI on port ${PORT:-8002}...${NC}"
        exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8002}"
        ;;
    pipeline)
        shift
        check_gpu
        echo -e "${CYAN}[Pipeline] Running full forecast pipeline...${NC}"
        python -m core.pipeline "$@"
        ;;
    download)
        shift
        echo -e "${CYAN}[Download] Downloading ERA5 data...${NC}"
        python -m core.download_era5 "$@"
        ;;
    inference)
        shift
        check_gpu
        echo -e "${CYAN}[Inference] Running model inference...${NC}"
        python -m core.inference "$@"
        ;;
    store)
        shift
        echo -e "${CYAN}[Store] Storing forecasts to MongoDB...${NC}"
        python -m core.store_forecasts "$@"
        ;;
    shell)
        exec /bin/bash
        ;;
    --help|-h|help)
        show_help
        ;;
    *)
        exec "$@"
        ;;
esac
