from unittest.mock import patch, Mock
from io import BytesIO
from app import app, allowed_file, validateCaptcha, pdfdata


class TestAllowedFile:
    """Test the allowed_file function."""
    
    def test_allowed_file_valid_pdf(self):
        """Test that PDF files are allowed."""
        assert allowed_file('test.pdf') is True
        assert allowed_file('document.PDF') is True
    
    def test_allowed_file_invalid_extension(self):
        """Test that non-PDF files are not allowed."""
        assert allowed_file('test.txt') is False
        assert allowed_file('document.doc') is False
        assert allowed_file('image.jpg') is False
    
    def test_allowed_file_no_extension(self):
        """Test that files without extensions are not allowed."""
        assert allowed_file('test') is False
    
    def test_allowed_file_empty_string(self):
        """Test that empty filename is not allowed."""
        assert allowed_file('') is False


class TestRoutes:
    """Test Flask route handlers."""
    
    def test_upload_form_get(self, client):
        """Test GET request to upload form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'upload.html' in response.data or b'captcha' in response.data
    
    def test_about_page(self, client):
        """Test about page."""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_projects_page(self, client):
        """Test projects page."""
        response = client.get('/projects')
        assert response.status_code == 200
    
    def test_practices_page(self, client):
        """Test best practices page."""
        response = client.get('/best-practices')
        assert response.status_code == 200
    
    def test_research_page(self, client):
        """Test research page."""
        response = client.get('/research')
        assert response.status_code == 200
    
    def test_policies_page(self, client):
        """Test policies page."""
        response = client.get('/policies')
        assert response.status_code == 200
    
    def test_contribute_page(self, client):
        """Test contribute page."""
        response = client.get('/contribute')
        assert response.status_code == 200
    
    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404


class TestUploadPDF:
    """Test PDF upload functionality."""
    
    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/', data={})
        assert response.status_code == 200
        # Should return to upload form
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename."""
        data = {'file': (BytesIO(b''), '')}
        response = client.post('/', data=data)
        assert response.status_code == 200
    
    def test_upload_invalid_file_extension(self, client):
        """Test upload with invalid file extension."""
        data = {
            'file': (BytesIO(b'test content'), 'test.txt'),
            'g-recaptcha-response': 'test'
        }
        response = client.post('/', data=data)
        assert response.status_code == 200
        # Should return error for invalid file type
    
    @patch('app.validateCaptcha')
    @patch('app.pdfdata')
    def test_upload_valid_pdf(self, mock_pdfdata, mock_captcha, client, sample_pdf_file):
        """Test successful PDF upload."""
        mock_captcha.return_value = True
        mock_pdfdata.return_value = ({}, [], [], [], [], 'task_id_123')
        
        with open(sample_pdf_file, 'rb') as f:
            data = {
                'file': (f, 'test.pdf'),
                'g-recaptcha-response': 'test'
            }
            response = client.post('/', data=data)
        
        assert response.status_code == 200
        mock_captcha.assert_called_once()
        mock_pdfdata.assert_called_once()
    
    @patch('app.validateCaptcha')
    def test_upload_invalid_captcha(self, mock_captcha, client, sample_pdf_file):
        """Test upload with invalid captcha."""
        mock_captcha.return_value = False
        
        with open(sample_pdf_file, 'rb') as f:
            data = {
                'file': (f, 'test.pdf'),
                'g-recaptcha-response': 'invalid'
            }
            response = client.post('/', data=data)
        
        assert response.status_code == 200
        mock_captcha.assert_called_once()


class TestValidateCaptcha:
    """Test captcha validation."""
    
    @patch('app.app.config')
    def test_validate_captcha_dev_env(self, mock_config):
        """Test captcha validation in dev environment."""
        mock_config.get.return_value = 'DEV'
        app.config['ENV'] = 'DEV'
        result = validateCaptcha('any_response')
        assert result is True
    
    @patch('requests.post')
    def test_validate_captcha_prod_env_success(self, mock_post):
        """Test successful captcha validation in prod environment."""
        app.config['ENV'] = 'PROD'
        app.config['CAPTCHA_SECRET_KEY'] = 'test_secret'
        mock_post.return_value.json.return_value = {'success': True}
        
        result = validateCaptcha('valid_response')
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_validate_captcha_prod_env_failure(self, mock_post):
        """Test failed captcha validation in prod environment."""
        app.config['ENV'] = 'PROD'
        app.config['CAPTCHA_SECRET_KEY'] = 'test_secret'
        mock_post.return_value.json.return_value = {'success': False}
        
        result = validateCaptcha('invalid_response')
        assert result is False


class TestPDFData:
    """Test PDF data processing."""
    
    @patch('app.pdfdata_task.delay')
    def test_pdfdata(self, mock_task, client):
        """Test pdfdata function."""
        mock_task.return_value = 'task_id_123'
        
        with client.session_transaction() as sess:
            metadata, pdfs, urls, arxiv, doi, task_id = pdfdata(
                '/test/path.pdf')
            
            assert metadata == {}
            assert pdfs == []
            assert urls == []
            assert arxiv == []
            assert doi == []
            assert task_id == 'task_id_123'
            assert sess['path'] == '/test/path.pdf'


class TestCheckRoute:
    """Test URL checking functionality."""
    
    @patch('app.sanitize_url')
    @patch('app.get_status_code')
    def test_check_url(self, mock_status, mock_sanitize, client):
        """Test URL status checking."""
        mock_sanitize.return_value = 'https://example.com'
        mock_status.return_value = 200
        
        response = client.get('/check?url=example.com')
        assert response.status_code == 200
        assert response.data == b'200'
        
        mock_sanitize.assert_called_once_with('example.com')
        mock_status.assert_called_once_with('https://example.com')


class TestTaskResult:
    """Test task result endpoint."""
    
    @patch('app.AsyncResult')
    def test_task_result_ready(self, mock_result, client):
        """Test task result when ready."""
        mock_result_instance = Mock()
        mock_result_instance.ready.return_value = True
        mock_result_instance.successful.return_value = True
        mock_result_instance.result = {'test': 'data'}
        mock_result.return_value = mock_result_instance
        
        response = client.get('/result/task_id_123')
        assert response.status_code == 200
        
        result_data = response.get_json()
        assert result_data['ready'] is True
        assert result_data['successful'] is True
        assert result_data['value'] == {'test': 'data'}
    
    @patch('app.AsyncResult')
    def test_task_result_not_ready(self, mock_result, client):
        """Test task result when not ready."""
        mock_result_instance = Mock()
        mock_result_instance.ready.return_value = False
        mock_result_instance.successful.return_value = False
        mock_result_instance.result = None
        mock_result.return_value = mock_result_instance
        
        response = client.get('/result/task_id_123')
        assert response.status_code == 200
        
        result_data = response.get_json()
        assert result_data['ready'] is False
        assert result_data['successful'] is False
        assert result_data['value'] is None


class TestDownloadPDF:
    """Test PDF download functionality."""
    
    @patch('app.linkrot.linkrot')
    @patch('app.shutil.make_archive')
    @patch('app.os.mkdir')
    @patch('app.os.remove')
    @patch('app.shutil.rmtree')
    @patch('app.send_from_directory')
    def test_download_pdf(self, mock_send, mock_rmtree, mock_remove,
                          mock_mkdir, mock_archive, mock_linkrot, client):
        """Test PDF download functionality."""
        mock_linkrot_instance = Mock()
        mock_linkrot.return_value = mock_linkrot_instance
        mock_send.return_value = 'file_response'
        
        with client.session_transaction() as sess:
            sess['file'] = 'test'
            sess['path'] = '/test/path.pdf'
            sess['type'] = 'file'
        
        client.get('/downloadpdf')
        
        mock_linkrot.assert_called_once()
        mock_linkrot_instance.download_pdfs.assert_called_once()
        mock_archive.assert_called_once()
        mock_mkdir.assert_called_once()
        mock_remove.assert_called_once()
        mock_rmtree.assert_called_once()
