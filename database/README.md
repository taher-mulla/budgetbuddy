# Database - PostgreSQL Schema for BudgetBuddy

## Purpose

The database stores expense records and agent session state. Two simple tables in Amazon RDS PostgreSQL.

## What CloudFormation Will Create

When you deploy `cloudformation/rds-stack.yaml`, AWS will create:

### Network Infrastructure (FREE)
- ✅ **VPC** - New isolated network (10.0.0.0/16)
- ✅ **2 Subnets** - In different availability zones (required by RDS)
- ✅ **Internet Gateway** - For public access
- ✅ **Route Table** - Network routing
- ✅ **Security Group** - Firewall allowing PostgreSQL port 5432 from anywhere

### Database (~$15-20/month, FREE for first 12 months)
- ✅ **RDS PostgreSQL 15** - db.t3.micro instance
- ✅ **20 GB Storage** - SSD (gp3)
- ✅ **Public Access** - So you can connect with pgAdmin
- ✅ **Automatic Backups** - 7 days retention
- ✅ **Encryption** - Data encrypted at rest

**Total Cost:** $0 if you have AWS Free Tier (first 12 months), otherwise ~$15-20/month

## Quick Start

### Step 1: Deploy CloudFormation Stack (5 minutes)

1. Log into AWS Console → CloudFormation
2. Click "Create stack" → "With new resources"
3. Choose "Upload a template file"
4. Upload `cloudformation/rds-stack.yaml`
5. Click "Next"
6. Fill in parameters:
   - **Stack name**: `budgetbuddy-database`
   - **DBPassword**: Choose a strong password (min 8 chars) - **SAVE THIS!**
   - **DBUsername**: `postgres` (default is fine)
   - **DBName**: `budgetbuddy` (default is fine)
7. Click "Next" → "Next" → "Create stack"
8. Wait 10-15 minutes for "CREATE_COMPLETE"

### Step 2: Get Connection Details (1 minute)

1. Go to CloudFormation → Stacks → `budgetbuddy-database`
2. Click "Outputs" tab
3. You'll see:
   - **DBEndpoint**: `budgetbuddy-db.xxxxx.us-east-1.rds.amazonaws.com`
   - **DBPort**: `5432`
   - **DBName**: `budgetbuddy`
   - **DBUsername**: `postgres`
   - **ConnectionString**: Copy this

### Step 3: Connect with pgAdmin (2 minutes)

1. Download and install [pgAdmin](https://www.pgadmin.org/download/) if you don't have it
2. Open pgAdmin
3. Right-click "Servers" → "Register" → "Server"
4. **General tab:**
   - Name: `BudgetBuddy`
5. **Connection tab:**
   - Host: (paste DBEndpoint from CloudFormation outputs)
   - Port: `5432`
   - Database: `budgetbuddy`
   - Username: `postgres`
   - Password: (the password you set in Step 1)
   - Save password: ✅ (optional)
6. Click "Save"

### Step 4: Run Schema (1 minute)

1. In pgAdmin, expand `BudgetBuddy` → `Databases` → `budgetbuddy`
2. Right-click `budgetbuddy` → "Query Tool"
3. Open `schema.sql` file in a text editor, copy contents
4. Paste into pgAdmin Query Tool
5. Click "Execute" (▶️ button)
6. You should see: "Tables created successfully!"

### Step 5: Verify Tables (30 seconds)

In pgAdmin:
1. Refresh `budgetbuddy` database
2. Expand `Schemas` → `public` → `Tables`
3. You should see:
   - ✅ `expenses`
   - ✅ `sessions`

**Done!** Database is ready for the agent to use.

## Connection Info for Agent Lambda

Save these for when you deploy the agent:

```
DB_HOST=<your-endpoint>.rds.amazonaws.com
DB_NAME=budgetbuddy
DB_USER=postgres
DB_PASSWORD=<your-password>
DB_PORT=5432
```

You'll set these as environment variables in Lambda.

## Testing Your Database

Run this in pgAdmin Query Tool:

```sql
-- Insert test expense
INSERT INTO expenses (amount, category, note)
VALUES (25.50, 'groceries', 'Test from pgAdmin');

-- Query it back
SELECT * FROM expenses;

-- Should show your test expense

-- Clean up
DELETE FROM expenses WHERE note = 'Test from pgAdmin';
```

## What NOT to Worry About (For MVP)

- ❌ Multi-AZ deployment - Single AZ is fine for personal use
- ❌ Read replicas - Not needed for low traffic
- ❌ Performance tuning - Default settings are sufficient
- ❌ Secrets Manager - Environment variables are fine for MVP
- ❌ VPC peering - We made DB publicly accessible for simplicity

## Stopping/Starting Database (To Save Money)

If you want to pause the database when not using:

1. Go to RDS → Databases → `budgetbuddy-db`
2. Click "Actions" → "Stop temporarily"
3. AWS will auto-start it after 7 days

**Note:** You can't stop Free Tier instances, but you're not charged anyway.

## Deleting Everything

When you're done and want to delete:

1. Go to CloudFormation → Stacks → `budgetbuddy-database`
2. Click "Delete"
3. Confirm deletion
4. Wait 5-10 minutes - everything will be removed

**Warning:** This deletes all your data! Export expenses first if you want to keep them.

## Troubleshooting

**Can't connect from pgAdmin:**
- Wait 10-15 minutes - RDS takes time to initialize
- Check CloudFormation stack is "CREATE_COMPLETE"
- Verify you're using the correct endpoint from Outputs
- Check your password is correct

**Stack creation failed:**
- Check you have < 2 VPCs in the region (soft limit is 5)
- Try a different region
- Delete the failed stack and try again

**Tables already exist error:**
- You ran schema.sql twice - that's okay
- Or manually drop tables and re-run

## Files in this Folder

- `schema.sql` - SQL to create tables (run once in pgAdmin)
- `llmcoder.md` - Context and details for AI/future reference
- `cloudformation/rds-stack.yaml` - Infrastructure template (deploy in AWS Console)

## Next Steps

After database is set up:
1. ✅ Database ready
2. ⏭️ Deploy agent Lambda function (see `/agent` folder)
3. ⏭️ Deploy frontend (see `/frontend` folder)
