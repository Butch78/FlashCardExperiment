import psycopg2
import os

from schema import User, Participant, Demographics

url = os.getenv("DATABASE_URL")


def create_participant(participant: Participant):
    """Creates a new participant in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO  pilot_participants (donation_preference, donation_other, data_policy_agreement, user_id) VALUES (%s, %s, %s, %s)",
                (
                    participant.donation_preference,
                    participant.donation_other,
                    participant.data_policy_agreement,
                    participant.user_id,
                ),
            )


def create_demographic(demographics: Demographics):
    """Create a new PreExperimentFormData in the database."""

    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            # TODO: Update SQL
            cursor.execute(
                "INSERT INTO pilot_demographics (english_level, education_level, flashcard_experience, flashcard_preference, flashcard_usage_frequency, study_duration, current_tiredness, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    demographics.english_level,
                    demographics.education_level,
                    demographics.flashcard_experience,
                    demographics.flashcard_preference,
                    demographics.flashcard_usage_frequency,
                    demographics.study_duration,
                    demographics.current_tiredness,
                    demographics.user_id,
                ),
            )


def create_user(user: User):
    """Creates a new user in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pilot_users (id, creator, flashcard_section_id, review_section_id) VALUES (%s, %s, %s, %s)",
                (
                    user.id,
                    user.creator,
                    user.flashcard_section_id,
                    user.review_section_id,
                ),
            )


def get_user(user_id: str) -> User:
    """Retrieves a user from the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, creator, flashcard_section_id, review_section_id FROM pilot_users WHERE id = %s",
                (user_id,),
            )
            result = cursor.fetchone()
            if result:
                user_data = {
                    "id": result[0],
                    "creator": result[1],
                    "flashcard_section_id": result[2],
                    "review_section_id": result[3],
                }
                return User(**user_data)
            else:
                return None
