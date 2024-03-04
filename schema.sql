CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TABLE IF EXISTS pilot_demographics, pilot_feedback_responses, pilot_reviews, pilot_flashcards,  pilot_participants, pilot_users, pilot_sections CASCADE;

CREATE TABLE pilot_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_heading TEXT NOT NULL,
    file_name TEXT NOT NULL,
    character_count BIGINT NOT NULL,
    token_count BIGINT NOT NULL
);

CREATE TABLE pilot_users (
    id UUID PRIMARY KEY,
    creator VARCHAR NOT NULL,
    flashcard_section_id UUID REFERENCES pilot_sections(id),
    review_section_id UUID REFERENCES pilot_sections(id)
);


CREATE TABLE pilot_participants (
    id SERIAL PRIMARY KEY,
    donation_preference INT,
    donation_other TEXT,
    data_policy_agreement INT NOT NULL,
    user_id UUID REFERENCES pilot_users(id)
);

CREATE TABLE pilot_flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    section_id UUID REFERENCES pilot_sections(id),
    section_heading TEXT NOT NULL,
    file_name TEXT NOT NULL,
    user_id UUID REFERENCES pilot_users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pilot_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flashcard_id UUID REFERENCES pilot_flashcards(id),
    file_name TEXT NOT NULL,
    accuracy INT,
    comprehension INT,
    relevance INT 
);


CREATE TABLE pilot_demographics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender TEXT,
    english_level INT NOT NULL,
    education_level INT NOT NULL,
    academic_performance INT NOT NULL
    flashcard_experience INT NOT NULL,
    flashcard_preference INT,
    user_id UUID REFERENCES pilot_users(id),
    flashcard_usage_frequency INT NOT NULL,
    study_duration INT NOT NULL,
    current_tiredness INT NOT NULL,
    interview_email TEXT NOT NULL,
    results TEXT NOT NULL
);
