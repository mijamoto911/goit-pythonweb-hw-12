import pytest
from unittest.mock import AsyncMock
from src.services.email import send_email


@pytest.mark.asyncio
async def test_send_email():
    """
    Тестує виклик send_email без помилок.
    """
    mock_email_service = AsyncMock()
    mock_email_service.send_email = AsyncMock(return_value=True)
    await send_email("test@example.com", "testuser", "http://localhost")
    mock_email_service.send_email.assert_called_once()
