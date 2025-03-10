# Sales Tracking App

A Flask web application for tracking sales activities, including PR visits and telecaller activities.

## Features

### PR Visits Section
- Track visit start time
- Record client name and PR name
- Document manager responses
- Monitor visit status
- Add visit updates and notes

### Telecaller (TC) Section
- Track calls made
- Record manager in charge
- Monitor visits booked and confirmed
- Track leads acquired and bucket leads

## Installation and Setup

1. Clone the repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python run.py
   ```
4. Access the application at http://localhost:5001

## Database

The application uses SQLite by default. The database will be created automatically when the application is first run.

## Project Structure

```
daily_sales/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── static/
│   │   └── css/
│   │       └── main.css
│   ├── templates/
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── pr/
│   │   │   ├── index.html
│   │   │   ├── new.html
│   │   │   └── edit.html
│   │   └── tc/
│   │       ├── index.html
│   │       ├── new.html
│   │       └── edit.html
│   └── routes/
│       ├── __init__.py
│       ├── main.py
│       ├── pr.py
│       └── tc.py
│
├── run.py
├── requirements.txt
└── README.md
```