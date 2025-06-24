import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Set test configuration
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['ENV'] = 'TEST'
    app.config['CAPTCHA_DISPLAY'] = 'none'
    app.config['CAPTCHA_KEY_ID'] = 'test-key'
    app.config['CAPTCHA_SECRET_KEY'] = 'test-secret'
    
    # Mock environment variables
    with patch.dict(os.environ, {
        'REDIS_URL': 'redis://localhost:6379/0',
        'APP_SECRET_KEY': 'test-secret-key',
        'CAPTCHA_KEY_ID': 'test-key',
        'CAPTCHA_SECRET_KEY': 'test-secret',
        'ENV': 'TEST'
    }):
        with app.test_client() as client:
            with app.app_context():
                yield client
    
    # Cleanup
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])


@pytest.fixture
def app_context():
    """Create application context for testing."""
    with app.app_context():
        yield app


@pytest.fixture
def test_upload_folder():
    """Create a temporary upload folder for testing."""
    folder = tempfile.mkdtemp()
    yield folder
    if os.path.exists(folder):
        shutil.rmtree(folder)


@pytest.fixture
def mock_celery():
    """Mock Celery for testing."""
    with patch('app.celery_app') as mock:
        yield mock


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    folder = tempfile.mkdtemp()
    pdf_path = os.path.join(folder, 'test.pdf')
    
    # Create a minimal PDF content
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
174
%%EOF"""
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_content)
    
    yield pdf_path
    
    if os.path.exists(folder):
        shutil.rmtree(folder)


@pytest.fixture
def mock_linkrot():
    """Mock linkrot library for testing."""
    mock_linkrot_instance = Mock()
    mock_linkrot_instance.get_metadata.return_value = {
        'Title': 'Test PDF',
        'Author': 'Test Author',
        'CreationDate': "D:20240101120000+00'00'"
    }
    mock_linkrot_instance.get_references.return_value = []
    
    with patch('linkrot.linkrot', return_value=mock_linkrot_instance) as mock:
        yield mock, mock_linkrot_instance


@pytest.fixture
def mock_requests():
    """Mock requests for testing."""
    with patch('requests.post') as mock:
        mock.return_value.json.return_value = {'success': True}
        yield mock