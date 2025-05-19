import sqlite3
import json
from pathlib import Path

# 🗂 مسار قاعدة البيانات المحلي
db_path = r"S:\liebemama\systems.db"

# 🔌 الاتصال بقاعدة البيانات
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 📂 مجلد حفظ ملفات workspace
output_dir = Path(r"S:\liebemama\systems_workspaces")
output_dir.mkdir(parents=True, exist_ok=True)

# 🧠 جلب أسماء الأنظمة
cursor.execute("SELECT DISTINCT system_name FROM system_files")
systems = cursor.fetchall()

for (system,) in systems:
    # 📄 استخراج الملفات لهذا النظام
    cursor.execute("SELECT full_path FROM system_files WHERE system_name = ?", (system,))
    paths = [row[0] for row in cursor.fetchall()]
    folders = sorted(set(str(Path(p).parent) for p in paths))

    # 🔧 بناء ملف .code-workspace
    workspace_data = {
        "folders": [{"path": f"../{folder}"} for folder in folders],
        "settings": {
            "python.pythonPath": "venv/bin/python",
            "terminal.integrated.env.linux": {
                "FLASK_ENV": "development",
                "FLASK_APP": "myapp.py"
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True
            }
        }
    }

    # 📝 حفظ الملف
    system_folder = output_dir / system
    system_folder.mkdir(parents=True, exist_ok=True)
    workspace_path = system_folder / f"{system}.code-workspace"

    with open(workspace_path, "w", encoding="utf-8") as f:
        json.dump(workspace_data, f, indent=4)

    print(f"✅ created: {workspace_path}")

conn.close()
