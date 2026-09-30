# 🎫 EventVault — Event Management System with Ticket Booking

A full-stack Python web application for discovering and booking events, with a beautiful dark-themed frontend.

---

## 📁 Project Structure

```
event_management/
├── backend/
│   └── app.py              ← Flask REST API + SQLite DB
├── frontend/
│   ├── index.html          ← Single-page frontend
│   └── static/
│       ├── css/style.css   ← Full styling
│       └── js/app.js       ← Frontend logic
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
dir
py -m pip install -r requirements.txt
```

### 2. Run the server
```bash
cd backend
py app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Event Discovery** | Browse 10+ seeded events with search & filters |
| 🏷️ **Category Filters** | Music, Sports, Tech, Arts, Food, Wellness & more |
| 🎫 **Ticket Booking** | Select quantity, ticket type, real-time availability |
| 👤 **User Accounts** | Sign in with email, sessions stored locally |
| 🗂️ **My Tickets** | View all bookings with booking reference codes |
| ❌ **Cancellations** | Cancel bookings and restore ticket availability |
| 📊 **Live Stats** | Events, bookings, and city counts on the hero |
| 🌐 **Open Data** | Event data seeded from curated sample (no API key needed) |

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/events` | List events (with search/filter/sort) |
| GET | `/api/events/:id` | Single event detail |
| GET | `/api/categories` | All event categories |
| POST | `/api/users` | Create/login user |
| POST | `/api/bookings` | Book tickets |
| GET | `/api/bookings/:user_id` | User's bookings |
| PUT | `/api/bookings/cancel/:id` | Cancel a booking |
| GET | `/api/stats` | Dashboard statistics |

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-CORS, SQLite3
- **Frontend**: Vanilla JS, CSS3 (no frameworks needed)
- **Fonts**: Syne + DM Sans (Google Fonts)
- **Data**: Curated open sample events (easily extendable with Ticketmaster API)

---

## 🔌 Extending with Real API Data

To pull live events from Ticketmaster (free tier):

1. Get a free API key at https://developer.ticketmaster.com
2. In `backend/app.py`, update `fetch_and_seed_events()`:

```python
url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey=YOUR_KEY&countryCode=IN&size=20"
response = requests.get(url)
data = response.json()
# Map data['_embedded']['events'] to your events schema
```
