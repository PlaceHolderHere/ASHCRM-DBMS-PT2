from dotenv import load_dotenv
import os
import mysql.connector

def get_env_variables(env_path: str) -> dict:
    load_dotenv(env_path)
    env_variables: dict = {
        "HOST": os.getenv("HOST"),
        "USER": os.getenv("USER"),
        "PASSWORD": os.getenv("PASSWORD"),
        "DATABASE": os.getenv("DATABASE")
    }

    return env_variables

def create_database_connection(env_variables: dict):
    try:
        connection = mysql.connector.connect(
            host=env_variables.get("HOST"),
            user=env_variables.get("USER"),
            password=env_variables.get("PASSWORD"),
            database=env_variables.get("DATABASE")
        )
    except Exception as e:
        print(f"Something went wrong: {e}")

    return connection