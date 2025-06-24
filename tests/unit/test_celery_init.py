from unittest.mock import Mock, patch
from flask import Flask
from celery_init import celery_init_app


class TestCeleryInitApp:
    """Test the celery_init_app function."""
    
    @patch('celery_init.Celery')
    def test_celery_init_app(self, mock_celery_class):
        """Test Celery app initialization."""
        # Create a mock Flask app
        app = Flask(__name__)
        app.config['CELERY'] = {
            'broker_url': 'redis://localhost:6379/0',
            'result_backend': 'redis://localhost:6379/0'
        }
        
        # Mock Celery instance
        mock_celery_instance = Mock()
        mock_celery_class.return_value = mock_celery_instance
        
        # Call the function
        result = celery_init_app(app)
        
        # Verify Celery was initialized correctly
        mock_celery_class.assert_called_once()
        mock_celery_instance.config_from_object.assert_called_once_with(
            app.config['CELERY']
        )
        mock_celery_instance.set_default.assert_called_once()
        
        # Verify the result is the Celery instance
        assert result == mock_celery_instance
    
    @patch('celery_init.Celery')
    def test_flask_task_integration(self, mock_celery_class):
        """Test that FlaskTask is properly integrated."""
        app = Flask(__name__)
        app.config['CELERY'] = {}
        
        mock_celery_instance = Mock()
        mock_celery_class.return_value = mock_celery_instance
        
        celery_init_app(app)
        
        # Verify that Celery was called with the custom task class
        call_args = mock_celery_class.call_args
        assert call_args[0][0] == app.name  # First positional arg is app.name
        assert 'task_cls' in call_args[1]  # task_cls is in keyword args
    
    def test_flask_task_call_method(self):
        """Test FlaskTask.__call__ method works with app context."""
        app = Flask(__name__)
        app.config['CELERY'] = {}
        
        with patch('celery_init.Celery') as mock_celery_class:
            mock_celery_instance = Mock()
            mock_celery_class.return_value = mock_celery_instance
            
            # Get the FlaskTask class from the call
            celery_init_app(app)
            call_args = mock_celery_class.call_args
            flask_task_class = call_args[1]['task_cls']
            
            # Create an instance of FlaskTask
            task_instance = flask_task_class()
            task_instance.run = Mock(return_value='test_result')
            
            # Test the __call__ method
            with app.app_context():
                result = task_instance('arg1', 'arg2', kwarg1='value1')
                
                # Verify the task's run method was called
                task_instance.run.assert_called_once_with(
                    'arg1', 'arg2', kwarg1='value1'
                )
                assert result == 'test_result'
