# Getting Started with BudgetBuddy

Welcome! This guide will help you get BudgetBuddy up and running quickly.

## 🎯 What You're Building

A voice-activated expense tracker where you can:
- Speak: "add thirty dollars for groceries"
- Get confirmation: "$30.00 added to groceries"
- Track all your expenses in a database
- Query your spending by category

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] AWS Account with admin access (or permissions for S3, CloudFront, Lambda, API Gateway, RDS, Bedrock)
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Chrome browser (for Web Speech API testing)
- [ ] Python 3.12+ (for local Lambda testing)
- [ ] PostgreSQL client (psql) for database setup
- [ ] Basic knowledge of AWS, Python, and JavaScript

## 🚀 Quick Start (30 Minutes)

### Step 1: Database Setup (10 minutes)

```bash
# 1. Navigate to database folder
cd database

# 2. Read the setup guide
cat README.md

# 3. Follow detailed instructions in llmcoder.md for:
#    - Creating RDS PostgreSQL instance
#    - Running schema.sql to create tables
#    - Testing database connection

# 4. Note your database endpoint and credentials
#    You'll need these for the agent configuration
```

**Key Files:**
- `schema.sql` - Run this to create tables
- `llmcoder.md` - Complete setup instructions

**What You'll Get:**
- RDS PostgreSQL instance
- Two tables: `expenses` and `sessions`
- Optimized indexes for queries

### Step 2: Agent Deployment (15 minutes)

```bash
# 1. Navigate to agent folder
cd ../agent

# 2. Read the overview
cat README.md

# 3. Follow detailed instructions in llmcoder.md for:
#    - Packaging Lambda function
#    - Deploying to AWS
#    - Configuring environment variables
#    - Creating API Gateway endpoint

# 4. Note your API Gateway URL
#    You'll need this for frontend configuration
```

**Key Files:**
- `code/lambda_function.py` - Lambda entry point (ready to deploy)
- `requirements.txt` - Python dependencies
- `prompts.json` - LLM prompts
- `llmcoder.md` - Complete deployment instructions

**What You'll Get:**
- Lambda function processing expenses
- API Gateway endpoint
- LangGraph agent with Bedrock LLM

### Step 3: Frontend Deployment (5 minutes)

```bash
# 1. Navigate to frontend folder
cd ../frontend

# 2. Update API Gateway URL in code/app.js
#    Replace 'YOUR_API_GATEWAY_URL' with your actual endpoint

# 3. Follow detailed instructions in llmcoder.md for:
#    - Creating S3 bucket
#    - Uploading files
#    - Configuring CloudFront
#    - Setting up basic authentication

# 4. Access your frontend URL and test!
```

**Key Files:**
- `code/index.html` - Main web page (ready to deploy)
- `code/styles.css` - Styling
- `code/app.js` - JavaScript logic (update API URL)
- `llmcoder.md` - Complete deployment instructions

**What You'll Get:**
- Beautiful web interface
- Voice input button
- Text fallback input
- Deployed on S3 + CloudFront

## 🧪 Testing Your Deployment

### Test 1: Database Connection

```sql
-- Connect to your RDS instance
psql -h YOUR_RDS_ENDPOINT -U budgetbuddy_admin -d budgetbuddy

-- Verify tables exist
\dt

-- Insert test expense
INSERT INTO expenses (amount, category) VALUES (10.00, 'groceries');

-- Query expenses
SELECT * FROM expenses;
```

### Test 2: Agent API

```bash
# Test your API Gateway endpoint
curl -X POST https://YOUR_API_GATEWAY_URL/expense \
  -H "Content-Type: application/json" \
  -d '{"text": "add thirty dollars for groceries", "timestamp": "2025-10-21T19:53:00Z"}'

# Expected response:
# {"status": "success", "message": "$30.00 added to groceries", "expense_id": 1}
```

### Test 3: Frontend

1. Open your CloudFront URL in Chrome
2. Click the microphone button
3. Say: "add twenty dollars for dining"
4. Verify success popup appears
5. Check database to confirm expense was saved

## 📂 Understanding the Structure

```
budgetbuddy/
├── README.md                  # ← Start here: Project overview
├── GETTING_STARTED.md         # ← You are here!
├── .project-structure.md      # ← Navigation guide
│
├── frontend/                  # Web interface
│   ├── README.md              # What it does
│   ├── llmcoder.md           # How to build it (DETAILED)
│   └── code/                  # Ready-to-deploy files
│
├── agent/                     # Backend Lambda
│   ├── README.md              # What it does
│   ├── llmcoder.md           # How to build it (DETAILED)
│   └── code/                  # Ready-to-deploy files
│
└── database/                  # PostgreSQL
    ├── README.md              # What it contains
    ├── llmcoder.md           # How to set it up (DETAILED)
    └── schema.sql             # Run this to create tables
```

## 🔑 Key Configuration Points

### 1. Database Credentials (Agent)

Set these environment variables in Lambda:
```
DB_HOST=your-rds-endpoint.us-east-1.rds.amazonaws.com
DB_NAME=budgetbuddy
DB_USER=budgetbuddy_admin
DB_PASSWORD=your_secure_password
DB_PORT=5432
```

### 2. Bedrock Model (Agent)

```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v2:0
```

### 3. Allowed Categories (Agent)

```
ALLOWED_CATEGORIES=groceries,dining,entertainment,transportation,utilities,shopping,health,other
```

### 4. API Gateway URL (Frontend)

Update in `frontend/code/app.js`:
```javascript
const API_GATEWAY_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod';
```

## 🎨 Customization Ideas

Once it's working, try customizing:

### Add More Categories
1. Update `ALLOWED_CATEGORIES` in Lambda environment variables
2. Update prompt in `agent/prompts.json`
3. Test with new categories

### Change Color Scheme
Edit `frontend/code/styles.css`:
```css
/* Change microphone button color */
.mic-button {
    background-color: #your-color;
}
```

### Modify LLM Behavior
Edit `agent/prompts.json` to change how expenses are parsed

### Add Database Views
Add queries to `database/schema.sql`:
```sql
CREATE VIEW weekly_summary AS
SELECT DATE_TRUNC('week', date_added) AS week,
       SUM(amount) AS total
FROM expenses
GROUP BY week;
```

## 🐛 Common Issues & Solutions

### Issue: Lambda can't connect to database
**Solution:** Check VPC configuration and security groups. Lambda must be in same VPC as RDS.

### Issue: Microphone button doesn't work
**Solution:** Ensure you're using Chrome and HTTPS. Web Speech API requires secure context.

### Issue: API Gateway returns CORS error
**Solution:** Enable CORS in API Gateway and check Lambda response headers include `Access-Control-Allow-Origin`.

### Issue: Bedrock returns authentication error
**Solution:** Check Lambda IAM role has `bedrock:InvokeModel` permission.

### Issue: Database connection timeout
**Solution:** Verify Lambda security group can access RDS security group on port 5432.

## 📚 Next Steps

After basic deployment works:

1. **Add Authentication**: Replace basic auth with AWS Cognito
2. **Add Analytics**: Create dashboard for expense visualization
3. **Export Feature**: Add CSV export functionality
4. **Mobile App**: Create React Native app using same backend
5. **Multi-User**: Extend to support multiple users

## 💡 Pro Tips

- **Start Simple**: Get basic flow working before adding features
- **Test Each Layer**: Verify database → agent → frontend separately
- **Use CloudWatch**: Check Lambda logs for debugging
- **Version Control**: Commit working versions before major changes
- **Cost Monitoring**: Set up billing alerts in AWS

## 🆘 Need Help?

1. **Check llmcoder.md files** - They have detailed troubleshooting sections
2. **Check CloudWatch Logs** - Lambda and API Gateway logs show errors
3. **Test Components Individually** - Isolate the problem area
4. **Review Integration Points** - Check README files for how components connect

## 📞 Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

## ✅ Deployment Checklist

Use this checklist to track your progress:

- [ ] AWS account set up and CLI configured
- [ ] RDS PostgreSQL instance created
- [ ] Database schema applied (schema.sql)
- [ ] Database connection tested
- [ ] Lambda function packaged with dependencies
- [ ] Lambda function deployed to AWS
- [ ] Environment variables configured in Lambda
- [ ] API Gateway endpoint created
- [ ] API Gateway tested with curl
- [ ] Frontend files uploaded to S3
- [ ] CloudFront distribution configured
- [ ] API URL updated in frontend app.js
- [ ] Frontend tested in Chrome browser
- [ ] Voice input working
- [ ] Expense successfully saved to database
- [ ] End-to-end flow verified

## 🎉 Success!

Once all checkboxes are complete, you have a working expense tracker! 

Try saying: "add fifty dollars for groceries" and watch the magic happen! 🎤💰

---

**Remember**: This is an MVP. Start with the basics, get it working, then iterate and improve!

Good luck! 🚀


