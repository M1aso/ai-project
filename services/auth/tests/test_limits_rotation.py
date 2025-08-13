from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

import pytest
from fastapi import HTTPException

from services.auth.app.services import phone_flows
from services.auth.app.security import refresh_family


def setup_function(function):
    phone_flows.reset()
    refresh_family.reset()


def test_rate_limit_and_lockout():
    phone_flows.send_code("+79990000000", "1.1.1.1")
    with pytest.raises(HTTPException) as exc:
        phone_flows.send_code("+79990000000", "1.1.1.1")
    assert exc.value.status_code == 429

    for i in range(5):
        phone_flows.send_code(f"+7999000001{i}", "2.2.2.2")
    with pytest.raises(HTTPException) as exc:
        phone_flows.send_code("+79990000016", "2.2.2.2")
    assert exc.value.status_code == 429

    code = phone_flows.send_code("+79990000017", "3.3.3.3")
    for _ in range(4):
        with pytest.raises(HTTPException) as exc:
            phone_flows.verify_code("+79990000017", "000000")
        assert exc.value.status_code == 400
    with pytest.raises(HTTPException) as exc:
        phone_flows.verify_code("+79990000017", "000000")
    assert exc.value.status_code == 423
    with pytest.raises(HTTPException) as exc:
        phone_flows.verify_code("+79990000017", code)
    assert exc.value.status_code == 423


def test_refresh_rotation_and_revoke():
    rt1 = refresh_family.issue_token("u1", "fam1")
    rt2 = refresh_family.rotate(rt1.token)
    assert rt2.prev_id == rt1.token
    assert refresh_family._store[rt1.token].revoked_at is not None

    rt3 = refresh_family.rotate(rt2.token)
    refresh_family.revoke_family(rt3.family)
    assert refresh_family._store[rt2.token].revoked_at is not None
    assert refresh_family._store[rt3.token].revoked_at is not None
