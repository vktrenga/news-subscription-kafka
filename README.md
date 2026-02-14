
## Kafka-Based News Notification Service

A scalable, event-driven **News Notification Service** built using **Apache Kafka**, **Docker**, and **PostgreSQL**.

This system publishes news events and routes them to multiple notification channels (**Email, SMS, Push**) with retry handling and Dead Letter Topic (DLT) support.

> ⚠️ All channels (Email, SMS, Push) are statically configured and applied to every news event.

---

### 🚀 Tech Stack

* **Message Broker**: Apache Kafka
* **Containerization**: Docker
* **Orchestration**: Docker Compose
* **Kafka Monitoring UI**: Kafka UI
* **Database**: PostgreSQL
* **DB Management UI**: pgAdmin
* **Shared Database**: Used for notification tracking (custom structure)

---

## 📌 System Overview

This system implements an asynchronous, event-driven notification pipeline.

### 🔄 Flow Diagram

```
Client → Publish API → Kafka (news-topic) → Router Service →
Email Service
SMS Service
Push Service
        ↓
Retry (3 times)
        ↓
Dead Letter Topic (notification-dlt)
```

---

## 🏗 Architecture Components

### 1️⃣ Publish API

* Accepts incoming news payload.
* Publishes message to Kafka topic: `news-topic`.
* Channels are NOT passed in request.
* System automatically sends notification to:

  * Email
  * SMS
  * Push

### Example Request

```json
POST /publish
{
  "newsId": "123",
  "title": "Breaking News",
  "content": "Important announcement"
}
```

---

### 2️⃣ Kafka Topics

* `news-topic` → Receives published news.
* `notification-dlt` → Stores failed notifications after retries.

---

### 3️⃣ Router Service

* Consumes messages from `news-topic`.
* Automatically routes to:

  * Email Service
  * SMS Service
  * Push Service
* Fetches 10,000 users.
* Processes users in **batch size of 100**.
* Publishes notification messages per channel.

---

### 4️⃣ Notification Services (Email / SMS / Push)

Each service:

* Consumes channel-specific messages.
* Attempts delivery.
* If success:

  * Stores status in DB.
* If failure:

  * Retries up to 3 times.
  * After 3 failures:

    * Moves message to `notification-dlt`.

---

## 🔁 Retry & Dead Letter Strategy

| Attempt          | Action                       |
| ---------------- | ---------------------------- |
| 1                | Initial delivery attempt     |
| 2                | Retry                        |
| 3                | Retry                        |
| After 3 Failures | Publish to Dead Letter Topic |

This prevents infinite retries and ensures system stability.

---

## ⚙️ Execution Process (Step-by-Step)

### Step 1: Client Calls Publish API

* News payload is received.
* Message is produced to Kafka `news-topic`.

### Step 2: Router Service Consumes Event

* Router reads the news event.
* Fetches user list.
* Splits users into batches of 100.

### Step 3: Channel Distribution

* Router publishes messages to:

  * Email topic
  * SMS topic
  * Push topic

### Step 4: Notification Processing

* Each service processes its messages.
* Delivery attempt is made.
* Status is recorded.

### Step 5: Retry Handling

* If delivery fails:

  * Retry up to 3 times.
* If still failing:

  * Send to `notification-dlt`.

### Step 6: Monitoring & Observability

* Use Kafka UI to monitor topics.
* Check logs for delivery status.
* Review DLT messages for failure analysis.

---

## 🐳 Running the Project

### Start All Services

```bash
docker-compose up -d
```

This will start:

* Kafka
* Zookeeper
* Kafka UI
* PostgreSQL
* pgAdmin
* Application Services

---

### Kafka UI Access

```
http://localhost:8080
```

Monitor:

* Topics
* Consumers
* Message flow
* Dead Letter Topic

---

### PostgreSQL

```
localhost:5432
```

pgAdmin:

```
http://localhost:5050
```

---

## 📊 Performance Design

* Batch processing (100 users per batch)
* Horizontal scaling support
* Kafka partitioning
* Asynchronous processing
* Retry with DLT fallback

---

## 🔒 Reliability Features

* At-least-once delivery
* Controlled retry (max 3)
* Dead Letter Topic isolation
* Fault-tolerant message handling
* Consumer group scaling

---

## 📈 Scalability Strategy

* Increase Kafka partitions
* Run multiple router instances
* Scale notification services independently
* Optimize user fetch queries
* Add caching layer if needed

---

## 🏆 System Qualities Achieved

* ✅ High Throughput
* ✅ Horizontal Scalability
* ✅ Fault Tolerance
* ✅ Reliable Delivery
* ✅ Observability
* ✅ Production-Ready Design

