import json
import logging
from typing import Dict, Any
from confluent_kafka import Consumer, KafkaException
from app.core.database import SessionLocal
from app.services.services import process_kafka_message

logger = logging.getLogger(__name__)


class WarehouseKafkaConsumer:
    def __init__(self, config: Dict[str, Any], topic: str = "warehouse_movements"):
        """
        Инициализация Kafka consumer

        param: config: Конфигурация
        param: topic: Topic для подписки
        """

        self.consumer = Consumer(config)
        self.topic = topic
        self.running = False

    def consume_messages(self):
        """Старт Kafka"""
        self.consumer.subscribe([self.topic])
        self.running = True
        logger.info(f"Started consuming messages from topic: {self.topic}")

        try:
            while self.running:
                msg = self.consumer.poll(1.0)

                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())

                try:
                    message_value = json.loads(msg.value().decode('utf-8'))
                    db = SessionLocal()
                    process_kafka_message(db, message_value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                finally:
                    db.close()
                    self.consumer.commit(msg)

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()

    def close(self):
        self.running = False
        self.consumer.close()
        logger.info("Kafka consumer closed")
