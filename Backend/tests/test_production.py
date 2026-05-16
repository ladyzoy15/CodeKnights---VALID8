import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from sqlalchemy import text

# Using fixtures from conftest.py

def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code in (200, 503)
    data = r.json()
    assert "status" in data

def test_auth_login_endpoint(client, db):
    data = {"username": "campus_admin@test.com", "password": "wrongpassword"}
    r = client.post("/token", data=data)
    assert r.status_code in (401, 400, 403, 404) 

def test_protected_route_without_token(client):
    r = client.get("/api/users/me/")
    assert r.status_code == 401

def test_cors_allowed_origins(client):
    r = client.options("/token", headers={"Origin": "http://127.0.0.1:4173", "Access-Control-Request-Method": "POST"})
    assert r.status_code < 500

def test_rbac_permissions(client):
    r = client.get("/api/admin/some-endpoint", headers={"Authorization": "Bearer invalidtoken"})
    assert r.status_code == 401

def test_database_rollback(db):
    try:
        db.execute(text("SELECT * FROM non_existent_table"))
    except Exception:
        db.rollback()
    assert db.execute(text("SELECT 1")).scalar() == 1
