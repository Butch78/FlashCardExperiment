CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS experiment_responses, feedback_responses, reviews, flashcards, section_assignments, users, sections CASCADE;


CREATE TABLE participant_responses (
    id SERIAL PRIMARY KEY,
    donation_preference INT NULL,
    donation_other TEXT,
    data_policy_agreement BOOLEAN NOT NULL
);



CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_heading TEXT NOT NULL,
    file_name TEXT NOT NULL,
    tokens TEXT NOT NULL,
    character_count INT NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    ai BOOLEAN NOT NULL,
    flashcard_section_id UUID REFERENCES sections(id),
    review_section_id UUID REFERENCES sections(id)
);


CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    section_id UUID REFERENCES sections(id),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flashcard_id UUID REFERENCES flashcards(id),
    file_name TEXT NOT NULL,
    accuracy INT CHECK (accuracy BETWEEN 1 AND 5),
    comprehension INT CHECK (comprehension BETWEEN 1 AND 5),
    relevance INT CHECK (relevance BETWEEN 1 AND 5)
);

CREATE TABLE section_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    create_section_id UUID REFERENCES sections(id),
    review_section_id UUID REFERENCES sections(id)
);


CREATE TABLE feedback_responses (
    id SERIAL PRIMARY KEY,
    gender TEXT,
    education_level INT NOT NULL,
    academic_performance INT NOT NULL
);

CREATE TABLE experiment_responses (
    id SERIAL PRIMARY KEY,
    english_level INT NOT NULL,
    education_level INT NOT NULL,
    flashcard_experience INT NOT NULL,
    flashcard_preference INT,
    flashcard_usage_frequency INT NOT NULL,
    study_duration INT NOT NULL,
    current_tiredness INT NOT NULL
);
