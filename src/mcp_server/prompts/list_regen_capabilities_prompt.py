"""List Regen MCP capabilities prompt implementation."""


async def list_regen_capabilities() -> str:
    """
    Comprehensive list of all Regen MCP server capabilities.
    Provides a complete reference for available tools, prompts, and resources.
    """
    
    return """# 🌱 **Regen Network MCP Server - Complete Capabilities**

*Your comprehensive toolkit for exploring Regen Network's ecological credit ecosystem!*

---

## 🔧 **Tools** (44 Available Functions - Complete TypeScript Parity)

### **🏦 Bank Module (11 tools)**
Query accounts, balances, and token supply information:

• **list_accounts(limit, page)** - List all accounts on Regen Network
• **get_account(address)** - Get detailed account information by bech32 address
• **get_balance(address, denom)** - Get specific token balance for account
• **get_all_balances(address, limit, page)** - Get all token balances for account
• **get_spendable_balances(address, limit, page)** - Get spendable balances
• **get_total_supply(limit, page)** - Total supply of all denominations
• **get_supply_of(denom)** - Total supply of specific denomination
• **get_bank_params()** - Get bank module parameters and settings
• **get_denoms_metadata(limit, page)** - Get metadata for all tokens
• **get_denom_metadata(denom)** - Get metadata for specific token
• **get_denom_owners(denom, limit, page)** - Get all holders of token

### **💰 Distribution Module (9 tools)**
Query validator rewards, delegation rewards, and community pool:

• **get_distribution_params()** - Get distribution module parameters
• **get_validator_outstanding_rewards(validator_address)** - Get validator rewards
• **get_validator_commission(validator_address)** - Get validator commission
• **get_validator_slashes(validator_address, starting_height, ending_height)** - Get slash events
• **get_delegation_rewards(delegator_address, validator_address)** - Get delegation rewards
• **get_delegation_total_rewards(delegator_address)** - Get total delegation rewards
• **get_delegator_validators(delegator_address)** - Get bonded validators
• **get_delegator_withdraw_address(delegator_address)** - Get withdrawal address
• **get_community_pool()** - Get community pool balance

### **🏛️ Governance Module (8 tools)**
Access governance proposals, votes, and parameters:

• **get_governance_proposal(proposal_id)** - Get specific governance proposal
• **list_governance_proposals(limit, page, proposal_status)** - List governance proposals
• **get_governance_vote(proposal_id, voter)** - Get specific vote on proposal
• **list_governance_votes(proposal_id, limit, page)** - List votes on proposal
• **list_governance_deposits(proposal_id, limit, page)** - List proposal deposits
• **get_governance_params(params_type)** - Get governance parameters
• **get_governance_deposit(proposal_id, depositor)** - Get specific deposit
• **get_governance_tally_result(proposal_id)** - Get proposal vote tally

### **🏪 Marketplace Module (5 tools)**
Analyze carbon credit trading and market dynamics:

• **get_sell_order(sell_order_id)** - Get specific marketplace sell order
• **list_sell_orders(limit, page)** - List all active sell orders
• **list_sell_orders_by_batch(batch_denom, limit, page)** - Orders for specific batch
• **list_sell_orders_by_seller(seller, limit, page)** - Orders by seller
• **list_allowed_denoms(limit, page)** - Approved payment tokens

### **🌱 Ecocredits Module (6 tools)**
Explore credit classes, projects, and batch issuances:

• **list_credit_types()** - List all enabled credit types on Regen Network
• **list_classes(limit, offset)** - List credit class methodologies (C01, C02, etc.)
• **list_projects(limit, offset)** - List all registered ecological projects
• **list_credit_batches(limit, offset)** - List all issued credit batches
• **get_basket(basket_denom)** - Get specific basket information
• **get_basket_fee()** - Get basket creation fee

### **🗂️ Baskets Module (5 tools)**
Manage ecocredit baskets - collections of credits with unified pricing:

• **list_baskets(limit, offset)** - List all active ecocredit baskets
• **list_basket_balances(basket_denom, limit, offset)** - List credit batches in basket
• **get_basket_balance(basket_denom, batch_denom)** - Get specific batch balance in basket

---

## 📝 **Interactive Prompts** (8 Guided Workflows)

### **🔍 Exploration & Discovery**
• **chain_exploration_prompt(chain_info)** - Initial blockchain exploration guide
  - Overview of Regen Network modules and capabilities
  - Quick start commands and common queries
  - Connection setup and verification

• **project_discovery_prompt(criteria)** - Find and analyze ecological projects
  - Geographic and methodology-based search
  - Project comparison and performance metrics
  - Impact assessment workflows

### **🎓 Educational Workshops**
• **ecocredit_query_workshop_prompt(focus_area)** - Comprehensive ecocredit guide
  - Deep dive into credit classes, projects, and batches
  - Advanced query patterns and analysis techniques
  - Hands-on practice exercises with real data

• **credit_batch_analysis_prompt(batch_denom)** - Credit batch lifecycle analysis
  - Supply dynamics and retirement tracking
  - Market integration and price correlation
  - Vintage performance and impact verification

### **📈 Market Intelligence**
• **marketplace_investigation_prompt(market_focus)** - Carbon market analytics
  - Price discovery and trend analysis
  - Seller concentration and trading patterns
  - Arbitrage opportunities and risk assessment

### **🛠️ Utility & Configuration**
• **query_builder_assistant_prompt(query_type)** - Build complex queries step-by-step
  - Query composition patterns and best practices
  - Performance optimization and caching strategies
  - Error handling and troubleshooting

• **chain_config_setup_prompt()** - Chain connection configuration guide
  - RPC endpoint setup and validation
  - Network selection and connection troubleshooting
  - Environment configuration for different use cases

• **list_regen_capabilities_prompt()** - This comprehensive reference (you are here!)

---

## 🔗 **Resources** (2 Dynamic Data Sources)

• **regen://chain/config** - Real-time chain configuration and status
  - Current chain ID, RPC endpoints, and network version
  - Available modules and their operational status

• **regen://tools/summary** - Live server capability summary
  - Current tool availability and status
  - Performance metrics and cache statistics

---

## 🎯 **Quick Start Examples**

### **1. Explore Available Baskets**
```python
# List active baskets
baskets = await list_baskets_tool(limit=10, offset=0)

# Get detailed info for each basket
for basket in baskets.get('baskets', []):
    basket_info = await get_basket_tool(basket['denom'])
    balances = await list_basket_balances_tool(basket['denom'])
    print(f"Basket: {{basket_info['name']}}")
    print(f"Credits: {{len(balances.get('balances', []))}}")
```

### **2. Check Current Carbon Prices**
```python
# Get all market orders
orders = await list_sell_orders_tool(page=1, limit=100)

# Analyze prices by batch
for order in orders.get('sell_orders', []):
    batch_denom = order.get('batch_denom', '')
    price = float(order.get('ask_amount', 0))
    quantity = float(order.get('quantity', 0))
    
    print(f"Batch: {{batch_denom}}")
    print(f"Price: ${{price:.2f}}")
    print(f"Available: {{quantity:,.0f}} credits")
```

### **3. Analyze Account Holdings**
```python
# Check account balances
address = "regen1..."
balances = await get_all_balances_tool(address, page=1, limit=50)

# Filter for credit batches (contain "-" in denom)
credit_balances = []
for balance in balances.get('balances', []):
    if '-' in balance['denom']:  # Credit batch format
        credit_balances.append(balance)

print(f"Account holds {{len(credit_balances)}} credit batches")
for credit in credit_balances:
    print(f"  {{credit['denom']}}: {{credit['amount']}}")
```

### **4. Discover Projects and Classes**
```python
# Get all credit classes
classes = await list_credit_classes_tool(limit=20, offset=0)

# Get projects for each class
for class_info in classes.get('classes', []):
    class_id = class_info['id']
    print(f"Class: {{class_id}} - {{class_info.get('credit_type_abbrev', 'N/A')}}")
    
    # Get projects in this class
    projects = await list_projects_tool(limit=10, offset=0)
    class_projects = [p for p in projects.get('projects', []) 
                     if p.get('class_id') == class_id]
    
    print(f"  {{len(class_projects)}} projects in this class")
```

---

## 📊 **Common Query Patterns**

### **Portfolio Analysis**
```python
async def analyze_portfolio(address):
    # Get all balances for the address
    balances = await get_all_balances_tool(address, page=1, limit=100)
    holdings = []
    
    for balance in balances.get('balances', []):
        # Filter for credit batches (contain "-" in denom)
        if '-' in balance['denom']:
            # Try to get batch details
            batches = await list_credit_batches_tool(limit=100, offset=0)
            batch_info = next((b for b in batches.get('batches', []) 
                              if b['denom'] == balance['denom']), None)
            
            holdings.append({{
                'batch': balance['denom'],
                'amount': balance['amount'],
                'project': batch_info.get('project_id') if batch_info else 'Unknown'
            }})
    
    return holdings
```

### **Market Dashboard**
```python
async def market_overview():
    orders = await list_sell_orders_tool(page=1, limit=1000)
    order_list = orders.get('sell_orders', [])
    
    return {{
        'total_orders': len(order_list),
        'total_volume': sum(float(o.get('quantity', 0)) for o in order_list),
        'total_value': sum(
            float(o.get('quantity', 0)) * float(o.get('ask_amount', 0)) 
            for o in order_list
        ),
        'unique_sellers': len(set(o.get('seller', '') for o in order_list))
    }}
```

### **Analytics Toolkit**
```python
async def analyze_with_advanced_tools():
    # Use advanced analytics tools
    portfolio = ["regen1address1", "regen1address2"]
    impact = await analyze_portfolio_impact_tool(
        portfolio_addresses=portfolio,
        include_retired=True,
        calculate_metrics=True
    )
    
    # Market trends analysis
    trends = await analyze_market_trends_tool(
        time_period_days=30,
        credit_types=["carbon", "biodiversity"]
    )
    
    return {{
        'impact_analysis': impact,
        'market_trends': trends
    }}
```

---

## 🌍 **Credit Class Reference**

• **C01** - Carbon Sequestration through Reforestation
• **C02** - Soil Carbon Sequestration  
• **C03** - Blue Carbon (Coastal/Marine Ecosystems)
• **C04** - Avoided Emissions (Renewable Energy)
• **BIO01** - Biodiversity Conservation Credits

---

## 💡 **Pro Tips**

### **Performance**
• Cache frequently accessed data (credit classes, project lists)
• Use batch queries when analyzing multiple items
• Filter data early to reduce processing

### **Data Interpretation**
• Credits typically have 6 decimal places
• Prices are usually in USD or REGEN tokens
• Vintage periods indicate when ecological benefit occurred
• Retirement = permanent removal from circulation

### **Common Workflows**
1. **New User**: Start with `chain_exploration_prompt()`
2. **Investor**: Focus on `marketplace_investigation_prompt()`
3. **Project Developer**: Use `project_discovery_prompt()`
4. **Analyst**: Deep dive with `credit_batch_analysis_prompt()`

---

## 🔗 **Useful Resources**

• **Regen Network Docs**: https://docs.regen.network
• **Block Explorer**: https://www.mintscan.io/regen
• **Mainnet REST API**: https://rest.cosmos.directory/regen
• **Testnet Resources**: Available for development

---

## ❓ **Need Help?**

• Use `query_builder_assistant_prompt()` for help with complex queries
• Check `chain_config_setup_prompt()` for connection issues
• Explore specific areas with focused prompts

Ready to explore Regen Network? Start with any query or prompt!"""