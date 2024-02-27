import os
import psycopg2
import polars as pl

from schema import Flashcard, SectionAssignment, User, Section, Review

# Ensure your DATABASE_URL environment variable is correctly set
url = os.getenv("DATABASE_URL")

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
    
def create_section_assignment(user_id: str, create_section_id: str, review_section_id: str):
    """ Creates a new section assignment in the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO section_assignments (user_id, create_section_id, review_section_id) VALUES (%s, %s, %s)",
                (user_id, create_section_id, review_section_id),
            )


def get_section(section_id: str) -> Section:
    """ Retrieves a section from the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, section_heading, file_name, tokens, character_count FROM sections WHERE id = %s",
                (section_id,),
            )
            result = cursor.fetchone()
            if result:
                return Section(*result)
            else:
                return None
    
def get_section_assignment(user_id: str) -> SectionAssignment:
    """ Retrieves a user's section assignment from the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, user_id, create_section_id, review_section_id FROM section_assignments WHERE user_id = %s",
                (user_id,),
            )
            result = cursor.fetchone()
            if result:
                return SectionAssignment(*result)
            else:
                return None
    
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

    


def create_user(user: User):
    """ Creates a new user in the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (id, ai) VALUES (%s, %s)",
                (user.id, user.ai),
            )

def create_section(section: Section):
    """ Creates a new section in the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sections (id, section_heading, file_name, tokens, character_count) VALUES (%s, %s, %s, %s, %s)",
                (section.id, section.section_heading, section.file_name, section.tokens, section.character_count),
            )

def create_flashcard(flashcard: Flashcard):
    """ Creates a new flashcard in the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO flashcards (id, front, back, section_id, user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (flashcard.id, flashcard.front, flashcard.back, flashcard.section_id, flashcard.user_id, flashcard.created_at),
            )

def create_review(review: Review):
    """ Creates a new review in the database. """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO reviews (id, flashcard_id, file_name, accuracy, comphrension, relevance) VALUES (%s, %s, %s, %s, %s, %s)",
                (review.id, review.flashcard_id, review.file_name, review.accuracy, review.comphrension, review.relevance),
            )
