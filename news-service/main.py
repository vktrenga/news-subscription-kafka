from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import uuid

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


class NewsEvent(BaseModel):
    title: str
    content: str
    topic: str

@app.post("/publish")
def publish(event: NewsEvent):
    event_data = {
        "event_id": str(uuid.uuid4()),
        "title": event.title,
        "content": event.content,
        "topic": event.topic
    }
    print("[NEWS.PUBLISHED] ->", event_data)
    producer.send("news.published", event_data)
    producer.flush()
    return {"message": "News published successfully"}
