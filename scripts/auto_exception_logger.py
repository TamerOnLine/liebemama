import os
import re
import shutil
import logging


PROJECT_DIR = "."  # Change this to the desired project directory path

pattern = re.compile(
    r"except Exception as e:\n(\s*)print\((.*?)\)\n(\s*)return (.*?)"
)

replacement = (
    "except Exception as e:\n"
    "\1current_app.logger.exception(\"An exception occurred during execution\")\n"
    "\3return \"An unexpected error occurred. Please try again later.\", 500"
)


logging.basicConfig(level=logging.INFO)


def process_file(filepath):
    """
    Process a single Python file to update its exception handling.

    Args:
        filepath (str): Full path to the Python file to process.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        new_content = pattern.sub(replacement, content)

        if content != new_content:
            backup_filepath = f"{filepath}.bak"
            shutil.copy(filepath, backup_filepath)

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)

            logging.info("Modified: %s", filepath)
        else:
            logging.info("No modification needed: %s", filepath)

    except Exception as e:
        logging.error("Error processing the file %s: %s", filepath, e)


def scan_project():
    """
    Recursively scan all Python files in the project directory.

    Modifies files containing direct exception prints.
    """
    for root, _, files in os.walk(PROJECT_DIR):
        for filename in files:
            if filename.endswith(".py"):
                full_path = os.path.join(root, filename)
                process_file(full_path)


if __name__ == "__main__":
    scan_project()
