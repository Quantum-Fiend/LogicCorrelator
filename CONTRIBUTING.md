# Contributing to LogicCorrelator

Thank you for your interest in contributing to LogicCorrelator! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

### 1. Correlation Rules
- Add new detection rules for emerging threats
- Improve existing rule accuracy
- Reduce false positives
- Add MITRE ATT&CK mappings

### 2. Event Collectors
- Support for additional log sources
- Improved event normalization
- Performance optimizations
- Cross-platform compatibility

### 3. Dashboard Enhancements
- New visualization features
- UI/UX improvements
- Additional metrics
- Mobile responsiveness

### 4. Documentation
- Tutorial improvements
- Code examples
- Architecture documentation
- Translation to other languages

### 5. Bug Fixes
- Report bugs via GitHub Issues
- Submit fixes with tests
- Improve error handling

## 🚀 Getting Started

### 1. Fork the Repository

```bash
git clone https://github.com/yourusername/LogicCorrelator.git
cd LogicCorrelator
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Follow the coding standards below
- Add tests for new features
- Update documentation

### 4. Test Your Changes

```bash
make test
```

### 5. Submit a Pull Request

- Provide a clear description
- Reference related issues
- Include screenshots for UI changes

## 📝 Coding Standards

### Python
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Maximum line length: 100 characters

```python
def process_event(event: Dict[str, Any]) -> bool:
    """
    Process and validate an event.
    
    Args:
        event: Event dictionary to process
        
    Returns:
        True if processing succeeded, False otherwise
    """
    pass
```

### JavaScript
- Use ES6+ features
- Consistent indentation (2 spaces)
- Add JSDoc comments
- Use meaningful variable names

```javascript
/**
 * Handle new event from WebSocket
 * @param {Object} event - Event data
 */
function handleNewEvent(event) {
    // Implementation
}
```

### Lua
- Follow Lua style guide
- Add comments for complex logic
- Use local variables when possible

```lua
-- Process correlation rule
local function evaluate_rule(rule, events)
    -- Implementation
end
```

### YAML (Rules)
- Consistent indentation (2 spaces)
- Add descriptive comments
- Include MITRE ATT&CK techniques

```yaml
# Detect credential stuffing attacks
- name: "Credential Stuffing"
  description: "Multiple failed logins followed by success"
  mitre_techniques:
    - T1110.004
```

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Aim for >80% code coverage

### Integration Tests
- Test component interactions
- Use realistic test data
- Verify end-to-end workflows

### Rule Testing
- Provide sample events
- Document expected behavior
- Test edge cases

## 📋 Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] No merge conflicts
- [ ] Descriptive commit messages
- [ ] PR description is clear

## 🐛 Bug Reports

When reporting bugs, include:

1. **Description** - Clear description of the issue
2. **Steps to Reproduce** - Detailed steps
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment** - OS, versions, configuration
6. **Logs** - Relevant log output
7. **Screenshots** - If applicable

## 💡 Feature Requests

When requesting features:

1. **Use Case** - Why is this needed?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other approaches considered
4. **Additional Context** - Any other information

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Questions?

- Open a GitHub Discussion
- Join our community chat
- Email: logiccorrelator@example.com

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

### Enforcement

Violations may result in temporary or permanent ban from the project.

## 🙏 Thank You!

Your contributions make LogicCorrelator better for everyone. We appreciate your time and effort!

---

**Happy Contributing! 🚀**
