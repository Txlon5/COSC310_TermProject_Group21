from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app) # I discovered FastAPI has its own test component

def test_no_params_returns_200():
    r = client.get("/restaurants")
    assert r.status_code == 200 # Status code 200 means success, which works if no params are provided

#UPDATED TEST for FEAT3-US1
# def test_empty_q_returns_empty_list():
    # r = client.get("/restaurants", params={"q": "   "})
    # assert r.status_code == 200  # Expecting 200 OK since empty q now returns an empty list
    # assert r.json() == []  # The response should be an empty list
def test_empty_q_returns_400():
    r = client.get("/restaurants", params={"q": "   "})
    assert r.status_code == 400 # Status code 400 means bad request, which is what we want if an invalid search query is provided (in this case, just an empty string with whitespace)
    assert "q cannot be empty" in r.json()["detail"]

def test_empty_tag_returns_400():
    r = client.get("/restaurants", params={"tag": ""})
    assert r.status_code == 400 # Same as above, just now for when an invalid tag is provided (in this case, just an empty string)
    assert "tag cannot be empty" in r.json()["detail"]