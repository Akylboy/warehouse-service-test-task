from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.services.services import get_warehouse_stock
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{warehouse_id}/products/{product_id}")
async def get_stock(warehouse_id: UUID, product_id: UUID, db: Session = Depends(get_db)):
    try:
        return await get_warehouse_stock(db, str(warehouse_id), str(product_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
