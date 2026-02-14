import json
import uuid
import time
from kafka import KafkaConsumer, KafkaProducer


class RouterService:

    def __init__(self):
        self.consumer = self._wait_for_kafka()

        # Optimized Producer Configuration
        self.producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            linger_ms=10,            # small batching delay for performance
            batch_size=16384,        # batch size in bytes
            acks="all",              # strongest durability guarantee
            retries=5
        )

    def _wait_for_kafka(self):
        """
        Wait until Kafka is available
        """
        while True:
            try:
                consumer = KafkaConsumer(
                    "news.published",
                    bootstrap_servers="kafka:9092",
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    group_id="router_group",
                    auto_offset_reset="earliest",
                    enable_auto_commit=False,  # manual commit for reliability
                    api_version=(2, 8, 1)
                )
                print("Connected to Kafka ✅")
                return consumer
            except Exception as e:
                print(f"Kafka not ready, retrying in 5s... Error: {e}")
                time.sleep(5)

    def get_users(self, limit=100, offset=0):
        """
        Simulated DB fetch for users.
        Replace with real DB query using LIMIT/OFFSET.
        """
        TOTAL_USERS = 10000  # simulate DB

        if offset >= TOTAL_USERS:
            return []

        users = []

        for i in range(limit):
            index = offset + i
            if index >= TOTAL_USERS:
                break

            users.append({
                "user_id": index,
                "email": f"user{index}@mail.com",
                "phone": f"+91123456{index:04d}",
                "device_token": f"device_token_{index}"
            })

        return users

    def publish_news_batches(self, event):
        """
        Split users into batches of 100
        and publish to email, sms, and push topics.
        """
        base_payload = {
            "notification_id": str(uuid.uuid4()),
            "title": event["title"],
            "content": event["content"],
            "retry": 0
        }

        offset = 0
        total_batches = 0

        while True:
            users = self.get_users(100, offset)
            if not users:
                break

            email_users = [u["email"] for u in users]
            sms_users = [u["phone"] for u in users]
            push_users = [u["device_token"] for u in users]

            self.producer.send("email.topic", {**base_payload, "users": email_users})
            self.producer.send("sms.topic", {**base_payload, "users": sms_users})
            self.producer.send("push.topic", {**base_payload, "users": push_users})

            offset += 100
            total_batches += 1

        self.producer.flush()
        print(f"Published {total_batches} batches successfully ✅")

    def start(self):
        """
        Start consuming news events.
        """
        print("Router Service Started 🚀")

        for message in self.consumer:
            try:
                event = message.value
                print("Received news:", event)

                self.publish_news_batches(event)

                # Commit offset ONLY after successful publish
                self.consumer.commit()
                print("Offset committed ✅\n")

            except Exception as e:
                print(f"Error processing message: {e}")
                # No commit → Kafka will retry


if __name__ == "__main__":
    router = RouterService()
    router.start()
