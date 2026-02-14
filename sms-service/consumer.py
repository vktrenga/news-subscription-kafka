import json
import time
from kafka import KafkaConsumer, KafkaProducer
from shared_lib.repository import EventRepository


class SmsService:

    MAX_RETRY = 3
    repo = EventRepository()

    def __init__(self):
        self.consumer = KafkaConsumer(
            "sms.topic",
            bootstrap_servers="kafka:9092",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="sms_group",
            auto_offset_reset="earliest",
            enable_auto_commit=False
        )

        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=5
        )

    def send_bulk_sms(self, users, content):
        print(f"Sending SMS to {len(users)} users")
        time.sleep(0.3)
        print("SMS sent successfully ✅")

    def start(self):
        print("SMS Service Started 🚀")

        for message in self.consumer:
            data = message.value

            try:
                self.send_bulk_sms(
                    users=data["users"],
                    content=data["content"]
                )

                self.repo.save_event(
                    service_name="sms-service",
                    topic=message.topic,
                    partition=message.partition,
                    kafka_offset=message.offset,
                    event_key=str(message.key),
                    payload=data,
                    status='Done'
                )
                self.consumer.commit()

                print("SMS Offset committed ✅\n")

            except Exception as e:
                print("SMS failed ❌", e)

                if data["retry"] < self.MAX_RETRY:
                    data["retry"] += 1
                    self.producer.send("sms.topic", data)
                else:
                    self.producer.send("sms.topic.dlq", data)
                    self.repo.save_event(
                        service_name="sms-service",
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
    SmsService().start()
