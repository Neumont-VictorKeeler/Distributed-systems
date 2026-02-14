from kafka import KafkaProducer
import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.topic = os.getenv("KAFKA_TOPIC_NOTIFICATIONS", "email-notifications")
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Kafka producer initialized successfully. Bootstrap servers: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def send_notification(self, event_type: str, data: Dict[str, Any]):
        if not self.producer:
            logger.warning("Kafka producer not initialized. Skipping notification.")
            return
        
        try:
            message = {
                "event_type": event_type,
                "data": data
            }
            
            future = self.producer.send(self.topic, value=message)
            future.get(timeout=10)
            logger.info(f"Notification sent: {event_type}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def close(self):
        if self.producer:
            self.producer.close()


notification_producer = NotificationProducer()

