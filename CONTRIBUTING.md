# Contributing to Special Agents

Thank you for your interest in contributing to Special Agents! This project aims to create an ethical AI agents marketplace that brings positive change to humanity.

## 🌟 How to Contribute

### 1. Code Contributions

We welcome contributions in these areas:

- **Backend Development** (Python/Flask/gevent)
- **Frontend Development** (HTML/CSS/JavaScript)
- **AI Integration** (Anthropic Claude API)
- **Package System** (.sagent format improvements)
- **Security** (Ethical review, input validation)
- **Testing** (Unit tests, integration tests)
- **Documentation** (Guides, tutorials, examples)

### 2. Getting Started

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone git@github.com:YOUR_USERNAME/special-agents.git
cd special-agents

# 3. Set up the development environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Add your ANTHROPIC_API_KEY

# 5. Run the application
python run.py
```

### 3. Making Changes

```bash
# 1. Create a new branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# - Follow PEP 8 for Python code
# - Write clear commit messages
# - Add comments where needed

# 3. Test your changes
# - Manual testing
# - Add unit tests if applicable

# 4. Commit your changes
git add .
git commit -m "Add: brief description of your changes"

# 5. Push to your fork
git push origin feature/your-feature-name

# 6. Create a Pull Request on GitHub
```

### 4. Pull Request Guidelines

- **Clear Description**: Explain what your PR does and why
- **One Feature Per PR**: Keep PRs focused on a single feature/fix
- **Test Your Code**: Ensure it works before submitting
- **Follow Code Style**: Consistent with existing codebase
- **Update Documentation**: If you change functionality

## 🎯 Priority Areas

We're especially looking for help with:

1. **AI-Powered Ethical Review**
   - Automated agent validation
   - Harmful content detection
   - Bias detection

2. **Payment Integration**
   - Stripe integration
   - Transaction handling
   - Seller payouts

3. **Testing**
   - Unit tests for routes
   - Integration tests
   - End-to-end tests

4. **Security**
   - Input validation
   - CSRF protection
   - Rate limiting
   - SQL injection prevention

5. **Performance**
   - Database optimization
   - Caching layer
   - Load testing

6. **Agent Package System**
   - CLI tool for package creation
   - Package versioning
   - MCP (Model Context Protocol) support

## 📋 Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Document functions with docstrings
- Maximum line length: 100 characters

```python
def example_function(param1: str, param2: int) -> dict:
    """
    Brief description of what this function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    # Implementation
    return {}
```

### HTML/CSS/JavaScript
- Use semantic HTML
- BEM naming for CSS classes
- ES6+ JavaScript
- Clear, descriptive variable names

## 🐛 Reporting Bugs

Found a bug? Please create an issue with:

- **Clear Title**: Brief description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, browser
- **Screenshots**: If applicable

## 💡 Feature Requests

Have an idea? Create an issue with:

- **Clear Title**: Brief description of the feature
- **Problem**: What problem does this solve?
- **Proposed Solution**: How would it work?
- **Alternatives**: Other approaches you considered
- **Additional Context**: Mockups, examples, etc.

## 🔒 Security

Found a security vulnerability? Please **DO NOT** create a public issue.

Instead, email: security@special-agents.ai (placeholder - update when ready)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

✅ **Do:**
- Be respectful and inclusive
- Welcome newcomers
- Give and accept constructive feedback
- Focus on what's best for the community
- Show empathy towards others

❌ **Don't:**
- Use offensive or unwelcoming language
- Engage in personal attacks
- Harass others publicly or privately
- Publish others' private information
- Act unprofessionally

## 📜 Ethical Guidelines

All contributions must align with our ethical principles:

1. **Safety First**: No harmful or dangerous agents
2. **Privacy**: Respect user privacy and data protection
3. **Fairness**: Avoid bias and discrimination
4. **Transparency**: Be honest about capabilities and limitations
5. **Positive Impact**: Focus on benefiting humanity

## 🎓 Learning Resources

New to the technologies we use?

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Anthropic Claude**: https://docs.anthropic.com/
- **gevent**: http://www.gevent.org/
- **Python**: https://docs.python.org/3/

## 📞 Getting Help

- **Documentation**: Check README.md and other docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join our Discord (coming soon!)

## 🏆 Recognition

Contributors will be:
- Listed in our Contributors section
- Mentioned in release notes
- Recognized in our community highlights

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make Special Agents better! 🚀

Every contribution, no matter how small, makes a difference. Whether it's fixing a typo, adding a feature, or reporting a bug - we appreciate your effort!

Happy coding! 🤖
