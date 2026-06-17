# 🚀 AMFI Mutual Fund Data Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)

## 📌 Executive Summary
The **AMFI Mutual Fund Data Intelligence Platform** is a full-stack, enterprise-grade financial analytics application. It is engineered to autonomously ingest, process, and visualize real-time and historical Mutual Fund data from the Association of Mutual Funds in India (AMFI). 

Built with scalability and high performance in mind, this platform leverages a decoupled architecture featuring an asynchronous Python backend and a highly reactive Next.js frontend. It empowers users with advanced portfolio insights, fund overlap analysis, automated reporting, and rich data visualization.

---

## 🏗️ Architecture Overview
The system follows a microservice-oriented design, orchestrated via **Docker Compose**. It ensures distinct separation of concerns across data ingestion, analytical processing, API serving, and user interface.

1. **Ingestion Layer (Scraper)**: Asynchronous crawlers fetching real-time NAVs, metadata, and AUM details with robust retry and fallback mechanisms.
2. **Processing Layer (Pipeline)**: Dedicated analytical engines utilizing Pandas/NumPy for heavy computations like portfolio overlaps and data enrichment.
3. **API Layer (Backend)**: An asynchronous RESTful API serving data via FastAPI, handling authentication, scheduling, and database interactions.
4. **Presentation Layer (Frontend)**: A server-rendered Next.js dashboard providing interactive charts and financial comparisons.
5. **Infrastructure**: PostgreSQL for persistent storage, managed via SQLAlchemy ORM and Alembic migrations, with pgAdmin for database administration.

---

## 🛠️ Comprehensive Technology Stack

### 🔹 Backend & API (Python)
- **FastAPI**: Chosen for its high performance, native `asyncio` support, and automatic OpenAPI documentation generation.
- **Pydantic V2**: Enforces strict data validation, schema definition, and environment settings management.
- **SQLAlchemy 2.0 & asyncpg**: Fully asynchronous ORM paired with a high-performance PostgreSQL driver to handle high-throughput financial transactions without blocking the event loop.
- **Alembic**: Robust database schema migration management.
- **Passlib & PyJWT**: Secure user authentication utilizing `bcrypt` hashing and stateless JSON Web Tokens (JWT).

### 🔹 Data Engineering & Pipeline
- **Pandas & NumPy**: Employed for vectorized, high-speed computations of complex financial metrics, portfolio overlaps, and historical trend analysis.
- **BeautifulSoup4 & HTTPX**: Modern, asynchronous scraping infrastructure for reliable ingestion of AMFI data, complete with custom exception handling and automated retries.
- **APScheduler**: Distributed background task scheduling handling automated nightly data ingests and recurring analytical jobs.
- **ReportLab & OpenPyXL**: Dynamic programmatic generation of PDF and Excel financial reports for end-users.

### 🔹 Frontend Dashboard (TypeScript/JavaScript)
- **Next.js 14 (App Router)**: Leverages Server-Side Rendering (SSR) and Server Components for optimal SEO, rapid first-contentful-paint, and robust routing.
- **React 18**: Component-driven architecture utilizing the latest concurrency features.
- **SWR (State While Revalidate)**: Highly efficient, cache-first data fetching strategy ensuring the UI is always synced with the backend without redundant network requests.
- **Tailwind CSS**: Utility-first CSS framework enabling a highly responsive, modern, and customized design system.
- **Recharts**: Declarative, responsive charting library utilized for rendering dynamic financial data (NAVs, AUM growth, comparisons).
- **Lucide-React**: Consistent, lightweight, and clean iconography.

### 🔹 DevOps & Infrastructure
- **Docker & Docker Compose**: Seamless multi-container orchestration ensuring parity across development, staging, and production environments.
- **PostgreSQL 15**: Enterprise-grade relational database optimized for complex aggregations and financial record persistence.
- **pytest & pytest-asyncio**: Comprehensive, asynchronous testing suite designed to ensure the highest degree of financial accuracy and platform stability.
- **pgAdmin**: Containerized database management tool for easy inspection and querying of the PostgreSQL instance.

---

## 🌟 Key Features
*   **Automated Ingestion**: Scheduled scrapers pull the latest NAVs daily from AMFI, seamlessly falling back to cached files upon network degradation.
*   **Advanced Analytics Engine**: Computes fund overlaps and enriches raw data, providing actionable insights into portfolio diversification.
*   **Interactive Dashboard**: Users can visually compare funds, analyze historical performance, and track customized portfolios.
*   **Secure Authentication**: Role-based access control protecting user portfolios and sensitive report generations.
*   **Dynamic Reporting**: Exports complex analytical views directly to highly formatted Excel or PDF files on the fly.
*   **Resilience & Logging**: Custom middlewares track latency and log all errors, guaranteeing high observability.

---

## 📂 Project Structure

```bash
amfi-dashboard/
├── api/             # FastAPI Application (Routers, Middlewares, Dependencies, Services)
├── config/          # Application & Environment Configurations (Pydantic Settings)
├── dashboard/       # Next.js 14 Frontend Application (App Router, Components, Hooks)
├── database/        # SQLAlchemy Models, Alembic Migrations, and DB Session Management
├── pipeline/        # Pandas/NumPy Data Processing Engines (Overlap & Enrichment)
├── scraper/         # Async HTTPX/BS4 Scrapers for AMFI data ingestion
├── scheduler/       # APScheduler Configuration for recurring background jobs
├── tests/           # Pytest suite for end-to-end and unit testing
├── docker/          # Dockerfiles for Backend, Scheduler, and associated services
└── docker-compose.yml # Container Orchestration file
```

---

## ⚙️ Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (For local frontend development)
- Python 3.10+ (For local backend development)

### One-Click Deployment (Recommended)
Launch the entire stack (Database, pgAdmin, FastAPI Backend, and Scheduler) using Docker:
```bash
docker-compose up --build -d
```
*   **API Docs**: `http://localhost:8000/docs`
*   **pgAdmin**: `http://localhost:5050`

### Running the Dashboard Locally
```bash
cd dashboard
npm install
npm run dev
```
*   **Dashboard**: `http://localhost:3000`
