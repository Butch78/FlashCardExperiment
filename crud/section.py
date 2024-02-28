import os
import psycopg2

from schema import SectionAssignment, Section

url = os.getenv("DATABASE_URL")

# Ensure your DATABASE_URL environment variable is correctly set
url = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV")


def create_section(section: Section):
    """Creates a new section in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sections (id, section_heading, file_name, tokens, character_count) VALUES (%s, %s, %s, %s, %s)",
                (
                    section.id,
                    section.section_heading,
                    section.file_name,
                    section.tokens,
                    section.character_count,
                ),
            )


def create_section_assignment(section_assignemnt: SectionAssignment):
    """Creates a new section assignment in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO section_assignments (user_id, create_section_id, review_section_id) VALUES (%s, %s, %s)",
                (
                    section_assignemnt.user_id,
                    section_assignemnt.create_section_id,
                    section_assignemnt.review_section_id,
                ),
            )


def get_section_assignment(user_id: str) -> SectionAssignment:
    """Retrieves a user's section assignment from the database."""
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


def get_section(section_id: str) -> Section:
    """Retrieves a section from the database."""
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
