import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.api import auth as auth_api
from app.database import session as database_session
from app.main import app
from app.models.user import User
from app.services.auth_service import create_access_token, hash_password
from app.database.config import settings


@pytest.fixture()
def client(db_session):
    admin = User(username="admin", hashed_password=hash_password("admin123"))
    db_session.add(admin)
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[auth_api.get_db] = override_get_db
    app.dependency_overrides[database_session.get_db] = override_get_db
    def make_request(method, path, headers=None, body=None):
        request_body = json.dumps(body).encode() if body is not None else b""
        request_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
        if body is not None:
            request_headers.append((b"content-type", b"application/json"))
        response = {"status": None, "headers": [], "body": b""}
        body_sent = False

        async def receive():
            nonlocal body_sent
            if body_sent:
                return {"type": "http.disconnect"}
            body_sent = True
            return {"type": "http.request", "body": request_body, "more_body": False}

        async def send(message):
            if message["type"] == "http.response.start":
                response["status"] = message["status"]
                response["headers"] = message["headers"]
            elif message["type"] == "http.response.body":
                response["body"] += message.get("body", b"")

        async def execute():
            await app(
                {
                    "type": "http",
                    "http_version": "1.1",
                    "method": method,
                    "scheme": "http",
                    "path": path,
                    "raw_path": path.encode(),
                    "query_string": b"",
                    "headers": request_headers,
                    "client": ("testclient", 50000),
                    "server": ("testserver", 80),
                },
                receive,
                send,
            )

        asyncio.run(execute())
        response["json"] = json.loads(response["body"]) if response["body"] else None
        response["headers"] = {key.decode().lower(): value.decode() for key, value in response["headers"]}
        return response

    yield make_request

    app.dependency_overrides.clear()


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_works_without_authentication(client):
    response = client(
        "POST",
        "/api/auth/login",
        body={"username": "admin", "password": "admin123"},
    )

    assert response["status"] == 200
    assert response["json"]["token_type"] == "bearer"
    assert response["json"]["access_token"]


def test_flags_requires_authentication(client):
    response = client("GET", "/api/flags")

    assert response["status"] == 401
    assert response["headers"]["www-authenticate"] == "Bearer"


def test_flags_rejects_invalid_token(client):
    response = client("GET", "/api/flags", headers=auth_header("invalid-token"))

    assert response["status"] == 401
    assert response["headers"]["www-authenticate"] == "Bearer"


def test_flags_rejects_non_bearer_credentials(client):
    response = client(
        "GET",
        "/api/flags",
        headers={"Authorization": "Basic invalid-credentials"},
    )

    assert response["status"] == 401
    assert response["headers"]["www-authenticate"] == "Bearer"


def test_flags_rejects_expired_token(client):
    token = jwt.encode(
        {
            "sub": "admin",
            "user_id": 1,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client("GET", "/api/flags", headers=auth_header(token))

    assert response["status"] == 401


def test_flags_accepts_valid_token(client):
    token = create_access_token({"sub": "admin", "user_id": 1})

    response = client("GET", "/api/flags", headers=auth_header(token))

    assert response["status"] == 200
    assert isinstance(response["json"], list)


def test_create_flag_accepts_valid_token(client):
    token = create_access_token({"sub": "admin", "user_id": 1})

    response = client(
        "POST",
        "/api/flags",
        headers=auth_header(token),
        body={
            "environment_id": 1,
            "key": "new_flag",
            "name": "New Flag",
            "type": "boolean",
            "default_value": "false",
            "enabled": False,
            "description": "A test flag",
            "owner_team": "platform",
        },
    )

    assert response["status"] == 200
    assert response["json"]["key"] == "new_flag"


def test_evaluation_requires_authentication(client):
    response = client(
        "POST",
        "/api/evaluate",
        body={"flag_key": "dark_mode", "environment_name": "development"},
    )

    assert response["status"] == 401


def test_evaluation_accepts_valid_token(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.flag_routes.evaluate_flag",
        lambda **_: {"success": True, "enabled": True, "value": "true"},
    )
    token = create_access_token({"sub": "admin", "user_id": 1})

    response = client(
        "POST",
        "/api/evaluate",
        headers=auth_header(token),
        body={
            "flag_key": "dark_mode",
            "environment_name": "development",
            "user_context": {"user_id": "user123"},
        },
    )

    assert response["status"] == 200
    assert response["json"]["success"] is True


@pytest.mark.parametrize(
    "path",
    ["/api/environment", "/api/targeting-rules"],
)
def test_management_endpoints_require_authentication(client, path):
    response = client("GET", path)

    assert response["status"] == 401
    assert response["headers"]["www-authenticate"] == "Bearer"
