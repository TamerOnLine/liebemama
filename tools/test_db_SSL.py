import psycopg2
import logging

logging.basicConfig(level=logging.INFO)

try:
    conn = psycopg2.connect(
        dbname="myprojectdb",
        user="myuser",
        password="GD98AAF8PXHPAVGnTTSmRRFgc1MDAM4R",
        host="78.47.205.8",
        port="5432",
        sslmode="require"
    )
    logging.info("✅ Secure connection successful.")
    conn.close()
except Exception as e:
    logging.error("❌ Connection failed:")
    logging.error(e)
