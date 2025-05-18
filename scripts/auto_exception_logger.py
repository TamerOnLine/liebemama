import os
import re
import shutil

PROJECT_DIR = "."  # Change this to the desired project directory path

pattern = re.compile(r"except Exception as e:\n(\s*)print\((.*?)\)\n(\s*)return (.*?)")

replacement = (
    "except Exception as e:\n"
    "\1current_app.logger.exception(\"\u274C An exception occurred during execution\")\n"
    "\3return \"An unexpected error occurred. Please try again later.\", 500"
)

def process_file(filepath):
    """Process the Python file and update error handling with logging."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Apply the regex substitution
        new_content = pattern.sub(replacement, content)

        # If the content has changed, write it back to the file
        if content != new_content:
            # Create a backup of the original file before modifying
            backup_filepath = f"{filepath}.bak"
            shutil.copy(filepath, backup_filepath)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print(f"✅ Modified: {filepath}")
        else:
            print(f"🔍 No modification needed: {filepath}")
    except Exception as e:
        print(f"❌ Error processing the file {filepath}: {e}")

def scan_project():
    """Recursively scan all Python files in the project directory."""
    for root, dirs, files in os.walk(PROJECT_DIR):
        for filename in files:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                process_file(full_path)

if __name__ == "__main__":
    scan_project()
