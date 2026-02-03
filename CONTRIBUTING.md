# Contributing to Thirsty's Value Finder

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/IAmSoThirsty/IAmSoThirsty-marketplace-analyzer/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/IAmSoThirsty/IAmSoThirsty-marketplace-analyzer/issues)
2. Create a new issue describing:
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/IAmSoThirsty-marketplace-analyzer.git
cd IAmSoThirsty-marketplace-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start services with Docker
docker-compose up -d
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Maximum line length: 100 characters

Example:
```python
async def analyze_image(image_id: int) -> Dict[str, Any]:
    """
    Analyze an image using ML models.
    
    Args:
        image_id: The ID of the image to analyze
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If image_id is invalid
    """
    pass
```

### JavaScript/React

- Use ES6+ features
- Use functional components with hooks
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable names

Example:
```javascript
const ImageUpload = ({ onImageSelected }) => {
  const [preview, setPreview] = useState(null);
  
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      onImageSelected(file);
    }
  };
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

Example:
```python
@pytest.mark.asyncio
async def test_upload_image_success(db_session):
    """Test successful image upload."""
    # Arrange
    user = create_test_user()
    image_data = create_test_image()
    
    # Act
    result = await upload_image(user.id, image_data)
    
    # Assert
    assert result.id is not None
    assert result.filename == "test.jpg"
```

## Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── tasks/           # Celery tasks
├── frontend/            # React frontend
│   └── src/
│       ├── components/  # Reusable components
│       ├── pages/       # Page components
│       ├── services/    # API client
│       └── hooks/       # Custom hooks
├── tests/               # Test files
├── alembic/             # Database migrations
└── docker-compose.yml   # Docker services
```

## Database Migrations

When modifying database models:

```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Adding New Dependencies

### Python

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Update installed packages
pip install -r requirements.txt
```

### JavaScript

```bash
cd frontend
npm install new-package
```

## Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add inline comments for complex logic
- Update docstrings when modifying functions

## Commit Messages

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(api): add marketplace search filtering
fix(frontend): resolve image upload on mobile
docs(readme): update installation instructions
```

## Review Process

1. All PRs require review before merging
2. Address review comments
3. Keep PRs focused and reasonably sized
4. Ensure CI passes
5. Squash commits when merging

## Getting Help

- Open an issue for questions
- Join discussions
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
