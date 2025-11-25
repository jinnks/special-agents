# Special Agents - Ethical AI Marketplace

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)
![Claude](https://img.shields.io/badge/claude-3.5%20sonnet-purple.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)
![Contributors](https://img.shields.io/github/contributors/jinnks/special-agents.svg)
![Stars](https://img.shields.io/github/stars/jinnks/special-agents.svg)

**The world's first standardized package format for AI agents**

[Live Demo](http://localhost:5000) • [Documentation](AGENT_PACKAGE_SPEC.md) • [Roadmap](ROADMAP.md) • [Contributing](CONTRIBUTING.md)

</div>

---

## 🎯 What is Special Agents?

A marketplace for specialized AI agents that bring positive change to humanity. Built with Flask, gevent, and Anthropic Claude API.

### 🚀 Key Innovation: The `.sagent` Package Format

Special Agents introduces the **industry's first standardized package format** for AI agents - think npm for AI!

**Why this matters:**
- ❌ OpenAI GPTs are platform-locked
- ❌ LangChain requires heavy coding
- ❌ No portability between platforms
- ✅ `.sagent` packages work anywhere!

## Features

- **Agent Marketplace**: Browse and purchase specialized AI agents
- **User Authentication**: Secure registration and login for buyers and sellers
- **Chat Interface**: Interact with purchased agents through a real-time chat interface
- **Ethical Review**: All agents reviewed for ethical compliance
- **Seller Platform**: Create and sell your own specialized AI agents
- **📦 .sagent Package Format**: Industry-leading package system for professional agents (see below)

## Technology Stack

### Backend
- **Flask 3.0.0**: Lightweight web framework
- **gevent 24.2.1**: Async I/O for handling concurrent chat requests efficiently
- **Anthropic Claude API**: Powers the AI agents with Claude 3.5 Sonnet
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **Flask-Bcrypt**: Password hashing

### Frontend
- Simple HTML/CSS/JS for fast prototyping
- Responsive design
- Real-time chat interface

## Setup Instructions

### 1. Clone and Navigate
```bash
cd ~/special-agents/backend
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```bash
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Get your Anthropic API key from**: https://console.anthropic.com/

### 5. Run the Application

```bash
python run.py
```

The application will be available at: http://localhost:5000

## Usage

### For Buyers

1. **Register**: Create an account as a buyer
2. **Browse**: Explore the marketplace for specialized agents
3. **Purchase**: Buy agents that fit your needs
4. **Chat**: Interact with your agents through the chat interface
5. **Review**: Share your experience to help others

### For Sellers

1. **Register as Seller**: Create an account and check "Register as seller"
2. **Create Agent**: Design a specialized AI agent with a custom system prompt
3. **Ethical Review**: Wait for approval (agents are reviewed for ethical compliance)
4. **Earn**: Once approved, your agent will be listed in the marketplace

## Agent Categories

- **Productivity**: Task management, scheduling, organization
- **Education**: Math tutors, language learning, study assistants
- **Travel**: Holiday planning, itinerary creation, travel advice
- **Health**: Wellness coaching, nutrition guidance, fitness planning
- **Finance**: Budget planning, savings advice, financial education
- **Creative**: Writing assistance, brainstorming, creative projects

## Ethical Guidelines

All agents must:
- Promote positive outcomes for users and society
- Respect privacy, fairness, and human autonomy
- Cannot be misused for harmful purposes
- Align with Constitutional AI principles

## Performance

The application uses **gevent** for async I/O, making it efficient for:
- Concurrent chat requests
- Multiple agent interactions
- Real-time API calls to Claude

For future optimization, performance-critical sections can be Cythonized.

## Database

The app uses SQLite by default (specified in `.env`). For production, switch to PostgreSQL:

```bash
DATABASE_URL=postgresql://user:password@localhost/special_agents
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── claude_service.py    # Anthropic API integration
│   └── routes/
│       ├── main.py          # Homepage routes
│       ├── auth.py          # Authentication routes
│       ├── agents.py        # Marketplace routes
│       └── chat.py          # Chat interface routes
├── templates/               # HTML templates
├── static/
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variables template
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user

### Agents
- `GET /agents/` - Browse marketplace
- `GET /agents/<id>` - View agent details
- `POST /agents/create` - Create new agent (sellers only)
- `POST /agents/<id>/purchase` - Purchase an agent
- `POST /agents/<id>/review` - Add review
- `GET /agents/my-agents` - View created agents (sellers)
- `GET /agents/my-purchases` - View purchased agents

### Chat
- `GET /chat/agent/<id>` - Chat interface
- `POST /chat/agent/<id>/message` - Send message to agent
- `POST /chat/agent/<id>/clear` - Clear conversation history

## 📦 .sagent Package Format

Special Agents introduces the **`.sagent` package format** - a standardized way to create and distribute AI agents.

### What is .sagent?

A `.sagent` file is a ZIP archive containing:
- `agent.yaml` - Metadata, pricing, configuration
- `system_prompt.txt` - AI instructions
- `examples/` - Sample conversations (optional)
- `knowledge/` - Reference materials (optional)
- `README.md` - Documentation (optional)

### Why Use Packages?

- ✅ **Professional**: Shows quality and attention to detail
- ✅ **Versioned**: Track changes and updates (semver)
- ✅ **Portable**: Works across platforms (not locked-in)
- ✅ **Knowledge**: Include reference data for better agents
- ✅ **Examples**: Show buyers how your agent works
- ✅ **Documentation**: Help users get the most value

### Creating a Package

```bash
# 1. Create directory structure
mkdir my-agent
cd my-agent

# 2. Create required files
cat > agent.yaml << EOF
version: "1.0"
metadata:
  name: "My Agent"
  version: "1.0.0"
  author: "username"
  description: "What it does"
  category: "productivity"
  price: 9.99
  currency: "USD"
EOF

cat > system_prompt.txt << EOF
You are a helpful AI agent that...
EOF

# 3. Package it
python3 -m zipfile -c my-agent.sagent .

# 4. Upload via web interface
```

### Documentation

- **Full Specification**: See `AGENT_PACKAGE_SPEC.md`
- **Upload Guide**: See `PACKAGE_UPLOAD_GUIDE.md`
- **Example Package**: See `examples/sample-packages/holiday-planner.sagent`
- **Summary**: See `AGENT_PACKAGING_SUMMARY.md`

### Upload Methods

1. **Simple Form**: `/agents/create` - Quick method for basic agents
2. **Package Upload**: `/agents/upload-package` - Professional method with full features

## Future Enhancements

### Phase 2:
- CLI tool: `sagent create`, `sagent validate`, `sagent publish`
- Package versioning (update existing agents)
- AI-powered ethical review automation

### Phase 3:
- Payment integration (Stripe)
- Agent analytics and usage metrics
- Advanced search and filtering
- Agent preview mode
- Admin dashboard for ethical review

### Phase 4:
- MCP (Model Context Protocol) tool support
- PostgreSQL for production
- Cythonize performance-critical code
- Docker deployment
- Agent marketplace API

## License

MIT License

## Credits

Built with Anthropic Claude API for ethical AI assistance.
