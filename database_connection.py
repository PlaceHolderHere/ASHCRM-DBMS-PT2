from dotenv import load_dotenv
import os
import mysql.connector

def create_database_connection():
    load_dotenv(".env")

    try:
        connection = mysql.connector.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            database=os.getenv('DATABASE')
        )
    except Exception as e:
        print(f"Something went wrong: {e}")
    return connection