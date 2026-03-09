# SALES-AI-ASSISTANT
https://sales-ai-assistant-h5wuusmwlgp49eqm8ehfdd.streamlit.app/
---

# 🚀 BizSight AI

### Intelligent Sales Forecasting & Scenario Simulation Platform

BizSight AI is a modular, production-structured sales analytics system built using Streamlit and Python.

It enables businesses to:

* Upload raw CSV data in any format
* Automatically learn and adapt to schema structures
* Generate intelligent monthly forecasts
* Simulate marketing impact scenarios
* Plan revenue growth targets
* Track system usage activity

This project is designed with SaaS architecture principles and modular engineering practices.

---

# 🌍 Live Concept

BizSight AI replicates a lightweight SaaS analytics dashboard used by:

* Retail businesses
* E-commerce stores
* Regional sales teams
* Small & mid-sized enterprises

---

# 🧠 Core Capabilities

## 1️⃣ Smart Schema Learning Engine

* Accepts unknown CSV formats
* Detects known schema automatically
* Learns new schema mappings
* Stores mapping memory in JSON
* Self-adapting structure recognition

> Simulates intelligent data ingestion pipeline

---

## 2️⃣ Forecasting Engine

* Monthly revenue aggregation
* 3-Month moving average trend analysis
* ML model prediction (if model available)
* Intelligent fallback logic (trend-based growth)
* Forecast confidence range

Architecture separated into `utils/forecast.py`

---

## 3️⃣ What-If Simulation System

* Adjustable marketing impact slider
* Instant revenue simulation
* Real-time growth comparison
* Scenario-based decision support

---

## 4️⃣ Revenue Target Planner

* Define desired growth %
* Compute required target revenue
* Display revenue gap
* Business-oriented planning tool

---

## 5️⃣ Dataset Management System

* Save dataset locally
* Load dataset
* Delete dataset
* Persistent structured storage

Implements local SaaS-style data management.

---

## 6️⃣ Authentication System

* First-time registration
* Login session handling
* JSON-based credential storage
* Modularized authentication logic (`utils/auth.py`)

---

## 7️⃣ Activity Logging System

Tracks:

* Dataset loads
* Forecast generation
* Simulation usage
* User actions

Log stored in structured JSON format (`utils/logger.py`)

---

# 🏗️ System Architecture

```
sales-ai-assistant/
│
├── app.py
│
├── utils/
│   ├── auth.py
│   ├── forecast.py
│   ├── logger.py
│   ├── schema.py
│
├── model/
│   └── sales_model.pkl
│
├── data/
│   ├── user.json
│   ├── activity_log.json
│   ├── schema_memory.json
│
├── saved_datasets/
│
├── notebooks/
│   └── eda.ipynb
│
└── requirements.txt
```

---

# ⚙️ Installation & Setup

```bash
git clone https://github.com/<your-username>/sales-ai-assistant.git
cd sales-ai-assistant
pip install -r requirements.txt
streamlit run app.py
```

If port conflict:

```bash
streamlit run app.py --server.port 8502
```

---

# 🛠️ Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| Frontend        | Streamlit                    |
| Backend         | Python                       |
| Data Processing | Pandas                       |
| ML Model        | Scikit-Learn                 |
| Storage         | JSON-based local persistence |
| Architecture    | Modular utility-based design |

---

# 🧩 Engineering Highlights

* Modular code separation (utils architecture)
* State management using Streamlit session
* Schema abstraction logic
* Forecast abstraction layer
* Fault-tolerant numeric/date conversion
* Clean separation of concerns
* Production-ready project structure

---

# 📊 Sample Forecast Output

* Monthly sales visualization
* Forecasted next-month revenue
* Growth percentage
* Confidence range
* Trend analysis

---

# 🚀 Future Roadmap

* PostgreSQL / Cloud DB integration
* Multi-user authentication with roles
* REST API for forecasting
* Docker containerization
* CI/CD pipeline
* Streamlit Cloud deployment
* Real ML model retraining pipeline

---

# 👨‍💻 Author

**Abhishek Bhosale**
Computer Engineering
Machine Learning & SaaS Systems Enthusiast

Focused on building production-ready AI systems.

---


