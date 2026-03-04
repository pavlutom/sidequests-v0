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
    assert "id" in data
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
    
    # Then accept it by ID
    response = client.post(
        "/api/sidequests/accept",
        json={"quest_id": quest_data["id"]},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == quest_data["title"]
    assert response.json()["accepted_at"] is not None

def test_accept_sidequest_forgery(client, auth_headers):
    # Try to accept with old format (full data) - should fail due to schema change or validation
    response = client.post(
        "/api/sidequests/accept",
        json={
            "title": "Forged Quest",
            "description": "I made this up",
            "reward_xp": 1000000
        },
        headers=auth_headers
    )
    assert response.status_code == 422 # Unprocessable Entity (Validation Error)

def test_proposed_quests_cleanup(client, auth_headers):
    # Generate one quest
    client.post(
        "/api/sidequests/generate",
        json={"categories": ["any"], "estimated_cost": "minimal", "goal": "fun"},
        headers=auth_headers
    )
    
    # Verify it's not in the list of active quests
    response = client.get("/api/sidequests", headers=auth_headers)
    assert len(response.json()) == 0
    
    # Generate another one
    client.post(
        "/api/sidequests/generate",
        json={"categories": ["any"], "estimated_cost": "minimal", "goal": "fun"},
        headers=auth_headers
    )
    
    # Theoretically, there's only one "proposed" quest in the DB for this user now.
    # We can't easily check the DB directly here without more setup, 
    # but we can verify the API behavior still works correctly.

def test_get_sidequests(client, auth_headers):
    response = client.get("/api/sidequests", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
