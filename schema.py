from pydantic import BaseModel
from pydantic import Field
from typing import Optional


class Section(BaseModel):
    """
    There will be a maximum of 6 sections in total. 2 easy, 2 medium, 2 hard.
    """

    id: str
    section_heading: str
    file_name: str
    token_count: int
    character_count: int


class User(BaseModel):
    # uuid PK
    id: str
    creator: str
    # FK to Section they will be creating Flashcards for
    flashcard_section_id: str
    # FK to Section they will be reviewing Flashcards for
    review_section_id: str


class CreateFlashcard(BaseModel):
    front: str
    back: str
    file_name: str
    section_heading: str
    # FK to Section
    section_id: str
    # FK to User
    user_id: str


class Flashcard(BaseModel):
    """
    5 will already be created by an AI user.
    """

    id: str
    front: str
    back: str
    file_name: str
    section_heading: str
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
    english_level: int = Field(..., alias="english_level")
    education_level: int = Field(..., alias="education_level")
    flashcard_experience: int = Field(..., alias="flashcard_experience")
    flashcard_preference: Optional[int] = Field(None, alias="flashcard_preference")
    flashcard_usage_frequency: int = Field(..., alias="flashcard_usage_frequency")
    study_duration: int = Field(..., alias="study_duration")
    current_tiredness: int = Field(..., alias="current_tiredness")
    # FK to User
    user_id: str

    class Config:
        populate_by_name = True


class ParticipantForm(BaseModel):
    donation_preference: int = Field(..., alias="donation_to")
    donation_other: Optional[str] = Field(None, alias="donation_to_other")
    data_policy_agreement: int = Field(..., alias="data_policy")
    # FK to User
    user_id: str

    class Config:
        use_enum_values = True
        populate_by_name = True
