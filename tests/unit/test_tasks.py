from unittest.mock import Mock, patch
from tasks import pdfdata_task, sort_ref


class TestPDFDataTask:
    """Test the pdfdata_task Celery task."""
    
    @patch('tasks.linkrot.linkrot')
    @patch('tasks.group')
    def test_pdfdata_task_success(self, mock_group, mock_linkrot):
        """Test successful PDF data processing."""
        # Mock linkrot instance
        mock_pdf = Mock()
        mock_pdf.get_metadata.return_value = {
            'Title': 'Test PDF',
            'Author': 'Test Author',
            'CreationDate': "D:20240101120000+00'00'"
        }
        
        # Mock references
        mock_ref = Mock()
        mock_ref.reftype = 'url'
        mock_ref.ref = 'https://example.com'
        mock_pdf.get_references.return_value = [mock_ref]
        
        mock_linkrot.return_value = mock_pdf
        
        # Mock group execution
        mock_group_result = Mock()
        mock_group_result.ready.return_value = True
        mock_child_result = Mock()
        mock_child_result.result = {
            'pdfs': [],
            'urls': ['https://example.com'],
            'arxiv': [],
            'doi': [],
            'check': ['200']
        }
        mock_group_result.__iter__ = Mock(
            return_value=iter([mock_child_result]))
        mock_group.return_value.return_value = mock_group_result
        
        result = pdfdata_task('/test/path.pdf')
        
        # Verify metadata processing
        assert 'Title' in result['metadata']
        assert 'Author' in result['metadata']
        assert 'CreationDate' in result['metadata']
        
        # Verify date formatting
        expected_date = '2024-01-01 12:00 UTC+00:00'
        assert result['metadata']['CreationDate'] == expected_date
        
        # Verify result data
        assert len(result['result_data']) == 1
        assert result['result_data'][0]['urls'] == ['https://example.com']
    
    @patch('tasks.linkrot.linkrot')
    def test_pdfdata_task_no_references(self, mock_linkrot):
        """Test PDF processing with no references."""
        mock_pdf = Mock()
        mock_pdf.get_metadata.return_value = {'Title': 'Test PDF'}
        mock_pdf.get_references.return_value = []
        mock_linkrot.return_value = mock_pdf
        
        result = pdfdata_task('/test/path.pdf')
        
        assert result['metadata']['Title'] == 'Test PDF'
        assert result['result_data'] == []


class TestSortRef:
    """Test the sort_ref Celery task."""
    
    @patch('tasks.get_status_code')
    def test_sort_ref_arxiv(self, mock_status):
        """Test sorting arXiv references."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'arxiv', 'ref': '1234.5678'}
        result = sort_ref(ref_dict)
        
        assert result['arxiv'] == ['https://arxiv.org/abs/1234.5678']
        assert result['check'] == ['200']
        assert result['pdfs'] == []
        assert result['urls'] == []
        assert result['doi'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_doi(self, mock_status):
        """Test sorting DOI references."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'doi', 'ref': '10.1000/182'}
        result = sort_ref(ref_dict)
        
        assert result['doi'] == ['https://doi.org/10.1000/182']
        assert result['check'] == ['200']
        assert result['pdfs'] == []
        assert result['urls'] == []
        assert result['arxiv'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_pdf(self, mock_status):
        """Test sorting PDF references."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'pdf', 'ref': 'document.pdf'}
        result = sort_ref(ref_dict)
        
        assert result['pdfs'] == ['document.pdf']
        assert result['check'] == ['200']
        assert result['urls'] == []
        assert result['arxiv'] == []
        assert result['doi'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_url_doi_domain(self, mock_status):
        """Test URL that points to DOI domain."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'url', 'ref': 'https://dx.doi.org/10.1000/182'}
        result = sort_ref(ref_dict)
        
        assert result['doi'] == ['https://dx.doi.org/10.1000/182']
        assert result['check'] == ['200']
        assert result['pdfs'] == []
        assert result['urls'] == []
        assert result['arxiv'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_url_arxiv_domain(self, mock_status):
        """Test URL that points to arXiv domain."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'url', 'ref': 'https://arxiv.org/abs/1234.5678'}
        result = sort_ref(ref_dict)
        
        assert result['arxiv'] == ['https://arxiv.org/abs/1234.5678']
        assert result['check'] == ['200']
        assert result['pdfs'] == []
        assert result['urls'] == []
        assert result['doi'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_regular_url(self, mock_status):
        """Test regular URL sorting."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'url', 'ref': 'https://example.com/page'}
        result = sort_ref(ref_dict)
        
        assert result['urls'] == ['https://example.com/page']
        assert result['check'] == ['200']
        assert result['pdfs'] == []
        assert result['arxiv'] == []
        assert result['doi'] == []
    
    @patch('tasks.get_status_code')
    def test_sort_ref_url_no_scheme(self, mock_status):
        """Test URL without scheme gets https:// added."""
        mock_status.return_value = 200
        
        ref_dict = {'reftype': 'url', 'ref': 'example.com/page'}
        result = sort_ref(ref_dict)
        
        assert result['urls'] == ['https://example.com/page']
        assert result['check'] == ['200']
    
    @patch('tasks.get_status_code')
    def test_sort_ref_status_code_exception(self, mock_status):
        """Test handling of status code exceptions."""
        mock_status.side_effect = Exception('Network error')
        
        ref_dict = {'reftype': 'url', 'ref': 'https://example.com'}
        result = sort_ref(ref_dict)
        
        assert result['check'] == [0]
        assert result['urls'] == ['https://example.com']
