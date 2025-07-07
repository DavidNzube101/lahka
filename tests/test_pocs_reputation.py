import time
import random
from core import LahkaBlockchain, Transaction, TransactionType

def test_validator_peer_rating():
    """Test that validators can rate each other"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.add_transaction(Transaction("genesis", "bob", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    
    lahka.register_validator("alice", 50.0)
    lahka.register_validator("bob", 50.0)
    
    alice = lahka.validators["alice"]
    bob = lahka.validators["bob"]
    
    # Alice rates Bob
    alice.rate_peer("bob", 85.0, "Good performance")
    assert "bob" in alice.peer_ratings
    assert alice.peer_ratings["bob"][0] == 85.0
    assert alice.peer_ratings["bob"][2] == "Good performance"

def test_average_peer_rating():
    """Test average peer rating calculation"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    alice = lahka.validators["alice"]
    
    # No ratings yet
    assert alice.get_average_peer_rating() == 100.0
    
    # Add some ratings
    alice.rate_peer("bob", 80.0, "Good")
    alice.rate_peer("charlie", 90.0, "Excellent")
    alice.rate_peer("dave", 70.0, "Average")
    
    avg_rating = alice.get_average_peer_rating()
    assert 70.0 <= avg_rating <= 90.0
    assert avg_rating == 80.0  # (80+90+70)/3

def test_reputation_score_update():
    """Test reputation score calculation"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    alice = lahka.validators["alice"]
    
    # Set some initial values
    alice.reliability_score = 95.0
    alice.contribution_score = 50.0
    
    # Add peer ratings
    alice.rate_peer("bob", 85.0, "Good")
    alice.rate_peer("charlie", 90.0, "Excellent")
    
    # Update reputation score
    alice.update_reputation_score()
    
    # Reputation score should be calculated
    assert alice.reputation_score > 0
    assert alice.average_peer_rating == 87.5  # (85+90)/2

def test_peer_review_assignment():
    """Test random peer review assignment"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.add_transaction(Transaction("genesis", "bob", 100, TransactionType.TRANSFER))
    lahka.add_transaction(Transaction("genesis", "charlie", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    
    lahka.register_validator("alice", 50.0)
    lahka.register_validator("bob", 50.0)
    lahka.register_validator("charlie", 50.0)
    
    assignments = lahka.assign_peer_reviews()
    
    # Should have assignments
    assert len(assignments) >= 1
    
    # Each assignment should have 2 validators
    for reviewer, reviewee in assignments:
        assert reviewer in lahka.validators
        assert reviewee in lahka.validators
        assert reviewer != reviewee

def test_peer_review_triggering():
    """Test that peer reviews are triggered periodically"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.add_transaction(Transaction("genesis", "bob", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    
    lahka.register_validator("alice", 50.0)
    lahka.register_validator("bob", 50.0)
    
    alice = lahka.validators["alice"]
    bob = lahka.validators["bob"]
    
    # Mine blocks to trigger peer reviews (every 5 blocks)
    for i in range(10):
        lahka.add_transaction(Transaction("genesis", f"user{i}", 10, TransactionType.TRANSFER))
        lahka.mine_block()
    
    # Should have some peer ratings after peer reviews
    assert len(alice.peer_ratings) > 0 or len(bob.peer_ratings) > 0

def test_pocs_score_with_reputation():
    """Test that PoCS score includes reputation component"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    alice = lahka.validators["alice"]
    
    # Get initial score
    initial_score = alice.calculate_pocs_score(time.time())
    
    # Add peer ratings and update reputation
    alice.rate_peer("bob", 95.0, "Excellent")
    alice.update_reputation_score()
    
    # Score should change due to reputation
    new_score = alice.calculate_pocs_score(time.time())
    assert new_score != initial_score

def test_rating_validation():
    """Test that ratings are validated (1-100 scale)"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    alice = lahka.validators["alice"]
    
    # Valid ratings
    alice.rate_peer("bob", 1.0, "Poor")
    alice.rate_peer("charlie", 100.0, "Perfect")
    alice.rate_peer("dave", 50.0, "Average")
    
    # Invalid ratings should raise ValueError
    try:
        alice.rate_peer("eve", 0.0, "Invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        alice.rate_peer("frank", 101.0, "Invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass 