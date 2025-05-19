import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)

def main():
    """
    Test connection to the database using SQLAlchemy.

    Loads the DATABASE_URL from environment variables and attempts
    a basic SQL query to confirm connectivity.
    """
    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logging.error("DATABASE_URL not found in .env file")
        exit(1)

    logging.info("Attempting connection to: %s", db_url)
    engine = create_engine(db_url)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logging.info("Database connection successful.")
    except OperationalError as e:
        logging.error("Database connection failed:")
        logging.error("%s", str(e.orig))


if __name__ == "__main__":
    main()
