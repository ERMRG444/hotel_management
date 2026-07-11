# Grand Hotel Management System – Full-Stack Web App

A full-stack hotel management system with role-based dashboards enabling real-time room booking, food ordering, and staff operations.

**Live Demo:** https://hotel-management-o52d.onrender.com

> Note: hosted on Render's free tier — the app may take 30-60 seconds to load on first visit if it's been idle.

## Overview

Grand Hotel Management System digitizes core hotel operations — bookings, food ordering, and staff task tracking — through role-specific dashboards for Admins, Staff, and Guests, backed by a centralized database and RESTful APIs.

## Features

- **Real-Time Room Booking** — Guests can browse and book available rooms with live availability updates.
- **Food Ordering** — In-app food ordering system tied to guest accounts/rooms.
- **Role-Based Dashboards** — Separate, tailored dashboard views for Admin, Staff, and Guest roles.
- **Live Activity Tracking** — Staff and admin dashboards reflect ongoing hotel activity in real time.
- **Simulated Payment System** — End-to-end booking flow including a simulated payment step.
- **RESTful API Backend** — Clean separation between Flask backend APIs and the frontend.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Environment | Python venv |

## Installation

```bash
git clone https://github.com/ERMRG444/hotel_management.git
cd hotel_management
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

### Default Roles

The app supports three role types on login/signup:
- **Admin** — Full access to hotel operations, staff, and reporting
- **Staff** — Access to bookings, food orders, and day-to-day operational tasks
- **Guest** — Room browsing, booking, and food ordering

## Project Structure

```
hotel_management/
├── app.py                 # Flask application entry point
├── models.py               # Database models
├── routes/
│   ├── admin.py
│   ├── staff.py
│   └── guest.py
├── static/                 # CSS/JS assets
├── templates/               # HTML templates per role dashboard
└── requirements.txt
```

## Future Improvements

- Integrate a real payment gateway (e.g., Razorpay/Stripe) in place of the simulated flow
- Migrate from SQLite to PostgreSQL for production scalability
- Add automated email/SMS booking confirmations

## Author

Vinit Hemkant Chaudhari — [LinkedIn](https://www.linkedin.com/in/vinit-chaudhari-154020376)
