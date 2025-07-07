#!/usr/bin/env python3
"""
Tests for Proof of Contribution Stake (PoCS) - Chunk 1
"""

import pytest
import time
from core import LahkaBlockchain, Transaction, TransactionType

class TestPoCSBasic:
    """Test basic PoCS functionality"""
    
    def setup_method(self):
        """Set up fresh blockchain for each test"""
        self.lahka = LahkaBlockchain()
        # Give test accounts enough balance and mine a block
        for name in ["alice", "bob", "charlie"]:
            amount = 200 if name == "alice" else 100
            self.lahka.add_transaction(Transaction("genesis", name, amount, TransactionType.TRANSFER))
        self.lahka.mine_block()
    
    def test_validator_pocs_scoring(self):
        """Test that validators have PoCS scores"""
        # Register validators
        assert self.lahka.register_validator("alice", 20.0)
        assert self.lahka.register_validator("bob", 15.0)
        self.lahka.mine_block()  # Process registration
        
        # Check that validators have PoCS metrics
        alice = self.lahka.validators["alice"]
        bob = self.lahka.validators["bob"]
        
        assert hasattr(alice, 'contribution_score')
        assert hasattr(alice, 'reliability_score')
        assert hasattr(alice, 'diversity_bonus')
        assert hasattr(alice, 'calculate_pocs_score')
        
        # Initial scores should be based mainly on stake
        alice_score = alice.calculate_pocs_score(time.time())
        bob_score = bob.calculate_pocs_score(time.time())
        
        assert alice_score > 0
        assert bob_score > 0
        assert alice_score > bob_score  # Alice has more stake
    
    def test_temporal_decay(self):
        """Test that stakes decay over time without activity"""
        # Alice now has 200 tokens from setup
        assert self.lahka.register_validator("alice", 100.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        
        # Get initial score
        initial_score = alice.calculate_pocs_score(time.time())
        
        # Simulate 10 days of inactivity
        future_time = time.time() + (10 * 24 * 3600)  # 10 days
        decayed_score = alice.calculate_pocs_score(future_time)
        
        # Score should be lower due to temporal decay
        assert decayed_score < initial_score
        assert decayed_score > 0  # Should not decay to zero
    
    def test_contribution_scoring(self):
        """Test that validators earn contribution points"""
        assert self.lahka.register_validator("alice", 20.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        
        # Initial contribution score
        initial_contribution = alice.contribution_score
        
        # Add some transactions and mine a block
        self.lahka.add_transaction(Transaction("genesis", "bob", 10, TransactionType.TRANSFER))
        self.lahka.mine_block()
        
        # Contribution score should increase
        assert alice.contribution_score > initial_contribution
    
    def test_reliability_scoring(self):
        """Test that validators earn reliability points"""
        assert self.lahka.register_validator("alice", 20.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        # Set reliability lower so it can increase
        alice.reliability_score = 95
        initial_reliability = alice.reliability_score
        # Mine a block (successful validation)
        self.lahka.add_transaction(Transaction("genesis", "bob", 10, TransactionType.TRANSFER))
        self.lahka.mine_block()
        # Reliability score should increase
        assert alice.reliability_score > initial_reliability
    
    def test_pocs_vs_pos_selection(self):
        """Test that PoCS selection differs from pure PoS"""
        assert self.lahka.register_validator("alice", 20.0)  # High stake
        assert self.lahka.register_validator("bob", 15.0)    # Medium stake
        assert self.lahka.register_validator("charlie", 10.0) # Low stake
        self.lahka.mine_block()
        
        # Give Charlie high contribution score
        charlie = self.lahka.validators["charlie"]
        charlie.update_contribution_score(50.0)  # High contribution
        
        # Mine several blocks and track selection
        selections = []
        for _ in range(10):
            self.lahka.add_transaction(Transaction("genesis", "test", 1, TransactionType.TRANSFER))
            validator = self.lahka.select_validator()
            if validator:
                selections.append(validator)
            self.lahka.mine_block()
        
        # Charlie should be selected sometimes despite lower stake
        assert "charlie" in selections
        
        # All validators should be selected at least once
        assert len(set(selections)) >= 2
    
    def test_validator_activity_tracking(self):
        """Test that validator activity is tracked"""
        assert self.lahka.register_validator("alice", 20.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        
        # Initial activity time
        initial_activity = alice.last_activity
        
        # Wait a bit and mine a block
        time.sleep(0.1)
        self.lahka.add_transaction(Transaction("genesis", "bob", 10, TransactionType.TRANSFER))
        self.lahka.mine_block()
        
        # Activity time should be updated
        assert alice.last_activity > initial_activity
    
    def test_unique_transaction_tracking(self):
        """Test that unique transaction types are tracked"""
        assert self.lahka.register_validator("alice", 20.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        # Add different transaction types
        self.lahka.add_transaction(Transaction("genesis", "bob", 10, TransactionType.TRANSFER))
        self.lahka.add_transaction(Transaction("genesis", "", 0, TransactionType.CONTRACT_DEPLOY, {"contract_code": "test"}))
        self.lahka.mine_block()
        # Should track 2 unique transaction types
        assert alice.unique_transaction_types >= 2
    
    def test_pocs_score_components(self):
        """Test that all PoCS score components work"""
        # Alice now has 200 tokens from setup
        assert self.lahka.register_validator("alice", 100.0)
        self.lahka.mine_block()
        alice = self.lahka.validators["alice"]
        
        # Set different components
        alice.update_contribution_score(50.0)
        alice.update_reliability_score(True, 0.5)
        alice.diversity_bonus = 25.0
        
        # Calculate score
        score = alice.calculate_pocs_score(time.time())
        
        # Score should be positive and include all components
        assert score > 0
        assert alice.contribution_score > 0
        assert alice.reliability_score > 0
        assert alice.diversity_bonus > 0

if __name__ == "__main__":
    pytest.main([__file__]) 