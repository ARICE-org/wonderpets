from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.farmer import Farmer as FarmerModel
from app.schemas.farmer import FarmerBase, FarmerCreate, FarmerUpdate, Farmer

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("/", response_model=List[FarmerBase])
def list_farmers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(FarmerModel).offset(skip).limit(limit).all()


@router.get("/{farmer_id}", response_model=FarmerBase)
def get_farmer(farmer_id: str, db: Session = Depends(get_db)):
    farmer = db.get(FarmerModel, farmer_id)
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return farmer


@router.post("/", response_model=FarmerBase, status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db)):
    farmer = FarmerModel(
        first_name=payload.first_name,
        middle_name=payload.middle_name,
        last_name=payload.last_name,
        address=payload.address,
        phone_number=payload.phone_number,
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.put("/{farmer_id}", response_model=FarmerBase)
def update_farmer(farmer_id: str, payload: FarmerUpdate, db: Session = Depends(get_db)):
    farmer = db.get(FarmerModel, farmer_id)
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    # Since we used aliases (camelCase), ensure we access by field names
    for field, value in data.items():
        setattr(farmer, field, value)

    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmer(farmer_id: str, db: Session = Depends(get_db)):
    farmer = db.get(FarmerModel, farmer_id)
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(farmer)
    db.commit()
    return None
