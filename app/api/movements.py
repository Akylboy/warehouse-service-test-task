from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.services.services import get_movement_info
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{movement_id}")
async def get_movement(movement_id: UUID, db: Session = Depends(get_db)):
    try:
        return await get_movement_info(db, str(movement_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
