from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# User Retrival
def test_get_user():
    r = client.get("/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7")
    assert r.status_code == 200
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "test"}

# User Creation
def test_create_user():
    r = client.post(
        "/users/",
        json={"name": "Talon Lusk", "email": "txlon5@student.ubc.ca", "password": "test123"},
    )
    assert r.status_code == 201

    # Save json response to variable
    data = r.json() 

    # Check if id exists and is not empty
    assert "id" in data
    assert data["id"] != ""

    # Check that returned user data matches input
    assert data["name"] == "Talon Lusk"
    assert data["email"] == "txlon5@student.ubc.ca"
    assert data["password"] == "test123"

