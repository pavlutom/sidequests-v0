import pytest
from services import sidequest_service
from datetime import datetime, timezone
import uuid
import models

def test_get_active_sidequests(db, test_user):
    # Create an accepted quest
    quest1 = models.Sidequest(
        id=uuid.uuid4(),
        title="Accepted Quest",
        description="Testing",
        reward_xp=10,
        user_id=test_user.id,
        accepted_at=datetime.now(timezone.utc)
    )
    # Create a proposed quest
    quest2 = models.Sidequest(
        id=uuid.uuid4(),
        title="Proposed Quest",
        description="Testing",
        reward_xp=10,
        user_id=test_user.id,
        accepted_at=None
    )
    db.add_all([quest1, quest2])
    db.commit()
    
    active = sidequest_service.get_active_sidequests(db, test_user.id)
    assert len(active) == 1
    assert active[0].title == "Accepted Quest"

def test_generate_and_propose_sidequest_cleanup(db, test_user):
    # Pre-populate with an old proposed quest
    old_quest = models.Sidequest(
        id=uuid.uuid4(),
        title="Old Quest",
        description="Testing",
        reward_xp=10,
        user_id=test_user.id,
        accepted_at=None
    )
    db.add(old_quest)
    db.commit()
    
    # Generate new
    preferences = {"categories": ["any"], "estimated_cost": "minimal", "goal": "fun"}
    new_quest = sidequest_service.generate_and_propose_sidequest(db, test_user.id, preferences)
    
    # Verify old is gone
    remaining = db.query(models.Sidequest).filter(models.Sidequest.user_id == test_user.id, models.Sidequest.accepted_at == None).all()
    assert len(remaining) == 1
    assert remaining[0].id == new_quest.id
    assert remaining[0].title != "Old Quest"

def test_accept_sidequest_success(db, test_user):
    quest = models.Sidequest(
        id=uuid.uuid4(),
        title="Proposed Quest",
        description="Testing",
        reward_xp=10,
        user_id=test_user.id,
        accepted_at=None
    )
    db.add(quest)
    db.commit()
    
    accepted = sidequest_service.accept_sidequest(db, test_user.id, quest.id)
    assert accepted.accepted_at is not None
    
    # Reload from DB
    db.refresh(quest)
    assert quest.accepted_at is not None

def test_accept_sidequest_already_accepted(db, test_user):
    quest = models.Sidequest(
        id=uuid.uuid4(),
        title="Active Quest",
        description="Testing",
        reward_xp=10,
        user_id=test_user.id,
        accepted_at=datetime.now(timezone.utc)
    )
    db.add(quest)
    db.commit()
    
    with pytest.raises(ValueError, match="Sidequest already accepted"):
        sidequest_service.accept_sidequest(db, test_user.id, quest.id)

def test_complete_sidequest_rewards_xp(db, test_user):
    initial_xp = test_user.total_xp
    quest = models.Sidequest(
        id=uuid.uuid4(),
        title="Active Quest",
        description="Testing",
        reward_xp=50,
        user_id=test_user.id,
        accepted_at=datetime.now(timezone.utc)
    )
    db.add(quest)
    db.commit()
    
    completed = sidequest_service.complete_sidequest(db, test_user, quest.id)
    assert completed.completed_at is not None
    assert test_user.total_xp == initial_xp + 50
