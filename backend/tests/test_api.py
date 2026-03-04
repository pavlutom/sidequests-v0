from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime, timezone
import models

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("services.sidequest_service.get_active_sidequests")
def test_get_sidequests_mocked(mock_get, client, auth_headers):
    quest = MagicMock()
    quest.id = uuid.uuid4()
    quest.title = "Mocked Quest"
    quest.description = "Mocked"
    quest.reward_xp = 10
    quest.user_id = uuid.uuid4()
    quest.created_at = datetime.now(timezone.utc)
    quest.accepted_at = datetime.now(timezone.utc)
    quest.completed_at = None
    
    mock_get.return_value = [quest]
    
    response = client.get("/api/sidequests", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Mocked Quest"

@patch("services.sidequest_service.generate_and_propose_sidequest")
def test_generate_sidequest_api_mocked(mock_gen, client, auth_headers):
    quest = MagicMock()
    quest.id = uuid.uuid4()
    quest.title = "Mocked Generated Quest"
    quest.description = "Description"
    quest.reward_xp = 20
    mock_gen.return_value = quest
    
    preferences = {"categories": ["fun"], "estimated_cost": "minimal", "goal": "fun"}
    response = client.post("/api/sidequests/generate", json=preferences, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Mocked Generated Quest"
    assert "id" in data

@patch("services.sidequest_service.accept_sidequest")
def test_accept_sidequest_api_mocked(mock_accept, client, auth_headers):
    quest_id = uuid.uuid4()
    quest = MagicMock()
    quest.id = quest_id
    quest.title = "Accepted Quest"
    quest.description = "Desc"
    quest.reward_xp = 10
    quest.user_id = uuid.uuid4()
    quest.created_at = datetime.now(timezone.utc)
    quest.accepted_at = datetime.now(timezone.utc)
    quest.completed_at = None
    mock_accept.return_value = quest
    
    response = client.post("/api/sidequests/accept", json={"quest_id": str(quest_id)}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Accepted Quest"

@patch("services.sidequest_service.accept_sidequest")
def test_accept_sidequest_not_found(mock_accept, client, auth_headers):
    mock_accept.return_value = None
    
    response = client.post("/api/sidequests/accept", json={"quest_id": str(uuid.uuid4())}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Sidequest not found"

@patch("services.sidequest_service.accept_sidequest")
def test_accept_sidequest_already_accepted_error(mock_accept, client, auth_headers):
    mock_accept.side_effect = ValueError("Sidequest already accepted")
    
    response = client.post("/api/sidequests/accept", json={"quest_id": str(uuid.uuid4())}, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Sidequest already accepted"
