from pydantic import BaseModel




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

