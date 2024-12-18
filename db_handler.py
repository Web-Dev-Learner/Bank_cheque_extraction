import psycopg2
# from psycopg2 import sql
import os
import logging

from urllib.parse import urlparse



# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up the connection
def get_db_connection():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        parsed_url = urlparse(DATABASE_URL)

        db_host = parsed_url.hostname
        db_port = parsed_url.port if parsed_url.port else 5432  # Default to 5432 if not specified
        db_user = parsed_url.username
        db_password = parsed_url.password
        db_name = parsed_url.path[1:]  
        # Strip the leading '/' from the path
        
        return psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name
        )


        # return psycopg2.connect(
        #     dbname=os.getenv('DB_NAME'),
        #     user=os.getenv('DB_USER'),
        #     password=os.getenv('DB_PASSWORD'),
        #     host=os.getenv('DB_HOST'),
        #     port=os.getenv('DB_PORT')
        # )
    except Exception as error:
        logging.error(f"Error connecting to the database: {error}")
        raise




# Insert cheque details into the database
def insert_cheque_details(details):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO cheque_details (
            payee_name, cheque_date, cheque_number, account_number, 
            bank_name, branch, amount_in_words, amount_in_numbers, 
            signature_name, micr_code, ifsc_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            details.get("payeeName", ""),
            details.get("date", ""),
            details.get("chequeNumber", ""),
            details.get("accountNumber", ""),
            details.get("bankName", ""),
            details.get("branch", ""),
            details.get("amountInWords", ""),
            details.get("amountInNumbers", ""),
            details.get("signatureName", ""),
            details.get("micrCode", ""),
            details.get("ifscCode", "")
        )

        cursor.execute(insert_query, data)
        connection.commit()
        cursor.close()
        connection.close()
        logging.info("Cheque details inserted successfully.")

    except Exception as error:
        logging.error(f"Error inserting cheque details: {error}")
        raise

# Fetch cheque details from the database
def fetch_cheque_details():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        select_query = "SELECT * FROM cheque_details"
        cursor.execute(select_query)

        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        if not rows:
            logging.info("No cheque details found in the database.")
        
        return rows

    except Exception as error:
        logging.error(f"Error fetching cheque details: {error}")
        return []

