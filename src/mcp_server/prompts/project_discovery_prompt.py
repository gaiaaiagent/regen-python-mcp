"""Project discovery prompt implementation."""

from typing import Optional, Dict, Any


async def project_discovery(criteria: Optional[Dict[str, Any]] = None) -> str:
    """
    Guide users through project discovery and analysis.
    Helps explore ecological projects generating carbon credits.
    """
    
    # Customize based on search criteria
    if criteria:
        if criteria.get("location"):
            focus_section = f"""
**🎯 Focus: Projects in {criteria['location']}**
You're looking for projects in a specific location. Let's find:
• All projects in {criteria['location']}
• Their credit generation history
• Market activity for these projects
"""
        elif criteria.get("credit_class"):
            focus_section = f"""
**🎯 Focus: {criteria['credit_class']} Projects**
You're interested in projects using a specific methodology. Let's explore:
• All {criteria['credit_class']} projects
• Their performance metrics
• Credit issuance patterns
"""
        else:
            focus_section = """
**🎯 Custom Search Criteria**
Let's find projects matching your specific requirements!
"""
    else:
        focus_section = """
**🎯 Open Project Discovery**
Let's explore all ecological projects on Regen Network!
"""

    return f"""🌿 **Regen Project Discovery Session**

{focus_section}

**🌍 Understanding Regen Projects:**

Projects are real-world ecological initiatives that generate carbon credits through verified environmental benefits. Each project represents actual on-the-ground work like reforestation, soil improvement, or ecosystem restoration.

**Project Components:**
• **Project ID**: Unique identifier (e.g., C01-001)
• **Credit Class**: Methodology used (e.g., C01 for reforestation)
• **Jurisdiction**: Geographic location
• **Reference ID**: External registry reference
• **Metadata**: Additional project documentation

---

## 🔍 **Discovery Methods**

### 1. Browse All Projects
```python
# Get complete project list
projects = get_all_projects()
print(f"Total projects on Regen: {{len(projects)}}")

# Quick overview
for project in projects[:10]:  # First 10 projects
    print(f"{{project['id']}}: {{project.get('name', 'Unnamed')}}")
    print(f"  Location: {{project.get('jurisdiction', 'Unknown')}}")
    print(f"  Class: {{project.get('class_id', 'Unknown')}}")
```

### 2. Filter by Credit Class
```python
# Find all reforestation projects (C01)
reforestation = get_projects_by_class('C01')
print(f"Reforestation projects: {{len(reforestation)}}")

# Find soil carbon projects (C02)
soil_carbon = get_projects_by_class('C02')
print(f"Soil carbon projects: {{len(soil_carbon)}}")

# Compare methodologies
def compare_project_classes():
    classes = get_credit_classes()
    comparison = []
    
    for cls in classes:
        projects = get_projects_by_class(cls['id'])
        comparison.append({{
            'class': cls['id'],
            'name': cls.get('name', 'Unknown'),
            'project_count': len(projects)
        }})
    
    return sorted(comparison, key=lambda x: x['project_count'], reverse=True)
```

### 3. Geographic Search
```python
def find_projects_by_location(location_code):
    \"\"\"Find projects in specific geographic regions.\"\"\"
    all_projects = get_all_projects()
    
    matching = []
    for project in all_projects:
        jurisdiction = project.get('jurisdiction', '')
        
        # Check various location formats
        if location_code.upper() in jurisdiction.upper():
            matching.append(project)
    
    return matching

# Example searches
us_projects = find_projects_by_location('US')
costa_rica = find_projects_by_location('CR')
california = find_projects_by_location('US-CA')

print(f"US Projects: {{len(us_projects)}}")
print(f"Costa Rica: {{len(costa_rica)}}")
print(f"California: {{len(california)}}")
```

---

## 📋 **Project Analysis Workflow**

### Step 1: Project Details
```python
def analyze_project(project_id):
    \"\"\"Deep dive into a specific project.\"\"\"
    
    # Get project details
    project = get_project_by_id(project_id)
    
    print(f"=== Project Analysis: {{project_id}} ===")
    print(f"Name: {{project.get('name', 'N/A')}}")
    print(f"Credit Class: {{project.get('class_id', 'N/A')}}")
    print(f"Location: {{project.get('jurisdiction', 'N/A')}}")
    print(f"Start Date: {{project.get('project_start_date', 'N/A')}}")
    print(f"Admin: {{project.get('admin', 'N/A')}}")
    
    # Check for external references
    if project.get('reference_id'):
        print(f"External Registry: {{project['reference_id']}}")
    
    return project

# Example
project_analysis = analyze_project('C01-001')
```

### Step 2: Credit Issuance History
```python
def analyze_project_credits(project_id):
    \"\"\"Analyze all credits issued by a project.\"\"\"
    
    batches = get_batches_by_project(project_id)
    
    if not batches:
        return {{'status': 'No credits issued yet'}}
    
    total_issued = 0
    vintage_periods = []
    
    for batch in batches:
        amount = float(batch.get('total_amount', 0))
        total_issued += amount
        
        vintage_periods.append({{
            'batch': batch['denom'],
            'amount': amount,
            'start': batch.get('start_date', 'N/A'),
            'end': batch.get('end_date', 'N/A')
        }})
    
    # Calculate statistics
    avg_batch = total_issued / len(batches) if batches else 0
    
    return {{
        'total_credits': total_issued,
        'num_batches': len(batches),
        'average_batch_size': avg_batch,
        'vintages': vintage_periods,
        'first_issuance': vintage_periods[0]['start'] if vintage_periods else None,
        'latest_issuance': vintage_periods[-1]['end'] if vintage_periods else None
    }}

# Analyze credit generation
credits = analyze_project_credits('C01-001')
print(f"Total credits issued: {{credits['total_credits']:,.0f}}")
print(f"Number of batches: {{credits['num_batches']}}")
```

### Step 3: Market Activity
```python
def analyze_project_market_activity(project_id):
    \"\"\"Check if project credits are being traded.\"\"\"
    
    batches = get_batches_by_project(project_id)
    market_activity = []
    
    for batch in batches:
        orders = get_sell_orders_by_batch(batch['denom'])
        
        if orders:
            total_for_sale = sum(float(o.get('quantity', 0)) for o in orders)
            prices = [float(o.get('ask_price', 0)) for o in orders]
            
            market_activity.append({{
                'batch': batch['denom'],
                'orders': len(orders),
                'credits_for_sale': total_for_sale,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'avg_price': sum(prices) / len(prices) if prices else 0
            }})
    
    return {{
        'active_batches': len(market_activity),
        'total_orders': sum(b['orders'] for b in market_activity),
        'details': market_activity
    }}

# Check market presence
market = analyze_project_market_activity('C01-001')
print(f"Batches on market: {{market['active_batches']}}")
print(f"Total sell orders: {{market['total_orders']}}")
```

---

## 🎯 **Advanced Discovery Patterns**

### Find High-Performance Projects
```python
def find_top_projects(limit=10):
    \"\"\"Find projects with most credits issued.\"\"\"
    
    all_projects = get_all_projects()
    project_stats = []
    
    for project in all_projects:
        batches = get_batches_by_project(project['id'])
        total_credits = sum(float(b.get('total_amount', 0)) for b in batches)
        
        if total_credits > 0:
            project_stats.append({{
                'id': project['id'],
                'name': project.get('name', 'Unnamed'),
                'location': project.get('jurisdiction', 'Unknown'),
                'class': project.get('class_id', 'Unknown'),
                'total_credits': total_credits,
                'num_batches': len(batches)
            }})
    
    # Sort by total credits
    top_projects = sorted(project_stats, key=lambda x: x['total_credits'], reverse=True)
    
    return top_projects[:limit]

# Get top 10 projects
top_10 = find_top_projects(10)
for i, project in enumerate(top_10, 1):
    print(f"{{i}}. {{project['id']}}: {{project['total_credits']:,.0f}} credits")
```

### Recent Project Activity
```python
def find_recent_projects(days=30):
    \"\"\"Find projects with recent credit issuances.\"\"\"
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_projects = []
    
    all_projects = get_all_projects()
    
    for project in all_projects:
        batches = get_batches_by_project(project['id'])
        
        for batch in batches:
            # Check if batch is recent (simplified date comparison)
            batch_date = batch.get('end_date', '')
            if batch_date > cutoff_date.isoformat()[:10]:
                recent_projects.append({{
                    'project': project['id'],
                    'batch': batch['denom'],
                    'date': batch_date,
                    'amount': batch.get('total_amount', 0)
                }})
                break  # Found recent activity, move to next project
    
    return recent_projects
```

### Project Comparison Tool
```python
def compare_projects(project_ids):
    \"\"\"Compare multiple projects side by side.\"\"\"
    
    comparison = []
    
    for project_id in project_ids:
        project = get_project_by_id(project_id)
        batches = get_batches_by_project(project_id)
        
        # Calculate metrics
        total_credits = sum(float(b.get('total_amount', 0)) for b in batches)
        
        # Check market activity
        market_orders = 0
        for batch in batches:
            orders = get_sell_orders_by_batch(batch['denom'])
            market_orders += len(orders)
        
        comparison.append({{
            'id': project_id,
            'name': project.get('name', 'Unnamed'),
            'location': project.get('jurisdiction', 'Unknown'),
            'class': project.get('class_id', 'Unknown'),
            'total_credits': total_credits,
            'num_batches': len(batches),
            'market_orders': market_orders,
            'start_date': project.get('project_start_date', 'Unknown')
        }})
    
    return comparison

# Compare specific projects
comparison = compare_projects(['C01-001', 'C01-002', 'C01-003'])
```

---

## 🌍 **Project Categories & Types**

### By Methodology
• **C01 - Reforestation**: Tree planting and forest restoration
• **C02 - Soil Carbon**: Agricultural practices for soil improvement
• **C03 - Blue Carbon**: Coastal and marine ecosystems
• **C04 - Renewable Energy**: Clean energy generation
• **BIO01 - Biodiversity**: Habitat conservation and species protection

### By Geography
• **North America**: US, Canada, Mexico
• **Central America**: Costa Rica, Panama, Guatemala
• **South America**: Brazil, Colombia, Peru
• **Europe**: Various EU countries
• **Asia-Pacific**: Australia, Indonesia, Philippines
• **Africa**: Kenya, South Africa, Ghana

### By Scale
• **Small**: < 10,000 credits/year
• **Medium**: 10,000 - 100,000 credits/year
• **Large**: > 100,000 credits/year

---

## 💡 **Discovery Tips**

**Efficient Searching:**
• Cache project lists locally to avoid repeated queries
• Use batch queries when analyzing multiple projects
• Filter early to reduce data processing

**Key Metrics to Track:**
• Credit generation rate (credits per year)
• Market liquidity (% of credits for sale)
• Price premium vs class average
• Vintage consistency

**Due Diligence Questions:**
• How long has the project been active?
• Is credit generation consistent?
• Are credits actively traded?
• What's the project's reputation?

---

## 🎯 **Practice Exercises**

**Exercise 1: Regional Analysis**
```python
# Task: Find all projects in Latin America and calculate total credits
# Hint: Check jurisdictions for country codes like CR, BR, CO, etc.
```

**Exercise 2: Methodology Comparison**
```python
# Task: Compare average project size across different credit classes
# Hint: Group projects by class and calculate average credits issued
```

**Exercise 3: Market Readiness**
```python
# Task: Find projects with credits issued but not yet on market
# Hint: Compare batches list with sell orders
```

Ready to discover ecological projects? What type of projects are you looking for?"""