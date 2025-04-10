from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import String, Integer, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class WarehouseMovement(Base):
    __tablename__ = "warehouse_movements"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Уникальный идентификатор записи"
    )
    movement_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True
    )

    warehouse_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_warehouse: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        comment="Дата создания записи"
    )

class WarehouseStock(Base):
    """Модель текущих остатков товаров на складах"""

    __tablename__ = "warehouse_stocks"

    warehouse_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Идентификатор склада"
    )

    product_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="Идентификатор товара"
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Текущее количество товара на складе"
    )

    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate="now()",
        comment="Дата последнего обновления остатков"
    )
