# 🚀 LAHKA Blockchain Interactive Guide

This guide shows you how to interact with your LAHKA blockchain and understand what's happening under the hood!

## 🎯 Quick Start

### 1. Run the Demo
```bash
python3 demo.py
```
This shows a complete walkthrough of the blockchain in action.

### 2. Run the Explorer
```bash
python3 explore_simple.py
```
This shows the current state of the blockchain.

## 🔍 Understanding What's Happening

### Blockchain Components

Your LAHKA blockchain has these main parts:

1. **📊 Ledger System** - Tracks all accounts and balances
2. **👥 Validators** - Proof of Stake validators who create blocks
3. **📄 Smart Contracts** - Deployable code that runs on the blockchain
4. **🔗 Blocks** - Contain transactions and link together
5. **💰 Transactions** - Transfer tokens, deploy contracts, etc.

### Key Concepts

#### 💰 Gas System
- Every operation costs "gas" (computational resources)
- Gas cost = gas_limit × gas_price
- Prevents spam and pays validators

#### 🏆 Proof of Stake (PoS)
- Validators stake tokens to participate
- Higher stake = higher chance to create blocks
- Validators earn rewards for creating blocks

#### 📄 Smart Contracts
- Deployable code that runs on the blockchain
- Have their own state and can emit events
- Can be called by users with parameters

## 🛠️ How to Interact Programmatically

### Basic Usage

```python
from core import LahkaBlockchain, Transaction, TransactionType

# Create blockchain
lahka = LahkaBlockchain()

# Check initial state
print(f"Blocks: {len(lahka.chain)}")
print(f"Genesis balance: {lahka.get_balance('genesis')}")
```

### Transfer Tokens

```python
# Create transfer transaction
tx = Transaction(
    from_address="genesis",
    to_address="alice",
    amount=100.0,
    transaction_type=TransactionType.TRANSFER
)

# Add to pending pool
lahka.add_transaction(tx)

# Mine block to process
lahka.mine_block()

# Check balances
print(f"Alice balance: {lahka.get_balance('alice')}")
```

### Register as Validator

```python
# Register validator (requires sufficient balance)
success = lahka.register_validator("alice", 20.0)
print(f"Validator registered: {success}")

# Check validator info
validator = lahka.validators["alice"]
print(f"Stake: {validator.stake}, Blocks: {validator.blocks_validated}")
```

### Deploy Smart Contract

```python
# Create contract deployment transaction
contract_code = """
class SchoolRecords:
    def __init__(self):
        self.students = {}
    
    def add_student(self, student_id, name):
        self.students[student_id] = name
        return True
"""

tx = Transaction(
    from_address="alice",
    to_address="",
    transaction_type=TransactionType.CONTRACT_DEPLOY,
    data={
        'contract_code': contract_code,
        'initial_state': {'students': {}}
    },
    gas_limit=50
)

lahka.add_transaction(tx)
lahka.mine_block()

# Get deployed contract address
contract_address = tx.data.get('deployed_address')
print(f"Contract deployed at: {contract_address}")
```

### Call Smart Contract

```python
# Call contract function
tx = Transaction(
    from_address="alice",
    to_address="",
    transaction_type=TransactionType.CONTRACT_CALL,
    data={
        'contract_address': contract_address,
        'function_name': 'add_student',
        'args': ['123', 'John Doe']
    },
    gas_limit=30
)

lahka.add_transaction(tx)
lahka.mine_block()

# Check contract state
state = lahka.get_contract_state(contract_address, 'students')
print(f"Contract state: {state}")
```

## 📊 Inspecting the Blockchain

### Get Blockchain Info

```python
info = lahka.get_chain_info()
print(f"Chain length: {info['chain_length']}")
print(f"Pending transactions: {info['pending_transactions']}")
print(f"Validators: {info['validators']}")
print(f"Contracts: {info['contracts']}")
```

### Check Account History

```python
# Get transaction history for an account
history = lahka.ledger.get_account_history("alice", 10)
for entry in history:
    print(f"{entry.timestamp}: {entry.amount:+.2f} - {entry.description}")
```

### View All Balances

```python
accounts = lahka.ledger.get_accounts_summary()
for address, info in accounts.items():
    print(f"{address}: {info['balance']:.2f} LAHKA")
```

### Export Blockchain Data

```python
import json

# Export entire blockchain state
data = lahka.to_dict()
with open('blockchain_export.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)
```

## 🔧 Advanced Features

### Custom Transaction Types

Your blockchain supports these transaction types:
- `TRANSFER` - Move tokens between accounts
- `CONTRACT_DEPLOY` - Deploy new smart contract
- `CONTRACT_CALL` - Execute contract function
- `STAKE` - Stake tokens to become validator
- `UNSTAKE` - Remove stake (not implemented yet)

### Gas Management

```python
# High gas for complex operations
tx = Transaction(
    from_address="alice",
    to_address="bob",
    amount=10.0,
    gas_limit=100000,  # High gas limit
    gas_price=2.0      # Higher gas price
)

# Low gas for simple transfers
tx = Transaction(
    from_address="alice", 
    to_address="bob",
    amount=10.0,
    gas_limit=21000,   # Standard gas limit
    gas_price=1.0      # Standard gas price
)
```

### Validator Selection

The blockchain uses weighted random selection based on stake:

```python
# Check validator selection
validator = lahka.select_validator()
print(f"Selected validator: {validator}")

# Check validator stats
for addr, val in lahka.validators.items():
    print(f"{addr}: {val.stake:.2f} stake, {val.blocks_validated} blocks")
```

## 🧪 Testing Your Understanding

Try these exercises:

1. **Create a simple economy**: Transfer tokens between multiple accounts
2. **Build a validator network**: Register multiple validators with different stakes
3. **Deploy a voting contract**: Create a contract that tracks votes
4. **Simulate a school system**: Deploy contracts for student records and grades
5. **Monitor gas costs**: Track how different operations consume gas

## 🚨 Common Issues

### "Insufficient balance" errors
- Check account balance before transactions
- Remember gas costs are deducted from sender
- Genesis account has 1,000,000 LAHKA initially

### "Gas limit exceeded" errors
- Reduce gas_limit for transactions
- Complex operations need more gas
- Contract deployment typically needs 50+ gas

### "Contract not found" errors
- Make sure contract is deployed before calling
- Check contract address is correct
- Verify contract status is ACTIVE

## 🎉 Next Steps

Now that you understand the basics:

1. **Week 2**: Build core apps (explorer, faucet, validator app)
2. **Week 3**: Create dApps (elections, payments, school records)
3. **Week 4**: Mobile validator app
4. **Week 5**: Advanced features and optimization

Happy building! 🚀 