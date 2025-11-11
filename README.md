# 🧭 Local Link – Smart Local Services Platform

## 🏗️ Overview
**Local Link** is a full-stack platform built to bridge the gap between **customers** and **local service providers**.  
It allows users to discover, book, and review nearby services, while enabling providers to manage their business and client interactions from a single dashboard.  

Developed using **Flask** and **SQLAlchemy**, this system demonstrates practical implementation of user roles, secure authentication, and CRUD-based service management — making it a perfect fit for both **academic mini-projects** and **advanced coursework** in web development.

---

## ⚡ Key Features
- **Multiple Roles:** Separate dashboards and permissions for **Customer**, **Service Provider**, and **Admin**.  
- **Service Management:** Providers can create, update, and delete their listed services.  
- **Bookings & Notifications:** Customers can schedule services and view their booking status.  
- **Ratings & Reviews:** Built-in feedback system for quality evaluation.  
- **Complaint Submission:** Users can log complaints that admins can track and resolve.  
- **User Authentication:** Registration and login secured using password hashing.  
- **Location Support:** Helps users view services relevant to their location.  
- **Admin Controls:** Manage all registered users, providers, and complaints.

---

## 🧰 Tech Stack
| Component | Technology |
|------------|-------------|
| **Backend** | Flask, SQLAlchemy, Flask-Login |
| **Frontend** | HTML5, Bootstrap 5, Jinja2 Templates |
| **Database** | SQLite |
| **Utilities** | Werkzeug (Password Hashing), Python 3.10 |

---

## 🗂️ Project Directory Layout

LocalLink/
├── app.py # Main Flask application file
├── local_services.db # SQLite database
├── templates/ # Jinja2 HTML templates
│ ├── base.html
│ ├── index.html
│ ├── profile.html
│ ├── services.html
│ ├── booking_form.html
│ ├── complaint.html
│ └── admin_dashboard.html
├── static/
│ ├── css/
│ │ └── style.css
│ └── js/
│ └── script.js
└── README.md


---

# ⚙️ INSTALLATION & SETUP GUIDE

# 1️⃣ Clone the repository
git clone https://github.com/vaibhavrawat27/local-link.git
cd local-link

# 2️⃣ Create a virtual environment
python -m venv venv

# 3️⃣ Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4️⃣ Install all required dependencies
pip install -r requirements.txt

# 5️⃣ Run the Flask application
python app.py

# 6️⃣ Open your browser and visit:
# http://127.0.0.1:5000

# ✅ Default Admin Login:
# Email: admin@example.com
# Password: admin123
