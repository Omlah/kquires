import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_postgres_tables(host, database, user, password, port=5432):
    try:
        logging.info("Connecting to the PostgreSQL database...")
        # Establish connection to the PostgreSQL database
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )

        logging.info("Connection established successfully.")

        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        logging.info("Fetching table names from the database...")
        # Query to get all table names from the connected database
        cursor.execute("
            SELECT table_name 
            FROM information_schema.tables
            WHERE table_schema = 'public';
        ")

        # Fetch all table names
        tables = cursor.fetchall()

        logging.info("Tables in the database:")
        for table in tables:
            logging.info(f"Table: {table[0]}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
            logging.info("Cursor closed.")
        if connection:
            connection.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    # Provide your PostgreSQL credentials
    HOST = "20.117.191.92"
    DATABASE = "postgres"
    USER = "sales-user"
    PASSWORD = "28I8/VUla<!g"
    PORT = 8001

    get_postgres_tables(HOST, DATABASE, USER, PASSWORD, PORT)
