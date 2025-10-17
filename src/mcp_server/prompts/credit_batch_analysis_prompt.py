"""Credit batch analysis prompt implementation."""

from typing import Optional


async def credit_batch_analysis(batch_denom: Optional[str] = None) -> str:
    """
    Deep dive analysis into credit batches.
    Helps users understand specific credit issuances and their lifecycle.
    """
    
    # Customize based on whether a specific batch is provided
    if batch_denom:
        focus_section = f"""
**🎯 Focus: Batch {batch_denom}**
Let's analyze this specific credit batch in detail:
• Supply and circulation metrics
• Retirement patterns
• Market activity
• Project and vintage information
"""
    else:
        focus_section = """
**🎯 Focus: Credit Batch Analysis**
Let's explore how to analyze credit batches - the fundamental units of carbon credits on Regen Network!
"""

    return f"""📦 **Credit Batch Deep Dive**

{focus_section}

**Understanding Credit Batches:**

A credit batch represents a specific issuance of ecological credits from a project during a defined vintage period. Each batch is a unique, tradeable asset with its own lifecycle from issuance through retirement.

**Batch Anatomy:**
• **Denom**: Unique identifier (e.g., C01-001-20240101-20240131-001)
• **Project ID**: Source project (e.g., C01-001)
• **Vintage Period**: When ecological benefit occurred
• **Issuance Date**: When credits were created
• **Total Amount**: Initial credits issued
• **Supply States**: Tradable, Retired, Cancelled

---

## 🔍 **Batch Identification**

### Decoding Batch Denoms
```python
def decode_batch_denom(denom):
    \"\"\"Parse batch denom into components.\"\"\"
    # Format: PROJECT-STARTDATE-ENDDATE-SEQUENCE
    # Example: C01-001-20240101-20240131-001
    
    parts = denom.split('-')
    
    if len(parts) >= 5:
        return {{
            'class_id': parts[0],
            'project_sequence': parts[1],
            'project_id': f"{{parts[0]}}-{{parts[1]}}",
            'start_date': parts[2],
            'end_date': parts[3],
            'batch_sequence': parts[4] if len(parts) > 4 else '001',
            'full_denom': denom
        }}
    
    return {{'error': 'Invalid denom format', 'denom': denom}}

# Example
batch_info = decode_batch_denom('C01-001-20240101-20240131-001')
print(f"Project: {{batch_info['project_id']}}")
print(f"Vintage: {{batch_info['start_date']}} to {{batch_info['end_date']}}")
```

### Finding Batches
```python
# Get all batches
all_batches = get_all_batches()
print(f"Total batches on chain: {{len(all_batches)}}")

# Filter by various criteria
def find_batches_by_criteria(class_id=None, project_id=None, year=None):
    batches = get_all_batches()
    filtered = []
    
    for batch in batches:
        # Apply filters
        if class_id and not batch.get('class_id', '').startswith(class_id):
            continue
        if project_id and batch.get('project_id') != project_id:
            continue
        if year and not batch.get('start_date', '').startswith(str(year)):
            continue
        
        filtered.append(batch)
    
    return filtered

# Find all 2024 vintage batches
batches_2024 = find_batches_by_criteria(year=2024)
```

---

## 📊 **Supply Analysis**

### Supply Breakdown
```python
def analyze_batch_supply(batch_denom):
    \"\"\"Comprehensive supply analysis for a batch.\"\"\"
    
    # Get batch details and supply
    batch = get_batch(batch_denom)
    supply = get_batch_supply(batch_denom)
    
    # Calculate percentages
    total = float(supply.get('total_amount', 0))
    tradable = float(supply.get('tradable_amount', 0))
    retired = float(supply.get('retired_amount', 0))
    cancelled = float(supply.get('cancelled_amount', 0))
    
    tradable_pct = (tradable / total * 100) if total > 0 else 0
    retired_pct = (retired / total * 100) if total > 0 else 0
    cancelled_pct = (cancelled / total * 100) if total > 0 else 0
    
    print(f"=== Supply Analysis: {{batch_denom}} ===")
    print(f"Total Issued: {{total:,.0f}} credits")
    print(f"")
    print(f"Current State:")
    print(f"  Tradable: {{tradable:,.0f}} ({{tradable_pct:.1f}}%)")
    print(f"  Retired: {{retired:,.0f}} ({{retired_pct:.1f}}%)")
    print(f"  Cancelled: {{cancelled:,.0f}} ({{cancelled_pct:.1f}}%)")
    print(f"")
    print(f"Retirement Rate: {{retired_pct:.1f}}%")
    print(f"Active Circulation: {{tradable_pct:.1f}}%")
    
    return {{
        'total': total,
        'tradable': tradable,
        'retired': retired,
        'cancelled': cancelled,
        'retirement_rate': retired_pct,
        'circulation_rate': tradable_pct
    }}

# Analyze specific batch
supply_stats = analyze_batch_supply('C01-001-20240101-20240131-001')
```

### Supply Trends
```python
def analyze_retirement_trends(project_id):
    \"\"\"Analyze retirement patterns across project batches.\"\"\"
    
    batches = get_batches_by_project(project_id)
    retirement_data = []
    
    for batch in batches:
        supply = get_batch_supply(batch['denom'])
        
        total = float(supply.get('total_amount', 0))
        retired = float(supply.get('retired_amount', 0))
        retirement_rate = (retired / total * 100) if total > 0 else 0
        
        retirement_data.append({{
            'batch': batch['denom'],
            'vintage': f"{{batch.get('start_date', '')}} to {{batch.get('end_date', '')}}",
            'total': total,
            'retired': retired,
            'rate': retirement_rate
        }})
    
    # Sort by vintage
    retirement_data.sort(key=lambda x: x['vintage'])
    
    # Calculate averages
    avg_rate = sum(b['rate'] for b in retirement_data) / len(retirement_data) if retirement_data else 0
    
    print(f"=== Retirement Trends: {{project_id}} ===")
    print(f"Average Retirement Rate: {{avg_rate:.1f}}%")
    print(f"")
    print("Vintage | Retirement Rate")
    print("--------|----------------")
    for batch in retirement_data:
        print(f"{{batch['vintage'][:7]}}... | {{batch['rate']:>6.1f}}%")
    
    return retirement_data
```

---

## 💼 **Holder Analysis**

### Distribution Analysis
```python
def analyze_batch_holders(batch_denom, top_n=10):
    \"\"\"Analyze credit distribution among holders.\"\"\"
    
    # Note: This would require querying all addresses
    # Simplified example showing the pattern
    
    holders = []  # Would be populated with actual holder data
    
    # Example holder analysis structure
    holder_analysis = {{
        'batch': batch_denom,
        'unique_holders': len(holders),
        'concentration': 0,  # Top 10 holders percentage
        'largest_holder': None,
        'distribution': 'even'  # even, concentrated, highly_concentrated
    }}
    
    # Classification based on concentration
    if holder_analysis['concentration'] > 80:
        holder_analysis['distribution'] = 'highly_concentrated'
    elif holder_analysis['concentration'] > 50:
        holder_analysis['distribution'] = 'concentrated'
    
    return holder_analysis
```

---

## 📈 **Market Integration**

### Batch Market Activity
```python
def analyze_batch_market(batch_denom):
    \"\"\"Analyze market activity for a specific batch.\"\"\"
    
    # Get batch info
    batch = get_batch(batch_denom)
    supply = get_batch_supply(batch_denom)
    
    # Get market orders
    orders = get_sell_orders_by_batch(batch_denom)
    
    if not orders:
        return {{
            'status': 'Not on market',
            'batch': batch_denom,
            'tradable_supply': supply.get('tradable_amount', 0)
        }}
    
    # Analyze orders
    total_for_sale = sum(float(o.get('quantity', 0)) for o in orders)
    prices = [float(o.get('ask_price', 0)) for o in orders]
    
    tradable = float(supply.get('tradable_amount', 0))
    market_depth = (total_for_sale / tradable * 100) if tradable > 0 else 0
    
    return {{
        'batch': batch_denom,
        'status': 'Active on market',
        'num_orders': len(orders),
        'total_for_sale': total_for_sale,
        'tradable_supply': tradable,
        'market_depth_pct': market_depth,
        'price_range': {{
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'avg': sum(prices) / len(prices) if prices else 0
        }},
        'sellers': list(set(o.get('seller', '') for o in orders))
    }}

# Check market presence
market_status = analyze_batch_market('C01-001-20240101-20240131-001')
print(f"Market Status: {{market_status['status']}}")
if market_status['num_orders']:
    print(f"Orders: {{market_status['num_orders']}}")
    print(f"For Sale: {{market_status['total_for_sale']:,.0f}} ({{market_status['market_depth_pct']:.1f}}% of tradable)")
```

---

## 🔬 **Batch Comparison**

### Compare Multiple Batches
```python
def compare_batches(batch_denoms):
    \"\"\"Compare multiple batches side by side.\"\"\"
    
    comparison = []
    
    for denom in batch_denoms:
        batch = get_batch(denom)
        supply = get_batch_supply(denom)
        orders = get_sell_orders_by_batch(denom)
        
        # Calculate metrics
        total = float(supply.get('total_amount', 0))
        retired_pct = (float(supply.get('retired_amount', 0)) / total * 100) if total > 0 else 0
        
        comparison.append({{
            'denom': denom,
            'project': batch.get('project_id', 'Unknown'),
            'vintage_start': batch.get('start_date', 'Unknown'),
            'total_amount': total,
            'retirement_rate': retired_pct,
            'on_market': len(orders) > 0,
            'num_orders': len(orders)
        }})
    
    # Sort by total amount
    comparison.sort(key=lambda x: x['total_amount'], reverse=True)
    
    print("Batch Comparison")
    print("=" * 60)
    for batch in comparison:
        print(f"{{batch['denom'][:30]}}...")
        print(f"  Total: {{batch['total_amount']:,.0f}} | Retired: {{batch['retirement_rate']:.1f}}%")
        print(f"  Market: {{'Yes' if batch['on_market'] else 'No'}} ({{batch['num_orders']}} orders)")
        print()
    
    return comparison
```

### Vintage Performance
```python
def analyze_vintage_performance(class_id, year):
    \"\"\"Compare all batches from a specific vintage year.\"\"\"
    
    # Find all batches from this vintage
    all_batches = get_all_batches()
    vintage_batches = []
    
    for batch in all_batches:
        if (batch.get('class_id', '') == class_id and 
            batch.get('start_date', '').startswith(str(year))):
            vintage_batches.append(batch)
    
    # Analyze performance
    total_issued = 0
    total_retired = 0
    market_active = 0
    
    for batch in vintage_batches:
        supply = get_batch_supply(batch['denom'])
        orders = get_sell_orders_by_batch(batch['denom'])
        
        total_issued += float(supply.get('total_amount', 0))
        total_retired += float(supply.get('retired_amount', 0))
        
        if orders:
            market_active += 1
    
    retirement_rate = (total_retired / total_issued * 100) if total_issued > 0 else 0
    market_participation = (market_active / len(vintage_batches) * 100) if vintage_batches else 0
    
    print(f"=== {{class_id}} Vintage {{year}} Performance ===")
    print(f"Total Batches: {{len(vintage_batches)}}")
    print(f"Total Credits: {{total_issued:,.0f}}")
    print(f"Retirement Rate: {{retirement_rate:.1f}}%")
    print(f"Market Active: {{market_participation:.1f}}% of batches")
    
    return {{
        'vintage': f"{{class_id}}-{{year}}",
        'batch_count': len(vintage_batches),
        'total_credits': total_issued,
        'retirement_rate': retirement_rate,
        'market_participation': market_participation
    }}
```

---

## 🎯 **Advanced Batch Analytics**

### Lifecycle Tracking
```python
def track_batch_lifecycle(batch_denom):
    \"\"\"Track complete lifecycle of a credit batch.\"\"\"
    
    batch = get_batch(batch_denom)
    supply = get_batch_supply(batch_denom)
    
    # Calculate age (simplified)
    issuance_date = batch.get('issuance_date', '')
    
    lifecycle = {{
        'batch': batch_denom,
        'stages': {{
            'issued': {{
                'date': issuance_date,
                'amount': batch.get('total_amount', 0)
            }},
            'current': {{
                'tradable': supply.get('tradable_amount', 0),
                'retired': supply.get('retired_amount', 0),
                'cancelled': supply.get('cancelled_amount', 0)
            }},
            'market': {{
                'first_listing': None,  # Would need historical data
                'current_orders': len(get_sell_orders_by_batch(batch_denom))
            }}
        }}
    }}
    
    return lifecycle
```

### Price Discovery
```python
def analyze_batch_pricing(batch_denom):
    \"\"\"Analyze pricing for a specific batch.\"\"\"
    
    orders = get_sell_orders_by_batch(batch_denom)
    
    if not orders:
        return {{'status': 'No pricing data available'}}
    
    prices = [float(o.get('ask_price', 0)) for o in orders]
    quantities = [float(o.get('quantity', 0)) for o in orders]
    
    # Volume-weighted average price
    vwap = sum(p * q for p, q in zip(prices, quantities)) / sum(quantities) if quantities else 0
    
    # Price distribution
    price_distribution = {{
        'min': min(prices),
        'max': max(prices),
        'avg': sum(prices) / len(prices),
        'vwap': vwap,
        'spread': max(prices) - min(prices),
        'spread_pct': ((max(prices) - min(prices)) / min(prices) * 100) if min(prices) > 0 else 0
    }}
    
    print(f"=== Price Analysis: {{batch_denom[:30]}}... ===")
    print(f"Price Range: ${{price_distribution['min']:.2f}} - ${{price_distribution['max']:.2f}}")
    print(f"Average: ${{price_distribution['avg']:.2f}}")
    print(f"VWAP: ${{price_distribution['vwap']:.2f}}")
    print(f"Spread: {{price_distribution['spread_pct']:.1f}}%")
    
    return price_distribution
```

---

## 💡 **Batch Analysis Best Practices**

**Key Metrics to Track:**
• **Retirement Rate**: Indicates actual environmental impact
• **Market Depth**: Percentage of tradable supply on market
• **Price Stability**: Spread between min and max prices
• **Holder Concentration**: Distribution of ownership

**Analysis Workflow:**
1. Identify batch using denom
2. Check supply status and retirement rate
3. Analyze market activity if applicable
4. Compare with similar vintages
5. Track trends over time

**Red Flags:**
• Very high retirement rate (might indicate low tradability)
• No market activity despite tradable supply
• Extreme price spreads
• Single holder concentration

Ready to analyze credit batches? Which batch or vintage would you like to explore?"""