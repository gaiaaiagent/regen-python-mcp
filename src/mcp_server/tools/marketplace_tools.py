"""Marketplace-related tools for Regen Network MCP server."""

import logging
from typing import Dict, Any, Union

from ..client.regen_client import get_regen_client, Pagination
from ..models.marketplace import (
    SellOrder,
    AllowedDenom,
    SellOrderResponse,
    SellOrdersResponse,
    AllowedDenomsResponse
)

logger = logging.getLogger(__name__)


async def get_sell_order(sell_order_id: Union[str, int]) -> Dict[str, Any]:
    """Retrieve a specific sell order by ID from the Regen marketplace.
    
    Args:
        sell_order_id: The unique identifier for the sell order
        
    Returns:
        dict: Response containing the sell order details including seller,
              batch information, quantity, price, and expiration.
    """
    try:
        # Validate sell order ID
        if not sell_order_id:
            raise ValueError("Sell order ID is required")
            
        # Convert to string for API call
        order_id_str = str(sell_order_id)
        
        client = get_regen_client()
        response = await client.query_sell_order(order_id_str)
        
        # Parse sell order from response
        sell_order = None
        sell_order_data = response.get("sell_order")
        if sell_order_data:
            sell_order = SellOrder(
                id=sell_order_data.get("id", ""),
                seller=sell_order_data.get("seller", ""),
                batch_denom=sell_order_data.get("batch_denom", ""),
                quantity=sell_order_data.get("quantity", "0"),
                ask_denom=sell_order_data.get("ask_denom", ""),
                ask_amount=sell_order_data.get("ask_amount", "0"),
                disable_auto_retire=sell_order_data.get("disable_auto_retire", False),
                expiration=sell_order_data.get("expiration"),
                market_id=sell_order_data.get("market_id")
            )
        
        result = SellOrderResponse(sell_order=sell_order)
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error retrieving sell order {sell_order_id}: {str(e)}")
        error_result = SellOrderResponse(
            success=False,
            error=f"Failed to query sell order {sell_order_id}: {str(e)}",
            sell_order=None
        )
        return error_result.dict()


async def list_sell_orders(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all active sell orders on the Regen marketplace.
    
    Args:
        limit: Maximum number of orders to return (1-1000, default 100)
        offset: Number of orders to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of sell orders with seller information,
              batch details, quantities, and pricing.
    """
    try:
        # Validate parameters
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
            
        client = get_regen_client()
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse,
            key=key
        )
        
        response = await client.query_sell_orders(pagination)
        
        # Parse sell orders from response
        sell_orders = []
        for order_data in response.get("sell_orders", []):
            sell_order = SellOrder(
                id=order_data.get("id", ""),
                seller=order_data.get("seller", ""),
                batch_denom=order_data.get("batch_denom", ""),
                quantity=order_data.get("quantity", "0"),
                ask_denom=order_data.get("ask_denom", ""),
                ask_amount=order_data.get("ask_amount", "0"),
                disable_auto_retire=order_data.get("disable_auto_retire", False),
                expiration=order_data.get("expiration"),
                market_id=order_data.get("market_id")
            )
            sell_orders.append(sell_order)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = SellOrdersResponse(
            sell_orders=sell_orders,
            pagination=pagination_response.dict() if pagination_response else None
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing sell orders: {str(e)}")
        error_result = SellOrdersResponse(
            success=False,
            error=f"Failed to query sell orders: {str(e)}",
            sell_orders=[]
        )
        return error_result.dict()


async def list_sell_orders_by_batch(
    batch_denom: str,
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all sell orders for a specific credit batch.
    
    Args:
        batch_denom: The batch denomination to filter by
        limit: Maximum number of orders to return (1-1000, default 100)
        offset: Number of orders to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of sell orders for the specified batch.
    """
    try:
        # Validate parameters
        if not batch_denom:
            raise ValueError("Batch denomination is required")
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
            
        client = get_regen_client()
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse,
            key=key
        )
        
        response = await client.query_sell_orders_by_batch(batch_denom, pagination)
        
        # Parse sell orders from response
        sell_orders = []
        for order_data in response.get("sell_orders", []):
            sell_order = SellOrder(
                id=order_data["id"],
                seller=order_data["seller"],
                batch_key=order_data["batch_key"],
                batch_denom=order_data.get("batch_denom", batch_denom),
                quantity=order_data["quantity"],
                ask_denom=order_data["ask_denom"],
                ask_amount=order_data["ask_amount"],
                disable_auto_retire=order_data["disable_auto_retire"],
                expiration=order_data.get("expiration"),
                market_id=order_data.get("market_id")
            )
            sell_orders.append(sell_order)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = SellOrdersResponse(
            sell_orders=sell_orders,
            pagination=pagination_response.dict() if pagination_response else None
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing sell orders for batch {batch_denom}: {str(e)}")
        error_result = SellOrdersResponse(
            success=False,
            error=f"Failed to query sell orders for batch {batch_denom}: {str(e)}",
            sell_orders=[]
        )
        return error_result.dict()


async def list_sell_orders_by_seller(
    seller: str,
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all sell orders created by a specific seller.
    
    Args:
        seller: The seller address to filter by
        limit: Maximum number of orders to return (1-1000, default 100)
        offset: Number of orders to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of sell orders for the specified seller.
    """
    try:
        # Validate parameters
        if not seller:
            raise ValueError("Seller address is required")
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
            
        client = get_regen_client()
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse,
            key=key
        )
        
        response = await client.query_sell_orders_by_seller(seller, pagination)
        
        # Parse sell orders from response
        sell_orders = []
        for order_data in response.get("sell_orders", []):
            sell_order = SellOrder(
                id=order_data.get("id", ""),
                seller=order_data.get("seller", ""),
                batch_denom=order_data.get("batch_denom", ""),
                quantity=order_data.get("quantity", "0"),
                ask_denom=order_data.get("ask_denom", ""),
                ask_amount=order_data.get("ask_amount", "0"),
                disable_auto_retire=order_data.get("disable_auto_retire", False),
                expiration=order_data.get("expiration"),
                market_id=order_data.get("market_id")
            )
            sell_orders.append(sell_order)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = SellOrdersResponse(
            sell_orders=sell_orders,
            pagination=pagination_response.dict() if pagination_response else None
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing sell orders for seller {seller}: {str(e)}")
        error_result = SellOrdersResponse(
            success=False,
            error=f"Failed to query sell orders for seller {seller}: {str(e)}",
            sell_orders=[]
        )
        return error_result.dict()


async def list_allowed_denoms(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all denominations approved for use in the marketplace.
    
    Args:
        limit: Maximum number of denoms to return (1-1000, default 100)
        offset: Number of denoms to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of allowed denominations with their
              bank denom, display name, and exponent information.
    """
    try:
        # Validate parameters
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        if offset < 0:
            raise ValueError("Offset must be non-negative")
            
        client = get_regen_client()
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse,
            key=key
        )
        
        response = await client.query_allowed_denoms(pagination)
        
        # Parse allowed denoms from response
        allowed_denoms = []
        for denom_data in response.get("allowed_denoms", []):
            allowed_denom = AllowedDenom(
                bank_denom=denom_data.get("bank_denom", ""),
                display_denom=denom_data.get("display_denom", ""),
                exponent=int(denom_data.get("exponent", 0))
            )
            allowed_denoms.append(allowed_denom)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = AllowedDenomsResponse(
            allowed_denoms=allowed_denoms,
            pagination=pagination_response.dict() if pagination_response else None
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing allowed denoms: {str(e)}")
        error_result = AllowedDenomsResponse(
            success=False,
            error=f"Failed to query allowed denoms: {str(e)}",
            allowed_denoms=[]
        )
        return error_result.dict()