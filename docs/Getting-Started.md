# Getting Started

## 🧩 Requirements

- Python 3.10+
- PostgreSQL (self-hosted on Hetzner)
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
python myapp.py
# or
flask run --host=0.0.0.0 --port=8030
```

> ✅ Note: `.env` file with DB and storage credentials is required.
