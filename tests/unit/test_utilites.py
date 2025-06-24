import os
import tempfile
from unittest.mock import patch
from utilites import get_tmp_folder


class TestGetTmpFolder:
    """Test the get_tmp_folder utility function."""
    
    def test_get_tmp_folder_default(self):
        """Test getting default temp folder."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_tmp_folder()
            expected = tempfile.gettempdir()
            assert result == expected
    
    def test_get_tmp_folder_custom_dir(self):
        """Test getting custom temp folder from environment."""
        custom_dir = '/custom/temp/dir'
        with patch.dict(os.environ, {'TMP_CUSTOM_DIR': custom_dir}):
            result = get_tmp_folder()
            assert result == custom_dir
    
    def test_get_tmp_folder_custom_dir_none(self):
        """Test with TMP_CUSTOM_DIR set to None."""
        with patch.dict(os.environ, {'TMP_CUSTOM_DIR': ''}):
            result = get_tmp_folder()
            # When TMP_CUSTOM_DIR is empty string, it should return default
            expected = tempfile.gettempdir()
            assert result == expected
    
    def test_get_tmp_folder_preserves_other_env_vars(self):
        """Test that function doesn't affect other environment variables."""
        with patch.dict(os.environ, {'OTHER_VAR': 'value'}):
            result = get_tmp_folder()
            assert os.getenv('OTHER_VAR') == 'value'
            assert result == tempfile.gettempdir()
