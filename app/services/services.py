from datetime import datetime
from typing import Dict
from sqlalchemy.orm import Session
from app.models.models import WarehouseMovement, WarehouseStock
from app.schemas.schemas import MovementResponse, WarehouseStockResponse
from app.core.exceptions import InsufficientStockError

def process_kafka_message(db: Session, message: Dict):
    """Обрабатывает входящее сообщение Kafka и обновляет базу данных.

    :param db: Сессия базы данных
    :param message: Сообщение Kafka в формате словаря

    :raises ValueError: Если сообщение некорректно
    """
    try:
        # Извлекаем данные из сообщения
        data = message['data']
        movement_id = data['movement_id']
        warehouse_id = data['warehouse_id']
        product_id = data['product_id']
        quantity = data['quantity']
        event_type = data['event']
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', ''))

        # Создаем запись о перемещении
        movement = WarehouseMovement(
            movement_id=movement_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
            event_type=event_type,
            quantity=quantity,
            timestamp=timestamp,
            source_warehouse=message.get('source')
        )
        db.add(movement)

        # Обновляем уровень запасов
        stock = db.query(WarehouseStock).filter_by(
            warehouse_id=warehouse_id,
            product_id=product_id
        ).first()

        # Если запись о запасах не найдена, создаем новую
        if not stock:
            stock = WarehouseStock(
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=0
            )
            db.add(stock)

        # Обрабатываем прибытие или убытие товара
        if event_type == 'arrival':
            stock.quantity += quantity
        else:  # departure
            if stock.quantity < quantity:
                raise ValueError(f"Insufficient stock for product {product_id} in warehouse {warehouse_id}")
            stock.quantity -= quantity

        stock.last_updated = datetime.utcnow()
        db.commit()

    except KeyError as e:
        raise ValueError(f"Missing required field in message: {e}")


def get_movement_info(db: Session, movement_id: str) -> MovementResponse:
    """Получает полную информацию о перемещении.

    :param db: Сессия базы данных
    :param movement_id: ID перемещения
    :return: Информация о перемещении
    :raises ValueError: Если перемещение не найдено
    """
    # Получаем все записи о перемещении
    movements = db.query(WarehouseMovement).filter_by(
        movement_id=movement_id
    ).order_by(WarehouseMovement.timestamp).all()

    if not movements:
        raise ValueError(f"Movement {movement_id} not found")

    # Находим события отправки и получения
    departure = next((m for m in movements if m.event_type == 'departure'), None)
    arrival = next((m for m in movements if m.event_type == 'arrival'), None)

    if not departure and not arrival:
        raise ValueError(f"No valid events found for movement {movement_id}")

    response = MovementResponse(
        movement_id=movement_id,
        product_id=movements[0].product_id,
        quantity=movements[0].quantity
    )

    # Заполняем информацию о отправке
    if departure:
        response.departure_warehouse = departure.warehouse_id
        response.departure_time = departure.timestamp

    # Заполняем информацию о получении
    if arrival:
        response.arrival_warehouse = arrival.warehouse_id
        response.arrival_time = arrival.timestamp

    # Рассчитываем длительность перевозки и разницу в количестве
    if departure and arrival:
        response.transit_duration = (
                arrival.timestamp - departure.timestamp
        ).total_seconds()
        response.quantity_difference = arrival.quantity - departure.quantity

    return response


def get_warehouse_stock(
        db: Session,
        warehouse_id: str,
        product_id: str
) -> WarehouseStockResponse:
    """Получает текущий уровень запасов товара на складе.

    :param db: Сессия базы данных
    :param warehouse_id: ID склада
    :param product_id: ID товара
    :return: Информация о запасах
    :raises InsufficientStockError: Если склад/товар не найдены
    """
    # Получаем информацию о запасах
    stock = db.query(WarehouseStock).filter_by(
        warehouse_id=warehouse_id,
        product_id=product_id
    ).first()

    if not stock:
        raise InsufficientStockError(f"Insufficient stock for product {product_id} in warehouse {warehouse_id}")

    return WarehouseStockResponse(
        warehouse_id=warehouse_id,
        product_id=product_id,
        quantity=stock.quantity,
        last_updated=stock.last_updated
    )