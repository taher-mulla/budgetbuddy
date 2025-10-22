# BudgetBuddy - Voice-Activated Expense Tracker

A fast, personal, voice-activated expense tracking system built on AWS, prioritizing rapid deployment over perfection. Track your expenses by simply speaking into your phone or typing manually.

## 🎯 Project Objective

Develop a minimal viable product (MVP) for personal expense tracking with:
- Voice-first interface using Chrome's Web Speech API
- Natural language processing via AWS Bedrock LLM
- Simple PostgreSQL database for storage
- Basic authentication (no complex user management)
- Single-user focus (expandable to multi-user later)

## 🏗️ Architecture Overview

### Three Main Components

1. **Frontend** (`/frontend`)
   - Single-page web application (HTML/CSS/JS)
   - Hosted on AWS S3 + CloudFront
   - Voice input via Web Speech API (Chrome native)
   - Fallback text input for manual entry
   - Basic HTTP authentication

2. **Agent** (`/agent`)
   - Python AWS Lambda function
   - LangGraph agent for conversational state management
   - AWS Bedrock LLM integration (Claude 3.5 Sonnet or Llama 3)
   - Natural language parsing and validation
   - API Gateway endpoint for frontend communication

3. **Database** (`/database`)
   - Amazon RDS PostgreSQL
   - Two tables: `expenses` and `sessions`
   - Optimized indexes for fast queries
   - Session state persistence for agent

### Data Flow

```
User speaks → Chrome Web Speech API → Frontend JS
                                           ↓
                                    POST to API Gateway
                                           ↓
                                    Lambda Agent
                                           ↓
                                    LangGraph + Bedrock LLM
                                           ↓
                                    Parse & Validate
                                           ↓
                                    Store in RDS PostgreSQL
                                           ↓
                                    Return confirmation to Frontend
```

## 📁 Directory Structure

```
budgetbuddy/
├── frontend/              # Web interface
│   ├── README.md          # Frontend overview
│   ├── llmcoder.md        # Detailed implementation guide for AI
│   ├── cloudformation/    # Infrastructure templates
│   └── code/              # HTML, CSS, JavaScript files
│       ├── index.html     # Main page with voice interface
│       ├── styles.css     # Responsive styling
│       └── app.js         # Web Speech API + API calls
│
├── agent/                 # Backend Lambda function
│   ├── README.md          # Agent overview
│   ├── llmcoder.md        # Detailed implementation guide for AI
│   ├── requirements.txt   # Python dependencies
│   ├── prompts.json       # LLM prompts for parsing
│   ├── cloudformation/    # Infrastructure templates
│   └── code/              # Python Lambda code
│       ├── lambda_function.py  # Entry point
│       ├── agent_logic.py      # LangGraph workflow
│       ├── bedrock_client.py   # AWS Bedrock wrapper
│       └── db_utils.py         # Database operations
│
└── database/              # PostgreSQL schema
    ├── README.md          # Database overview
    ├── llmcoder.md        # Detailed setup guide for AI
    ├── schema.sql         # Table definitions and indexes
    └── cloudformation/    # RDS infrastructure templates
```

## 🚀 Getting Started

### Prerequisites

- AWS Account with permissions for S3, CloudFront, Lambda, API Gateway, RDS, Bedrock
- AWS CLI configured
- Chrome browser (for Web Speech API)
- PostgreSQL client (for database setup)

### Deployment Steps

1. **Database Setup**
   ```bash
   cd database
   # Deploy RDS instance via CloudFormation
   # Run schema.sql to create tables
   # See database/llmcoder.md for detailed steps
   ```

2. **Agent Deployment**
   ```bash
   cd agent
   # Package Lambda function with dependencies
   # Deploy via CloudFormation or AWS Console
   # Configure environment variables
   # See agent/llmcoder.md for detailed steps
   ```

3. **Frontend Deployment**
   ```bash
   cd frontend
   # Upload code/ contents to S3 bucket
   # Configure CloudFront distribution
   # Update app.js with API Gateway URL
   # See frontend/llmcoder.md for detailed steps
   ```

### Quick Test

After deployment:
1. Open the frontend URL in Chrome
2. Tap the microphone button
3. Say: "add thirty dollars for groceries"
4. See confirmation: "$30.00 added to groceries"

## 💡 Usage Examples

### Voice Commands

- "add thirty dollars for groceries"
- "forty five dollars dining out"
- "spent twenty on transportation"
- "add fifteen dollars to entertainment, went to the movies"

### Expected Categories

- groceries
- dining
- entertainment
- transportation
- utilities
- shopping
- health
- other

## 📊 Current Features (MVP)

✅ Voice-activated expense entry  
✅ Text fallback for manual entry  
✅ Natural language parsing via LLM  
✅ Category validation  
✅ Clarification loops for ambiguous input  
✅ PostgreSQL storage with timestamps  
✅ Basic HTTP authentication  
✅ Session state persistence  

## 🔮 Future Enhancements

### Phase 2: Enhanced Functionality

**MCP Server Integration**
- FastAPI-based Model Context Protocol server
- Structured tools: `insert_expense`, `read_expenses`, `sum_by_category`, `compare_months`
- Replace direct SQL with tool calls for better abstraction

**CSV Export**
- Web page with date range picker
- Query database and generate CSV
- Store in S3 with signed URL for download
- Email option for automated monthly reports

**Smart Categorization**
- LLM-inferred categories from context (e.g., "movie with friends" → "entertainment")
- Learning from user's correction patterns
- Fuzzy matching for typos and variations

**Notifications & Reminders**
- Clarification prompts via SMS (Twilio or SNS)
- Daily/weekly expense summaries
- Budget alerts when approaching limits
- Web push notifications (experimental)

### Phase 3: Analytics & Insights

- Monthly spending trends dashboard
- Category-based budget tracking
- Comparison with previous months
- Expense predictions using historical data
- Visualizations (charts, graphs)

### Phase 4: Multi-User Support

- User authentication via Cognito
- Per-user expense isolation
- Shared household budgets
- Family/group expense tracking

## 🔒 Security Considerations

**Current (MVP):**
- Basic HTTP authentication (hardcoded credentials)
- HTTPS via CloudFront
- VPC isolation for RDS
- No public database access

**Recommended for Production:**
- AWS Cognito for user authentication
- Secrets Manager for database credentials
- API Gateway authorization
- Rate limiting and WAF
- Encrypted database connections (SSL/TLS)
- Regular security audits

## 📝 Documentation

Each component folder contains:
- **README.md**: Overview of what it does and files it contains
- **llmcoder.md**: Detailed implementation instructions for AI code generation

These files serve as comprehensive guides for implementing or modifying each component.

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Web Speech API
- **Backend**: Python 3.12, LangGraph, AWS Lambda
- **LLM**: AWS Bedrock (Claude 3.5 Sonnet / Llama 3 70B)
- **Database**: PostgreSQL 15 on Amazon RDS
- **Infrastructure**: AWS CloudFormation, S3, CloudFront, API Gateway
- **Development**: AWS CLI, psql, Git

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ for fast, practical expense tracking**
