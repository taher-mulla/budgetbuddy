# Agent Implementation - Scratch Pad

## What This Component Does

The agent is the brain of BudgetBuddy. It receives natural language text from the frontend, uses an LLM via AWS Bedrock to parse structured data, validates the information, saves it to the database, or asks for clarification if something is unclear.

The complete flow is: Frontend sends text like "add thirty dollars for groceries" to API Gateway, which triggers the Lambda agent. The agent uses Claude via Bedrock to extract the amount and category, validates both, inserts into RDS if valid, and returns a confirmation or clarification request back to the frontend.

## System Context

### Upstream Data Sources
The frontend at `/frontend` sends POST requests to API Gateway with JSON containing the user's spoken or typed text and a timestamp. API Gateway then invokes the Lambda function with this payload.

### Downstream Integrations
The agent connects to two main systems: the database at `/database` for storing expenses and reading session state, and AWS Bedrock for Claude LLM access to parse natural language into structured JSON.

### Data Flow Summary
User input flows from frontend through API Gateway to Lambda agent, which calls Bedrock LLM for parsing, then stores results in RDS PostgreSQL, and finally returns a response back through API Gateway to the frontend.

## Architecture Decisions

### Why LangGraph
LangGraph provides clear state management for multi-turn conversations, explicit workflow definition through nodes and edges, easy conditional routing for clarification loops, and a scalable structure for adding features like budget checking later.

The workflow is simple: parse with LLM, validate the data, then either save to database or request clarification. This structure makes debugging easy and allows each step to be tested independently.

### Why Separate Files
The code is organized into distinct modules for clarity and maintainability. The llm.py file handles only Bedrock connections and LLM invocations. The db_utils.py manages all database operations with connection pooling. The agent.py contains the core LangGraph workflow. The utils.py provides common functions like JSON parsing and config loading. The lambda_function.py serves as the AWS Lambda entry point.

This separation makes each component easy to test, modify, and understand independently. For example, changing from Claude to another LLM only requires modifying llm.py, not the entire agent logic.

### Why XML for Configuration
XML was chosen over JSON for config and prompts because it's more readable for humans editing prompts, provides clear hierarchical structure without escaping issues, and doesn't require escaping quotes in long prompt strings that JSON would need.

The trade-off is slightly more complex parsing, but for our use case where prompts contain natural language with lots of punctuation, XML is cleaner than JSON strings with escaped characters everywhere.

### Why Pydantic Models
Pydantic provides automatic validation of data types, better IDE support with type hints, easy serialization to and from JSON, and clear documentation of expected data structures through the model definitions.

Using Pydantic for ExpenseData ensures we catch invalid amounts or missing fields early, before trying to save to the database. It also makes the code self-documenting since the model shows exactly what fields are expected.

### Why Connection Pooling
Lambda containers are reused across invocations, so maintaining a connection pool improves performance by reusing database connections instead of creating new ones each time. This is a best practice for Lambda functions that access databases frequently.

The DatabaseManager class handles pooling automatically, getting connections from the pool when needed and returning them after use, which is both faster and more efficient than opening fresh connections.

## Implementation Notes

### LangGraph Workflow Structure
The workflow has three main nodes: parse uses the LLM to extract JSON from natural language, validate checks if the amount is positive and category is valid, and save inserts the expense into the database.

After validation, the workflow routes to either save for valid data or directly to END for clarification. This conditional routing is the key to handling invalid input gracefully without crashing or saving bad data.

### LLM Output Handling
The parse_json_from_text utility function handles various LLM response formats because Claude sometimes adds explanatory text before or after the JSON, might wrap JSON in markdown code blocks, or could include the JSON inline with other text.

The function tries multiple extraction strategies: first parsing the whole response as JSON, then using regex to find JSON objects, then checking for markdown code blocks. This robust approach prevents failures when the LLM doesn't return pure JSON.

### Category Validation Process
Category validation happens in two passes. First, exact matching checks if the category string exactly matches a valid category. If that fails, fuzzy matching tries substring matching to catch variations like "grocery" matching "groceries" or "gas" matching "transportation".

If both fail, the validation node sets clarification_needed to true and builds a message asking the user to pick from valid categories. This two-tier approach balances strict validation with user-friendly flexibility.

### Session State Management
Session state is stored in the database sessions table using JSONB format. Each user has one session row identified by user_id which is "me" for the MVP single-user case.

The state includes conversation history limited to the last ten interactions to prevent unbounded growth. This history could be used for multi-turn clarifications in future versions, though the MVP doesn't fully leverage it yet.

## Environment Variables Required

The Lambda function needs several environment variables to operate: DB_HOST for the RDS endpoint, DB_NAME for the database name (budgetbuddy), DB_USER and DB_PASSWORD for PostgreSQL credentials, DB_PORT for the PostgreSQL port (5432), BEDROCK_MODEL_ID for the Claude model identifier, and AWS_REGION for Bedrock API calls.

These are set automatically by CloudFormation except for DB_PASSWORD which must be provided as a parameter during stack creation.

## Files Created and Their Purposes

The llm.py file creates a clean interface to AWS Bedrock with the LLM class that handles authentication, request formatting, and response parsing for Claude. The db_utils.py implements connection pooling and provides functions for inserting expenses, getting session state, and saving session updates.

The agent.py file defines the ExpenseAgent class containing the LangGraph workflow, parsing logic, validation rules, and response formatting. The utils.py provides helper functions for extracting JSON from text, loading XML configs, formatting currency, and normalizing category names.

The lambda_function.py serves as the entry point, initializing the agent once and reusing it across invocations, parsing API Gateway events, and formatting responses. The prompts.xml stores LLM prompts as named templates, and agent_config.xml holds categories, LLM settings, and other configuration values.

## What We Deliberately Excluded for MVP

Multiple LLM providers are not supported because Claude via Bedrock meets all MVP needs and adding provider abstraction would complicate the code unnecessarily. Retry logic for LLM and database failures is absent to keep complexity low, though production should add this.

Caching of LLM responses is skipped since Lambda cold starts make caching less effective, and the cost savings wouldn't be significant for single-user MVP usage. Advanced fuzzy matching beyond simple substring comparison is overkill for eight categories and can be added if users report issues.

Budget tracking, multi-user support, expense editing and deletion, and analytics are all deferred to post-MVP phases since the core value is quick expense logging, not sophisticated financial management.

## Next Steps After MVP Deployment

After the MVP is working, priority improvements include adding retry logic with exponential backoff for both LLM and database operations, implementing proper error typing instead of generic exceptions, adding CloudWatch metrics for monitoring latency and errors, writing unit tests for each LangGraph node, and documenting common failure modes.

Secondary enhancements could include supporting additional LLM providers for cost optimization, implementing response caching for repeated queries, adding a budget checking node to the workflow, enabling expense editing and soft deletion, and building analytics views for spending trends.

---

## Analysis - October 22, 2024

### Issues Found During Code Review

**CRITICAL ISSUE #1 - FIXED: XML Config Parsing**
The original load_config function in utils.py did not handle multiple XML elements with the same tag name correctly. When the agent_config.xml contained multiple category tags, the parser would only keep the last one instead of creating a list.

Fixed by detecting when all children share the same tag name and creating a Python list in that case, otherwise creating a dictionary for mixed tag names. The agent.py code now checks if categories_config is a list and uses it directly.

**CRITICAL ISSUE #2 - FIXED: Database EngineVersion Missing**
The RDS CloudFormation template was missing the EngineVersion property which could cause unpredictable version selection or deployment failures. Added EngineVersion with value 15.4 to match the PostgreSQL version we're targeting.

**ISSUE #3: JSON Parsing Regex Limitation**
The parse_json_from_text function uses a simple regex that won't match nested JSON structures. If the LLM returns JSON with nested objects or arrays, the regex pattern will fail to extract it correctly.

For MVP this is acceptable because our expense JSON is flat with no nesting. Future versions should use a more sophisticated extraction approach or a proper JSON-aware parser that can handle arbitrary nesting depth.

**ISSUE #4: Prompt Formatting Safety**
The agent uses string format method on prompts loaded from XML, which could break if the prompt text contains curly braces that aren't intended as placeholders. Currently safe because our prompts are clean, but fragile for future changes.

Better approach would be using explicit keyword arguments or a templating engine that doesn't conflict with natural language punctuation. For MVP, documented the assumption that prompts shouldn't contain literal curly braces outside of placeholders.

**VERIFIED WORKING:**
LangGraph workflow structure with proper state typing and conditional edges is correctly implemented. Connection pooling in DatabaseManager follows Lambda best practices with get_connection context manager. Pydantic models provide validation without excessive complexity.

CloudFormation template correctly imports VPC and subnet IDs from the database stack, creates appropriate security groups, and sets all required IAM permissions. API Gateway configuration includes CORS headers and uses HTTP API for lower cost. Lambda VPC configuration properly splits the subnet string and selects both subnets.

### Priority Fixes Completed

Both high priority issues have been fixed: XML category parsing now correctly returns lists for repeated elements, and database CloudFormation includes the required EngineVersion property.

Medium priority items like improved JSON parsing can wait for post-MVP if they become actual problems rather than theoretical ones. Low priority formatting safety is documented and acceptable given current prompt structure.

### Deployment Readiness

The agent code is now ready for deployment. All critical bugs are fixed, CloudFormation templates are complete and correct, environment variables are properly configured, and integration points with database and frontend are well defined.

The only remaining manual step is uploading the Lambda deployment package to S3 before running CloudFormation, which is documented in the README with exact commands.

---

