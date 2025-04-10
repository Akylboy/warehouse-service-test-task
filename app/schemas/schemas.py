from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class MovementBase(BaseModel):
    """Базовая модель данных о перемещении товара.

    :param movement_id: Уникальный идентификатор перемещения
    :type movement_id: UUID
    :param warehouse_id: Идентификатор склада
    :type warehouse_id: UUID
    :param product_id: Идентификатор товара
    :type product_id: UUID
    :param event_type: Тип события ('arrival' - прибытие, 'departure' - убытие)
    :type event_type: str
    :param quantity: Количество товара
    :type quantity: int
    :param timestamp: Временная метка события
    :type timestamp: datetime
    """
    movement_id: UUID
    warehouse_id: UUID
    product_id: UUID
    event_type: str
    quantity: int
    timestamp: datetime


class MovementResponse(BaseModel):
    """Модель ответа с полной информацией о перемещении товара.

    :param movement_id: Уникальный идентификатор перемещения
    :type movement_id: UUID
    :param departure_warehouse: Идентификатор склада отправки (опционально)
    :type departure_warehouse: Optional[UUID]
    :param arrival_warehouse: Идентификатор склада получения (опционально)
    :type arrival_warehouse: Optional[UUID]
    :param product_id: Идентификатор товара
    :type product_id: UUID
    :param quantity: Количество товара
    :type quantity: int
    :param departure_time: Время отправки (опционально)
    :type departure_time: Optional[datetime]
    :param arrival_time: Время прибытия (опционально)
    :type arrival_time: Optional[datetime]
    :param transit_duration: Длительность перевозки в секундах (опционально)
    :type transit_duration: Optional[float]
    :param quantity_difference: Разница в количестве товара (опционально)
    :type quantity_difference: Optional[int]
    """
    movement_id: UUID
    departure_warehouse: Optional[UUID] = None
    arrival_warehouse: Optional[UUID] = None
    product_id: UUID
    quantity: int
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    transit_duration: Optional[float] = None
    quantity_difference: Optional[int] = None


class WarehouseStockResponse(BaseModel):
    """Модель ответа с информацией о запасах товара на складе.

    :param warehouse_id: Идентификатор склада
    :type warehouse_id: UUID
    :param product_id: Идентификатор товара
    :type product_id: UUID
    :param quantity: Текущее количество товара на складе
    :type quantity: int
    :param last_updated: Время последнего обновления информации
    :type last_updated: datetime
    """
    warehouse_id: UUID
    product_id: UUID
    quantity: int
    last_updated: datetime