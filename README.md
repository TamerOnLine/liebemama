# 🛍️ LiebeMama - Product Management System

[![Flask](https://img.shields.io/badge/Framework-Flask-blue)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/Storage-MinIO-orange)](https://min.io/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46C1F6?logo=render&logoColor=white)](https://render.com/)

---

## 🎯 Overview

LiebeMama is a professional multi-role **Product Management System** built with **Python Flask**, **PostgreSQL**, and **MinIO**. It supports Admin, Merchant, and Customer roles with secure image handling, dynamic approval workflows, and multilingual support.

---

## 🚀 Features

- 🔐 **Role-based authentication** (Admin, Merchant, Customer)
- 📦 **Product management** (Add, Edit, Delete, Approve)
- 📤 **Image uploads** via MinIO (secure & organized)
- ✅ **Approval flow** from merchant to admin
- 🔔 **Real-time notifications** with visibility control
- 🌐 **i18n** via Flask-Babel (Arabic 🇸🇦, German 🇩🇪)
- 🧼 **Form validation** and XSS protection
- 📊 Admin & Merchant dashboards
- 📁 Archived notification logs (achievement history)
- 🛠️ **Database reset & seed tools** for development

---

## 🗂️ Project Structure

```text
tameronline-liebemama/
├── myapp.py             # App entrypoint
├── routes/              # Blueprints (admin, merchant, auth, products, etc.)
├── models/              # SQLAlchemy models
├── logic/               # Core logic: validation, notifications, settings
├── templates/           # Jinja2 templates (multilingual, role-based)
├── static/              # CSS, images
├── scripts/             # Utilities (auto logger, DB reset, etc.)
├── config/              # Logging & configuration
├── translations/        # Flask-Babel language files
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment file
├── .env                 # Local environment config
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/tameronline-liebemama.git
cd tameronline-liebemama
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup `.env` file

```ini
DATABASE_URL=your_postgres_url
MINIO_ENDPOINT=your_minio_endpoint
MINIO_ACCESS_KEY=your_minio_access_key
MINIO_SECRET_KEY=your_minio_secret_key
MINIO_BASE_URL=https://files.liebemama.com/
MINIO_BUCKET_ADMIN=admin-product
MINIO_BUCKET_MERCHANT=merchant-product
cv_kay=your_flask_secret
TINYMCE_API_KEY=your_tinymce_key
```

### 5. Initialize the database

```bash
python init_db.py
```

### 6. Run the app

```bash
python myapp.py
```

Then visit: [http://localhost:1705](http://localhost:1705)

---

## 👤 Default Roles

Use the built-in method to create your first Super Admin:

```bash
python myapp.py  # will prompt if no admin exists
```

---

## 🌍 Multilingual Support

- Default: Arabic (RTL)
- Supported: `ar`, `de`, `en`
- Change via `/set_language/ar`, `/set_language/en`, etc.

---

## 🧪 Dev Utilities

- Reset DB (dev): `GET /dev/reset`
- Admin Reset: `POST /admin/reset_db`
- Test errors: `/test-errors/401`, `/403`, `/404`, `/500`
- Logs: Stored in `logs/error.log`

---

## 📌 Roadmap

- [x] Notifications Archive (Achievement Log)
- [x] Admin Setting Panel
- [x] Image Manager per product
- [x] Nutrition Analysis (UI)
- [ ] Stripe/PayPal integration
- [ ] RESTful API (Public + Authenticated)
- [ ] Shopping Cart & Order Workflow

---

## ☁️ Deployment (Render.com)

> Fully configured via `render.yaml`

- Auto-start with: `gunicorn myapp:app`
- PostgreSQL managed by Render
- `.env` loaded from Render dashboard

---

## 📜 License

MIT License – Free for personal and educational use.

---

## 👨‍💻 Author

**TamerOnline**  
[GitHub](https://github.com/TamerOnLine) | [LinkedIn](https://www.linkedin.com/in/tameronline)

---

## 🌐 Live Demo (optional)

> Coming soon on: https://www.liebemama.com/
