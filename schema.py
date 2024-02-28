from pydantic import BaseModel
from pydantic import Field
from typing import Optional


class SectionAssignment(BaseModel):
    """
    This will be a many-to-many relationship between User and Section
    """

    id: str
    # FK to User
    user_id: str
    # FK to Section
    create_section_id: str
    # FK to Section
    review_section_id: str


class Section(BaseModel):
    """
    There will be a maximum of 5 sections in total.
    """

    id: str
    section_heading: str
    file_name: str
    tokens: str
    character_count: int


class User(BaseModel):
    # uuid PK
    id: str
    ai: bool
    # FK to Section they will be creating Flashcards for
    flashcard_section_id: str
    # FK to Section they will be reviewing Flashcards for
    review_section_id: str


class Flashcard(BaseModel):
    """
    5 will already be created by an AI user.
    """

    id: str
    front: str
    back: str
    # FK to Section
    section_id: str
    # FK to User
    user_id: str
    # Created in the DB
    created_at: str


class Review(BaseModel):
    id: str
    # FK to Flashcard, User is on the Flashcard
    flashcard_id: str
    file_name: str
    # Likert Scale 1-5
    accuracy: int
    comphrension: int
    relevance: int


class PostExperientFormData(BaseModel):
    question_gender: Optional[str] = Field(None, alias="gender")
    question_1: int
    question_dem6: int
    # FK to User
    user_id: str


class PreExperimentFormData(BaseModel):
    question_english: int = Field(..., alias="english_level")
    question_1: int = Field(..., alias="education_level")
    question_2: int = Field(..., alias="flashcard_experience")
    question_3: Optional[int] = Field(None, alias="flashcard_preference")
    question_4: int = Field(..., alias="flashcard_usage_frequency")
    question_5: int = Field(..., alias="study_duration")
    question_6: int = Field(..., alias="current_tiredness")
    # FK to User
    user_id: str

    class Config:
        allow_population_by_field_name = True


class ParticipantForm(BaseModel):
    donation_preference: int = Field(..., alias="donation_to")
    donation_other: Optional[str] = Field(None, alias="donation_to_other")
    data_policy_agreement: int = Field(..., alias="data_policy")

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
