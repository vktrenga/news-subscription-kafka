# Kafka-Based News Notification Service

A scalable, event-driven **News Notification Service** built using **Apache Kafka**, **Docker**, and **PostgreSQL**.
This system publishes news events and routes them to multiple notification channels such as **Email**, **SMS**, and **Push Notifications** with retry and dead-letter handling.

---

## 🚀 Tech Stack

* **Message Broker**: Apache Kafka
* **Containerization**: Docker
* **Orchestration**: Docker Compose
* **Kafka Monitoring UI**: Kafka UI
* **Database**: PostgreSQL
* **DB Management UI**: pgAdmin
* **Shared Database**: Centralized DB for notification tracking and status storage

---

# 📌 System Overview

This system implements an asynchronous notification processing pipeline using Kafka.

### 🔄 Flow Diagram

```
Client → Publish API → Kafka Topic → Router Service → 
[Email | SMS | Push Services] → DB Update
                                   ↓
                              Retry (3 times)
                                   ↓
                           Dead Letter Topic (DLT)
```

---

# 🏗 Architecture Components

## 1️⃣ Publish API

* Accepts incoming news payload.
* Publishes the message to a Kafka topic (`news-topic`).

### Example Request

```json
POST /publish
{
  "newsId": "123",
  "title": "Breaking News",
  "content": "Important announcement",
  "channels": ["EMAIL", "SMS", "PUSH"]
}
```

---

## 2️⃣ Kafka Topic

* `news-topic` → Receives published news.
* `notification-dlt` → Stores failed notifications after retries.

---

## 3️⃣ Router Service

* Consumes messages from `news-topic`.
* Determines delivery channels (Email/SMS/Push).
* Reads **10,000 users** from database.
* Processes users **batch-wise (100 per batch)**.
* Publishes to respective channel services.

---

## 4️⃣ Notification Services

Each channel (Email/SMS/Push):

* Processes notifications
* On success:

  * Stores success status in DB
* On failure:

  * Retries up to **3 times**
  * If still fails:

    * Publishes to `notification-dlt`
    * Stores failure record in DB

---

# 🔁 Retry & Dead Letter Strategy

| Attempt          | Action                                                 |
| ---------------- | ------------------------------------------------------ |
| 1                | Try sending notification                               |
| 2                | Retry                                                  |
| 3                | Retry                                                  |
| After 3 Failures | Move to Dead Letter Topic (DLT) + Mark as FAILED in DB |

---

# 🗄 Database Schema (Sample)

### notifications

| Column      | Type      | Description        |
| ----------- | --------- | ------------------ |
| id          | UUID      | Unique ID          |
| news_id     | VARCHAR   | News reference     |
| user_id     | VARCHAR   | User ID            |
| channel     | VARCHAR   | EMAIL / SMS / PUSH |
| status      | VARCHAR   | SUCCESS / FAILED   |
| retry_count | INT       | Retry attempts     |
| created_at  | TIMESTAMP | Timestamp          |

---

# 🐳 Running the Project

## 1️⃣ Start Services

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

## 2️⃣ Kafka UI

Access Kafka UI:

```
http://localhost:8080
```

* View topics
* Monitor consumers
* Inspect messages

---

## 3️⃣ PostgreSQL

Database runs on:

```
localhost:5432
```

pgAdmin:

```
http://localhost:5050
```

---

# ⚙️ Configuration

Environment variables example:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=newsdb
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
```

---

# 📊 Performance Design

* Batch processing (100 users per batch)
* Horizontal scalability (multiple router instances)
* Kafka partitioning support
* Asynchronous processing
* Retry mechanism with DLT fallback

---

# 🔒 Reliability Features

* At-least-once delivery
* Retry with backoff
* Dead Letter Topic
* Persistent storage in PostgreSQL
* Consumer group support

---

# 📂 Project Structure

```
news-notification-service/
│
├── publish-service/
├── router-service/
├── email-service/
├── sms-service/
├── push-service/
├── docker-compose.yml
└── README.md
```

---

# 🧪 Testing

1. Start services
2. Call Publish API
3. Monitor:

   * Kafka UI
   * Database records
   * Logs
4. Verify success & failed messages

---

# 📈 Scalability

* Increase Kafka partitions
* Scale router & notification services horizontally
* Optimize DB indexing for large user sets
* Implement caching for user fetch

Here’s a clear explanation of the **implemented features** in your Kafka-based News Notification Service and **why each feature is important**.

---

# ✅ Implemented Features & Their Purpose

---

## 1️⃣ Event-Driven Architecture (Using Apache Kafka)

### ✅ What is implemented

* Publish API pushes news events to Kafka.
* Router service consumes and processes asynchronously.
* Decoupled services (Email, SMS, Push).

### 🎯 Why this feature?

* **Loose coupling** between services.
* **High scalability** (independent scaling).
* **Better fault tolerance**.
* Handles large volume (10,000+ users) efficiently.

---

## 2️⃣ Publish API

### ✅ What is implemented

* REST API to accept news.
* Publishes event to `news-topic`.

### 🎯 Why this feature?

* Provides a **single entry point**.
* Keeps producer logic separate from notification logic.
* Makes system extensible for future integrations.

---

## 3️⃣ Router-Based Channel Distribution

### ✅ What is implemented

* Router consumes news event.
* Identifies required channels (Email / SMS / Push).
* Routes messages accordingly.

### 🎯 Why this feature?

* Centralized **decision-making layer**.
* Makes adding new channels easy.
* Reduces duplication of routing logic.

---

## 4️⃣ Batch Processing (100 Users per Batch)

### ✅ What is implemented

* Reads 10,000 users.
* Processes in batches of 100.

### 🎯 Why this feature?

* Prevents memory overload.
* Improves throughput.
* Controls DB and network load.
* Supports large-scale user processing.

Without batching, system could crash or slow down significantly.

---

## 5️⃣ Retry Mechanism (3 Attempts)

### ✅ What is implemented

* Retry notification up to 3 times.
* Track retry count.
* Update status in DB.

### 🎯 Why this feature?

* Handles **temporary failures** (network issues, SMTP timeout, etc.).
* Increases delivery success rate.
* Prevents immediate message loss.

---

## 6️⃣ Dead Letter Topic (DLT)

### ✅ What is implemented

* Failed after 3 retries → moved to `notification-dlt`.
* Failure stored in database.

### 🎯 Why this feature?

* Prevents infinite retry loops.
* Enables later analysis & reprocessing.
* Improves system reliability and observability.

This is a critical production-grade pattern.

---

## 7️⃣ Status Persistence in PostgreSQL

### ✅ What is implemented

* Store SUCCESS / FAILED status.
* Store retry count.
* Track per user & channel.

### 🎯 Why this feature?

* Provides audit trail.
* Enables reporting & analytics.
* Supports debugging.
* Required for compliance in enterprise systems.

---

## 8️⃣ Containerized Deployment (Using Docker + Docker Compose)

### ✅ What is implemented

* Kafka, DB, services run in containers.
* One-command startup (`docker-compose up`).

### 🎯 Why this feature?

* Easy local setup.
* Environment consistency.
* Simplifies deployment.
* Supports CI/CD pipelines.

---

## 9️⃣ Kafka Monitoring with Kafka UI

### ✅ What is implemented

* View topics.
* Monitor consumers.
* Inspect messages.

### 🎯 Why this feature?

* Debug message flow.
* Monitor lag.
* Validate retry/DLT behavior.

Essential for troubleshooting distributed systems.

---

## 🔟 Shared Database Design

### ✅ What is implemented

* Central DB used by all services.
* Shared notification tracking table.

### 🎯 Why this feature?

* Single source of truth.
* Avoids data inconsistency.
* Easier reporting.

---

# 🔥 Architectural Benefits Achieved

| Feature          | Business Benefit                  |
| ---------------- | --------------------------------- |
| Kafka            | High throughput & decoupling      |
| Batch Processing | Efficient large user handling     |
| Retry Logic      | Improved reliability              |
| DLT              | Production-grade failure handling |
| DB Persistence   | Audit & reporting                 |
| Containerization | Easy deployment                   |
| Router Pattern   | Scalable architecture             |

---

# 🏆 Overall System Qualities Achieved

* ✅ Scalability
* ✅ Fault Tolerance
* ✅ Reliability
* ✅ Observability
* ✅ Extensibility
* ✅ Production-Ready Design
* ✅ High Throughput Processing

