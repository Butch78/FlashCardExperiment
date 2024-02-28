import os
import uuid
import psycopg2
import polars as pl


# Ensure your DATABASE_URL environment variable is correctly set
url = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV")


def init_db():
    """Initializes the database with the necessary tables using the schema in SQL file:
    schema.sql and then will load the data from the parquet file into the database.
    """

    # TODO: Remove Drop Table command for production

    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            with open("schema.sql", "r") as file:
                cursor.execute(file.read())

    write_sections_to_db()
    write_flashcards_to_db()

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


def write_sections_to_db():
    df_chapter_2 = pl.read_parquet(
        "resources/experiments/test_flashcards_gpt_4_1106_1_chapter_2.parquet",
        columns=["section_heading", "file_name", "character_count", "token_count"],
    )
    print(df_chapter_2.head())

    df_chapter_2.write_database(
        table_name="sections",
        connection=url,
        engine="adbc",
        if_table_exists="append",
    )


def create_ai_user(user_id: str, temperature: str):
    """
        CREATE TABLE users (
        id UUID PRIMARY KEY,
        creator VARCHAR NOT NULL,
        flashcard_section_id UUID REFERENCES sections(id),
        review_section_id UUID REFERENCES sections(id)
    );

    """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (id, creator) VALUES (%s, %s)",
                (
                    str(user_id),
                    f"gpt4-1106_{temperature}",
                ),
            )


def write_flashcards_to_db():
    for temperature in ["05", "1", "15"]:
        user_id = uuid.uuid4()
        create_ai_user(user_id, temperature)

        df_flashcards = pl.read_parquet(
            f"resources/experiments/test_flashcards_gpt_4_1106_{temperature}_chapter_2.parquet",
            columns=["section_heading", "file_name", "front", "back"],
        )

        file_names = [
            "section_2_1_4.pdf",
            "section_2_2.pdf",
            "section_2_4_6.pdf",
            "section_2_4_7.pdf",
            "section_2_4_8.pdf",
            "section_2_4_9.pdf",
        ]
        df_flashcards = df_flashcards.filter(pl.col("file_name").is_in(file_names))

        df_flashcards.write_database(
            table_name="flashcards",
            connection=url,
            engine="adbc",
            if_table_exists="append",
        )

        # with psycopg2.connect(url) as connection:
        #     with connection.cursor() as cursor:
        #         cursor.execute(f"UPDATE flashcards SET user_id = '{user_id}'")
        #     connection.commit()
