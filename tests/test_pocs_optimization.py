import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import random
from core import LahkaBlockchain, Transaction, TransactionType

def test_optimized_validator_selection():
    """Test optimized validator selection performance"""
    lahka = LahkaBlockchain()
    
    # Setup multiple validators
    for i in range(5):
        address = f"validator_{i}"
        lahka.add_transaction(Transaction("genesis", address, 100, TransactionType.TRANSFER))
    
    lahka.mine_block()
    
    # Register validators with different stakes
    lahka.register_validator("validator_0", 50.0)
    lahka.register_validator("validator_1", 75.0)
    lahka.register_validator("validator_2", 100.0)
    lahka.register_validator("validator_3", 25.0)
    lahka.register_validator("validator_4", 60.0)
    
    # Test optimized selection
    selected = lahka.optimize_validator_selection()
    assert selected is not None
    assert selected in lahka.validators
    
    # Test multiple selections
    selections = []
    for _ in range(10):
        selected = lahka.optimize_validator_selection()
        selections.append(selected)
    
    # Should have some variety in selection
    assert len(set(selections)) > 1

def test_network_conditions_adjustment():
    """Test network condition adjustments"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    
    alice = lahka.validators["alice"]
    
    # Test high load condition
    lahka.update_network_conditions("high_load")
    assert hasattr(alice, 'dynamic_weight_adjustment')
    assert alice.dynamic_weight_adjustment > 1.0
    
    # Test low load condition
    lahka.update_network_conditions("low_load")
    assert alice.dynamic_weight_adjustment < 1.0
    
    # Test normal condition
    lahka.update_network_conditions("normal")
    assert alice.dynamic_weight_adjustment == 1.0

def test_collaboration_scoring():
    """Test cross-validator collaboration scoring"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.add_transaction(Transaction("genesis", "bob", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    
    lahka.register_validator("alice", 50.0)
    lahka.register_validator("bob", 50.0)
    
    alice = lahka.validators["alice"]
    bob = lahka.validators["bob"]
    
    # Record collaboration activities
    lahka.record_collaboration("alice", "code_review", 10.0)
    lahka.record_collaboration("alice", "mentoring", 5.0)
    lahka.record_collaboration("bob", "security_audit", 15.0)
    
    assert hasattr(alice, 'collaboration_score')
    assert hasattr(bob, 'collaboration_score')
    assert alice.collaboration_score > 0
    assert bob.collaboration_score > 0

def test_network_health_contribution():
    """Test network health contribution tracking"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    
    alice = lahka.validators["alice"]
    
    # Record network health contributions
    lahka.record_network_health_contribution("alice", "latency_optimization", 8.0)
    lahka.record_network_health_contribution("alice", "bandwidth_improvement", 12.0)
    
    assert hasattr(alice, 'network_health_contribution')
    assert alice.network_health_contribution > 0

def test_performance_metrics():
    """Test comprehensive performance metrics"""
    lahka = LahkaBlockchain()
    lahka.add_transaction(Transaction("genesis", "alice", 100, TransactionType.TRANSFER))
    lahka.mine_block()
    lahka.register_validator("alice", 50.0)
    
    alice = lahka.validators["alice"]
    
    # Add some activities
    alice.earn_contribution_credits("code_audit", 20.0, "Test audit")
    alice.apply_penalty("test", 5.0, "Test penalty")
    
    # Get performance metrics
    metrics = alice.get_performance_metrics()
    
    assert 'pocs_score' in metrics
    assert 'stake' in metrics
    assert 'reputation' in metrics
    assert 'reliability' in metrics
    assert 'contribution_score' in metrics
    assert 'collaboration_score' in metrics
    assert 'network_health' in metrics
    assert 'penalty_multiplier' in metrics
    assert 'rehabilitation_progress' in metrics
    assert 'contribution_credits' in metrics
    assert 'blocks_success_rate' in metrics
    assert 'uptime_percentage' in metrics
    assert 'response_time_avg' in metrics
    assert 'total_activities' in metrics
    assert 'total_penalties' in metrics
    assert 'dynamic_weight' in metrics

def test_network_performance_summary():
    """Test network performance summary"""
    lahka = LahkaBlockchain()
    
    # Setup multiple validators
    stakes = [50.0, 75.0, 100.0]
    for i in range(3):
        address = f"validator_{i}"
        lahka.add_transaction(Transaction("genesis", address, stakes[i] + 10, TransactionType.TRANSFER))
    
    lahka.mine_block()
    
    # Register validators and verify they exist
    assert lahka.register_validator("validator_0", 50.0)
    assert lahka.register_validator("validator_1", 75.0)
    assert lahka.register_validator("validator_2", 100.0)
    
    # Verify validators are registered
    assert "validator_0" in lahka.validators
    assert "validator_1" in lahka.validators
    assert "validator_2" in lahka.validators
    
    # Add some activities and penalties
    lahka.validators["validator_0"].earn_contribution_credits("code_audit", 10.0, "Test")
    lahka.validators["validator_1"].apply_penalty("test", 5.0, "Test penalty")
    lahka.record_collaboration("validator_2", "mentoring", 8.0)
    
    # Get network summary
    summary = lahka.get_network_performance_summary()
    
    assert summary['total_validators'] == 3
    assert summary['active_validators'] == 3
    assert summary['total_stake'] == 225.0
    assert 'average_metrics' in summary
    assert summary['total_penalties'] > 0
    assert summary['total_activities'] > 0
    assert 'network_health_score' in summary
    assert 'collaboration_score' in summary

def test_integration_scenario():
    """Test complete PoCS integration scenario"""
    lahka = LahkaBlockchain()
    
    # Setup network with multiple validators
    validator_stakes = {"alice": 50.0, "bob": 100.0, "charlie": 75.0, "diana": 60.0, "eve": 80.0}
    for validator, stake in validator_stakes.items():
        lahka.add_transaction(Transaction("genesis", validator, stake + 10, TransactionType.TRANSFER))
    
    lahka.mine_block()
    
    # Register validators with different characteristics
    assert lahka.register_validator("alice", 50.0)   # Low stake, high contributor
    assert lahka.register_validator("bob", 100.0)    # High stake, reliable
    assert lahka.register_validator("charlie", 75.0) # Medium stake, penalized
    assert lahka.register_validator("diana", 60.0)   # Medium stake, collaborator
    assert lahka.register_validator("eve", 80.0)     # High stake, network health contributor
    
    # Verify all validators are registered
    for validator in validator_stakes:
        assert validator in lahka.validators
    
    # Simulate various activities
    # Alice: Contribution mining pathway
    lahka.validators["alice"].earn_contribution_credits("code_audit", 30.0, "Major audit")
    lahka.validators["alice"].earn_contribution_credits("documentation", 20.0, "API docs")
    
    # Bob: High reliability
    lahka.validators["bob"].update_reliability_score(True, 0.5)
    lahka.validators["bob"].update_reliability_score(True, 0.3)
    
    # Charlie: Gets penalized, then rehabilitates
    lahka.validators["charlie"].apply_penalty("malicious_behavior", 15.0, "First offense")
    lahka.validators["charlie"].earn_contribution_credits("bug_report", 25.0, "Found critical bug")
    
    # Diana: Collaboration activities
    lahka.record_collaboration("diana", "code_review", 12.0)
    lahka.record_collaboration("diana", "mentoring", 8.0)
    
    # Eve: Network health contributions
    lahka.record_network_health_contribution("eve", "latency_optimization", 15.0)
    lahka.record_network_health_contribution("eve", "security_audit", 20.0)
    
    # Test network conditions
    lahka.update_network_conditions("high_load")
    
    # Mine several blocks to test selection
    for _ in range(5):
        lahka.add_transaction(Transaction("genesis", f"user_{random.randint(1, 100)}", 1, TransactionType.TRANSFER))
        lahka.mine_block()
    
    # Get final network summary
    summary = lahka.get_network_performance_summary()
    
    # Verify all validators are active
    assert summary['active_validators'] == 5
    assert summary['total_validators'] == 5
    
    # Verify activities and penalties are recorded
    assert summary['total_activities'] > 0
    assert summary['total_penalties'] > 0
    
    # Verify collaboration and network health scores
    assert summary['collaboration_score'] > 0
    assert summary['network_health_score'] > 0

def test_performance_benchmark():
    """Test performance with many validators"""
    lahka = LahkaBlockchain()
    
    # Setup 20 validators
    for i in range(20):
        address = f"validator_{i:02d}"
        stake = 50.0 + (i * 5.0)
        lahka.add_transaction(Transaction("genesis", address, stake + 10, TransactionType.TRANSFER))
    
    lahka.mine_block()
    
    # Register all validators
    for i in range(20):
        address = f"validator_{i:02d}"
        stake = 50.0 + (i * 5.0)
        assert lahka.register_validator(address, stake)
    
    # Verify all validators are registered
    for i in range(20):
        address = f"validator_{i:02d}"
        assert address in lahka.validators
    
    # Add some random activities
    for i in range(20):
        address = f"validator_{i:02d}"
        validator = lahka.validators[address]
        
        # Random activities
        if i % 3 == 0:
            validator.earn_contribution_credits("code_audit", random.uniform(5, 25), "Random audit")
        if i % 4 == 0:
            validator.apply_penalty("test", random.uniform(1, 10), "Random penalty")
        if i % 5 == 0:
            lahka.record_collaboration(address, "mentoring", random.uniform(2, 15))
    
    # Test selection performance
    start_time = time.time()
    for _ in range(100):
        selected = lahka.optimize_validator_selection()
        assert selected is not None
    end_time = time.time()
    
    # Should complete 100 selections in reasonable time (< 1 second)
    assert (end_time - start_time) < 1.0
    
    # Test network summary performance
    start_time = time.time()
    summary = lahka.get_network_performance_summary()
    end_time = time.time()
    
    # Should complete summary in reasonable time (< 0.1 second)
    assert (end_time - start_time) < 0.1
    
    # Verify summary data
    assert summary['total_validators'] == 20
    assert summary['active_validators'] == 20
    assert summary['total_stake'] > 0 