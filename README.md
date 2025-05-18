# 🛍️ MyStore

[![Flask](https://img.shields.io/badge/Framework-Flask-blue)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![Cloudinary](https://img.shields.io/badge/Media-Cloudinary-3448C5?logo=cloudinary\&logoColor=white)](https://cloudinary.com/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46C1F6?logo=render\&logoColor=white)](https://render.com/)

## 🎯 Overview

A robust and professional **Product Management System** built with Python (Flask), PostgreSQL, and Cloudinary. It features a multi-role interface (Admin / Merchant / Customer), product approval workflows, dynamic notifications, and Arabic RTL support.

---

## 🚀 Features

* 🔒 Role-based login: Admin, Merchant, Customer
* ➕ Add, edit, delete, and approve products with rich text and image upload
* ✅ Dynamic product approval and notification system
* 🖼️ Cloudinary integration for secure and optimized image hosting
* 📨 Real-time notification flow for product tasks
* 🌐 Full Arabic RTL interface via Flask-Babel (i18n)
* 🧼 Form validation and input sanitization
* 📊 Admin dashboard and merchant portal
* 🛠️ Reset DB, seed accounts, test error pages (dev only)

---

## 🧱 Project Structure

```
tameronline-pro_product_pg/
├── myapp.py               # Main entry point (Flask app)
├── config.py              # App configuration
├── models/                # SQLAlchemy Models (User, Product, Notification)
├── routes/                # Route blueprints: auth, admin, merchant, reset, etc.
├── logic/                 # Notifications, validation, flow control
├── templates/             # Jinja2 HTML templates
├── static/                # CSS and media folders
├── render.yaml            # Deployment file for Render.com
├── requirements.txt       # Python dependencies
└── .env                   # Environment config (locally)
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository:

```bash
git clone https://github.com/your-username/tameronline-pro_product_pg.git
cd tameronline-pro_product_pg
```

### 2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set environment variables:

Create a `.env` file in the root:

```env
cv_kay=your_secret_key_here
DATABASE_URL=your_postgresql_url
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
TINYMCE_API_KEY=your_tinymce_key
```

### 5. Initialize the database:

```bash
python init_db.py
```

### 6. Run the app:

```bash
python myapp.py
```

Visit: [http://localhost:8030](http://localhost:8030)

---

## 🧪 Development Tools

* `/test-errors/401` or `/test-errors/500`: Simulate error pages
* `/dev/reset`: Wipe and recreate DB in development mode
* Logging stored in: `logs/error.log`

---

## 👤 Default Roles (on fresh DB)

Use `create_super_admin_if_needed()` to generate first admin.

---

## 📦 Deployment (Render.com)

Deployment is configured via `render.yaml`:

* PostgreSQL + Gunicorn + Cloudinary
* Environment variables are auto-synced
* `startCommand: gunicorn myapp:app`

---

## 📌 To-Do / Roadmap

* [x] Add multilingual support
* [x] Enable product categories
* [x] Implement cart system
* [x] Create REST API
* [ ] Customer order flow
* [ ] Stripe/PayPal integration

---

## 🌐 UI Language

This project defaults to **Arabic (RTL)**. Language switching can be implemented using Flask-Babel’s `locale_selector_func`.

---

## 📝 License

MIT License – Free for personal and educational use.

---

## 💡 Author

**TamerOnline** – [LinkedIn](https://www.linkedin.com/in/tameronline/) | [GitHub](https://github.com/TamerOnLine)
