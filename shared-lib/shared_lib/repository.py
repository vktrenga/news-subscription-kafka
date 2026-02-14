from .db import SessionLocal
from sqlalchemy import text
import json

def create_table():
    session = SessionLocal()
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
    session.close()


def save_event(service, topic, partition, offset, key, payload):
    create_table()
    session = SessionLocal()
    session.execute(text("""
        INSERT INTO consumer_events
        (service_name, topic, partition, kafka_offset, event_key, payload, status)
        VALUES (:service, :topic, :partition, :kafka_offset, :key, :payload, :status)
    """), {
        "service": service,
        "topic": topic,
        "partition": partition,
        "kafka_offset": offset,
        "key": key,
        "payload": json.dumps(payload),
        "status": "RECEIVED"
    })
    session.commit()
    session.close()
