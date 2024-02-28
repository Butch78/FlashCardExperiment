import psycopg2
import os


from schema import Flashcard, Review


url = os.getenv("DATABASE_URL")


def create_flashcard(flashcard: Flashcard):
    """Creates a new flashcard in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO flashcards (id, front, back, section_id, user_id, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    flashcard.id,
                    flashcard.front,
                    flashcard.back,
                    flashcard.section_id,
                    flashcard.user_id,
                    flashcard.created_at,
                ),
            )


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
