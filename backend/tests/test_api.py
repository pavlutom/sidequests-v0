import pytest

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate_sidequest_api(client, auth_headers):
    preferences = {
        "categories": ["social", "outdoors"],
        "estimated_cost": "minimal",
        "goal": "fun"
    }
    response = client.post(
        "/api/sidequests/generate",
        json=preferences,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "description" in data
    assert "reward_xp" in data
    assert "tags" in data

def test_accept_sidequest_api(client, auth_headers):
    # First generate one
    gen_response = client.post(
        "/api/sidequests/generate",
        json={"categories": ["any"], "estimated_cost": "minimal", "goal": "fun"},
        headers=auth_headers
    )
    quest_data = gen_response.json()
    
    # Then accept it
    # Note: schemas.SidequestCreate doesn't have tags, so we might need to filter
    accept_data = {
        "title": quest_data["title"],
        "description": quest_data["description"],
        "reward_xp": quest_data["reward_xp"]
    }
    
    
    response = client.post(
        "/api/sidequests/accept",
        json=accept_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == quest_data["title"]

def test_get_sidequests(client, auth_headers):
    response = client.get("/api/sidequests", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
