import os
import psycopg2
import polars as pl

from schema import Flashcard, SectionAssignment, User, Section, Review

# Ensure your DATABASE_URL environment variable is correctly set
url = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV")

def init_db():
    """ Initializes the database with the necessary tables using the schema in SQL file:
    schema.sql and then will load the data from the parquet file into the database.
    """

# TODO: Remove Drop Table command for production
        

    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            with open("schema.sql", "r") as file:
                cursor.execute(file.read())

    write_to_db()

    return True
                


def check_database_connection():
    try:
        # Use the connection in a context manager to ensure it gets closed
        with psycopg2.connect(url) as connection:
            # Create a cursor object
            with connection.cursor() as cursor:
                # Perform a simple query
                cursor.execute("SELECT 1")
                # Fetch the result (not necessary but included for completeness)
                cursor.fetchone()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
    
    

    
def write_to_db():

    # TODO 
    # 1. modify this function so it will write a Flashcard object to the database from the parquet file 
    # 2. Identify the correct section to use for the Flashcards objects created by the AI user

    df_chapter_1 = pl.read_parquet("resources/experiments/test_flashcards_chapter_1.parquet")
    df_chapter_2 = pl.read_parquet("resources/experiments/test_flashcards_chapter_2.parquet")
    df_chapter_3 = pl.read_parquet("resources/experiments/test_flashcards_chapter_3.parquet")

    # df_chapter_1.write_database(table_name="test_records", connection=url, engine="adbc", if_table_exists="replace")
    df_chapter_2.write_database(table_name="test_records", connection=url, engine="adbc", if_table_exists="append")
    df_chapter_3.write_database(table_name="test_records", connection=url, engine="adbc", if_table_exists="append")

    








