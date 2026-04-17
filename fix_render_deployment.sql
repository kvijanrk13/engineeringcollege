-- Fix for Render deployment: Manual database fix (if migration still fails)
-- Run this in Render's database console ONLY if the automated migration still fails

-- Create ResearchPublication table if it doesn't exist
CREATE TABLE IF NOT EXISTS dashboard_researchpublication (
    id BIGSERIAL PRIMARY KEY,
    research_type VARCHAR(20),
    title VARCHAR(500) NOT NULL,
    authors TEXT,
    department VARCHAR(100),
    publication_year INTEGER,
    academic_year VARCHAR(20),
    status VARCHAR(20),
    doi VARCHAR(100),
    url VARCHAR(200),
    abstract TEXT,
    keywords VARCHAR(500),
    journal_name VARCHAR(300),
    issn VARCHAR(20),
    volume VARCHAR(50),
    issue VARCHAR(50),
    page_numbers VARCHAR(50),
    conference_name VARCHAR(300),
    conference_location VARCHAR(200),
    conference_dates VARCHAR(100),
    book_title VARCHAR(300),
    isbn VARCHAR(20),
    edition VARCHAR(50),
    patent_number VARCHAR(100),
    filing_date DATE,
    grant_date DATE,
    project_title VARCHAR(300),
    funding_agency VARCHAR(200),
    sanction_amount VARCHAR(100),
    award_title VARCHAR(300),
    awarding_body VARCHAR(200),
    award_date DATE,
    publisher_name VARCHAR(200),
    proof_document VARCHAR(100),
    proof_document_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    faculty_id BIGINT REFERENCES dashboard_faculty(id) ON DELETE CASCADE
);

-- Create FDP table if it doesn't exist
CREATE TABLE IF NOT EXISTS dashboard_fdp (
    id BIGSERIAL PRIMARY KEY,
    fdp_type VARCHAR(20),
    title VARCHAR(300) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    academic_year VARCHAR(20),
    organized_by VARCHAR(200),
    place VARCHAR(200),
    mode VARCHAR(20),
    level VARCHAR(20),
    role VARCHAR(20),
    sponsored_by VARCHAR(200),
    remarks TEXT,
    certificate VARCHAR(100),
    certificate_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    faculty_id BIGINT REFERENCES dashboard_faculty(id) ON DELETE CASCADE
);

-- Create indexes if needed
CREATE INDEX IF NOT EXISTS dashboard_researchpublication_faculty_id_idx ON dashboard_researchpublication(faculty_id);
CREATE INDEX IF NOT EXISTS dashboard_researchpublication_publication_year_idx ON dashboard_researchpublication(publication_year);
CREATE INDEX IF NOT EXISTS dashboard_fdp_faculty_id_idx ON dashboard_fdp(faculty_id);
CREATE INDEX IF NOT EXISTS dashboard_fdp_from_date_idx ON dashboard_fdp(from_date);

-- NOTE: The migration 0003_fdp_certificate_url_and_more.py now includes
-- the table creation logic, so this manual fix should not be needed.
-- Only use this if the migration still fails after redeployment.