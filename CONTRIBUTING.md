# Contributing to AI SDLC Integration Agent

Thank you for your interest in contributing to the AI SDLC Integration Agent! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-sdlc-integration-agent.git
   cd ai-sdlc-integration-agent
   ```
3. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python reset_db.py
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📝 Contribution Guidelines

### Code Style
- **Python**: Follow PEP 8 standards
- **TypeScript/React**: Use ESLint and Prettier configurations
- **Commit Messages**: Use conventional commits format
  ```
  feat: add new AI agent for deployment automation
  fix: resolve authentication token expiration issue
  docs: update API documentation
  ```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**:
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend tests
   cd frontend && npm test
   ```
4. **Update the README.md** if adding new features
5. **Submit a pull request** with:
   - Clear description of changes
   - Screenshots for UI changes
   - Test results

### AI Agent Development

When contributing new AI agents:

1. **Follow the existing agent structure**:
   ```
   backend/app/agents/your_agent/
   ├── __init__.py
   ├── your_agent.py
   └── services/
       └── your_service.py
   ```

2. **Implement required methods**:
   - `process()` - Main agent logic
   - `generate_report()` - PDF report generation
   - Error handling and logging

3. **Add agent configuration** to constants and API endpoints

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment details** (OS, Python version, Node.js version)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error logs** and stack traces
- **Screenshots** if applicable

## 💡 Feature Requests

For new features:

- **Check existing issues** to avoid duplicates
- **Provide detailed description** of the feature
- **Explain the use case** and benefits
- **Consider implementation complexity**

## 🔒 Security Issues

For security vulnerabilities:

- **Do not create public issues**
- **Email directly** to the maintainers
- **Provide detailed reproduction steps**
- **Allow time for fix before disclosure**

## 📋 Code Review Process

All contributions go through code review:

1. **Automated checks** must pass (CI/CD)
2. **Manual review** by maintainers
3. **Address feedback** promptly
4. **Squash commits** before merge

## 🏆 Recognition

Contributors will be:

- **Listed in README.md** contributors section
- **Mentioned in release notes** for significant contributions
- **Invited as collaborators** for consistent contributions

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **Discussions** - For questions and general discussion
- **Documentation** - Check `/docs` folder and README.md

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **New AI Agents** (DevOps, Monitoring, Documentation)
- **Frontend UI/UX** improvements
- **Testing** and test coverage
- **Documentation** and tutorials
- **Performance** optimizations
- **Security** enhancements

Thank you for contributing to the future of AI-powered software development! 🚀