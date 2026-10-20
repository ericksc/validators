"""HA-03. Test public API validation error behavior."""

# standard
from typing import Callable

# external
import pytest

# local
from validators import ValidationError, email, ipv4, url


@pytest.mark.parametrize(
    "validator_func, valid_value, invalid_value",
    [
        (email, "test@example.com", "invalid@@example.com"),
        (url, "https://example.com", "not-a-url"),
        (ipv4, "192.168.1.1", "999.168.1.1"),
    ],
)
def test_public_api_validation_error(
    validator_func: Callable[..., object], valid_value: str, invalid_value: str
):
    """Test that validators return True for valid inputs and ValidationError for invalid."""
    assert validator_func(valid_value) is True

    result: object = validator_func(invalid_value)
    assert isinstance(result, ValidationError)
    assert not result

    with pytest.raises(ValidationError):
        validator_func(invalid_value, r_ve=True)
