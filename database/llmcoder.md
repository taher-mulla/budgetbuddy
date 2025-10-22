# Database Setup Instructions

## Context

### What BudgetBuddy Does
BudgetBuddy is a voice-activated expense tracker. User speaks "add thirty dollars for groceries" → Frontend captures it → Agent processes with LLM → **Database stores it**.

### Your Role in the System
You are the data persistence layer. You store:
1. **Expenses** - Every transaction the user logs
2. **Session State** - Agent's conversation memory for multi-turn clarifications

### Upstream (What Writes to You)
- **Agent Lambda function** (`/agent`) inserts expenses after parsing and validation
- **Agent Lambda function** reads/writes session state for conversation context

### Downstream (Who Reads from You)
- **Agent Lambda function** queries to check existing expenses (future: analytics)
- **Future: CSV Export feature** will query expense data for reports

## Database Schema

### Table 1: expenses

**Purpose:** Store every expense transaction

**Columns:**
- `id` - Auto-incrementing primary key
- `amount` - Money amount (NUMERIC for precision, e.g., 30.00)
- `category` - Text category (groceries, dining, etc.)
- `note` - Optional description
- `date_added` - Timestamp when logged

**Why these columns:**
- `amount` uses NUMERIC(10,2) not FLOAT to avoid rounding errors with money
- `category` is VARCHAR(50) to allow flexibility but enforce some limit
- `date_added` defaults to NOW() so we always know when expense happened
- Index on `(category, date_added)` for fast "sum groceries this month" queries

### Table 2: sessions

**Purpose:** Store LangGraph agent state so conversations can continue across requests

**Columns:**
- `user_id` - Identifier (just "me" for single-user MVP)
- `state_json` - JSONB blob containing chat history, pending actions
- `last_updated` - When this was last modified

**Why these columns:**
- `state_json` is JSONB (not TEXT) so we can query inside it if needed later
- `user_id` is primary key - one session per user
- `last_updated` auto-updates via trigger

## Setup Steps

### 1. Create RDS Instance

**Quick MVP Settings:**
- Engine: PostgreSQL 15
- Instance: db.t3.micro (cheapest, sufficient for single user)
- Storage: 20 GB
- Public Access: NO (Lambda connects via VPC)
- Backup: 7 days retention

**Using AWS Console:**
1. Go to RDS → Create Database
2. Choose PostgreSQL
3. Templates: Free tier (if available) or Dev/Test
4. Set DB instance identifier: `budgetbuddy-db`
5. Set master username: `postgres` (or your choice)
6. Set master password: (remember this!)
7. Instance: db.t3.micro
8. Storage: 20 GB, gp3
9. VPC: Choose your default VPC
10. Public access: No
11. Create database

### 2. Get Connection Info

After creation (takes ~5 minutes):
1. Click on your database instance
2. Find "Endpoint" - this is your `DB_HOST`
3. Note the port (usually 5432)

### 3. Connect and Initialize

**From a machine that can reach your RDS** (bastion host, or temporarily enable public access):

```bash
# Install PostgreSQL client if needed
# Ubuntu: sudo apt-get install postgresql-client
# macOS: brew install postgresql

# Connect (replace with your endpoint and username)
psql -h your-endpoint.region.rds.amazonaws.com -U postgres -d postgres

# Create database
CREATE DATABASE budgetbuddy;

# Connect to it
\c budgetbuddy

# Run schema file
\i schema.sql

# Verify tables exist
\dt

# You should see: expenses, sessions

# Exit
\q
```

### 4. Configure Lambda Access

**Security Group Setup:**
1. Your RDS has a security group (check in RDS console)
2. Edit that security group
3. Add inbound rule: PostgreSQL (port 5432) from Lambda security group
4. This allows Lambda to connect

**Lambda Environment Variables:**
Set these in your Lambda function:
```
DB_HOST=your-endpoint.region.rds.amazonaws.com
DB_NAME=budgetbuddy
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

**Lambda VPC Configuration:**
1. Lambda must be in same VPC as RDS
2. Lambda needs security group that can access RDS security group
3. Lambda needs at least 2 subnets in different AZs

## Testing

### Test the Schema

```sql
-- Insert test expense
INSERT INTO expenses (amount, category, note)
VALUES (25.50, 'groceries', 'Test expense');

-- Query it back
SELECT * FROM expenses;

-- Should show: id=1, amount=25.50, category=groceries, etc.

-- Test session state
SELECT * FROM sessions WHERE user_id = 'me';

-- Should show default empty session

-- Clean up test data
DELETE FROM expenses WHERE note = 'Test expense';
```

### Test from Lambda

The agent's `db_utils.py` has functions:
- `insert_expense(amount, category, note)` - Adds expense
- `get_session_state(user_id)` - Retrieves state
- `save_session_state(user_id, state)` - Saves state

Test by deploying Lambda and calling API endpoint.

## Common Queries You'll Use

```sql
-- Get all expenses
SELECT * FROM expenses ORDER BY date_added DESC;

-- Sum by category this month
SELECT category, SUM(amount) as total
FROM expenses
WHERE date_added >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY category;

-- Count expenses
SELECT COUNT(*) FROM expenses;

-- Get session state
SELECT state_json FROM sessions WHERE user_id = 'me';
```

## What NOT to Worry About (For MVP)

- ❌ Secrets Manager - Just use environment variables for now
- ❌ CloudWatch alarms - Can add later if needed
- ❌ Read replicas - Single instance is fine
- ❌ Multi-AZ - Not needed for personal project
- ❌ IAM database authentication - Too complex for MVP
- ❌ Advanced indexes - The basic ones in schema.sql are sufficient
- ❌ Backup testing - RDS auto-backup is enabled by default
- ❌ Performance monitoring - Worry about this if it's slow

## Troubleshooting

**Can't connect from psql:**
- Check security group allows your IP
- Try enabling "Public access" temporarily for setup
- Verify endpoint and credentials

**Lambda timeout connecting:**
- Lambda must be in VPC
- Security groups must allow connection
- Check Lambda logs in CloudWatch

**Table already exists error:**
- You ran schema.sql twice, that's fine
- Or drop tables first: `DROP TABLE IF EXISTS expenses, sessions CASCADE;`

## That's It!

Database setup should take 10-15 minutes. Once `schema.sql` runs successfully, you're done. The agent will handle all database operations from here.
