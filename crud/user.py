import psycopg2
import os

from schema import User, ParticipantForm, PreExperimentFormData

url = os.getenv("DATABASE_URL")


def create_participant(participant_form: ParticipantForm):
    """Creates a new participant in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO participant_responses (donation_preference, donation_other, data_policy_agreement, user_id) VALUES (%s, %s, %s, %s)",
                (
                    participant_form.donation_preference,
                    participant_form.donation_other,
                    participant_form.data_policy_agreement,
                    participant_form.user_id,
                ),
            )


def create_initial_questions(participant_form: PreExperimentFormData):
    """Create a new PreExperimentFormData in the database."""

    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO experiment_responses (english_level, education_level, flashcard_experience, flashcard_preference, flashcard_usage_frequency, study_duration, current_tiredness, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    participant_form.english_level,
                    participant_form.education_level,
                    participant_form.flashcard_experience,
                    participant_form.flashcard_preference,
                    participant_form.flashcard_usage_frequency,
                    participant_form.study_duration,
                    participant_form.current_tiredness,
                    participant_form.user_id,
                ),
            )


def create_user(user: User):
    """Creates a new user in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (id, creator, flashcard_section_id, review_section_id) VALUES (%s, %s, %s, %s)",
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
                "SELECT id, creator, flashcard_section_id, review_section_id FROM users WHERE id = %s",
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
