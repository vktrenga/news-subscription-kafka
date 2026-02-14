from kafka import KafkaConsumer, KafkaProducer
import json
import uuid
import time
from kafka import KafkaConsumer

def wait_for_kafka():
    while True:
        try:
            consumer = KafkaConsumer(
                "news.published",
                bootstrap_servers="kafka:9092",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="router_group",
                auto_offset_reset="earliest",
                api_version=(2, 8, 1)  # prevents version check failure
            )
            print("Connected to Kafka ✅")
            return consumer
        except Exception as e:
            print("Kafka not ready, retrying in 5s...")
            time.sleep(5)

consumer = wait_for_kafka()

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

for message in consumer:
    event = message.value

    base_payload = {
        "notification_id": str(uuid.uuid4()),
        "title": event["title"],
        "content": event["content"],
        "retry": 0
    }

    producer.send("email.topic", {**base_payload, "email": "user@example.com"})
    producer.send("sms.topic", {**base_payload, "phone": "+911234567890"})
    producer.send("push.topic", {**base_payload, "device_token": "device123"})
    producer.flush()
