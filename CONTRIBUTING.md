# Contributing to Cortex

Thank you for your interest in contributing to Cortex! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a welcoming environment

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing issues and discussions
2. Create a feature request with:
   - Clear use case
   - Expected behavior
   - Potential implementation approach
   - Impact on existing features

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cortex.git
   cd cortex
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Make your changes**
   - Follow the code style
   - Add tests for new features
   - Update documentation
   - Keep commits focused and atomic

5. **Run tests**
   ```bash
   python -m unittest discover tests -v
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints
- Write descriptive docstrings
- Keep functions focused and small
- Use meaningful variable names

Example:
```python
def learn_fact(self, topic: str, fact: str, confidence: float = 0.5) -> int:
    """Learn a new fact.
    
    Args:
        topic: Topic of the fact
        fact: The fact itself
        confidence: Confidence in this fact (0.0 to 1.0)
        
    Returns:
        memory_id: ID of the stored fact
    """
    # Implementation
```

### Testing

- Write tests for all new features
- Maintain test coverage
- Test edge cases
- Use descriptive test names

Example:
```python
class TestBrain(unittest.TestCase):
    def test_learn_fact_with_high_confidence(self):
        """Test learning a fact with high confidence score."""
        fact_id = self.brain.learn_fact(
            topic="python",
            fact="Python is dynamically typed",
            confidence=0.9
        )
        self.assertIsNotNone(fact_id)
```

### Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for design changes
- Add docstrings to all public methods
- Include usage examples
- Keep documentation up-to-date

### Commit Messages

Use conventional commits format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
```
feat: add internet learning capability
fix: correct confidence calculation in skills
docs: update usage guide with examples
test: add integration tests for learning engine
```

## Project Structure

```
cortex/
├── core/              # Brain and central coordination
│   └── brain.py
├── memory/            # Database and memory management
│   ├── schema.py
│   ├── database.py
│   └── consolidation.py
├── learning/          # Learning engine and patterns
│   ├── engine.py
│   └── internet.py
├── sandbox/           # Safe execution environment
│   └── runner.py
├── cli/               # Command-line interface
│   └── main.py
└── utils/             # Utilities and configuration
    └── config.py

tests/
├── test_brain.py           # Brain unit tests
└── test_integration.py     # Integration tests
```

## Areas for Contribution

### High Priority

1. **Internet Learning Enhancement**
   - Real search API integration
   - Better content extraction
   - Source quality assessment

2. **Document Parsing**
   - PDF parsing improvements
   - Markdown enhancement
   - Code repository analysis

3. **Performance Optimization**
   - Query optimization
   - Caching improvements
   - Memory usage reduction

4. **Testing**
   - Increase test coverage
   - Add performance tests
   - Add stress tests

### Medium Priority

1. **CLI Enhancements**
   - Interactive mode
   - Better output formatting
   - Progress indicators

2. **Learning Improvements**
   - Better pattern detection
   - Workflow suggestions
   - Auto-skill creation

3. **Documentation**
   - Video tutorials
   - More examples
   - API reference

### Low Priority

1. **UI/Web Interface**
   - Web dashboard
   - Visualizations
   - Real-time monitoring

2. **Integrations**
   - IDE plugins
   - CI/CD integration
   - Slack/Discord bots

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review
6. Address feedback
7. Squash commits if needed

## Questions?

- Open a discussion on GitHub
- Check existing documentation
- Ask in pull request comments

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
