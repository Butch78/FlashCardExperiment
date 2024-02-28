import os
import psycopg2

from schema import Section

url = os.getenv("DATABASE_URL")

# Ensure your DATABASE_URL environment variable is correctly set
url = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV")


def get_section_by_name(name: str) -> Section:
    """Retrieves a section from the database by name."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, section_heading, file_name, token_count, character_count FROM sections WHERE file_name = %s",
                (name,),
            )
            result = cursor.fetchone()
            if result:
                # Map the tuple result to a dictionary with appropriate keys
                # These keys must match your Section Pydantic model's fields
                section_data = {
                    "id": result[0],
                    "section_heading": result[1],
                    "file_name": result[2],
                    "token_count": result[
                        3
                    ],  # Ensure this matches your model field name
                    "character_count": result[4],
                }
                return Section(**section_data)
            else:
                return None


def create_section(section: Section):
    """Creates a new section in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sections (id, section_heading, file_name, token_count, character_count) VALUES (%s, %s, %s, %s, %s)",
                (
                    section.id,
                    section.section_heading,
                    section.file_name,
                    section.token_count,
                    section.character_count,
                ),
            )


def get_section(section_id: str) -> Section:
    """Retrieves a section from the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, section_heading, file_name, token_count, character_count FROM sections WHERE id = %s",
                (section_id,),
            )
            result = cursor.fetchone()
            if result:
                section_data = {
                    "id": result[0],
                    "section_heading": result[1],
                    "file_name": result[2],
                    "token_count": result[3],
                    "character_count": result[4],
                }

                return Section(**section_data)
            else:
                return None
