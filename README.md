# 🧭 Commute and Relocation Cost Analyzer

A Django-based web API that helps users calculate **commute distances**, **travel durations**, and **relocation cost savings** between two locations using OpenRouteService and cost comparison logic.

---

## 🚀 Features

- Calculate commute distance and time between two addresses.  
- Estimate fuel costs based on travel distance.  
- Compare living expenses between two cities (rent, groceries, utilities, etc.).  
- Provides JSON responses for easy integration with frontend or other apps.  

---

## 🏗️ Tech Stack

- **Backend Framework:** Django (Django REST Framework)
- **API Integration:** OpenRouteService (ORS)
- **Database:** SQLite (default, can be replaced with PostgreSQL/MySQL)
- **Language:** Python 3.11+
- **Environment:** Virtualenv / venv

---

## 📁 Project Structure

commute_and_relocation/
│
├── commute/
│ ├── migrations/
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ ├── utils.py
│ └── views.py
│
├── core/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── manage.py
├── db.sqlite3
├── .env
└── README.md


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/commute_and_relocation.git
cd commute_and_relocation

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate       # On Mac/Linux
venv\Scripts\activate          # On Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add environment variables

Create a .env file in the root directory:

ORS_API_KEY=your_openrouteservice_api_key

5️⃣ Run migrations
python manage.py migrate

6️⃣ Start the server
python manage.py runserver

🧩 API Endpoints
1. Commute Cost Calculation

POST /api/commute/

Example Request:
{
  "home_address": "Toronto, ON, Canada",
  "job_address": "Ottawa, ON, Canada",
  "mode": "driving"
}

Example Response:
{
  "ok": true,
  "data": {
    "distance_km": 334.22,
    "duration_min": 250.66,
    "mode": "driving",
    "fuel_cost_cad": 71.3,
    "summary": "Your commute is 250.7 minutes by driving, covering 334.2 km. Estimated round-trip fuel cost: CAD 71.3."
  }
}

2. Relocation Cost Comparison

POST /api/relocation/

Example Request:
{
  "current_address": "Toronto, ON, Canada",
  "target_address": "Ottawa, ON, Canada",
  "flat_rent_current": 2500.00,
  "flat_rent_target": 2200.00,
  "commute_cost_current": 400.00,
  "commute_cost_target": 150.00,
  "utilities_current": 200.00,
  "utilities_target": 180.00,
  "groceries_current": 300.00,
  "groceries_target": 280.00,
  "misc_current": 150.00,
  "misc_target": 120.00
}

Example Response:
{
  "ok": true,
  "summary": "Relocating from Toronto, ON, Canada to Ottawa, ON, Canada could save you approximately CAD 620.0 per month. Your flat rent decreases from CAD 2500.0 to CAD 2200.0, commute costs reduce, utilities and groceries are slightly lower, while miscellaneous expenses may also decrease slightly."
}

🧠 Future Enhancements

Add visualization dashboard for cost savings.

Include public transport and cycling modes.

Integrate housing/rent APIs for real-time estimates.

Add authentication and user profiles.

🧑‍💻 Author

Tushar Rastogi
💼 Django Developer | 🌐 GitHub Profile
