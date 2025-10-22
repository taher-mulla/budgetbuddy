# Agent - Expense Processing Lambda

## Purpose

The agent is a Python AWS Lambda function that processes natural language expense entries. It uses LangGraph for workflow management and AWS Bedrock (Claude) for LLM parsing.

## What It Does

1. Receives text from frontend: `"add thirty dollars for groceries"`
2. Calls LLM to parse into structured data: `{amount: 30, category: "groceries"}`
3. Validates amount and category
4. Saves to database if valid, or returns clarification request
5. Returns response to frontend

## Files

### Code (`code/`)
- `lambda_function.py` - AWS Lambda entry point
- `agent.py` - LangGraph workflow (parse → validate → save)
- `llm.py` - AWS Bedrock LLM client
- `db_utils.py` - Database operations with connection pooling
- `utils.py` - Helper functions (JSON parsing, config loading)

### Configuration
- `agent_config.yaml` - Categories, LLM settings, defaults
- `prompts.yaml` - LLM prompts for parsing and clarification
- `requirements.txt` - Python dependencies

### Infrastructure
- `cloudformation/` - Lambda, API Gateway, IAM roles (coming soon)
- `llmcoder.md` - AI scratch pad with design decisions

## Dependencies

```
langgraph>=0.2.0      # Workflow management
boto3>=1.34.0         # AWS Bedrock
psycopg2-binary>=2.9.9 # PostgreSQL
pydantic>=2.0.0       # Data validation
```

## Environment Variables

Set these in Lambda configuration:

```
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=budgetbuddy
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION=us-east-1
```

## LangGraph Workflow

```
Entry
  ↓
parse (LLM extracts JSON)
  ↓
validate (check amount + category)
  ├─ valid → save → success
  └─ invalid → clarification
```

## Integration Points

### Receives From
- **Frontend** via API Gateway POST: `{"text": "...", "timestamp": "..."}`

### Connects To
- **Database** (RDS PostgreSQL) for storing expenses and session state
- **AWS Bedrock** for Claude LLM

### Returns To
- **Frontend** with JSON response:
  - Success: `{"status": "success", "message": "$30.00 added to groceries"}`
  - Clarification: `{"status": "clarification_needed", "message": "..."}`
  - Error: `{"status": "error", "message": "..."}`

## Local Testing

```python
python code/lambda_function.py
```

## Deployment

### Step 1: Package Lambda
```bash
cd agent
mkdir package
pip install -r requirements.txt -t package/
cp code/*.py package/
cp *.xml package/
cd package
zip -r ../lambda-deployment.zip .
```

### Step 2: Create Lambda Function
1. Go to AWS Lambda → Create function
2. Runtime: Python 3.12
3. Upload `lambda-deployment.zip`
4. Handler: `lambda_function.lambda_handler`
5. Set environment variables (see above)
6. Set timeout: 30 seconds
7. Memory: 512 MB

### Step 3: Configure VPC
1. Lambda must be in same VPC as RDS
2. Use security group from database CloudFormation outputs
3. Add subnets (at least 2 in different AZs)

### Step 4: Create API Gateway
1. Create HTTP API
2. Add POST route: `/expense`
3. Integration: Lambda function
4. Enable CORS

### Step 5: Test
```bash
curl -X POST https://your-api-gateway-url/expense \
  -H "Content-Type: application/json" \
  -d '{"text": "add thirty dollars for groceries"}'
```

Expected response:
```json
{
  "status": "success",
  "message": "$30.00 added to groceries",
  "expense_id": 1
}
```

## CloudFormation Deployment

### Prerequisites
1. Database stack deployed (`budgetbuddy-database`)
2. Lambda deployment package uploaded to S3

### Step 1: Upload Lambda Package to S3
```bash
# Package Lambda
cd agent
mkdir package
pip install -r requirements.txt -t package/
cp code/*.py package/
cp *.yaml package/
cd package
zip -r ../lambda-deployment.zip .
cd ..

# Create S3 bucket (if needed)
aws s3 mb s3://budgetbuddy-lambda-deploy

# Upload package
aws s3 cp lambda-deployment.zip s3://budgetbuddy-lambda-deploy/
```

### Step 2: Deploy CloudFormation Stack
```bash
aws cloudformation create-stack \
  --stack-name budgetbuddy-agent \
  --template-body file://cloudformation/lambda-stack.yaml \
  --parameters \
    ParameterKey=DatabaseStackName,ParameterValue=budgetbuddy-database \
    ParameterKey=DBPassword,ParameterValue=YOUR_DB_PASSWORD \
    ParameterKey=LambdaS3Bucket,ParameterValue=budgetbuddy-lambda-deploy \
    ParameterKey=LambdaS3Key,ParameterValue=lambda-deployment.zip \
  --capabilities CAPABILITY_IAM
```

### Step 3: Get API Endpoint
```bash
aws cloudformation describe-stacks \
  --stack-name budgetbuddy-agent \
  --query 'Stacks[0].Outputs'
```

Look for `ApiEndpoint` output - this is your API Gateway URL.

### Step 4: Test
```bash
curl -X POST https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/expense \
  -H "Content-Type: application/json" \
  -d '{"text": "add thirty dollars for groceries"}'
```

### What CloudFormation Creates
- ✅ Lambda function with all dependencies
- ✅ IAM role with Bedrock and VPC permissions
- ✅ Lambda security group
- ✅ Database security group ingress rule (allows Lambda access)
- ✅ API Gateway HTTP API
- ✅ API Gateway integration and route
- ✅ CORS configuration

**Reuses from database stack:**
- VPC and subnets
- Database security group
- Database endpoint and credentials

## Troubleshooting

**Lambda timeout:**
- Increase timeout to 30 seconds
- Check database connection isn't hanging

**Can't connect to database:**
- Verify Lambda is in same VPC as RDS
- Check security groups allow connection
- Verify environment variables are correct

**Bedrock permission denied:**
- Add `bedrock:InvokeModel` to Lambda IAM role

**Import errors:**
- Ensure all dependencies in `requirements.txt` are in deployment package
- Check handler is set to `lambda_function.lambda_handler`

## What's Next

1. Deploy with CloudFormation
2. Add retry logic for failures
3. Add CloudWatch metrics
4. Add unit tests
