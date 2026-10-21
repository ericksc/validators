"""Regression tests for previously-fixed validator bugs.

This suite consolidates, in a single place, five concrete bugs that were
found and fixed in `src/validators/email.py` and `src/validators/ip_address.py`
during the HU-02/HU-04 test-coverage work. Each test pins down the exact
input that used to misbehave, so a future change cannot silently reintroduce
any of these defects. The individual scenario-specific tests
(`test_email_control_character.py`, `test_email_ipv6_literal.py`,
`test_email_quoted_at_sign.py`, `test_ipv4_strict_cidr.py`,
`test_ipv6_brackets.py`) remain the detailed/parametrized versions of these
same cases; this file is the single "do not regress" checklist.
"""

# external
import pytest

# local
from validators import ValidationError, email, ipv4, ipv6


def test_regression_email_rejects_control_characters_in_quoted_local_part():
    """Bug: the quoted-string regex used to accept ASCII control characters.

    Fixed in `src/validators/email.py`. A quoted local part containing a
    control character (e.g. SOH, VT, FF, ESC, US, DEL) must be rejected.
    """
    result = email('"user\x01name"@example.com')
    assert isinstance(result, ValidationError), repr(result)


def test_regression_email_accepts_ipv6_prefix_in_address_literal():
    """Bug: the `IPv6:` prefix inside an address literal was not stripped.

    Fixed in `src/validators/email.py`. With `ipv6_address=True`, an
    address literal like `[IPv6:2001:db8::1]` must be accepted.
    """
    result = email("usuario@[IPv6:2001:db8::1]", ipv6_address=True)
    assert result is True, repr(result)


def test_regression_email_accepts_at_sign_inside_quoted_local_part():
    """Bug: `email.count("@") != 1` rejected any `@` inside a quoted string.

    Fixed in `src/validators/email.py`. A quoted local part may legally
    contain an `@` character per RFC 5322.
    """
    result = email('"user@name"@example.com')
    assert result is True, repr(result)


def test_regression_ipv4_strict_cidr_rejects_non_prefix_netmask():
    """Bug: CIDR prefix length was not validated to be an integer 0-32.

    Fixed in `src/validators/ip_address.py`. Strict mode must reject a
    dotted netmask (e.g. `/255.255.255.0`) that is not a CIDR prefix.
    """
    result = ipv4("192.168.1.0/255.255.255.0", strict=True)
    assert isinstance(result, ValidationError), repr(result)


def test_regression_ipv6_strips_surrounding_brackets():
    """Bug: IPv6 literals wrapped in brackets (URL host syntax) were rejected.

    Fixed in `src/validators/ip_address.py`. `ipv6()` must strip a
    leading `[` and trailing `]` before validating the address.
    """
    result = ipv6("[2001:db8::1]")
    assert result is True, repr(result)


@pytest.mark.parametrize(
    "value",
    [
        '"user\x01name"@example.com',
        '"user@name"@example.com',
        "usuario@[IPv6:2001:db8::1]",
    ],
)
def test_regression_email_does_not_crash_on_fixed_edge_cases(value: str):
    """Sanity check: none of the fixed edge cases raise unhandled exceptions."""
    result = email(value, ipv6_address=True)
    assert result is True or isinstance(result, ValidationError)
