# 🚀 AI-Powered SDLC Automation Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0.0-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?style=flat&logo=python)](https://python.org)

A production-ready web application that integrates **7 specialized AI agents** to automate the entire Software Development Life Cycle (SDLC) using a PRD document as input.

## 🎯 Overview

Transform a Product Requirements Document (PRD) into a complete, production-ready software project through automated AI agents:

- **🎨 UI/UX Design** - Figma integration and design system generation
- **🏗️ System Architecture** - Scalable cloud-native infrastructure design  
- **📊 Impact Analysis** - Business and technical risk assessment
- **💻 Code Generation** - Clean, production-ready backend code
- **🧪 Testing** - Comprehensive test suites with high coverage
- **🛡️ Security Scanning** - Vulnerability assessment and compliance checks
- **👁️ Code Review** - Expert-level code review and optimization
- **🔗 GitHub Integration** - Automatic repository creation and deployment

## 🚀 Quick Start

### One-Click Startup
```bash
# Clone the repository
git clone https://github.com/santhoshCS2/ai-sdlc-integration-agent.git
cd ai-sdlc-integration-agent

# Run the automated startup script
python start_application.py
```

The startup script will:
- ✅ Check system requirements
- 📦 Install all dependencies  
- 🗄️ Set up the database
- 🚀 Start both backend and frontend servers
- 🌐 Open the application in your browser

## 🏗️ Architecture

### Frontend (React + TypeScript + Vite)
- Modern responsive UI with Tailwind CSS
- Real-time agent status tracking
- File upload and processing
- Authentication and authorization
- Interactive dashboard with progress visualization

### Backend (FastAPI + Python)
- RESTful API with OpenAPI documentation
- SQLAlchemy ORM with PostgreSQL
- 7 specialized AI agent services
- GitHub API integration
- Comprehensive error handling and logging

## 🤖 AI Agents

### 1. 🎨 UI/UX Agent
- **Smart PRD Analysis** - Extracts features, user roles, and business requirements
- **Figma Integration** - Generates detailed design prompts and specifications
- **Component Mapping** - Creates UI component specifications
- **User Journey Analysis** - Maps user workflows and interactions

### 2. 🏗️ Architecture Agent  
- **System Design** - Creates scalable, cloud-native architecture
- **Database Schema** - Generates optimized database designs
- **API Structure** - Designs RESTful API architecture
- **Security Architecture** - Implements security best practices

### 3. 📊 Impact Analysis Agent
- **Business Impact** - ROI analysis and financial projections
- **Technical Assessment** - Technology stack evaluation
- **Risk Analysis** - Comprehensive risk assessment with mitigation strategies
- **Timeline Estimation** - Project timeline and resource planning

### 4. 💻 Coding Agent
- **Production Code** - Clean, maintainable FastAPI backend
- **Architecture Patterns** - Implements clean architecture principles
- **Type Safety** - Comprehensive type hints and validation
- **Documentation** - Auto-generated API documentation

### 5. 🧪 Professional Testing Agent
- **Repository Cloning** - Clones and analyzes GitHub repositories
- **LLM Code Analysis** - Analyzes each file individually for logic and complexity
- **Comprehensive Tests** - Generates unit, integration, and API tests with proper naming
- **Test Infrastructure** - Creates conftest.py, pytest.ini, requirements-test.txt
- **Multi-Language Support** - Python, JavaScript, TypeScript, Java, Go, Rust, PHP, Ruby

### 6. 🛡️ Security Scanning Agent
- **Vulnerability Assessment** - OWASP Top 10 compliance checking
- **STRIDE Threat Modeling** - Comprehensive threat analysis
- **Dependency Scanning** - Security vulnerability detection
- **Compliance Reports** - GDPR, HIPAA, and other compliance checks

### 7. 👁️ Code Review Agent
- **Quality Assessment** - Multi-dimensional code quality scoring
- **Performance Analysis** - Performance optimization recommendations
- **Best Practices** - Industry standard compliance checking
- **Improvement Roadmap** - Prioritized improvement recommendations

## 📋 Features

### 🎯 Core Functionality
- **PRD Upload & Analysis** - Support for PDF, DOCX, and text files
- **Full SDLC Automation** - One-click workflow execution
- **Real-time Progress** - Live agent status and progress tracking
- **GitHub Integration** - Automatic repository creation and code deployment
- **Download Outputs** - PDF and JSON export of all agent results

### 🔐 Security & Authentication
- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- CORS configuration
- Security scanning and vulnerability assessment

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (SQLite for development)
- Git

### Backend Setup

1. **Clone and navigate**
   ```bash
   git clone https://github.com/santhoshCS2/ai-sdlc-integration-agent.git
   cd ai-sdlc-integration-agent/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # - DATABASE_URL
   # - GROQ_API_KEY (for LLM services)
   # - GITHUB_TOKEN (for GitHub integration)
   ```

5. **Initialize database**
   ```bash
   python reset_db.py
   ```

6. **Start the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Agents
- `GET /api/agents/` - List all agents
- `POST /api/agents/chat` - Chat with specific agent
- `POST /api/agents/orchestrate-sdlc` - Run full SDLC workflow
- `GET /api/agents/status` - Get pipeline status
- `GET /api/agents/download/{agent_type}/{file_id}` - Download agent outputs

## 🔄 Workflow Process

1. **Input Processing**
   - User uploads PRD document or enters text description
   - System validates and processes input

2. **Agent Orchestration**
   - UI/UX Agent analyzes requirements and generates design prompts
   - Architecture Agent creates system design and documentation
   - Impact Analysis Agent evaluates risks and requirements
   - Coding Agent generates production-ready code
   - Testing Agent clones repo, analyzes each file with LLM, generates comprehensive tests
   - Security Scanning Agent performs vulnerability assessment
   - Code Review Agent conducts final review and optimization

3. **GitHub Integration**
   - Automatic repository creation
   - Code and documentation deployment
   - Comprehensive README generation
   - Project structure organization

4. **Output Delivery**
   - Real-time progress updates
   - Downloadable reports and documentation
   - GitHub repository with complete project
   - Success metrics and recommendations

## 📁 Project Structure

```
ai-sdlc-integration-agent/
├── backend/
│   ├── app/
│   │   ├── agents/           # 7 AI agent services
│   │   │   ├── uiux/
│   │   │   ├── architecture/
│   │   │   ├── impact_analysis/
│   │   │   ├── coding/
│   │   │   ├── testing/      # Professional Testing Agent
│   │   │   ├── security/
│   │   │   └── code_review/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core configuration
│   │   ├── models/           # Database models
│   │   └── services/         # Business services
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   └── utils/            # Utility functions
│   ├── package.json
│   └── vite.config.ts
├── push_to_github.bat        # Windows Git push script
├── push_to_github.sh         # Linux/Mac Git push script
└── README.md
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Professional Testing Agent Features
- **Repository Analysis** - Clones and analyzes GitHub repositories
- **LLM-Powered Analysis** - Each code file analyzed individually for logic, complexity, and test requirements
- **Multi-Language Support** - Python, JavaScript, TypeScript, Java, Go, Rust, PHP, Ruby
- **Professional Test Generation** - Proper naming conventions (test_*.py, *.test.js, *Test.java)
- **Comprehensive Coverage** - Unit tests, integration tests, edge cases, error handling
- **Test Infrastructure** - Complete setup with conftest.py, pytest.ini, requirements

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Cloud Deployment
- **Google Cloud Run** - cloudbuild.yaml included
- **AWS ECS/Fargate** - Docker containers ready
- **Azure Container Instances** - Multi-container support

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
CORS_ORIGINS=["http://localhost:5173"]
SECRET_KEY=your_secret_key
```

#### Frontend
```env
VITE_API_URL=http://localhost:8000
```

## 📊 Monitoring & Analytics

- Real-time agent execution monitoring
- Success rate tracking
- Performance metrics
- Error logging and alerting
- User activity analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the agent output logs for debugging

## 🔗 Related Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**Built with ❤️ using AI-powered automation**

This platform represents the future of software development - where AI agents handle the entire SDLC process, allowing developers to focus on innovation and business value creation.