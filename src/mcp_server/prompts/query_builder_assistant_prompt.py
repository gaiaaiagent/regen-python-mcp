"""Query builder assistant prompt implementation."""

from typing import Optional


async def query_builder_assistant(query_type: Optional[str] = None) -> str:
    """
    Help users build complex queries step by step.
    Provides templates and patterns for common query scenarios.
    """
    
    # Customize based on query type
    if query_type == "aggregation":
        focus_section = """
**🎯 Focus: Aggregation Queries**
Let's build queries that combine and summarize data:
• Summing credits across projects
• Averaging prices by class
• Grouping and counting
"""
    elif query_type == "filtering":
        focus_section = """
**🎯 Focus: Filtering Queries**
Let's create precise data filters:
• Location-based filtering
• Date range selection
• Multi-criteria combinations
"""
    elif query_type == "analysis":
        focus_section = """
**🎯 Focus: Analysis Queries**
Let's build analytical queries:
• Correlation analysis
• Trend detection
• Performance metrics
"""
    else:
        focus_section = """
**🎯 General Query Building**
Let me help you construct effective queries for Regen Network data!
"""

    return f"""🛠️ **Query Builder Assistant**

{focus_section}

**Query Building Fundamentals:**

Every good query follows a pattern:
1. **Define your goal** - What question are you answering?
2. **Identify data sources** - Which endpoints do you need?
3. **Apply filters** - Narrow down to relevant data
4. **Transform/Calculate** - Process the raw data
5. **Format output** - Present results clearly

---

## 📋 **Query Templates**

### **Template 1: Find and Filter**
```python
def find_filtered_data(filter_criteria):
    \"\"\"Basic pattern for finding data with filters.\"\"\"
    
    # Step 1: Get all data
    all_data = get_all_projects()  # or get_all_batches(), etc.
    
    # Step 2: Apply filters
    filtered = []
    for item in all_data:
        # Check each criterion
        if meets_criteria(item, filter_criteria):
            filtered.append(item)
    
    # Step 3: Return results
    return filtered

# Example: Find US projects with C01 methodology
def find_us_reforestation():
    projects = get_all_projects()
    results = []
    
    for project in projects:
        if ('US' in project.get('jurisdiction', '') and 
            project.get('class_id', '') == 'C01'):
            results.append(project)
    
    return results
```

### **Template 2: Aggregate and Summarize**
```python
def aggregate_data(group_by_field):
    \"\"\"Pattern for grouping and aggregating data.\"\"\"
    
    # Step 1: Get data
    data = get_all_batches()
    
    # Step 2: Group
    grouped = {{}}
    for item in data:
        key = item.get(group_by_field, 'unknown')
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    # Step 3: Aggregate
    summary = {{}}
    for key, items in grouped.items():
        summary[key] = {{
            'count': len(items),
            'total': sum(float(i.get('total_amount', 0)) for i in items)
        }}
    
    return summary

# Example: Credits by project
def credits_by_project():
    batches = get_all_batches()
    by_project = {{}}
    
    for batch in batches:
        project_id = batch.get('project_id', 'unknown')
        amount = float(batch.get('total_amount', 0))
        
        if project_id not in by_project:
            by_project[project_id] = 0
        by_project[project_id] += amount
    
    return by_project
```

### **Template 3: Join and Enrich**
```python
def join_data_sources():
    \"\"\"Pattern for combining data from multiple sources.\"\"\"
    
    # Step 1: Get primary data
    projects = get_all_projects()
    
    # Step 2: Enrich with related data
    enriched = []
    for project in projects:
        # Get related batches
        batches = get_batches_by_project(project['id'])
        
        # Calculate additional fields
        total_credits = sum(float(b.get('total_amount', 0)) for b in batches)
        
        # Combine
        enriched_project = {{
            **project,  # Original project data
            'total_credits': total_credits,
            'num_batches': len(batches)
        }}
        enriched.append(enriched_project)
    
    return enriched
```

---

## 🔍 **Common Query Patterns**

### **Pattern 1: Multi-Step Analysis**
```python
def comprehensive_project_analysis(project_id):
    \"\"\"Multi-step query building example.\"\"\"
    
    analysis = {{}}
    
    # Step 1: Get basic info
    project = get_project_by_id(project_id)
    analysis['project_info'] = project
    
    # Step 2: Get credit history
    batches = get_batches_by_project(project_id)
    analysis['credit_history'] = {{
        'total_batches': len(batches),
        'total_credits': sum(float(b.get('total_amount', 0)) for b in batches)
    }}
    
    # Step 3: Check market activity
    market_activity = []
    for batch in batches:
        orders = get_sell_orders_by_batch(batch['denom'])
        if orders:
            market_activity.append({{
                'batch': batch['denom'],
                'orders': len(orders)
            }})
    analysis['market_presence'] = market_activity
    
    # Step 4: Calculate metrics
    analysis['metrics'] = {{
        'avg_batch_size': analysis['credit_history']['total_credits'] / len(batches) if batches else 0,
        'market_participation': len(market_activity) / len(batches) * 100 if batches else 0
    }}
    
    return analysis
```

### **Pattern 2: Conditional Aggregation**
```python
def conditional_aggregation():
    \"\"\"Aggregate with conditions.\"\"\"
    
    orders = get_sell_orders()
    
    # Group by condition
    high_value = []
    low_value = []
    
    for order in orders:
        price = float(order.get('ask_price', 0))
        if price > 50:
            high_value.append(order)
        else:
            low_value.append(order)
    
    return {{
        'high_value': {{
            'count': len(high_value),
            'total_volume': sum(float(o.get('quantity', 0)) for o in high_value),
            'avg_price': sum(float(o.get('ask_price', 0)) for o in high_value) / len(high_value) if high_value else 0
        }},
        'low_value': {{
            'count': len(low_value),
            'total_volume': sum(float(o.get('quantity', 0)) for o in low_value),
            'avg_price': sum(float(o.get('ask_price', 0)) for o in low_value) / len(low_value) if low_value else 0
        }}
    }}
```

### **Pattern 3: Time-Based Filtering**
```python
def time_based_query(start_date, end_date):
    \"\"\"Filter by date ranges.\"\"\"
    
    batches = get_all_batches()
    filtered = []
    
    for batch in batches:
        batch_start = batch.get('start_date', '')
        batch_end = batch.get('end_date', '')
        
        # Check if batch overlaps with date range
        if batch_start >= start_date and batch_end <= end_date:
            filtered.append(batch)
    
    return filtered

# Example: Get 2024 Q1 batches
q1_2024 = time_based_query('2024-01-01', '2024-03-31')
```

---

## 🎨 **Query Optimization Tips**

### **Performance Best Practices**
```python
# ❌ Inefficient: Multiple calls in loop
for project_id in project_ids:
    project = get_project_by_id(project_id)  # API call each iteration
    # Process...

# ✅ Efficient: Single call with filtering
all_projects = get_all_projects()  # One API call
relevant_projects = [p for p in all_projects if p['id'] in project_ids]
```

### **Error Handling**
```python
def safe_query(query_func, *args, **kwargs):
    \"\"\"Wrapper for safe query execution.\"\"\"
    try:
        result = query_func(*args, **kwargs)
        
        # Check for empty results
        if not result:
            return {{'status': 'no_data', 'result': []}}
        
        return {{'status': 'success', 'result': result}}
        
    except Exception as e:
        return {{'status': 'error', 'message': str(e)}}

# Usage
result = safe_query(get_project_by_id, 'C01-001')
if result['status'] == 'success':
    project = result['result']
```

### **Data Validation**
```python
def validate_and_process(data):
    \"\"\"Validate data before processing.\"\"\"
    
    # Check required fields
    required_fields = ['id', 'total_amount', 'project_id']
    
    valid_items = []
    invalid_items = []
    
    for item in data:
        if all(field in item for field in required_fields):
            valid_items.append(item)
        else:
            invalid_items.append(item)
    
    if invalid_items:
        print(f"Warning: {{len(invalid_items)}} items missing required fields")
    
    return valid_items
```

---

## 📊 **Complex Query Examples**

### **Example 1: Market Arbitrage Finder**
```python
def find_arbitrage_opportunities(min_spread_pct=10):
    \"\"\"Find price disparities in the market.\"\"\"
    
    # Get all orders
    orders = get_sell_orders()
    
    # Group by credit class and vintage
    grouped = {{}}
    
    for order in orders:
        # Get batch details for classification
        batch = get_batch(order['batch_key']['batch_denom'])
        
        # Create grouping key
        key = f"{{batch.get('class_id', '')}}-{{batch.get('start_date', '')[:7]}}"
        
        if key not in grouped:
            grouped[key] = []
        
        grouped[key].append({{
            'order_id': order['id'],
            'price': float(order.get('ask_price', 0)),
            'quantity': float(order.get('quantity', 0)),
            'seller': order.get('seller', '')
        }})
    
    # Find opportunities
    opportunities = []
    
    for key, orders_group in grouped.items():
        if len(orders_group) > 1:
            prices = [o['price'] for o in orders_group]
            min_price = min(prices)
            max_price = max(prices)
            spread = max_price - min_price
            spread_pct = (spread / min_price * 100) if min_price > 0 else 0
            
            if spread_pct >= min_spread_pct:
                opportunities.append({{
                    'credit_type': key,
                    'min_price': min_price,
                    'max_price': max_price,
                    'spread': spread,
                    'spread_pct': spread_pct,
                    'order_count': len(orders_group),
                    'total_volume': sum(o['quantity'] for o in orders_group)
                }})
    
    # Sort by spread percentage
    opportunities.sort(key=lambda x: x['spread_pct'], reverse=True)
    
    return opportunities
```

### **Example 2: Portfolio Optimizer**
```python
def optimize_portfolio(budget, risk_tolerance='medium'):
    \"\"\"Build optimal credit portfolio within budget.\"\"\"
    
    # Define risk profiles
    risk_profiles = {{
        'low': {{'max_price': 30, 'min_projects': 5}},
        'medium': {{'max_price': 50, 'min_projects': 3}},
        'high': {{'max_price': 100, 'min_projects': 1}}
    }}
    
    profile = risk_profiles.get(risk_tolerance, risk_profiles['medium'])
    
    # Get available orders
    orders = get_sell_orders()
    
    # Filter by risk profile
    eligible_orders = [
        o for o in orders 
        if float(o.get('ask_price', 0)) <= profile['max_price']
    ]
    
    # Sort by price (cheapest first)
    eligible_orders.sort(key=lambda x: float(x.get('ask_price', 0)))
    
    # Build portfolio
    portfolio = []
    spent = 0
    projects_included = set()
    
    for order in eligible_orders:
        price = float(order.get('ask_price', 0))
        quantity = float(order.get('quantity', 0))
        cost = price * quantity
        
        # Check budget constraint
        if spent + cost <= budget:
            # Get project for diversity check
            batch = get_batch(order['batch_key']['batch_denom'])
            project_id = batch.get('project_id', '')
            
            portfolio.append({{
                'order_id': order['id'],
                'batch': order['batch_key']['batch_denom'],
                'project': project_id,
                'quantity': quantity,
                'price': price,
                'cost': cost
            }})
            
            spent += cost
            projects_included.add(project_id)
            
            # Check if we've met diversity requirement
            if len(projects_included) >= profile['min_projects']:
                if spent >= budget * 0.8:  # Use at least 80% of budget
                    break
    
    return {{
        'portfolio': portfolio,
        'total_cost': spent,
        'total_credits': sum(p['quantity'] for p in portfolio),
        'avg_price': spent / sum(p['quantity'] for p in portfolio) if portfolio else 0,
        'num_projects': len(projects_included),
        'budget_utilization': (spent / budget * 100) if budget > 0 else 0
    }}
```

---

## 💡 **Query Building Checklist**

Before running your query, check:

✅ **Goal Definition**
- [ ] Clear question to answer
- [ ] Expected output format defined
- [ ] Success criteria established

✅ **Data Sources**
- [ ] All required endpoints identified
- [ ] API call sequence planned
- [ ] Data relationships understood

✅ **Performance**
- [ ] Minimal API calls
- [ ] Early filtering applied
- [ ] Caching considered

✅ **Error Handling**
- [ ] Empty result handling
- [ ] Invalid data handling
- [ ] Exception catching

✅ **Output**
- [ ] Clear result structure
- [ ] Meaningful field names
- [ ] Appropriate data types

---

## 🎯 **Practice Exercises**

**Exercise 1: Build a Location Filter**
```python
# Task: Create a function that finds all projects in a specific country
# Requirements: Handle different jurisdiction formats
# Bonus: Support multiple countries
```

**Exercise 2: Create a Price Analyzer**
```python
# Task: Build a query that analyzes price trends over time
# Requirements: Group by month, calculate averages
# Bonus: Identify outliers
```

**Exercise 3: Design a Credit Tracker**
```python
# Task: Track credit lifecycle from issuance to retirement
# Requirements: Show all states, calculate rates
# Bonus: Predict retirement timeline
```

Need help building a specific query? Describe what you're trying to achieve!"""