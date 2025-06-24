from unittest.mock import patch, Mock
from io import BytesIO


class TestApplicationIntegration:
    """Integration tests for the complete application."""
    
    @patch('app.linkrot.linkrot')
    @patch('app.validateCaptcha')
    @patch('tasks.linkrot.linkrot')
    @patch('tasks.get_status_code')
    def test_full_pdf_processing_integration(
            self, mock_status, mock_task_linkrot,
            mock_captcha, mock_app_linkrot,
            client, sample_pdf_file):
        """Test the complete PDF processing pipeline."""
        # Setup mocks
        mock_captcha.return_value = True
        mock_status.return_value = 200
        
        # Mock app linkrot
        mock_app_pdf = Mock()
        mock_app_linkrot.return_value = mock_app_pdf
        
        # Mock task linkrot 
        mock_task_pdf = Mock()
        mock_task_pdf.get_metadata.return_value = {
            'Title': 'Test Research Paper',
            'Author': 'Test Author',
            'CreationDate': "D:20240101120000+00'00'"
        }
        
        # Mock reference with mixed types
        mock_refs = []
        
        # Create mock reference objects
        mock_url_ref = Mock()
        mock_url_ref.reftype = 'url'
        mock_url_ref.ref = 'https://example.com/paper.html'
        mock_refs.append(mock_url_ref)
        
        mock_doi_ref = Mock()
        mock_doi_ref.reftype = 'doi'
        mock_doi_ref.ref = '10.1000/182'
        mock_refs.append(mock_doi_ref)
        
        mock_arxiv_ref = Mock()
        mock_arxiv_ref.reftype = 'arxiv'
        mock_arxiv_ref.ref = '1234.5678'
        mock_refs.append(mock_arxiv_ref)
        
        mock_task_pdf.get_references.return_value = mock_refs
        mock_task_linkrot.return_value = mock_task_pdf
        
        # Step 1: Upload PDF
        with open(sample_pdf_file, 'rb') as f:
            upload_response = client.post('/', data={
                'file': (f, 'research_paper.pdf'),
                'g-recaptcha-response': 'valid_captcha'
            })
        
        assert upload_response.status_code == 200
        
        # Verify session was set correctly
        with client.session_transaction() as sess:
            assert 'file' in sess
            assert 'path' in sess
            assert 'type' in sess
            assert sess['file'] == 'research_paper'
            assert sess['type'] == 'file'
        
        # Step 2: Check URL status
        check_response = client.get('/check?url=example.com')
        assert check_response.status_code == 200
        assert check_response.data == b'200'
        
        # Step 3: Simulate task completion and check result
        with patch('app.AsyncResult') as mock_result:
            mock_result_instance = Mock()
            mock_result_instance.ready.return_value = True
            mock_result_instance.successful.return_value = True
            mock_result_instance.result = {
                'metadata': {
                    'Title': 'Test Research Paper',
                    'Author': 'Test Author',
                    'CreationDate': '2024-01-01 12:00 UTC+00:00'
                },
                'result_data': [
                    {
                        'urls': ['https://example.com/paper.html'],
                        'doi': ['https://doi.org/10.1000/182'],
                        'arxiv': ['https://arxiv.org/abs/1234.5678'],
                        'pdfs': [],
                        'check': ['200', '200', '200']
                    }
                ]
            }
            mock_result.return_value = mock_result_instance
            
            result_response = client.get('/result/task_123')
            assert result_response.status_code == 200
            
            result_data = result_response.get_json()
            assert result_data['ready'] is True
            assert result_data['successful'] is True
            assert 'metadata' in result_data['value']
            assert 'result_data' in result_data['value']
    
    def test_error_scenarios_integration(self, client):
        """Test various error scenarios in the application."""
        # Test 1: Invalid file upload
        invalid_response = client.post('/', data={
            'file': (BytesIO(b'not a pdf'), 'document.txt'),
            'g-recaptcha-response': 'valid'
        })
        assert invalid_response.status_code == 200
        
        # Test 2: Missing file
        missing_response = client.post('/', data={
            'g-recaptcha-response': 'valid'
        })
        assert missing_response.status_code == 200
        
        # Test 3: 404 page
        not_found_response = client.get('/nonexistent')
        assert not_found_response.status_code == 404
        
        # Test 4: Task result for non-existent task
        with patch('app.AsyncResult') as mock_result:
            mock_result_instance = Mock()
            mock_result_instance.ready.return_value = False
            mock_result_instance.successful.return_value = False
            mock_result_instance.result = None
            mock_result.return_value = mock_result_instance
            
            pending_response = client.get('/result/nonexistent_task')
            assert pending_response.status_code == 200
            
            result_data = pending_response.get_json()
            assert result_data['ready'] is False
    
    @patch('app.validateCaptcha')
    def test_captcha_integration(self, mock_captcha, client, sample_pdf_file):
        """Test captcha validation integration."""
        # Test successful captcha
        mock_captcha.return_value = True
        
        with open(sample_pdf_file, 'rb') as f:
            success_response = client.post('/', data={
                'file': (f, 'test.pdf'),
                'g-recaptcha-response': 'valid_captcha'
            })
        
        assert success_response.status_code == 200
        mock_captcha.assert_called_with('valid_captcha')
        
        # Test failed captcha
        mock_captcha.return_value = False
        
        with open(sample_pdf_file, 'rb') as f:
            fail_response = client.post('/', data={
                'file': (f, 'test.pdf'),
                'g-recaptcha-response': 'invalid_captcha'
            })
        
        assert fail_response.status_code == 200
    
    def test_static_pages_integration(self, client):
        """Test all static pages are accessible."""
        static_pages = [
            ('/', 'GET'),
            ('/about', 'GET'),
            ('/projects', 'GET'),
            ('/best-practices', 'GET'),
            ('/research', 'GET'),
            ('/policies', 'GET'),
            ('/contribute', 'GET')
        ]
        
        for url, method in static_pages:
            if method == 'GET':
                response = client.get(url)
            else:
                response = client.post(url)
            
            assert response.status_code == 200, f"Failed for {url}"
    
    @patch('app.linkrot.linkrot')
    @patch('app.shutil.make_archive')
    @patch('app.os.mkdir')
    @patch('app.os.remove')
    @patch('app.shutil.rmtree')
    @patch('app.send_from_directory')
    def test_download_integration(self, mock_send, mock_rmtree, mock_remove,
                                  mock_mkdir, mock_archive, mock_linkrot,
                                  client):
        """Test download functionality integration."""
        mock_linkrot_instance = Mock()
        mock_linkrot.return_value = mock_linkrot_instance
        mock_send.return_value = 'download_response'
        
        # Set up session as if file was uploaded
        with client.session_transaction() as sess:
            sess['file'] = 'test_document'
            sess['path'] = '/tmp/test_document.pdf'
            sess['type'] = 'file'
        
        # Trigger download
        client.get('/downloadpdf')
        
        # Verify all file operations were called
        mock_linkrot.assert_called_once_with('/tmp/test_document.pdf')
        mock_linkrot_instance.download_pdfs.assert_called_once()
        mock_mkdir.assert_called_once()
        mock_archive.assert_called_once()
        mock_send.assert_called_once()
        mock_remove.assert_called_once()
        mock_rmtree.assert_called_once()
    
    @patch('app.sanitize_url')
    @patch('app.get_status_code')
    def test_url_checking_integration(self, mock_status, mock_sanitize,
                                      client):
        """Test URL checking integration with various scenarios."""
        test_cases = [
            ('example.com', 'https://example.com', 200),
            ('broken-site.com', 'https://broken-site.com', 404),
            # Timeout/error case
            ('timeout-site.com', 'https://timeout-site.com', 0)
        ]
        
        for input_url, sanitized_url, expected_status in test_cases:
            mock_sanitize.return_value = sanitized_url
            mock_status.return_value = expected_status
            
            response = client.get(f'/check?url={input_url}')
            assert response.status_code == 200
            assert response.data == str(expected_status).encode()
            
            mock_sanitize.assert_called_with(input_url)
            mock_status.assert_called_with(sanitized_url)
