"""Demo interactive prompt for showcasing Regen MCP capabilities."""

from typing import Optional
import asyncio

async def demo_interactive_prompt(demo_type: Optional[str] = None) -> str:
    """
    Interactive demo showcasing different aspects of Regen Network exploration.
    
    Args:
        demo_type: Optional focus area (quick, deep, marketplace, projects)
        
    Returns:
        Interactive prompt content with examples and guidance
    """
    
    if demo_type == "quick":
        return await _quick_demo()
    elif demo_type == "deep":
        return await _deep_dive_demo()
    elif demo_type == "marketplace":
        return await _marketplace_demo()
    elif demo_type == "projects":
        return await _projects_demo()
    else:
        return await _general_demo()

async def _general_demo() -> str:
    """General demo showcasing all capabilities."""
    return """
🌱 **Regen Network MCP Demo**

Welcome to the interactive exploration of Regen Network's ecological credit ecosystem!

---

## 🎯 **What You Can Do**

### **1. Explore Ecological Credits** 🌿
```python
# Get all credit classes (like C01, C02, etc.)
classes = get_credit_classes()

# Explore specific methodology
reforestation_projects = get_projects_by_class('C01')
```

### **2. Analyze Carbon Markets** 📈  
```python
# See what's for sale right now
orders = get_sell_orders()

# Find best prices
sorted_orders = sorted(orders, key=lambda x: float(x['ask_price']))
```

### **3. Track Real Projects** 🌍
```python
# Discover ecological projects
projects = get_all_projects()

# Analyze project impact
for project in projects:
    print(f"📍 {project['jurisdiction']}: {project['metadata']}")
```

---

## 🚀 **Interactive Demos Available**

Run these prompts for guided exploration:

• **Quick Start**: `demo_interactive_prompt("quick")` - 5 minute overview
• **Deep Dive**: `demo_interactive_prompt("deep")` - Complete analysis workflow  
• **Marketplace Focus**: `demo_interactive_prompt("marketplace")` - Trading analysis
• **Project Discovery**: `demo_interactive_prompt("projects")` - Impact exploration

---

## 💡 **Pro Tips**

1. **Start with capabilities**: `list_regen_capabilities()` to see all available tools
2. **Chain first**: `get_chain_config()` to verify connection 
3. **Explore methodically**: Use prompts to guide your exploration
4. **Real data**: All queries hit live Regen mainnet data!

**Ready to explore? Pick a demo type above or start with the tools directly!** 🌱
"""

async def _quick_demo() -> str:
    """Quick 5-minute demo."""
    return """
⚡ **Quick Start Demo** (5 minutes)

Let's get you started with Regen Network exploration!

---

## Step 1: Check Connection 🔗
```python
config = get_chain_config()
print(f"Connected to: {config['chain_id']}")
```

## Step 2: See What's Available 🔍
```python
# Credit methodologies on Regen
classes = get_credit_classes()
print(f"Found {len(classes)} credit methodologies")

# Real ecological projects  
projects = get_all_projects()
print(f"Tracking {len(projects)} projects worldwide")
```

## Step 3: Explore Marketplace 🏪
```python
# Active carbon credit listings
orders = get_sell_orders()
print(f"🛒 {len(orders)} credits available for purchase")

# Price analysis
if orders:
    prices = [float(order['ask_price']) for order in orders]
    print(f"💰 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
```

## Step 4: Dive Deeper 🌊
```python
# Pick a project to analyze
project = projects[0]
project_batches = get_project_batches(project['id'])
print(f"📊 Project {project['id']} has {len(project_batches)} credit batches")
```

**🎉 You're now ready to explore Regen Network!**

**Next Steps:**
- Run `demo_interactive_prompt("deep")` for comprehensive analysis
- Use `marketplace_investigation()` for trading insights
- Try `project_discovery()` for impact exploration
"""

async def _deep_dive_demo() -> str:
    """Deep dive comprehensive demo.""" 
    return """
🌊 **Deep Dive Demo** - Complete Analysis Workflow

Let's do a comprehensive analysis of Regen Network's ecological credit ecosystem.

---

## 🔬 **Phase 1: Ecosystem Overview**

### Credit Class Analysis
```python
# Get all methodologies
classes = get_credit_classes()

# Analyze credit types
for class_info in classes:
    print(f"🏷️ {class_info['id']}: {class_info['credit_type']['name']}")
    print(f"   Admin: {class_info['admin']}")
    
    # Get projects using this methodology
    projects = get_projects_by_class(class_info['id'])
    print(f"   📁 {len(projects)} active projects")
```

### Geographic Distribution
```python
# Analyze project locations
jurisdictions = {}
for project in projects:
    country = project.get('jurisdiction', 'Unknown')
    jurisdictions[country] = jurisdictions.get(country, 0) + 1

print("🌍 Global Distribution:")
for country, count in sorted(jurisdictions.items()):
    print(f"   {country}: {count} projects")
```

## 🔬 **Phase 2: Market Dynamics**

### Price Discovery
```python
orders = get_sell_orders()

# Group by credit class
class_prices = {}
for order in orders:
    batch_info = get_batch_info(order['batch_denom'])
    class_id = batch_info['class_id']
    price = float(order['ask_price'])
    
    if class_id not in class_prices:
        class_prices[class_id] = []
    class_prices[class_id].append(price)

# Price analysis by methodology
for class_id, prices in class_prices.items():
    avg_price = sum(prices) / len(prices)
    print(f"💰 {class_id} Average: ${avg_price:.2f} ({len(prices)} orders)")
```

### Volume Analysis  
```python
# Calculate available volume by class
total_credits = {}
for order in orders:
    batch_info = get_batch_info(order['batch_denom'])
    class_id = batch_info['class_id'] 
    volume = float(order['quantity'])
    
    total_credits[class_id] = total_credits.get(class_id, 0) + volume

print("📊 Available Volume by Credit Type:")
for class_id, volume in sorted(total_credits.items()):
    print(f"   {class_id}: {volume:,.0f} credits")
```

## 🔬 **Phase 3: Impact Assessment**

### Vintage Analysis
```python
# Analyze credit batch vintages
vintages = {}
all_batches = get_credit_batches()

for batch in all_batches:
    start_date = batch.get('start_date', '')
    year = start_date[:4] if start_date else 'Unknown'
    vintages[year] = vintages.get(year, 0) + 1

print("📅 Credit Vintages:")
for year in sorted(vintages.keys()):
    print(f"   {year}: {vintages[year]} batches")
```

### Retirement Tracking
```python
# Track retired credits (environmental benefit realized)
retired_total = 0
active_total = 0

for batch in all_batches:
    retired = float(batch.get('amount_retired', 0))
    active = float(batch.get('amount_tradable', 0))
    
    retired_total += retired
    active_total += active

total_issued = retired_total + active_total
retirement_rate = (retired_total / total_issued * 100) if total_issued > 0 else 0

print(f"🌱 Impact Summary:")
print(f"   Total Credits Issued: {total_issued:,.0f}")
print(f"   Retired (Impact Realized): {retired_total:,.0f} ({retirement_rate:.1f}%)")
print(f"   Still Tradable: {active_total:,.0f}")
```

**🎯 Analysis Complete!**

You've now analyzed:
✅ Credit methodologies and their usage
✅ Global project distribution  
✅ Market prices and liquidity
✅ Credit vintages and impact realization

**Next Level:** Use these insights for investment decisions, impact measurement, or market making strategies!
"""

async def _marketplace_demo() -> str:
    """Marketplace-focused demo."""
    return """
🏪 **Marketplace Demo** - Carbon Trading Analysis

Let's analyze Regen's decentralized carbon credit marketplace!

---

## 📊 **Order Book Analysis**

```python
# Get all active sell orders
orders = get_sell_orders()
print(f"📈 {len(orders)} active listings")

# Price distribution
prices = [float(order['ask_price']) for order in orders]
prices.sort()

print(f"💰 Price Range: ${min(prices):.2f} - ${max(prices):.2f}")
print(f"📊 Median Price: ${prices[len(prices)//2]:.2f}")

# Volume at price levels
price_levels = {}
for order in orders:
    price = f"${float(order['ask_price']):.2f}"
    volume = float(order['quantity'])
    price_levels[price] = price_levels.get(price, 0) + volume

print("🎯 Liquidity by Price:")
for price in sorted(price_levels.keys())[:5]:  # Top 5
    print(f"   {price}: {price_levels[price]:,.0f} credits")
```

## 🔍 **Arbitrage Opportunities**

```python
# Compare prices across different credit types
credit_prices = {}

for order in orders:
    # Get batch details to determine credit type
    batch_info = get_batch_info(order['batch_denom'])
    credit_class = batch_info['class_id']
    price = float(order['ask_price'])
    
    if credit_class not in credit_prices:
        credit_prices[credit_class] = []
    credit_prices[credit_class].append(price)

# Find price spreads
print("💸 Price Analysis by Credit Type:")
for class_id, prices in credit_prices.items():
    if len(prices) > 1:
        min_price = min(prices)
        max_price = max(prices)
        spread = max_price - min_price
        print(f"   {class_id}: ${min_price:.2f} - ${max_price:.2f} (spread: ${spread:.2f})")
```

## 📅 **Expiration Tracking**

```python
from datetime import datetime, timedelta

# Check order expirations
expiring_soon = []
current_time = datetime.now()

for order in orders:
    if 'expiration' in order and order['expiration']:
        # Parse expiration (format may vary)
        # This is a simplified example
        print(f"⏰ Order {order['id']}: expires {order['expiration']}")

print(f"⚠️ {len(expiring_soon)} orders expiring within 7 days")
```

## 🎯 **Trading Strategy Insights**

Based on this analysis:

**🟢 Buy Opportunities:**
- Look for orders below median price
- Consider credit types with high price spreads
- Monitor expiring orders for potential discounts

**🔴 Sell Opportunities:**  
- Price above current median
- List in credit types with limited supply
- Longer expiration times for flexibility

**📈 Market Making:**
- Identify credit types with low liquidity
- Place competitive bids below market
- Monitor for large order opportunities

**Next:** Run `get_sell_orders_by_batch()` to analyze specific credit batches!
"""

async def _projects_demo() -> str:
    """Projects-focused demo."""
    return """
🌍 **Projects Demo** - Real Environmental Impact

Let's explore the actual ecological projects creating these credits!

---

## 🌱 **Project Discovery**

```python
# Get all projects
projects = get_all_projects()
print(f"🌍 Tracking {len(projects)} ecological projects worldwide")

# Categorize by methodology
methodologies = {}
for project in projects:
    class_id = project['class_id']
    methodologies[class_id] = methodologies.get(class_id, 0) + 1

print("📊 Projects by Methodology:")
for method, count in sorted(methodologies.items()):
    print(f"   {method}: {count} projects")
```

## 🗺️ **Geographic Impact**

```python
# Map global distribution
countries = {}
for project in projects:
    country = project.get('jurisdiction', 'Unknown')
    countries[country] = countries.get(country, 0) + 1

print("🌏 Global Reach:")
for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"   {country}: {count} projects")

# Identify emerging markets
emerging = [country for country, count in countries.items() if count == 1]
print(f"🌱 {len(emerging)} countries with single projects (emerging opportunities)")
```

## 🔬 **Project Deep Dive**

```python
# Analyze a specific project
project = projects[0]
print(f"🔍 Analyzing Project: {project['id']}")
print(f"   📍 Location: {project.get('jurisdiction', 'Not specified')}")
print(f"   🏷️ Methodology: {project['class_id']}")

# Get project's credit batches
batches = get_project_batches(project['id'])
print(f"   📊 Credit Batches: {len(batches)}")

if batches:
    # Calculate total credits issued
    total_issued = sum(float(batch.get('amount_issued', 0)) for batch in batches)
    total_retired = sum(float(batch.get('amount_retired', 0)) for batch in batches)
    
    print(f"   🌱 Total Impact: {total_issued:,.0f} credits issued")
    print(f"   ✅ Realized Impact: {total_retired:,.0f} credits retired")
    
    # Vintage analysis
    vintages = [batch.get('start_date', '')[:4] for batch in batches if batch.get('start_date')]
    if vintages:
        print(f"   📅 Active Years: {min(vintages)} - {max(vintages)}")
```

## 🏆 **Impact Leaders**

```python
# Find projects with highest impact
project_impact = {}

for project in projects:
    batches = get_project_batches(project['id'])
    total_retired = sum(float(batch.get('amount_retired', 0)) for batch in batches)
    
    if total_retired > 0:
        project_impact[project['id']] = {
            'retired': total_retired,
            'country': project.get('jurisdiction', 'Unknown'),
            'class': project['class_id']
        }

# Top 5 by retired credits
top_projects = sorted(project_impact.items(), 
                     key=lambda x: x[1]['retired'], 
                     reverse=True)[:5]

print("🏆 Top Impact Projects (by credits retired):")
for project_id, data in top_projects:
    print(f"   {project_id}: {data['retired']:,.0f} retired ({data['country']}, {data['class']})")
```

## 🔮 **Future Projections**

```python
# Analyze project pipeline
active_projects = [p for p in projects if p.get('status') == 'active']
total_potential = len(active_projects) * 10000  # Rough estimate

print(f"🚀 Pipeline Analysis:")
print(f"   Active Projects: {len(active_projects)}")
print(f"   Potential Credits (est): {total_potential:,.0f}")
print(f"   Geographic Diversification: {len(countries)} countries")

# Methodology trends
newest_projects = sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
new_methodologies = set(p['class_id'] for p in newest_projects)
print(f"   🆕 Recent Methodology Focus: {', '.join(new_methodologies)}")
```

**🌱 Real Impact, Real Data**

These aren't just numbers - they represent:
- Forests being restored
- Soil carbon being sequestered  
- Marine ecosystems being protected
- Regenerative agriculture being practiced

**Next Steps:**
- Pick a project near you: Filter by jurisdiction
- Support impact: Buy credits from high-impact projects
- Track progress: Monitor project batch issuance over time
"""