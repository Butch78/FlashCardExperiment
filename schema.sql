CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


DROP TABLE IF EXISTS experiment_responses, feedback_responses, reviews, flashcards, participant_responses, users, sections CASCADE;

CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_heading TEXT NOT NULL,
    file_name TEXT NOT NULL,
    character_count BIGINT NOT NULL,
    token_count BIGINT NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    creator VARCHAR NOT NULL,
    flashcard_section_id UUID REFERENCES sections(id),
    review_section_id UUID REFERENCES sections(id)
);


CREATE TABLE participant_responses (
    id SERIAL PRIMARY KEY,
    donation_preference INT,
    donation_other TEXT,
    data_policy_agreement INT NOT NULL,
    user_id UUID REFERENCES users(id)
);

CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    section_id UUID REFERENCES sections(id),
    section_heading TEXT NOT NULL,
    file_name TEXT NOT NULL,
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



CREATE TABLE feedback_responses (
    id SERIAL PRIMARY KEY,
    gender TEXT,
    user_id UUID REFERENCES users(id),
    education_level INT NOT NULL,
    academic_performance INT NOT NULL
);

CREATE TABLE experiment_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    english_level INT NOT NULL,
    education_level INT NOT NULL,
    flashcard_experience INT NOT NULL,
    flashcard_preference INT,
    user_id UUID REFERENCES users(id),
    flashcard_usage_frequency INT NOT NULL,
    study_duration INT NOT NULL,
    current_tiredness INT NOT NULL
);
