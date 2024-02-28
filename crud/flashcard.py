from typing import List
import psycopg2
import os


from schema import CreateFlashcard, Flashcard, Review


url = os.getenv("DATABASE_URL")


def create_flashcard(flashcard: CreateFlashcard):
    """Creates a new flashcard in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO flashcards (front, back, section_id, section_heading, file_name, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    flashcard.front,
                    flashcard.back,
                    flashcard.section_id,
                    flashcard.section_heading,
                    flashcard.file_name,
                    flashcard.user_id,
                ),
            )


def get_flashcard(flashcard_id: str) -> Flashcard:
    """Retrieves a flashcard from the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, front, back, section_id, user_id, created_at FROM flashcards WHERE id = %s",
                (flashcard_id,),
            )
            result = cursor.fetchone()
            if result:
                return Flashcard(
                    id=result[0],
                    front=result[1],
                    back=result[2],
                    section_id=result[3],
                    user_id=result[4],
                    created_at=result[5],
                )


def get_flashcards(review_section_id: str) -> List[Flashcard]:
    """Retrieves all flashcards from the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, front, back, section_id, user_id, created_at FROM flashcards WHERE section_id = %s",
                (review_section_id,),
            )
            results = cursor.fetchall()
            return [
                Flashcard(
                    id=result[0],
                    front=result[1],
                    back=result[2],
                    section_id=result[3],
                    user_id=result[4],
                    created_at=result[5],
                )
                for result in results
            ]


def create_review(review: Review):
    """Creates a new review in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO reviews (id, flashcard_id, file_name, accuracy, comphrension, relevance) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    review.id,
                    review.flashcard_id,
                    review.file_name,
                    review.accuracy,
                    review.comphrension,
                    review.relevance,
                ),
            )
