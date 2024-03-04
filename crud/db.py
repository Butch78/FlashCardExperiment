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
        table_name="pilot_sections",
        connection=url,
        engine="adbc",
        if_table_exists="append",
    )


def create_ai_user(user_id: str, temperature: str):
    """
        CREATE TABLE pilot_users (
        id UUID PRIMARY KEY,
        creator VARCHAR NOT NULL,
        flashcard_section_id UUID REFERENCES pilot_sections(id),
        review_section_id UUID REFERENCES pilot_sections(id)
    );

    """
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pilot_users (id, creator) VALUES (%s, %s)",
                (
                    str(user_id),
                    f"gpt4-1106_{temperature}",
                ),
            )


def get_section_id_by_file_name(file_name: str) -> str:
    # This function should query your database and return the section_id for the given file_name.
    # Example implementation (you'll need to adjust this to your database schema and setup):
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM pilot_sections WHERE file_name = %s", (file_name,)
            )
            result = cursor.fetchone()
            if result:
                return result[0]  # Assuming 'id' is the first column
            else:
                return None


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

        flashcards = []

        for row in df_flashcards.rows(named=True):
            flashcards.append(
                {
                    "front": row["front"],
                    "back": row["back"],
                    "file_name": row["file_name"],
                    "section_heading": row["section_heading"],
                    "section_id": get_section_id_by_file_name(row["file_name"]),
                    "user_id": str(user_id),
                }
            )

        with psycopg2.connect(url) as connection:
            with connection.cursor() as cursor:
                for flashcard in flashcards:
                    cursor.execute(
                        "INSERT INTO pilot_flashcards (front, back, section_id, section_heading, file_name, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            flashcard["front"],
                            flashcard["back"],
                            flashcard["section_id"],
                            flashcard["section_heading"],
                            flashcard["file_name"],
                            flashcard["user_id"],
                        ),
                    )
