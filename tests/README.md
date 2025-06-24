# Test Suite Documentation

This directory contains comprehensive tests for the Rotting Research application.

## Test Structure

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test-requirements.txt       # Test dependencies
├── unit/                       # Unit tests
│   ├── test_app.py            # Tests for main Flask application
│   ├── test_tasks.py          # Tests for Celery tasks
│   ├── test_utilites.py       # Tests for utility functions
│   └── test_celery_init.py    # Tests for Celery initialization
└── functional/                 # Integration and functional tests
    ├── test_workflows.py       # End-to-end workflow tests
    └── test_integration.py     # Integration tests
```

## Running Tests

### Quick Start
```bash
# Make the test runner executable
chmod +x run_tests.sh

# Run all tests
./run_tests.sh
```

### Manual Testing
```bash
# Install test dependencies
pip install -r tests/test-requirements.txt

# Set environment variables
export FLASK_ENV=testing
export ENV=TEST
export REDIS_URL=redis://localhost:6379/0
export APP_SECRET_KEY=test-secret-key
export CAPTCHA_KEY_ID=test-key
export CAPTCHA_SECRET_KEY=test-secret

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/functional/              # Functional tests only
pytest tests/ -v                      # All tests with verbose output

# Run with coverage
pytest tests/ --cov=app --cov=tasks --cov=utilites --cov=celery_init --cov-report=html
```

## Test Categories

### Unit Tests
- **test_app.py**: Tests for Flask route handlers, helper functions, and validation logic
- **test_tasks.py**: Tests for Celery tasks including PDF processing and reference sorting
- **test_utilites.py**: Tests for utility functions like temporary folder management
- **test_celery_init.py**: Tests for Celery application initialization

### Functional Tests
- **test_workflows.py**: End-to-end workflow testing including file upload, processing, and download
- **test_integration.py**: Integration tests that verify components work together correctly

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ **Route Handlers**: All Flask routes (`/`, `/about`, `/check`, etc.)
- ✅ **File Upload**: PDF validation, captcha verification, error handling
- ✅ **PDF Processing**: Metadata extraction, reference parsing, link checking
- ✅ **Task Management**: Celery task execution and result handling
- ✅ **Download Functionality**: PDF compilation and file serving
- ✅ **Error Handling**: 404 pages, invalid inputs, network errors
- ✅ **Session Management**: User session persistence across requests
- ✅ **URL Validation**: Link checking and status code reporting

## Test Fixtures

Key fixtures available in `conftest.py`:

- `client`: Flask test client for making HTTP requests
- `app_context`: Application context for testing
- `test_upload_folder`: Temporary folder for file operations
- `sample_pdf_file`: Valid PDF file for upload testing
- `mock_linkrot`: Mocked linkrot library for PDF processing
- `mock_requests`: Mocked HTTP requests for external API calls

## Dependencies

Test-specific dependencies are listed in `test-requirements.txt`:

- **pytest**: Testing framework
- **pytest-flask**: Flask integration for pytest
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Enhanced mocking capabilities

## Continuous Integration

Tests are automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

See `.github/workflows/test.yml` for CI configuration.

## Coverage Reports

After running tests with coverage, view the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Writing New Tests

When adding new functionality:

1. **Unit Tests**: Add tests in `tests/unit/` for individual functions/methods
2. **Integration Tests**: Add tests in `tests/functional/` for feature workflows  
3. **Fixtures**: Add reusable test data/mocks to `conftest.py`
4. **Documentation**: Update this README with new test categories

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestUploadWorkflow`)
- Test methods: `test_*` (e.g., `test_valid_pdf_upload`)

### Example Test

```python
def test_new_feature(client, mock_dependency):
    """Test description of what this test verifies."""
    # Arrange
    mock_dependency.return_value = 'expected_result'
    
    # Act
    response = client.get('/new-endpoint')
    
    # Assert
    assert response.status_code == 200
    mock_dependency.assert_called_once()
```
