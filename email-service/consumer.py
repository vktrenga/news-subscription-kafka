import json
import time
from kafka import KafkaConsumer, KafkaProducer
from shared_lib.repository import EventRepository


class EmailService:

    MAX_RETRY = 3
    repo = EventRepository()

    def __init__(self):
        self.consumer = KafkaConsumer(
            "email.topic",
            bootstrap_servers="kafka:9092",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="email_group",
            auto_offset_reset="earliest",
            enable_auto_commit=False
        )

        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=5
        )
                

    def send_bulk_email(self, users, title, content):
        """
        Replace this with real email provider API (SES / SendGrid / SMTP)
        """
        print(f"Sending email to {len(users)} users | Title: {title}")

        # simulate email sending delay
        time.sleep(0.5)

        print("Email sent successfully ✅")

    def start(self):
        print("Email Service Started 🚀")

        for message in self.consumer:
            data = message.value

            print("[EMAIL RECEIVED] ->", data)

            try:
                self.send_bulk_email(
                    users=data["users"],
                    title=data["title"],
                    content=data["content"]
                )

                # commit only after successful send

                

                self.repo.save_event(
                    service_name="email-service",
                    topic=message.topic,
                    partition=message.partition,
                    kafka_offset=message.offset,
                    event_key=str(message.key),
                    payload=data,
                    status='Done'
                )
                self.consumer.commit()

                print("Offset committed ✅\n")

            except Exception as e:
                print("Email sending failed ❌", e)

                if data["retry"] < self.MAX_RETRY:
                    data["retry"] += 1
                    print(f"Retrying... Attempt {data['retry']}")
                    self.producer.send("email.topic", data)
                else:
                    print("Max retry reached. Sending to DLQ")
                    self.producer.send("email.topic.dlq", data)
                    self.repo.save_event(
                        service_name="email-service",
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
    service = EmailService()
    service.start()
