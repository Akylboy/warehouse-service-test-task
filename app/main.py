from fastapi import FastAPI
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base
from app.api import movements, warehouses
from app.kafka_consumer import WarehouseKafkaConsumer

app = FastAPI(title=settings.PROJECT_NAME)

Base.metadata.create_all(bind=engine)

app.include_router(movements.router, prefix="/api/movements", tags=["movements"])
app.include_router(warehouses.router, prefix="/api/warehouses", tags=["warehouses"])


@app.on_event("startup")
async def startup_event():
    """Запуск Kafka"""

    config = {
        'bootstrap.servers': settings.KAFKA_BROKER,
        'group.id': 'warehouse-monitoring',
        'auto.offset.reset': 'earliest',
        'socket.connection.setup.timeout.ms': 10000,
        'reconnect.backoff.max.ms': 10000
    }

    kafka_consumer = WarehouseKafkaConsumer(config=config, topic='warehouse_movements')
    kafka_consumer.consume_messages()


