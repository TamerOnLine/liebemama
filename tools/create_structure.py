import os

BASE_PATH = "my_project"

FOLDERS = [
    "models",
    "logic",
    "routes",
    "config",
    "templates/auth",
    "templates/admin",
    "templates/merchant",
    "templates/shared",
    "templates/errors",
    "static/css",
    "static/uploads",
    "logs"
]

ENV_FILE = os.path.join(BASE_PATH, ".env")


def create_structure():
    """
    Create the project folder structure.
    """
    try:
        os.makedirs(BASE_PATH, exist_ok=True)

        for folder in FOLDERS:
            path = os.path.join(BASE_PATH, folder)
            os.makedirs(path, exist_ok=True)

        # Create an empty .env file if it doesn't exist
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write("# Environment variables\n")

        print(f"✅ Project structure created successfully at '{BASE_PATH}'")

    except Exception as e:
        print(f"❌ Error creating project structure: {e}")


if __name__ == "__main__":
    create_structure()
