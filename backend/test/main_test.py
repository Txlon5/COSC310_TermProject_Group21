from fastapi.testclient import TestClient 
from app.main import app

client = TestClient(app)

def test_home():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"msg": "Hello World"}

def test_get_item():
    r = client.get("/items/coffee")
    assert r.status_code == 200
    assert r.json() == {"item": "coffee", "status": "ok"}