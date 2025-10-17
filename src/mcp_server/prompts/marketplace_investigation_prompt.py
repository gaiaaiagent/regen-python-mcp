"""Marketplace investigation prompt implementation."""

from typing import Optional


async def marketplace_investigation(market_focus: Optional[str] = None) -> str:
    """
    Guide marketplace analysis and trading queries.
    Helps users understand carbon credit markets and trading dynamics.
    """
    
    # Customize based on market focus
    if market_focus == "pricing":
        focus_section = """
**🎯 Focus: Price Discovery**
You want to understand carbon credit pricing. Let's analyze:
• Current ask prices across credit classes
• Price trends and volatility
• Premium factors (vintage, location, methodology)
"""
    elif market_focus == "liquidity":
        focus_section = """
**🎯 Focus: Market Liquidity**
You're interested in market depth and trading volume. Let's explore:
• Available supply by credit class
• Order book depth
• Trading velocity and turnover
"""
    elif market_focus == "sellers":
        focus_section = """
**🎯 Focus: Seller Analysis**
You want to understand who's selling credits. Let's investigate:
• Top sellers by volume
• Seller concentration metrics
• Primary vs secondary market activity
"""
    else:
        focus_section = """
**🎯 Focus: General Market Analysis**
Let's explore all aspects of Regen's carbon credit marketplace!
"""

    return f"""🏪 **Regen Marketplace Investigation**

{focus_section}

**📈 Understanding Regen's Marketplace:**

The marketplace module enables decentralized trading of ecological credits with transparent price discovery and automatic settlement.

**Key Market Concepts:**
• **Sell Order**: Listing of credits for sale at a specific price
• **Ask Price**: Price per credit (usually in REGEN or USD)
• **Batch Key**: Identifies which credit batch is for sale
• **Expiration**: When the sell order expires
• **Maker/Taker**: Order creator vs order filler

---

## 📊 **Market Orders** - Current Listings

**Basic Market Queries:**
```python
# Get all active sell orders
all_orders = get_sell_orders()
print(f"Total active orders: {{len(all_orders)}}")

# Analyze order distribution
orders_by_status = {{'active': 0, 'partial': 0, 'expired': 0}}
for order in all_orders:
    status = 'active'  # Determine based on quantity vs quantity_filled
    orders_by_status[status] += 1

# Get orders for specific batch
batch_orders = get_sell_orders_by_batch('C01-001-20240101-20240131-001')
for order in batch_orders:
    print(f"Seller: {{order['seller']}}")
    print(f"Price: {{order['ask_price']}} per credit")
    print(f"Quantity: {{order['quantity']}}")
```

**Order Details Analysis:**
```python
# Get specific order details
order = get_sell_order('order_123')
print(f"Order ID: {{order['id']}}")
print(f"Credit Batch: {{order['batch_key']}}")
print(f"Ask Price: {{order['ask_price']}}")
print(f"Quantity Available: {{order['quantity']}}")
print(f"Expiration: {{order['expiration']}}")
```

---

## 💹 **Price Discovery** - Market Analytics

**Price Analysis Patterns:**
```python
def analyze_market_prices():
    \"\"\"Analyze current market prices by credit class.\"\"\"
    orders = get_sell_orders()
    prices_by_class = {{}}
    
    for order in orders:
        class_id = order.get('batch_key', {{}}).get('class_id', 'unknown')
        price = float(order.get('ask_price', 0))
        
        if class_id not in prices_by_class:
            prices_by_class[class_id] = []
        prices_by_class[class_id].append(price)
    
    # Calculate statistics
    price_stats = {{}}
    for class_id, prices in prices_by_class.items():
        if prices:
            price_stats[class_id] = {{
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'count': len(prices)
            }}
    
    return price_stats

# Get current price ranges
prices = analyze_market_prices()
for class_id, stats in prices.items():
    print(f"{{class_id}}: ${{stats['min']:.2f}} - ${{stats['max']:.2f}} (avg: ${{stats['avg']:.2f}})")
```

**Price Premium Analysis:**
```python
def analyze_price_premiums():
    \"\"\"Identify factors affecting credit pricing.\"\"\"
    orders = get_sell_orders()
    
    # Group by various factors
    vintage_premiums = {{}}
    location_premiums = {{}}
    
    for order in orders:
        batch = get_batch(order['batch_key']['batch_denom'])
        project = get_project_by_id(batch['project_id'])
        
        # Analyze by vintage year
        vintage_year = batch.get('start_date', '')[:4]
        if vintage_year:
            if vintage_year not in vintage_premiums:
                vintage_premiums[vintage_year] = []
            vintage_premiums[vintage_year].append(float(order['ask_price']))
        
        # Analyze by location
        location = project.get('jurisdiction', 'Unknown')
        if location not in location_premiums:
            location_premiums[location] = []
        location_premiums[location].append(float(order['ask_price']))
    
    return {{
        'vintage_analysis': vintage_premiums,
        'location_analysis': location_premiums
    }}
```

---

## 🔄 **Market Activity** - Trading Patterns

**Volume Analysis:**
```python
def calculate_market_volume():
    \"\"\"Calculate total market volume and liquidity.\"\"\"
    orders = get_sell_orders()
    
    total_volume = 0
    total_value = 0
    
    for order in orders:
        quantity = float(order.get('quantity', 0))
        price = float(order.get('ask_price', 0))
        
        total_volume += quantity
        total_value += quantity * price
    
    return {{
        'total_credits_for_sale': total_volume,
        'total_market_value': total_value,
        'average_order_size': total_volume / len(orders) if orders else 0,
        'number_of_orders': len(orders)
    }}

market_stats = calculate_market_volume()
print(f"Credits for sale: {{market_stats['total_credits_for_sale']:,.0f}}")
print(f"Total value: ${{market_stats['total_market_value']:,.2f}}")
```

**Seller Concentration:**
```python
def analyze_seller_concentration():
    \"\"\"Analyze market concentration and top sellers.\"\"\"
    orders = get_sell_orders()
    
    # Aggregate by seller
    sellers = {{}}
    for order in orders:
        seller = order.get('seller', 'unknown')
        quantity = float(order.get('quantity', 0))
        value = quantity * float(order.get('ask_price', 0))
        
        if seller not in sellers:
            sellers[seller] = {{'orders': 0, 'volume': 0, 'value': 0}}
        
        sellers[seller]['orders'] += 1
        sellers[seller]['volume'] += quantity
        sellers[seller]['value'] += value
    
    # Sort by volume
    top_sellers = sorted(sellers.items(), key=lambda x: x[1]['volume'], reverse=True)
    
    # Calculate concentration (top 5 sellers)
    total_volume = sum(s['volume'] for s in sellers.values())
    top5_volume = sum(s[1]['volume'] for s in top_sellers[:5])
    concentration = (top5_volume / total_volume * 100) if total_volume > 0 else 0
    
    return {{
        'top_sellers': top_sellers[:10],
        'total_sellers': len(sellers),
        'top5_concentration': concentration
    }}
```

---

## 📈 **Market Depth** - Order Book Analysis

**Order Book Visualization:**
```python
def build_order_book(credit_class=None):
    \"\"\"Build order book showing price levels and depth.\"\"\"
    orders = get_sell_orders()
    
    # Filter by credit class if specified
    if credit_class:
        orders = [o for o in orders if o.get('batch_key', {{}}).get('class_id') == credit_class]
    
    # Group by price level
    price_levels = {{}}
    for order in orders:
        price = float(order.get('ask_price', 0))
        quantity = float(order.get('quantity', 0))
        
        if price not in price_levels:
            price_levels[price] = {{'orders': 0, 'total_quantity': 0}}
        
        price_levels[price]['orders'] += 1
        price_levels[price]['total_quantity'] += quantity
    
    # Sort by price
    sorted_levels = sorted(price_levels.items())
    
    print("Price | Orders | Quantity")
    print("------|--------|----------")
    for price, data in sorted_levels[:10]:  # Show top 10 price levels
        print(f"${{price:>5.2f}} | {{data['orders']:>6}} | {{data['total_quantity']:>10,.0f}}")
    
    return sorted_levels
```

---

## 🎯 **Trading Strategies** - Market Opportunities

**Arbitrage Detection:**
```python
def find_arbitrage_opportunities():
    \"\"\"Find price disparities for similar credits.\"\"\"
    orders = get_sell_orders()
    
    # Group by credit class and vintage
    grouped = {{}}
    for order in orders:
        batch = get_batch(order['batch_key']['batch_denom'])
        key = f"{{batch['class_id']}}-{{batch.get('start_date', '')[:4]}}"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append({{
            'order_id': order['id'],
            'price': float(order['ask_price']),
            'quantity': float(order['quantity'])
        }})
    
    # Find spreads
    opportunities = []
    for key, orders_list in grouped.items():
        if len(orders_list) > 1:
            prices = [o['price'] for o in orders_list]
            spread = max(prices) - min(prices)
            spread_pct = (spread / min(prices) * 100) if min(prices) > 0 else 0
            
            if spread_pct > 10:  # Significant spread
                opportunities.append({{
                    'credit_type': key,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'spread_pct': spread_pct,
                    'orders': len(orders_list)
                }})
    
    return sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True)
```

**Bulk Purchase Planning:**
```python
def plan_bulk_purchase(target_credits, max_price=None):
    \"\"\"Plan optimal purchase strategy for bulk buying.\"\"\"
    orders = get_sell_orders()
    
    # Filter by max price if specified
    if max_price:
        orders = [o for o in orders if float(o['ask_price']) <= max_price]
    
    # Sort by price (cheapest first)
    orders.sort(key=lambda x: float(x['ask_price']))
    
    purchase_plan = []
    total_credits = 0
    total_cost = 0
    
    for order in orders:
        if total_credits >= target_credits:
            break
        
        quantity = min(float(order['quantity']), target_credits - total_credits)
        cost = quantity * float(order['ask_price'])
        
        purchase_plan.append({{
            'order_id': order['id'],
            'quantity': quantity,
            'price': float(order['ask_price']),
            'cost': cost
        }})
        
        total_credits += quantity
        total_cost += cost
    
    return {{
        'plan': purchase_plan,
        'total_credits': total_credits,
        'total_cost': total_cost,
        'average_price': total_cost / total_credits if total_credits > 0 else 0,
        'orders_needed': len(purchase_plan)
    }}
```

---

## 📊 **Market Insights Dashboard**

**Quick Market Overview:**
```python
def market_dashboard():
    \"\"\"Generate comprehensive market overview.\"\"\"
    orders = get_sell_orders()
    
    # Basic metrics
    total_orders = len(orders)
    total_volume = sum(float(o.get('quantity', 0)) for o in orders)
    total_value = sum(float(o.get('quantity', 0)) * float(o.get('ask_price', 0)) for o in orders)
    
    # Price metrics
    prices = [float(o.get('ask_price', 0)) for o in orders if float(o.get('ask_price', 0)) > 0]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    # Credit class breakdown
    by_class = {{}}
    for order in orders:
        class_id = order.get('batch_key', {{}}).get('class_id', 'unknown')
        if class_id not in by_class:
            by_class[class_id] = {{'orders': 0, 'volume': 0}}
        by_class[class_id]['orders'] += 1
        by_class[class_id]['volume'] += float(order.get('quantity', 0))
    
    print("=== REGEN MARKETPLACE DASHBOARD ===")
    print(f"Active Orders: {{total_orders}}")
    print(f"Total Volume: {{total_volume:,.0f}} credits")
    print(f"Market Value: ${{total_value:,.2f}}")
    print(f"Price Range: ${{min_price:.2f}} - ${{max_price:.2f}} (avg: ${{avg_price:.2f}})")
    print(f"Credit Classes: {{len(by_class)}}")
    
    return {{
        'total_orders': total_orders,
        'total_volume': total_volume,
        'total_value': total_value,
        'avg_price': avg_price,
        'price_range': (min_price, max_price),
        'by_class': by_class
    }}
```

---

## 💡 **Market Analysis Tips**

**Key Metrics to Track:**
• **Spread**: Difference between lowest and highest ask prices
• **Depth**: Total volume available at each price level
• **Velocity**: How quickly orders are filled
• **Concentration**: Market share of top sellers

**Price Factors:**
• **Vintage**: Newer vintages often command premiums
• **Location**: Developed country projects may have price premiums
• **Methodology**: Different credit classes have different values
• **Volume**: Bulk orders may negotiate discounts

**Market Patterns:**
• End of quarter often sees increased activity
• New project launches can affect class-wide pricing
• Large institutional orders move markets

Ready to investigate Regen's carbon credit marketplace? What aspect would you like to explore?"""