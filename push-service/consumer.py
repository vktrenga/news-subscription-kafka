from kafka import KafkaConsumer, KafkaProducer
import json
import random
import time
from shared_lib.repository import save_event

consumer = KafkaConsumer(
    "push.topic",
    bootstrap_servers="kafka:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="push_group",
    auto_offset_reset="earliest"
)

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

processed_ids = set()
MAX_RETRY = 3

for message in consumer:
    print("[PUSH.TOPIC RECEIVED] ->", message.value)
    data = message.value
    save_event(
        "push-service",
        message.topic,
        message.partition,
        message.offset,
        str(message.key),
        data
    )
    if data["notification_id"] in processed_ids:
        continue

    try:
        if random.choice([False, True]):
            raise Exception("Simulated Failure")

        print("[PUSH.TOPIC SENT] ->", data)
        processed_ids.add(data["notification_id"])

    except Exception as e:
        print("[PUSH.TOPIC FAILED] ->", e)

        if data["retry"] < MAX_RETRY:
            data["retry"] += 1
            time.sleep(1)
            producer.send("push.topic", data)
        else:
            producer.send("push.topic.dlq", data)
