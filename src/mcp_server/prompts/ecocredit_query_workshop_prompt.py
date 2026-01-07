"""Eco credit query workshop prompt implementation."""

from typing import Optional


async def ecocredit_query_workshop(focus_area: Optional[str] = None) -> str:
    """
    Interactive guide for eco credit module queries.
    Provides detailed exploration paths for carbon credits and ecological assets.
    """
    
    # Customize based on focus area
    if focus_area == "credits":
        focus_section = """
**🎯 Focus: Credit Analysis**
You're interested in understanding carbon credits. Let's explore:
• Credit issuance and retirement mechanics
• Supply dynamics and circulation
• Credit provenance and verification
"""
    elif focus_area == "projects":
        focus_section = """
**🎯 Focus: Project Analysis**
You want to explore ecological projects. Let's discover:
• Project locations and jurisdictions
• Credit generation history
• Project metadata and documentation
"""
    elif focus_area == "trading":
        focus_section = """
**🎯 Focus: Trading & Markets**
You're interested in carbon credit trading. Let's analyze:
• Current market prices and liquidity
• Trading volume and patterns
• Seller and buyer activity
"""
    else:
        focus_section = """
**🎯 Focus: General Exploration**
Let's explore all aspects of Regen's ecological credit system!
"""

    return f"""💚 **Eco Credit Query Workshop**

{focus_section}

**📚 Understanding Regen's Credit System:**

The eco credit module manages tokenized ecological assets representing real-world environmental benefits.

**🌍 Key Concepts:**
• **Credit Class**: Methodology / program definition (e.g., C01 = Verified Carbon Standard)
• **Project**: Real-world initiative generating credits (e.g., a forest in Costa Rica)
• **Batch**: Specific issuance of credits with vintage period
• **Denom**: Unique identifier for each credit batch

---

## 📋 **Credit Classes** - The Foundation

Credit classes define HOW ecological benefits are measured and verified.

**Basic Queries:**
```python
# List all credit classes (names are resolved from on-chain metadata IRIs)
result = list_classes(limit=100, offset=0)
for cls in result.get("classes", []):
    print(f"{{cls['id']}}: {{cls.get('name')}}")

# Filter down to one class by ID
c01 = next((c for c in result.get("classes", []) if c.get("id") == "C01"), None)
print(c01)
```

**Common Credit Classes:**
• **C01**: Verified Carbon Standard
• **C02**: Urban Forest Carbon Credit Class (source registry: City Forest Credits)
• **C07**: CarbonPlus Grasslands Credit Class

---

## 🌳 **Projects** - Real-World Impact

Projects are where credits are actually generated through ecological action.

**Project Discovery:**
```python
# Browse all projects
all_projects = get_all_projects()
print(f"Total projects: {{len(all_projects)}}")

# Filter by credit class
reforestation = get_projects_by_class('C01')
for project in reforestation:
    print(f"{{project['id']}}: {{project['name']}} in {{project['jurisdiction']}}")

# Deep dive into a project
project = get_project_by_id('C01-001')
print(f"Location: {{project['jurisdiction']}}")
print(f"Start Date: {{project['project_start_date']}}")
```

**Advanced Project Analysis:**
```python
# Find projects by location
def find_projects_by_location(location):
    projects = get_all_projects()
    return [p for p in projects if location in p.get('jurisdiction', '')]

us_projects = find_projects_by_location('US')
costa_rica_projects = find_projects_by_location('CR')

# Analyze project productivity
def analyze_project_credits(project_id):
    batches = get_batches_by_project(project_id)
    total_issued = sum(float(b.get('total_amount', 0)) for b in batches)
    num_issuances = len(batches)
    return {{
        'total_credits': total_issued,
        'num_batches': num_issuances,
        'avg_per_batch': total_issued / num_issuances if num_issuances > 0 else 0
    }}
```

---

## 📦 **Credit Batches** - Tokenized Carbon

Batches represent specific issuances of credits with defined vintage periods.

**Batch Queries:**
```python
# Get all batches
all_batches = get_all_batches()
print(f"Total batches issued: {{len(all_batches)}}")

# Get batches for a specific project
project_batches = get_batches_by_project('C01-001')
for batch in project_batches:
    print(f"Batch: {{batch['denom']}}")
    print(f"  Amount: {{batch['total_amount']}}")
    print(f"  Vintage: {{batch['start_date']}} to {{batch['end_date']}}")

# Analyze specific batch
batch_denom = 'C01-001-20240101-20240131-001'
batch = get_batch(batch_denom)
supply = get_batch_supply(batch_denom)
```

**Batch Analysis Patterns:**
```python
# Calculate retirement rates
def calculate_retirement_rate(batch_denom):
    supply = get_batch_supply(batch_denom)
    total = float(supply.get('total_amount', 0))
    retired = float(supply.get('retired_amount', 0))
    if total > 0:
        return (retired / total) * 100
    return 0

# Find most active batches
def find_active_batches():
    batches = get_all_batches()
    active = []
    for batch in batches:
        orders = get_sell_orders_by_batch(batch['denom'])
        if orders:
            active.append({{
                'denom': batch['denom'],
                'orders': len(orders),
                'total_for_sale': sum(float(o.get('quantity', 0)) for o in orders)
            }})
    return sorted(active, key=lambda x: x['orders'], reverse=True)
```

---

## 💰 **Balances & Supply** - Credit Holdings

Track who owns credits and overall supply dynamics.

**Balance Queries:**
```python
# Check specific address balance
address = 'regen1...'
batch_denom = 'C01-001-20240101-20240131-001'
balance = get_credit_balance(address, batch_denom)
print(f"Address holds: {{balance['tradable_amount']}} tradable credits")
print(f"Retired: {{balance['retired_amount']}} credits")

# Get batch supply breakdown
supply = get_batch_supply(batch_denom)
print(f"Total Issued: {{supply['total_amount']}}")
print(f"Tradable: {{supply['tradable_amount']}}")
print(f"Retired: {{supply['retired_amount']}}")
print(f"Cancelled: {{supply['cancelled_amount']}}")
```

---

## 🔍 **Advanced Query Patterns**

**1. Portfolio Analysis:**
```python
def analyze_address_portfolio(address):
    # Get all batches
    batches = get_all_batches()
    portfolio = []
    
    for batch in batches:
        balance = get_credit_balance(address, batch['denom'])
        if float(balance.get('tradable_amount', 0)) > 0:
            portfolio.append({{
                'batch': batch['denom'],
                'amount': balance['tradable_amount'],
                'project': batch['project_id'],
                'class': batch['class_id']
            }})
    
    return portfolio
```

**2. Credit Class Comparison:**
```python
def compare_credit_classes():
    classes = get_credit_classes()
    comparison = []
    
    for cls in classes:
        projects = get_projects_by_class(cls['id'])
        total_credits = 0
        
        for project in projects:
            batches = get_batches_by_project(project['id'])
            total_credits += sum(float(b.get('total_amount', 0)) for b in batches)
        
        comparison.append({{
            'class': cls['id'],
            'name': cls['name'],
            'num_projects': len(projects),
            'total_credits': total_credits
        }})
    
    return sorted(comparison, key=lambda x: x['total_credits'], reverse=True)
```

**3. Vintage Analysis:**
```python
def analyze_vintages(project_id):
    batches = get_batches_by_project(project_id)
    vintages = []
    
    for batch in batches:
        start = batch.get('start_date', '')
        end = batch.get('end_date', '')
        vintages.append({{
            'period': f"{{start}} to {{end}}",
            'credits': batch.get('total_amount', 0),
            'denom': batch['denom']
        }})
    
    return sorted(vintages, key=lambda x: x['period'])
```

---

## 💡 **Query Tips & Best Practices**

**Performance Tips:**
• Cache frequently accessed data like credit classes
• Batch multiple queries when analyzing portfolios
• Use project IDs instead of searching by name

**Data Interpretation:**
• Credits are typically denominated with 6 decimal places
• Vintage periods indicate when the ecological benefit occurred
• Retirement means credits have been permanently removed from circulation

**Common Workflows:**
1. **New User Exploration**: Start with credit classes → projects → batches
2. **Market Analysis**: Begin with sell orders → trace back to batches → projects
3. **Impact Assessment**: Project → batches → retirement rates

---

## 🎯 **Practice Exercises**

**Exercise 1: Find the most productive project**
```python
# Your task: Find which project has issued the most credits
# Hint: Iterate through all projects and sum their batch amounts
```

**Exercise 2: Calculate market cap by credit class**
```python
# Your task: Calculate total value of credits for sale by class
# Hint: Use sell orders and group by credit class
```

**Exercise 3: Identify recently retired credits**
```python
# Your task: Find batches with high retirement rates (>50%)
# Hint: Compare retired_amount to total_amount in supply
```

Ready to explore Regen's ecological credits? What would you like to investigate first?"""
