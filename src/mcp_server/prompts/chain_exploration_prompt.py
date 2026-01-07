"""Chain exploration prompt implementation for Regen Network."""

from typing import Optional, Dict, Any


async def chain_exploration(chain_config: Optional[Dict[str, Any]] = None) -> str:
    """
    Initial exploration guide for Regen Network chain.
    Provides context-aware guidance based on current chain configuration.
    """
    
    # Determine chain status
    if not chain_config:
        chain_id = "Not configured"
        chain_status = "⚠️ No chain configured"
        config_hint = """
**⚠️ Chain Not Configured**
Start by setting up your chain connection:
```python
# Configure for mainnet
config = {
    "chain_id": "regen-1",
    "rest_endpoint": "https://rest.cosmos.directory/regen",
    "rpc_endpoint": "https://rpc.cosmos.directory/regen",
    "grpc_endpoint": "grpc.cosmos.directory:443"
}
```
"""
    else:
        chain_id = chain_config.get("chain_id", "Unknown")
        chain_status = "✅ Connected"
        config_hint = f"""
**✅ Chain Connected**
• Chain ID: `{chain_id}`
• REST API: Ready
• RPC: Ready
"""

    return f"""🌱 **Regen Network Chain Explorer**

Welcome to the Regen Network ecosystem! Let's explore ecological credits and carbon markets.

{config_hint}

**📊 Available Modules:**
• **Eco Credit** - Carbon credits and ecological assets
• **Marketplace** - Trading and price discovery
• **Data Module** - Ecological data attestation

**🎯 Quick Start Commands:**

**1. Basic Chain Info**
```python
get_chain_config()          # View current configuration
get_node_info()            # Node connection details
```

**2. Explore Credit Classes**
```python
classes = list_classes(limit=100, offset=0)  # List all credit classes (includes resolved names)
# Each class includes:
# - id (e.g., "C01")
# - name (resolved from the on-chain metadata IRI)
# - source_registry (when available, e.g., City Forest Credits)
```

**3. Discover Projects**
```python
get_all_projects()         # Browse all ecological projects
get_projects_by_class('C01')  # Projects by methodology
get_project_by_id('C01-001')  # Specific project details
```

**4. View Credit Batches**
```python
get_all_batches()          # All issued credit batches
get_batches_by_project('C01-001')  # Project's credit issuances
get_batch('C01-001-20240101-20240131-001')  # Batch details
```

**5. Check Marketplace**
```python
get_sell_orders()          # Current market listings
get_sell_orders_by_batch('batch_denom')  # Specific batch orders
```

**📈 Data Discovery Paths:**

**🌳 Path 1: Project Explorer**
Start with a specific project and explore its impact:
```python
# 1. Find a project
project = get_project_by_id('C01-001')

# 2. Check its credit issuances
batches = get_batches_by_project('C01-001')

# 3. Analyze market activity
for batch in batches:
    orders = get_sell_orders_by_batch(batch['denom'])
```

**💰 Path 2: Market Analysis**
Understand current carbon credit pricing:
```python
# 1. Get all sell orders
orders = get_sell_orders()

# 2. Analyze prices by credit class
prices_by_class = {{}}
for order in orders:
    class_id = order.get('batch_key', {{}}).get('class_id', 'unknown')
    # Aggregate prices...
```

**🔬 Path 3: Credit Class Investigation**
Deep dive into methodologies:
```python
# 1. List all credit classes
classes = get_credit_classes()

# 2. Pick one to explore
class_info = get_credit_class('C01')

# 3. Find all projects using this methodology
projects = get_projects_by_class('C01')
```

**💡 Pro Tips:**
• Start with `get_credit_classes()` to understand available carbon credit types
• Use `get_all_projects()` to browse real-world ecological initiatives
• Check `get_sell_orders()` for current market prices and liquidity
• Each credit batch has a unique denom that tracks its lifecycle

**🔍 Common Queries:**

**Find US-based reforestation projects:**
```python
projects = get_projects_by_class('C01')
us_projects = [p for p in projects if 'US' in p.get('jurisdiction', '')]
```

**Calculate total carbon credits issued:**
```python
batches = get_all_batches()
total_credits = sum(float(b.get('total_amount', 0)) for b in batches)
```

**Check credit retirement rates:**
```python
batch = get_batch('batch_denom')
supply = get_batch_supply('batch_denom')
retirement_rate = supply['retired_amount'] / supply['total_amount']
```

What aspect of Regen Network would you like to explore first?"""
