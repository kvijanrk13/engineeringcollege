-- Fix for Render deployment: Manual database fix (if migration still fails)
-- Run this in Render's database console ONLY if the automated migration still fails

-- Create FDP table if it doesn't exist (PostgreSQL syntax)
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

-- Ensure certificate_url column exists
ALTER TABLE dashboard_fdp ADD COLUMN IF NOT EXISTS certificate_url VARCHAR(500);

-- Ensure proof_document_url column exists in researchpublication
ALTER TABLE dashboard_researchpublication ADD COLUMN IF NOT EXISTS proof_document_url VARCHAR(500);

-- Create indexes if needed
CREATE INDEX IF NOT EXISTS dashboard_fdp_faculty_id_idx ON dashboard_fdp(faculty_id);
CREATE INDEX IF NOT EXISTS dashboard_fdp_from_date_idx ON dashboard_fdp(from_date);

-- NOTE: The migration 0003_fdp_certificate_url_and_more.py now includes
-- the table creation logic, so this manual fix should not be needed.
-- Only use this if the migration still fails after redeployment.