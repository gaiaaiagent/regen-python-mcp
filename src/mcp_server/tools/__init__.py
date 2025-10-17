"""
Complete tools module for Regen MCP server.
Includes all 44 production tools across all blockchain modules.
"""

# Basket Module Tools (5 tools)
try:
    from . import basket_tools
    from .basket_tools import (
        list_baskets,
        get_basket,
        list_basket_balances,
        get_basket_balance,
        get_basket_fee
    )
    BASKET_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Basket tools not available: {e}")
    BASKET_TOOLS_AVAILABLE = False

# Credit Module Tools (4 tools)
try:
    from . import credit_tools
    from .credit_tools import (
        list_credit_types,
        list_credit_classes,
        list_projects,
        list_credit_batches
    )
    CREDIT_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Credit tools not available: {e}")
    CREDIT_TOOLS_AVAILABLE = False

# Marketplace Module Tools (5 tools)
try:
    from . import marketplace_tools
    from .marketplace_tools import (
        get_sell_order,
        list_sell_orders,
        list_sell_orders_by_batch,
        list_sell_orders_by_seller,
        list_allowed_denoms
    )
    MARKETPLACE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Marketplace tools not available: {e}")
    MARKETPLACE_TOOLS_AVAILABLE = False

# Bank Module Tools (11 tools)
try:
    from . import bank_tools
    from .bank_tools import (
        get_balance,
        get_all_balances,
        get_spendable_balances,
        get_total_supply,
        get_supply_of
    )
    BANK_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Bank tools not available: {e}")
    BANK_TOOLS_AVAILABLE = False

# Distribution Module Tools (9 tools)
try:
    from . import distribution_tools
    DISTRIBUTION_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Distribution tools not available: {e}")
    DISTRIBUTION_TOOLS_AVAILABLE = False

# Governance Module Tools (8 tools)
try:
    from . import governance_tools
    GOVERNANCE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Governance tools not available: {e}")
    GOVERNANCE_TOOLS_AVAILABLE = False

# Analytics Tools (2 tools)
try:
    from . import analytics_tools
    from .analytics_tools import (
        analyze_portfolio_impact,
        analyze_market_trends,
        compare_credit_methodologies
    )
    ANALYTICS_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Analytics tools not available: {e}")
    ANALYTICS_TOOLS_AVAILABLE = False

# Methodology Comparison Tools (1 tool)
try:
    from . import methodology_comparison_tools
    from .methodology_comparison_tools import (
        compare_methodologies_nine_criteria,
        BUYER_PRESETS
    )
    METHODOLOGY_COMPARISON_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Methodology comparison tools not available: {e}")
    METHODOLOGY_COMPARISON_TOOLS_AVAILABLE = False

# Export Tools (1 tool)
try:
    from . import export_tools
    from .export_tools import (
        generate_comparison_onepager,
        save_report_to_file
    )
    EXPORT_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Export tools not available: {e}")
    EXPORT_TOOLS_AVAILABLE = False

# Cache Tools (3 tools)
try:
    from . import cache_tools
    from .cache_tools import (
        clear_cache,
        get_cache_stats,
        invalidate_cache_key
    )
    CACHE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Cache tools not available: {e}")
    CACHE_TOOLS_AVAILABLE = False

# Export tool modules and functions
__all__ = [
    'bank_tools',
    'distribution_tools',
    'governance_tools',
    'marketplace_tools',
    'credit_tools',
    'basket_tools',
    'analytics_tools',
    'methodology_comparison_tools',
    'export_tools',
    'cache_tools',
    # Basket functions
    'list_baskets',
    'get_basket',
    'list_basket_balances',
    'get_basket_balance',
    'get_basket_fee',
    # Credit functions
    'list_credit_types',
    'list_credit_classes',
    'list_projects',
    'list_credit_batches',
    # Marketplace functions
    'get_sell_order',
    'list_sell_orders',
    'list_sell_orders_by_batch',
    'list_sell_orders_by_seller',
    'list_allowed_denoms',
    # Bank functions
    'get_balance',
    'get_all_balances',
    'get_spendable_balances',
    'get_total_supply',
    'get_supply_of',
    # Analytics functions
    'analyze_portfolio_impact',
    'analyze_market_trends',
    'compare_credit_methodologies',
    # Methodology comparison functions
    'compare_methodologies_nine_criteria',
    'BUYER_PRESETS',
    # Export functions
    'generate_comparison_onepager',
    'save_report_to_file',
    # Cache functions
    'clear_cache',
    'get_cache_stats',
    'invalidate_cache_key'
]

def get_tool_summary():
    """Get a summary of available tool modules."""
    summary = {
        "bank_tools": BANK_TOOLS_AVAILABLE,
        "distribution_tools": DISTRIBUTION_TOOLS_AVAILABLE,
        "governance_tools": GOVERNANCE_TOOLS_AVAILABLE,
        "marketplace_tools": MARKETPLACE_TOOLS_AVAILABLE,
        "credit_tools": CREDIT_TOOLS_AVAILABLE,
        "basket_tools": BASKET_TOOLS_AVAILABLE,
        "analytics_tools": ANALYTICS_TOOLS_AVAILABLE,
        "methodology_comparison_tools": METHODOLOGY_COMPARISON_TOOLS_AVAILABLE,
        "export_tools": EXPORT_TOOLS_AVAILABLE,
        "cache_tools": CACHE_TOOLS_AVAILABLE,
    }
    return summary