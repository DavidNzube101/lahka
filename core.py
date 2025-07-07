import hashlib
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import random
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    TRANSFER = "transfer"
    CONTRACT_DEPLOY = "contract_deploy"
    CONTRACT_CALL = "contract_call"
    STAKE = "stake"
    UNSTAKE = "unstake"

class ContractStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DESTROYED = "destroyed"

@dataclass
class Account:
    """Represents an account in the ledger"""
    address: str
    balance: float = 0.0
    nonce: int = 0
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    is_contract: bool = False
    contract_address: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'address': self.address,
            'balance': self.balance,
            'nonce': self.nonce,
            'created_at': self.created_at,
            'last_updated': self.last_updated,
            'is_contract': self.is_contract,
            'contract_address': self.contract_address
        }

@dataclass
class LedgerEntry:
    """Represents a ledger entry for double-entry bookkeeping"""
    id: str
    transaction_hash: str
    block_number: int
    timestamp: float
    from_address: str
    to_address: str
    amount: float
    transaction_type: str
    description: str
    gas_cost: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)

class Ledger:
    """Main ledger system for account management and transaction history"""
    
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.transactions: List[LedgerEntry] = []
        self.account_history: Dict[str, List[LedgerEntry]] = defaultdict(list)
        
    def create_account(self, address: str, initial_balance: float = 0.0) -> Account:
        """Create a new account"""
        if address in self.accounts:
            return self.accounts[address]
        
        account = Account(
            address=address,
            balance=initial_balance
        )
        self.accounts[address] = account
        return account
    
    def get_account(self, address: str) -> Optional[Account]:
        """Get account by address"""
        return self.accounts.get(address)
    
    def get_or_create_account(self, address: str) -> Account:
        """Get existing account or create new one"""
        account = self.get_account(address)
        if not account:
            account = self.create_account(address)
        return account
    
    def update_balance(self, address: str, amount: float, transaction_hash: str, 
                      block_number: int, description: str, gas_cost: float = 0.0):
        """Update account balance and record transaction"""
        account = self.get_or_create_account(address)
        
        # Update balance
        old_balance = account.balance
        account.balance += amount
        account.last_updated = time.time()
        
        # Create ledger entry
        entry = LedgerEntry(
            id=str(uuid.uuid4()),
            transaction_hash=transaction_hash,
            block_number=block_number,
            timestamp=time.time(),
            from_address="",  # Will be set by caller
            to_address=address,
            amount=amount,
            transaction_type="balance_update",
            description=description,
            gas_cost=gas_cost
        )
        
        self.transactions.append(entry)
        self.account_history[address].append(entry)
    
    def record_transaction(self, transaction_hash: str, block_number: int,
                          from_address: str, to_address: str, amount: float,
                          transaction_type: str, description: str, gas_cost: float = 0.0):
        """Record a complete transaction with double-entry bookkeeping"""
        # Debit from sender
        if from_address and amount > 0:
            self.update_balance(from_address, -amount, transaction_hash, block_number, 
                              f"Debit: {description}", gas_cost)
        
        # Credit to receiver
        if to_address and amount > 0:
            self.update_balance(to_address, amount, transaction_hash, block_number, 
                              f"Credit: {description}")
        
        # Record gas cost separately
        if gas_cost > 0 and from_address:
            self.update_balance(from_address, -gas_cost, transaction_hash, block_number, 
                              f"Gas cost for {transaction_type}", 0.0)
    
    def get_account_history(self, address: str, limit: int = 100) -> List[LedgerEntry]:
        """Get transaction history for an account"""
        return self.account_history[address][-limit:]
    
    def get_balance(self, address: str) -> float:
        """Get current balance for an account"""
        account = self.get_account(address)
        return account.balance if account else 0.0
    
    def get_total_supply(self) -> float:
        """Get total token supply"""
        return sum(account.balance for account in self.accounts.values())
    
    def get_accounts_summary(self) -> Dict[str, Dict]:
        """Get summary of all accounts"""
        return {
            address: {
                'balance': account.balance,
                'nonce': account.nonce,
                'is_contract': account.is_contract,
                'transaction_count': len(self.account_history[address])
            }
            for address, account in self.accounts.items()
        }
    
    def to_dict(self) -> Dict:
        """Convert ledger to dictionary for JSON serialization"""
        return {
            'accounts': {addr: account.to_dict() for addr, account in self.accounts.items()},
            'transactions': [tx.to_dict() for tx in self.transactions],
            'total_supply': self.get_total_supply()
        }

@dataclass
class ContractState:
    """Represents the state of a smart contract"""
    contract_address: str
    data: Dict[str, Any] = field(default_factory=dict)
    code: str = ""
    owner: str = ""
    status: ContractStatus = ContractStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'contract_address': self.contract_address,
            'data': self.data,
            'code': self.code,
            'owner': self.owner,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

@dataclass
class ContractEvent:
    """Represents an event emitted by a smart contract"""
    contract_address: str
    event_name: str
    data: Dict[str, Any]
    block_number: int
    transaction_hash: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
@dataclass
class Transaction:
    """Represents a transaction in the Lahka blockchain"""
    from_address: str
    to_address: str
    amount: float = 0.0
    transaction_type: TransactionType = TransactionType.TRANSFER
    data: Dict[str, Any] = field(default_factory=dict)
    gas_limit: int = 21000
    gas_price: float = 1.0
    timestamp: float = field(default_factory=time.time)
    signature: str = ""
    hash: str = ""
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate hash of transaction"""
        tx_data = {
            'from_address': self.from_address,
            'to_address': self.to_address,
            'amount': self.amount,
            'transaction_type': self.transaction_type.value,
            'data': self.data,
            'gas_limit': self.gas_limit,
            'gas_price': self.gas_price,
            'timestamp': self.timestamp
        }
        tx_string = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'from_address': self.from_address,
            'to_address': self.to_address,
            'amount': self.amount,
            'transaction_type': self.transaction_type.value,
            'data': self.data,
            'gas_limit': self.gas_limit,
            'gas_price': self.gas_price,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash
        }

@dataclass
class Block:
    """Represents a block in the Lahka blockchain"""
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    validator: str
    state_root: str = ""
    nonce: int = 0
    hash: str = ""
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate hash of block"""
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'validator': self.validator,
            'state_root': self.state_root,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'validator': self.validator,
            'state_root': self.state_root,
            'nonce': self.nonce,
            'hash': self.hash
        }

@dataclass
class Validator:
    """Represents a validator in the PoCS (Proof of Contribution Stake) system"""
    address: str
    stake: float
    reputation: float = 100.0
    is_active: bool = True
    last_block_time: float = 0
    blocks_validated: int = 0
    total_rewards: float = 0.0
    
    # PoCS-specific metrics
    registered_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    uptime_percentage: float = 95.0
    response_time_avg: float = 1.0  # seconds
    geographic_location: str = "unknown"
    unique_transaction_types: int = 0
    contribution_score: float = 0.0
    reliability_score: float = 100.0
    diversity_bonus: float = 0.0
    total_uptime_seconds: float = 0.0
    last_seen: float = field(default_factory=time.time)
    blocks_attempted: int = 0
    blocks_successful: int = 0
    txs_processed: int = 0
    contribution_history: list = field(default_factory=list)
    # Chunk 3: Reputation system
    peer_ratings: dict = field(default_factory=dict)  # {peer_address: (rating, timestamp, reason)}
    average_peer_rating: float = 100.0
    reputation_score: float = 100.0
    last_peer_review: float = 0.0
    # Chunk 4: Dynamic penalties and contribution mining
    penalty_history: list = field(default_factory=list)  # [(timestamp, penalty_type, severity, reason)]
    current_penalty_multiplier: float = 1.0
    rehabilitation_progress: float = 0.0  # 0-100, progress toward penalty reduction
    contribution_credits: float = 0.0  # Credits earned through non-monetary contributions
    contribution_activities: list = field(default_factory=list)  # [(timestamp, activity_type, credits_earned)]
    # Chunk 5: Performance optimizations and advanced features
    _cached_pocs_score: float = 0.0
    _last_score_calculation: float = 0.0
    _score_cache_duration: float = 5.0  # Cache for 5 seconds
    collaboration_score: float = 0.0  # Cross-validator collaboration
    network_health_contribution: float = 0.0  # Contribution to network health
    dynamic_weight_adjustment: float = 1.0  # Dynamic weight based on network conditions
    
    def calculate_pocs_score(self, current_time: float, force_recalculate: bool = False) -> float:
        """Calculate PoCS score using optimized multi-dimensional formula with caching"""
        # Use cached score if recent enough
        if not force_recalculate and (current_time - self._last_score_calculation) < self._score_cache_duration:
            return self._cached_pocs_score
        
        # Temporal decay: stakes lose power over time without activity
        days_inactive = (current_time - self.last_activity) / (24 * 3600)  # days
        effective_stake = self.stake * max(0.1, 1 - 0.001 * days_inactive)  # Max 90% decay
        
        # Multi-dimensional scoring formula with dynamic weights
        stake_component = effective_stake * 0.35 * self.dynamic_weight_adjustment  # 35% weight (reduced from 40%)
        
        # Uptime and block success rate
        uptime_factor = min(1.0, self.total_uptime_seconds / max(1, (current_time - self.registered_at)))
        block_success_rate = self.blocks_successful / max(1, self.blocks_attempted)
        txs_factor = min(1.0, self.txs_processed / 100)
        
        # Enhanced contribution component
        contribution_component = (
            self.contribution_score * 0.2 +
            uptime_factor * 10 +
            block_success_rate * 10 +
            txs_factor * 10 +
            self.collaboration_score * 5 +  # New: collaboration bonus
            self.network_health_contribution * 3  # New: network health bonus
        ) * 0.25  # 25% weight (reduced from 30%)
        
        reliability_component = self.reliability_score * 0.2  # 20% weight
        reputation_component = self.reputation_score * 0.1  # 10% weight (increased from 5%)
        diversity_component = self.diversity_bonus * 0.1  # 10% weight (increased from 5%)
        
        total_score = (stake_component + contribution_component + reliability_component + 
                      reputation_component + diversity_component)
        
        # Cache the result
        self._cached_pocs_score = max(0, total_score)
        self._last_score_calculation = current_time
        
        return self._cached_pocs_score
    
    def update_collaboration_score(self, collaboration_activity: str, score_increase: float):
        """Update collaboration score based on cross-validator activities"""
        self.collaboration_score = min(100.0, self.collaboration_score + score_increase)
        
        # Log collaboration activity
        self.contribution_history.append((
            time.time(), 
            f"collaboration_{collaboration_activity}", 
            score_increase
        ))
        
        # Invalidate score cache
        self._last_score_calculation = 0.0
    
    def update_network_health_contribution(self, health_metric: str, contribution: float):
        """Update network health contribution score"""
        self.network_health_contribution = min(100.0, self.network_health_contribution + contribution)
        
        # Log network health activity
        self.contribution_history.append((
            time.time(), 
            f"network_health_{health_metric}", 
            contribution
        ))
        
        # Invalidate score cache
        self._last_score_calculation = 0.0
    
    def adjust_dynamic_weight(self, network_condition: str, adjustment_factor: float):
        """Adjust dynamic weight based on network conditions"""
        if network_condition == "high_load":
            self.dynamic_weight_adjustment = min(1.5, self.dynamic_weight_adjustment * adjustment_factor)
        elif network_condition == "low_load":
            self.dynamic_weight_adjustment = max(0.5, self.dynamic_weight_adjustment * adjustment_factor)
        elif network_condition == "normal":
            self.dynamic_weight_adjustment = 1.0
        
        # Invalidate score cache
        self._last_score_calculation = 0.0
    
    def get_performance_metrics(self) -> dict:
        """Get comprehensive performance metrics"""
        current_time = time.time()
        return {
            'pocs_score': self.calculate_pocs_score(current_time),
            'stake': self.stake,
            'reputation': self.reputation_score,
            'reliability': self.reliability_score,
            'contribution_score': self.contribution_score,
            'collaboration_score': self.collaboration_score,
            'collaboration': self.collaboration_score,
            'network_health_contribution': self.network_health_contribution,
            'network_health': self.network_health_contribution,
            'penalty_multiplier': self.current_penalty_multiplier,
            'rehabilitation_progress': self.rehabilitation_progress,
            'contribution_credits': self.contribution_credits,
            'blocks_success_rate': self.blocks_successful / max(1, self.blocks_attempted),
            'uptime_percentage': self.uptime_percentage,
            'response_time_avg': self.response_time_avg,
            'total_activities': len(self.contribution_activities),
            'total_penalties': len(self.penalty_history),
            'dynamic_weight': self.dynamic_weight_adjustment
        }
    
    def update_activity(self, current_time: float):
        """Update validator activity timestamp"""
        self.last_activity = current_time
        self.last_seen = current_time
    
    def update_contribution_score(self, new_contribution: float, event: str = ""):
        """Update contribution score based on network participation"""
        self.contribution_score = self.contribution_score * 0.9 + new_contribution * 0.1
        if event:
            self.contribution_history.append((time.time(), event, new_contribution))
    
    def update_reliability_score(self, success: bool, response_time: float):
        """Update reliability score based on performance"""
        # Update response time average
        self.response_time_avg = self.response_time_avg * 0.9 + response_time * 0.1
        
        # Update reliability based on success/failure
        if success:
            self.reliability_score = min(100, self.reliability_score + 1)
        else:
            self.reliability_score = max(0, self.reliability_score - 5)
    
    def update_uptime(self, seconds: float):
        self.total_uptime_seconds += seconds
    
    def record_block_attempt(self, success: bool, tx_count: int):
        self.blocks_attempted += 1
        if success:
            self.blocks_successful += 1
        self.txs_processed += tx_count
    
    def rate_peer(self, peer_address: str, rating: float, reason: str = ""):
        """Rate another validator (1-100 scale)"""
        if not (1 <= rating <= 100):
            raise ValueError("Rating must be between 1 and 100")
        
        current_time = time.time()
        self.peer_ratings[peer_address] = (rating, current_time, reason)
        self.last_peer_review = current_time
    
    def get_average_peer_rating(self) -> float:
        """Calculate average rating received from peers"""
        if not self.peer_ratings:
            return 100.0  # Default rating if no peer ratings
        
        ratings = [rating for rating, _, _ in self.peer_ratings.values()]
        return sum(ratings) / len(ratings)
    
    def update_reputation_score(self):
        """Update reputation score based on peer ratings and other factors"""
        peer_rating = self.get_average_peer_rating()
        
        # Combine peer rating with reliability and contribution
        reputation_factors = [
            peer_rating * 0.4,  # 40% peer rating
            self.reliability_score * 0.3,  # 30% reliability
            min(100, self.contribution_score) * 0.3  # 30% contribution (capped at 100)
        ]
        
        self.reputation_score = sum(reputation_factors)
        self.average_peer_rating = peer_rating
    
    def apply_penalty(self, penalty_type: str, severity: float, reason: str = ""):
        """Apply penalty to validator with escalating multiplier"""
        current_time = time.time()
        
        # Add penalty to history first
        self.penalty_history.append((current_time, penalty_type, severity, reason))
        
        # Calculate penalty multiplier based on updated history
        multiplier = self.calculate_penalty_multiplier()
        
        # Apply penalty
        actual_penalty = severity * multiplier
        self.current_penalty_multiplier = multiplier
        
        # Reduce reputation and reliability scores
        self.reputation_score = max(0, self.reputation_score - actual_penalty * 0.5)
        self.reliability_score = max(0, self.reliability_score - actual_penalty * 0.3)
        
        # Reset rehabilitation progress
        self.rehabilitation_progress = 0.0
    
    def calculate_penalty_multiplier(self) -> float:
        """Calculate escalating penalty multiplier based on history"""
        recent_penalties = [p for p in self.penalty_history 
                          if time.time() - p[0] < 30 * 24 * 3600]  # Last 30 days
        
        # Base multiplier increases with each recent penalty
        base_multiplier = 1.0 + (len(recent_penalties) * 0.5)
        
        # Cap at 5x multiplier
        return min(5.0, base_multiplier)
    
    def update_rehabilitation_progress(self, contribution: float):
        """Update rehabilitation progress through positive contributions"""
        self.rehabilitation_progress = min(100.0, self.rehabilitation_progress + contribution)
        
        # If rehabilitation is complete, reduce penalty multiplier
        if self.rehabilitation_progress >= 100.0:
            self.current_penalty_multiplier = max(1.0, self.current_penalty_multiplier * 0.8)
            self.rehabilitation_progress = 0.0  # Reset for next cycle
    
    def earn_contribution_credits(self, activity_type: str, credits: float, description: str = ""):
        """Earn contribution credits through non-monetary activities"""
        current_time = time.time()
        
        self.contribution_credits += credits
        self.contribution_activities.append((current_time, activity_type, credits, description))
        
        # Update rehabilitation progress
        self.update_rehabilitation_progress(credits * 0.1)
        
        # Update contribution score
        self.update_contribution_score(credits * 0.5, f"contribution_activity_{activity_type}")
    
    def convert_credits_to_stake(self, credits_to_convert: float) -> float:
        """Convert contribution credits to stake (1 credit = 0.1 stake)"""
        if credits_to_convert > self.contribution_credits:
            credits_to_convert = self.contribution_credits
        
        stake_earned = credits_to_convert * 0.1
        self.contribution_credits -= credits_to_convert
        self.stake += stake_earned
        
        return stake_earned
    
    def get_contribution_summary(self) -> dict:
        """Get summary of contribution activities"""
        total_credits = sum(credits for _, _, credits, _ in self.contribution_activities)
        activity_types = set(activity_type for _, activity_type, _, _ in self.contribution_activities)
        
        return {
            'total_credits_earned': total_credits,
            'current_credits': self.contribution_credits,
            'activity_types': list(activity_types),
            'rehabilitation_progress': self.rehabilitation_progress,
            'penalty_multiplier': self.current_penalty_multiplier
        }
    
    def to_dict(self) -> Dict:
        return {
            'address': self.address,
            'stake': self.stake,
            'reputation': self.reputation,
            'is_active': self.is_active,
            'last_block_time': self.last_block_time,
            'blocks_validated': self.blocks_validated,
            'total_rewards': self.total_rewards,
            'registered_at': self.registered_at,
            'last_activity': self.last_activity,
            'uptime_percentage': self.uptime_percentage,
            'response_time_avg': self.response_time_avg,
            'geographic_location': self.geographic_location,
            'unique_transaction_types': self.unique_transaction_types,
            'contribution_score': self.contribution_score,
            'reliability_score': self.reliability_score,
            'diversity_bonus': self.diversity_bonus,
            'total_uptime_seconds': self.total_uptime_seconds,
            'last_seen': self.last_seen,
            'blocks_attempted': self.blocks_attempted,
            'blocks_successful': self.blocks_successful,
            'txs_processed': self.txs_processed,
            'contribution_history': self.contribution_history,
            'peer_ratings': self.peer_ratings,
            'average_peer_rating': self.average_peer_rating,
            'reputation_score': self.reputation_score,
            'last_peer_review': self.last_peer_review,
            'penalty_history': self.penalty_history,
            'current_penalty_multiplier': self.current_penalty_multiplier,
            'rehabilitation_progress': self.rehabilitation_progress,
            'contribution_credits': self.contribution_credits,
            'contribution_activities': self.contribution_activities,
            'collaboration_score': self.collaboration_score,
            'network_health_contribution': self.network_health_contribution,
            'dynamic_weight_adjustment': self.dynamic_weight_adjustment,
            'pocs_score': self.calculate_pocs_score(time.time())
        }

class SmartContractEngine:
    """Generic smart contract execution engine"""
    
    def __init__(self):
        self.contracts: Dict[str, ContractState] = {}
        self.events: List[ContractEvent] = []
        self.gas_used: int = 0
        self.max_gas_limit = 1000000
        
    def deploy_contract(self, contract_code: str, initial_state: Dict[str, Any], 
                       deployer_address: str, gas_limit: int) -> str:
        """Deploy a new smart contract"""
        if gas_limit > self.max_gas_limit:
            raise Exception("Gas limit exceeded")
        
        # Generate unique contract address
        contract_address = self._generate_contract_address(deployer_address, contract_code)
        
        # Create contract state
        contract_state = ContractState(
            contract_address=contract_address,
            code=contract_code,
            data=initial_state,
            owner=deployer_address
        )
        
        # Store contract
        self.contracts[contract_address] = contract_state
        
        # Emit deployment event
        self._emit_event(contract_address, "ContractDeployed", {
            "deployer": deployer_address,
            "contract_address": contract_address,
            "initial_state": initial_state
        })
        
        return contract_address
    
    def call_contract(self, contract_address: str, function_name: str, 
                     args: List[Any], caller_address: str, gas_limit: int) -> Any:
        """Execute a function on a smart contract"""
        if contract_address not in self.contracts:
            raise Exception("Contract not found")
        
        contract = self.contracts[contract_address]
        if contract.status != ContractStatus.ACTIVE:
            raise Exception("Contract is not active")
        
        # Execute contract function
        try:
            # Create execution context
            context = {
                'msg_sender': caller_address,
                'contract_address': contract_address,
                'block_timestamp': time.time(),
                'gas_limit': gas_limit
            }
            
            # Execute function (simplified - in real implementation, this would be a proper VM)
            result = self._execute_contract_function(contract, function_name, args, context)
            
            # Update contract state
            contract.updated_at = time.time()
            
            return result
            
        except Exception as e:
            # Revert state changes on error
            self._revert_contract_state(contract_address)
            raise e
    
    def get_contract_state(self, contract_address: str, key_path: str = "") -> Any:
        """Get contract state data"""
        if contract_address not in self.contracts:
            raise Exception("Contract not found")
        
        contract = self.contracts[contract_address]
        
        if not key_path:
            return contract.data
        
        # Navigate nested key path (e.g., "students.123.grades.math")
        keys = key_path.split('.')
        data = contract.data
        
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        
        return data
    
    def _generate_contract_address(self, deployer: str, code: str) -> str:
        """Generate unique contract address"""
        unique_string = f"{deployer}{code}{time.time()}{random.random()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:40]
    
    def _execute_contract_function(self, contract: ContractState, function_name: str, 
                                 args: List[Any], context: Dict[str, Any]) -> Any:
        """Execute a contract function (simplified implementation)"""
        # This is a simplified execution - in a real implementation, you'd have a proper VM
        # For now, we'll simulate basic function execution
        
        if function_name == "set_state":
            key, value = args[0], args[1]
            contract.data[key] = value
            return True
        
        elif function_name == "get_state":
            key = args[0]
            return contract.data.get(key)
        
        elif function_name == "emit_event":
            event_name, event_data = args[0], args[1]
            self._emit_event(contract.contract_address, event_name, event_data)
            return True
        
        else:
            # Try to execute custom function from contract code
            # This would require a proper VM implementation
            raise Exception(f"Function {function_name} not found or not implemented")
    
    def _emit_event(self, contract_address: str, event_name: str, data: Dict[str, Any]):
        """Emit a contract event"""
        event = ContractEvent(
            contract_address=contract_address,
            event_name=event_name,
            data=data,
            block_number=0,  # Will be set by blockchain
            transaction_hash=""  # Will be set by blockchain
        )
        self.events.append(event)
    
    def _revert_contract_state(self, contract_address: str):
        """Revert contract state changes (simplified)"""
        # In a real implementation, you'd have state snapshots
        pass

class LahkaBlockchain:
    """Main Lahka blockchain implementation with smart contracts and Proof of Stake"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.validators: Dict[str, Validator] = {}
        self.ledger = Ledger()  # Replace simple balances with proper ledger
        self.contract_engine = SmartContractEngine()
        
        # Configuration
        self.minimum_stake = 10.0
        self.block_time = 5.0
        self.block_reward = 1.0
        self.gas_price = 1.0
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0",
            validator="genesis"
        )
        self.chain.append(genesis_block)
        
        # Give initial tokens to genesis address
        self.ledger.create_account("genesis", 1000000.0)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the pending pool"""
        if not self.validate_transaction(transaction):
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def validate_transaction(self, transaction: Transaction) -> bool:
        """Validate a transaction"""
        # Check if sender has enough balance for gas
        gas_cost = transaction.gas_limit * transaction.gas_price
        total_cost = transaction.amount + gas_cost
        
        if self.ledger.get_balance(transaction.from_address) < total_cost:
                return False
        
        # Validate based on transaction type
        if transaction.transaction_type == TransactionType.TRANSFER:
            if transaction.amount <= 0:
                return False
        
        elif transaction.transaction_type == TransactionType.CONTRACT_DEPLOY:
            if not transaction.data.get('contract_code'):
                return False
        
        elif transaction.transaction_type == TransactionType.CONTRACT_CALL:
            if not transaction.data.get('contract_address'):
                return False
        
        elif transaction.transaction_type == TransactionType.STAKE:
            if transaction.amount < self.minimum_stake:
                return False
        
        return True
    
    def process_transaction(self, transaction: Transaction):
        """Process a transaction and update state"""
        gas_cost = transaction.gas_limit * transaction.gas_price
        block_number = len(self.chain)
        
        # Process based on transaction type
        if transaction.transaction_type == TransactionType.TRANSFER:
            # Record the transfer transaction
            self.ledger.record_transaction(
                transaction_hash=transaction.hash,
                block_number=block_number,
                from_address=transaction.from_address,
                to_address=transaction.to_address,
                amount=transaction.amount,
                transaction_type="transfer",
                description="Token transfer",
                gas_cost=gas_cost
            )
        
        elif transaction.transaction_type == TransactionType.CONTRACT_DEPLOY:
            contract_code = transaction.data['contract_code']
            initial_state = transaction.data.get('initial_state', {})
            
            try:
                contract_address = self.contract_engine.deploy_contract(
                    contract_code, initial_state, transaction.from_address, 
                    transaction.gas_limit
                )
                # Store contract address in transaction data for reference
                transaction.data['deployed_address'] = contract_address
                
                # Record gas cost for contract deployment
                self.ledger.update_balance(
                    transaction.from_address, -gas_cost, transaction.hash, 
                    block_number, "Gas cost for contract deployment", 0.0
                )
            except Exception as e:
                # Revert gas cost on failure
                self.ledger.update_balance(
                    transaction.from_address, gas_cost, transaction.hash, 
                    block_number, "Gas cost reverted", 0.0
                )
                raise e
        
        elif transaction.transaction_type == TransactionType.CONTRACT_CALL:
            contract_address = transaction.data['contract_address']
            function_name = transaction.data['function_name']
            args = transaction.data.get('args', [])
            
            try:
                result = self.contract_engine.call_contract(
                    contract_address, function_name, args, 
                    transaction.from_address, transaction.gas_limit
                )
                transaction.data['result'] = result
                
                # Record gas cost for contract call
                self.ledger.update_balance(
                    transaction.from_address, -gas_cost, transaction.hash, 
                    block_number, "Gas cost for contract call", 0.0
                )
            except Exception as e:
                # Revert gas cost on failure
                self.ledger.update_balance(
                    transaction.from_address, gas_cost, transaction.hash, 
                    block_number, "Gas cost reverted", 0.0
                )
                raise e
        
        elif transaction.transaction_type == TransactionType.STAKE:
            # Record the stake transaction
            self.ledger.record_transaction(
                transaction_hash=transaction.hash,
                block_number=block_number,
                from_address=transaction.from_address,
                to_address="stake_pool",
                amount=transaction.amount,
                transaction_type="stake",
                description="Validator stake",
                gas_cost=gas_cost
            )
    
    def register_validator(self, address: str, stake_amount: float) -> bool:
        """Register a new validator"""
        if stake_amount < self.minimum_stake:
            return False
        
        if self.ledger.get_balance(address) < stake_amount:
            return False
        
        # Create stake transaction with very low gas limit
        stake_tx = Transaction(
            from_address=address,
            to_address="stake_pool",
            amount=stake_amount,
            transaction_type=TransactionType.STAKE,
            gas_limit=10  # Very low gas limit for staking
        )
        
        if self.add_transaction(stake_tx):
            self.validators[address] = Validator(
                address=address,
                stake=stake_amount
            )
            return True
        
        return False
    
    def select_validator(self) -> Optional[str]:
        """Select a validator using PoCS (Proof of Contribution Stake) scoring"""
        if not self.validators:
            return None
        
        active_validators = {addr: val for addr, val in self.validators.items() 
                           if val.is_active}
        
        if not active_validators:
            return None
        
        current_time = time.time()
        
        # Calculate PoCS scores for all active validators
        validator_scores = {}
        total_score = 0
        
        for address, validator in active_validators.items():
            # Update activity timestamp
            validator.update_activity(current_time)
            
            # Calculate PoCS score
            pocs_score = validator.calculate_pocs_score(current_time)
            validator_scores[address] = pocs_score
            total_score += pocs_score
        
        if total_score <= 0:
            # Fallback to simple stake-based selection if no PoCS scores
            total_stake = sum(val.stake for val in active_validators.values())
        random_value = random.uniform(0, total_stake)
        current_weight = 0
        
        for address, validator in active_validators.items():
            current_weight += validator.stake
            if random_value <= current_weight:
                return address
        
            return list(active_validators.keys())[0]
        
        # Use PoCS scores for weighted random selection
        random_value = random.uniform(0, total_score)
        current_weight = 0
        
        for address, score in validator_scores.items():
            current_weight += score
            if random_value <= current_weight:
                return address
        
        return list(active_validators.keys())[0]
    
    def create_block(self, validator_address: str) -> Block:
        """Create a new block with pending transactions"""
        transactions_to_include = self.pending_transactions[:100]
        
        # Calculate state root (simplified)
        state_root = self._calculate_state_root()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions_to_include,
            previous_hash=self.get_latest_block().hash,
            validator=validator_address,
            state_root=state_root
        )
        
        return new_block
    
    def add_block(self, block: Block) -> bool:
        """Add a validated block to the chain"""
        if not self.validate_block(block):
            return False
        
        # Process transactions in the block
        for transaction in block.transactions:
            try:
            self.process_transaction(transaction)
            except Exception as e:
                print(f"Transaction processing failed: {e}")
                continue
        
        # Remove processed transactions from pending pool
        for transaction in block.transactions:
            if transaction in self.pending_transactions:
                self.pending_transactions.remove(transaction)
        
        # Add block to chain
        self.chain.append(block)
        
        # Reward validator
        self.ledger.update_balance(block.validator, self.block_reward, "", len(self.chain), "Block reward")
        
        # Update validator stats and PoCS metrics
        if block.validator in self.validators:
            validator = self.validators[block.validator]
            validator.blocks_validated += 1
            validator.last_block_time = time.time()
            validator.total_rewards += self.block_reward
            current_time = time.time()
            validator.update_activity(current_time)
            # Reward for successful block validation
            validator.update_contribution_score(10.0, event="block_validated")
            validator.update_reliability_score(True, 1.0)
            tx_types = set(tx.transaction_type.value for tx in block.transactions)
            validator.unique_transaction_types = max(validator.unique_transaction_types, len(tx_types))
            # Chunk 2: Update uptime, block attempts, txs processed
            block_time = self.block_time if hasattr(self, 'block_time') else 5.0
            validator.update_uptime(block_time)
            validator.record_block_attempt(True, len(block.transactions))
            
            # Chunk 3: Trigger peer reviews every 5 blocks
            if len(self.chain) % 5 == 0 and len(self.validators) >= 2:
                self.trigger_peer_reviews()
        
        return True
    
    def validate_block(self, block: Block) -> bool:
        """Validate a block before adding to chain"""
        if block.index != len(self.chain):
            return False
        
        if block.previous_hash != self.get_latest_block().hash:
            return False
        
        # Allow genesis validator or registered validators
        if block.validator != "genesis" and block.validator not in self.validators:
            return False
        
        if block.hash != block.calculate_hash():
            return False
        
        return True
    
    def mine_block(self) -> bool:
        """Mine a new block (PoS version)"""
        if not self.pending_transactions:
            return False
        
        # For the first block after genesis, use genesis validator
        if len(self.chain) == 1 and not self.validators:
            validator = "genesis"
        else:
        validator = self.select_validator()
        if not validator:
            return False
        
        new_block = self.create_block(validator)
        return self.add_block(new_block)
    
    def _calculate_state_root(self) -> str:
        """Calculate state root (simplified)"""
        state_data = {
            'ledger': self.ledger.to_dict(),
            'contracts': {addr: contract.to_dict() for addr, contract in self.contract_engine.contracts.items()}
        }
        state_string = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(state_string.encode()).hexdigest()
    
    def assign_peer_reviews(self) -> List[tuple]:
        """Randomly assign validators to rate each other (anti-collusion)"""
        if len(self.validators) < 2:
            return []
        
        validators = list(self.validators.keys())
        assignments = []
        
        # Randomly pair validators for peer review
        import random
        random.shuffle(validators)
        
        for i in range(0, len(validators) - 1, 2):
            reviewer = validators[i]
            reviewee = validators[i + 1]
            assignments.append((reviewer, reviewee))
        
        return assignments
    
    def process_peer_ratings(self, ratings: List[tuple]):
        """Process peer ratings and update reputation scores"""
        for reviewer, reviewee, rating, reason in ratings:
            if reviewer in self.validators and reviewee in self.validators:
                # Rate the peer
                self.validators[reviewer].rate_peer(reviewee, rating, reason)
                
                # Update reputation scores
                self.validators[reviewee].update_reputation_score()
    
    def trigger_peer_reviews(self):
        """Trigger a round of peer reviews"""
        assignments = self.assign_peer_reviews()
        
        # For demo purposes, generate some sample ratings
        # In a real system, validators would submit their actual ratings
        ratings = []
        for reviewer, reviewee in assignments:
            # Simulate rating based on performance
            reviewee_validator = self.validators[reviewee]
            base_rating = min(100, max(1, reviewee_validator.reliability_score))
            
            # Add some randomness to simulate real ratings
            import random
            rating = max(1, min(100, base_rating + random.uniform(-10, 10)))
            reason = f"Performance review based on reliability score"
            
            ratings.append((reviewer, reviewee, rating, reason))
        
        self.process_peer_ratings(ratings)
    
    def apply_validator_penalty(self, validator_address: str, penalty_type: str, severity: float, reason: str = ""):
        """Apply penalty to a validator"""
        if validator_address in self.validators:
            self.validators[validator_address].apply_penalty(penalty_type, severity, reason)
    
    def community_override_penalty(self, validator_address: str, new_penalty_multiplier: float, reason: str = ""):
        """Community governance override of algorithmic penalty"""
        if validator_address in self.validators:
            validator = self.validators[validator_address]
            old_multiplier = validator.current_penalty_multiplier
            validator.current_penalty_multiplier = new_penalty_multiplier
            
            # Log the override
            validator.penalty_history.append((
                time.time(), 
                "community_override", 
                old_multiplier - new_penalty_multiplier, 
                f"Community override: {reason}"
            ))
    
    def get_contribution_mining_activities(self) -> dict:
        """Get available contribution mining activities"""
        return {
            'code_audit': {
                'description': 'Audit smart contract code for security issues',
                'credits_per_hour': 10.0,
                'max_credits': 100.0
            },
            'documentation': {
                'description': 'Write or improve documentation',
                'credits_per_hour': 5.0,
                'max_credits': 50.0
            },
            'community_support': {
                'description': 'Help other users and validators',
                'credits_per_hour': 3.0,
                'max_credits': 30.0
            },
            'bug_report': {
                'description': 'Report bugs or security vulnerabilities',
                'credits_per_bug': 20.0,
                'max_credits': 200.0
            },
            'educational_content': {
                'description': 'Create educational content about the blockchain',
                'credits_per_hour': 8.0,
                'max_credits': 80.0
            }
        }
    
    def optimize_validator_selection(self) -> Optional[str]:
        """Optimized validator selection with performance improvements"""
        if not self.validators:
            return None
        
        active_validators = {addr: val for addr, val in self.validators.items() 
                           if val.is_active}
        
        if not active_validators:
            return None
        
        current_time = time.time()
        
        # Use cached scores where possible
        validator_scores = {}
        total_score = 0
        
        for address, validator in active_validators.items():
            # Update activity timestamp
            validator.update_activity(current_time)
            
            # Calculate PoCS score (with caching)
            pocs_score = validator.calculate_pocs_score(current_time)
            validator_scores[address] = pocs_score
            total_score += pocs_score
        
        if total_score <= 0:
            # Fallback to simple stake-based selection
            total_stake = sum(val.stake for val in active_validators.values())
            random_value = random.uniform(0, total_stake)
            current_weight = 0
            
            for address, validator in active_validators.items():
                current_weight += validator.stake
                if random_value <= current_weight:
                    return address
            
            return list(active_validators.keys())[0]
        
        # Use PoCS scores for weighted random selection
        random_value = random.uniform(0, total_score)
        current_weight = 0
        
        for address, score in validator_scores.items():
            current_weight += score
            if random_value <= current_weight:
                return address
        
        return list(active_validators.keys())[0]
    
    def update_network_conditions(self, condition: str):
        """Update network conditions and adjust validator weights"""
        adjustment_factors = {
            'high_load': 1.2,  # Increase weight for high-performance validators
            'low_load': 0.8,   # Decrease weight for low-load scenarios
            'normal': 1.0      # Normal conditions
        }
        
        factor = adjustment_factors.get(condition, 1.0)
        
        for validator in self.validators.values():
            validator.adjust_dynamic_weight(condition, factor)
    
    def record_collaboration(self, validator_address: str, activity: str, score: float):
        """Record cross-validator collaboration activity"""
        if validator_address in self.validators:
            self.validators[validator_address].update_collaboration_score(activity, score)
    
    def record_network_health_contribution(self, validator_address: str, metric: str, contribution: float):
        """Record network health contribution"""
        if validator_address in self.validators:
            self.validators[validator_address].update_network_health_contribution(metric, contribution)
    
    def get_network_performance_summary(self) -> dict:
        """Get comprehensive network performance summary"""
        if not self.validators:
            return {}
        
        total_validators = len(self.validators)
        active_validators = len([v for v in self.validators.values() if v.is_active])
        
        # Calculate average metrics
        avg_scores = {
            'pocs_score': 0.0,
            'reputation': 0.0,
            'reliability': 0.0,
            'collaboration': 0.0,
            'network_health': 0.0
        }
        
        total_stake = 0.0
        total_penalties = 0
        total_activities = 0
        
        for validator in self.validators.values():
            metrics = validator.get_performance_metrics()
            for key in avg_scores:
                if key in metrics:
                    avg_scores[key] += metrics[key]
            
            total_stake += validator.stake
            total_penalties += len(validator.penalty_history)
            total_activities += len(validator.contribution_activities)
        
        # Calculate averages
        if total_validators > 0:
            for key in avg_scores:
                avg_scores[key] /= total_validators
        
        return {
            'total_validators': total_validators,
            'active_validators': active_validators,
            'total_stake': total_stake,
            'average_metrics': avg_scores,
            'total_penalties': total_penalties,
            'total_activities': total_activities,
            'network_health_score': avg_scores['network_health'],
            'collaboration_score': avg_scores['collaboration']
        }
    
    def get_balance(self, address: str) -> float:
        """Get balance for an address"""
        return self.ledger.get_balance(address)
    
    def get_contract_state(self, contract_address: str, key_path: str = "") -> Any:
        """Get contract state"""
        return self.contract_engine.get_contract_state(contract_address, key_path)
    
    def get_chain_info(self) -> Dict:
        """Get blockchain information"""
        return {
            'chain_length': len(self.chain),
            'pending_transactions': len(self.pending_transactions),
            'validators': len(self.validators),
            'contracts': len(self.contract_engine.contracts),
            'latest_block': self.get_latest_block().to_dict()
        }
    
    def to_dict(self) -> Dict:
        """Convert blockchain to dictionary for JSON serialization"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'validators': {addr: val.to_dict() for addr, val in self.validators.items()},
            'ledger': self.ledger.to_dict(),
            'contracts': {addr: contract.to_dict() for addr, contract in self.contract_engine.contracts.items()}
        }