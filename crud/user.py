import psycopg2
import os

from schema import User, ParticipantForm

url = os.getenv("DATABASE_URL")


def create_participant(participant_form: ParticipantForm):
    """Creates a new participant in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO participants (donation_preference, donation_other, data_policy_agreement) VALUES (%s, %s, %s)",
                (
                    participant_form.donation_preference,
                    participant_form.donation_other,
                    participant_form.data_policy_agreement,
                ),
            )


def create_user(user: User):
    """Creates a new user in the database."""
    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (id, ai) VALUES (%s, %s)",
                (user.id, user.ai),
            )
