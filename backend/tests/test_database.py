import pytest
from database import get_db
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

def test_get_db():
    # We can use the actual get_db generator here
    db_gen = get_db()
    
    # We have to patch SessionLocal itself so it returns a mock session
    # that we can spy on.
    with patch('database.SessionLocal') as mock_session_local:
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        
        db_gen = get_db()
        session = next(db_gen)
        
        # Verify it yielded our mock
        assert session is mock_session
        
        # Trigger finally block
        with pytest.raises(StopIteration):
            next(db_gen)
            
        # Verify close was called
        mock_session.close.assert_called_once()
