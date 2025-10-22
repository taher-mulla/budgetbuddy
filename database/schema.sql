-- BudgetBuddy Database Schema
-- Simple schema for MVP: expenses and session state

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    category VARCHAR(50) NOT NULL,
    note TEXT,
    date_added TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for fast queries by category and date
CREATE INDEX IF NOT EXISTS idx_expenses_category_date 
    ON expenses(category, date_added DESC);

-- Index for date-based queries
CREATE INDEX IF NOT EXISTS idx_expenses_date_added 
    ON expenses(date_added DESC);

-- Sessions table for LangGraph state
CREATE TABLE IF NOT EXISTS sessions (
    user_id VARCHAR(50) PRIMARY KEY,
    state_json JSONB NOT NULL DEFAULT '{}',
    last_updated TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Trigger to auto-update last_updated
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sessions_last_updated
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- Insert default session for single user
INSERT INTO sessions (user_id, state_json)
VALUES ('me', '{"history": [], "context": {}}')
ON CONFLICT (user_id) DO NOTHING;

-- Verify tables created
SELECT 'Tables created successfully!' AS status;
