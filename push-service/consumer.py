from kafka import KafkaConsumer, KafkaProducer
import json
import random
import time
from shared_lib.repository import EventRepository

class NotificationService:

    MAX_RETRY = 3
    repo = EventRepository()

    def __init__(self):
        self.consumer = KafkaConsumer(
            "push.topic",
            bootstrap_servers="kafka:9092",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="notification_group",
            auto_offset_reset="earliest",
            enable_auto_commit=False
        )

        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=5
        )

    def send_push_notification(self, users, title, content):
        print(f"Sending Push to {len(users)} users | {title} {content}")
        time.sleep(0.2)
     
        print("Push sent successfully ✅")

    def start(self):
        print("Notification Service Started 🚀")

        for message in self.consumer:
            data = message.value

            try:
                self.send_push_notification(
                    users=data["users"],
                    title=data["title"],
                    content=data["content"]
                )
                self.repo.save_event(
                    service_name="push-service",
                    topic=message.topic,
                    partition=message.partition,
                    kafka_offset=message.offset,
                    event_key=str(message.key),
                    payload=data,
                    status='Done'
                )
                self.consumer.commit()
                print("Push Offset committed ✅\n")

            except Exception as e:
                print("Push failed ❌", e)

                if data["retry"] < self.MAX_RETRY:
                    data["retry"] += 1
                    self.producer.send("notification.topic", data)
                else:
                    self.producer.send("notification.topic.dlq", data)
                    self.repo.save_event(
                        service_name="push-service",
                        topic=message.topic,
                        partition=message.partition,
                        kafka_offset=message.offset,
                        event_key=str(message.key),
                        payload=data,
                        status='FAILED'
                    )

                self.producer.flush()
                self.consumer.commit()


if __name__ == "__main__":
    NotificationService().start()
