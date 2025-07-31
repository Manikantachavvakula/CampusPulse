# Hostel Feedback Portal

A web application for managing hostel feedback submissions built with Flask and Bootstrap 4.

## Features

### Student Features
- User registration and login
- Submit feedback for different categories (Food, Library, Washrooms, Sports Grounds, Labs)
- Track feedback status
- Upload images with feedback
- Food-specific feedback with day selection and quality rating

### Admin Features
- Admin dashboard with all feedbacks
- Filter feedbacks by category and status
- Change feedback status (pending/resolved/rejected)
- Analytics dashboard with charts
- Visual insights into feedback patterns

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Bootstrap 4
- **Database**: SQLite3
- **Charts**: Chart.js v3
- **Templating**: Jinja2

## Installation & Setup

1. **Clone or download the project**
```bash
cd E:\new_projects\hostel_feedback_portal
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
cd app
python app.py
```

5. **Access the application**
- Open browser and go to: `http://localhost:5000`
- Admin login: username `admin`, password `admin123`

## Project Structure

```
hostel_feedback_portal/
├── app/
│   ├── templates/          # HTML templates
│   ├── static/
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript files
│   │   └── uploads/       # Uploaded images
│   ├── app.py             # Main Flask application
│   ├── models.py          # Database models
│   └── routes.py          # Route handlers
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Usage

### For Students
1. Register a new account or login
2. Navigate to "Submit Feedback"
3. Select category and fill in details
4. For food feedback, select applicable days and quality
5. Optionally upload an image
6. Track your feedback status in "Track Feedback"

### For Admins
1. Login with admin credentials
2. View all feedbacks in the admin dashboard
3. Filter by category or status
4. Update feedback status as needed
5. View analytics for insights

## Database Schema

### Users Table
- id, username, email, password_hash, role, created_at

### Feedback Table  
- id, user_id, category, days, quality, rating, comments, image_path, status, created_at

## Default Admin Account
- Username: `admin`
- Password: `admin123`

## File Upload
- Supports JPG and PNG images only
- Files are stored in `app/static/uploads/`
- Automatic filename sanitization

## Development Notes
- Built as a college-level project (circa 2021)
- Uses technologies popular in that era
- Clean, professional UI without over-engineering
- Ready for automation testing with Selenium
- SQLite database for simplicity

## License
Educational project - free to use and modify."# CampusPulse" 
