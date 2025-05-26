# Getting Started

## 🧩 Requirements

- Python 3.10+
- PostgreSQL / Supabase
- MinIO
- Gunicorn + Nginx
- Flask

## 🛠 Installation

```bash
git clone https://github.com/liebemama/liebemama.git
cd liebemama
pip install -r requirements.txt
```

## 🚀 Run Local Server

```bash
python app.py
# or
flask run --host=0.0.0.0 --port=8030
```

> ✅ Note: `.env` file with DB and storage credentials is required.
