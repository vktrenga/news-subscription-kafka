from .db import SessionLocal
from sqlalchemy import text
import json


class EventRepository:

    def __init__(self):
        self.create_table()

    def create_table(self):
        session = SessionLocal()
        try:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS consumer_events (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(50),
                    topic VARCHAR(100),
                    partition INT,
                    kafka_offset BIGINT,
                    event_key TEXT,
                    payload JSONB,
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            session.commit()
        finally:
            session.close()

    def save_event(self, service_name, topic, partition, kafka_offset, event_key, payload, status="RECEIVED"):
        session = SessionLocal()
        try:
            session.execute(text("""
                INSERT INTO consumer_events
                (service_name, topic, partition, kafka_offset, event_key, payload, status)
                VALUES (:service, :topic, :partition, :kafka_offset, :event_key, :payload, :status)
            """), {
                "service": service_name,
                "topic": topic,
                "partition": partition,
                "kafka_offset": kafka_offset,
                "event_key": event_key,
                "payload": json.dumps(payload),
                "status": status
            })
            session.commit()
        finally:
            session.close()
