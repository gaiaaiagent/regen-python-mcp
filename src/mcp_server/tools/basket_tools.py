"""Basket-related MCP tools for Regen Network.

This module implements MCP tools for querying ecocredit baskets, their balances,
and related functionality on the Regen Network blockchain.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List

from mcp.server.fastmcp import FastMCP

from ..client.regen_client import get_regen_client, Pagination, RegenClientError
from ..models.basket import (
    BasketInfo,
    BasketBalance,
    BasketFee,
    ListBasketsResponse,
    GetBasketResponse,
    ListBasketBalancesResponse,
    GetBasketBalanceResponse
)

logger = logging.getLogger(__name__)


async def list_baskets(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False
) -> Dict[str, Any]:
    """List all active ecocredit baskets on Regen Ledger.
    
    Args:
        limit: Number of baskets to return (1-1000)
        offset: Number of baskets to skip
        count_total: Whether to return total count
        reverse: Whether to reverse the order
        
    Returns:
        Dict containing baskets list and pagination info
        
    Raises:
        RegenClientError: If the API request fails
        ValueError: If parameters are invalid
    """
    # Validate parameters
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")
    if offset < 0:
        raise ValueError("offset must be non-negative")
    
    client = get_regen_client()
    
    try:
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse
        )
        
        logger.info(f"Querying baskets with pagination: limit={limit}, offset={offset}")
        response = await client.query_baskets(pagination)
        
        # Parse response into structured format
        baskets_data = response.get("baskets", [])
        baskets = []
        
        for basket_data in baskets_data:
            try:
                basket = BasketInfo(
                    basket_denom=basket_data.get("basket_denom", ""),
                    name=basket_data.get("name", ""),
                    disable_auto_retire=basket_data.get("disable_auto_retire", False),
                    credit_type_abbrev=basket_data.get("credit_type_abbrev", ""),
                    date_criteria=basket_data.get("date_criteria"),
                    exponent=basket_data.get("exponent", 0),
                    curator=basket_data.get("curator", "")
                )
                baskets.append(basket.dict())
            except Exception as e:
                logger.warning(f"Failed to parse basket data: {e}")
                continue
        
        # Extract pagination info
        pagination_info = response.get("pagination", {})
        
        result = ListBasketsResponse(
            baskets=baskets,
            pagination=pagination_info
        )
        
        logger.info(f"Successfully retrieved {len(baskets)} baskets")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Failed to list baskets: {e}")
        raise RegenClientError(f"Failed to list baskets: {e}")


async def get_basket(basket_denom: str) -> Dict[str, Any]:
    """Retrieve detailed information about a specific basket.
    
    Args:
        basket_denom: Basket denomination (e.g., "eco.uC.NCT")
        
    Returns:
        Dict containing basket information
        
    Raises:
        RegenClientError: If the API request fails
        ValueError: If basket_denom is invalid
    """
    # Validate basket denomination
    if not basket_denom or not isinstance(basket_denom, str):
        raise ValueError("basket_denom must be a non-empty string")
    
    client = get_regen_client()
    
    try:
        logger.info(f"Querying basket: {basket_denom}")
        response = await client.query_basket(basket_denom)
        
        # Parse response
        basket_data = response.get("basket", {})
        if not basket_data:
            logger.warning(f"No basket found for denomination: {basket_denom}")
            return GetBasketResponse(basket=None).dict()
        
        try:
            basket = BasketInfo(
                basket_denom=basket_data.get("basket_denom", ""),
                name=basket_data.get("name", ""),
                disable_auto_retire=basket_data.get("disable_auto_retire", False),
                credit_type_abbrev=basket_data.get("credit_type_abbrev", ""),
                date_criteria=basket_data.get("date_criteria"),
                exponent=basket_data.get("exponent", 0),
                curator=basket_data.get("curator", "")
            )
            
            result = GetBasketResponse(basket=basket.dict())
            logger.info(f"Successfully retrieved basket: {basket_denom}")
            return result.dict()
            
        except Exception as e:
            logger.error(f"Failed to parse basket data: {e}")
            raise RegenClientError(f"Failed to parse basket data: {e}")
        
    except Exception as e:
        logger.error(f"Failed to get basket {basket_denom}: {e}")
        raise RegenClientError(f"Failed to get basket {basket_denom}: {e}")


async def list_basket_balances(
    basket_denom: str,
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False
) -> Dict[str, Any]:
    """List all credit batches held in a specific basket.
    
    Args:
        basket_denom: Basket denomination
        limit: Number of balances to return (1-1000)
        offset: Number of balances to skip
        count_total: Whether to return total count
        reverse: Whether to reverse the order
        
    Returns:
        Dict containing basket balances and pagination info
        
    Raises:
        RegenClientError: If the API request fails
        ValueError: If parameters are invalid
    """
    # Validate parameters
    if not basket_denom or not isinstance(basket_denom, str):
        raise ValueError("basket_denom must be a non-empty string")
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")
    if offset < 0:
        raise ValueError("offset must be non-negative")
    
    client = get_regen_client()
    
    try:
        pagination = Pagination(
            limit=limit,
            offset=offset,
            count_total=count_total,
            reverse=reverse
        )
        
        logger.info(f"Querying basket balances for: {basket_denom}")
        response = await client.query_basket_balances(basket_denom, pagination)
        
        # Parse response
        balances_data = response.get("balances", [])
        balances = []
        
        for balance_data in balances_data:
            try:
                balance = BasketBalance(
                    basket_denom=basket_denom,
                    batch_denom=balance_data.get("batch_denom", ""),
                    balance=balance_data.get("balance", "0")
                )
                balances.append(balance.dict())
            except Exception as e:
                logger.warning(f"Failed to parse balance data: {e}")
                continue
        
        # Extract pagination info
        pagination_info = response.get("pagination", {})
        
        result = ListBasketBalancesResponse(
            balances=balances,
            pagination=pagination_info
        )
        
        logger.info(f"Successfully retrieved {len(balances)} basket balances")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Failed to list basket balances for {basket_denom}: {e}")
        raise RegenClientError(f"Failed to list basket balances for {basket_denom}: {e}")


async def get_basket_balance(
    basket_denom: str,
    batch_denom: str
) -> Dict[str, Any]:
    """Get balance of a specific credit batch in a basket.
    
    Args:
        basket_denom: Basket denomination
        batch_denom: Credit batch denomination
        
    Returns:
        Dict containing balance information
        
    Raises:
        RegenClientError: If the API request fails
        ValueError: If parameters are invalid
    """
    # Validate parameters
    if not basket_denom or not isinstance(basket_denom, str):
        raise ValueError("basket_denom must be a non-empty string")
    if not batch_denom or not isinstance(batch_denom, str):
        raise ValueError("batch_denom must be a non-empty string")
    
    client = get_regen_client()
    
    try:
        logger.info(f"Querying basket balance for: {basket_denom}/{batch_denom}")
        response = await client.query_basket_balance(basket_denom, batch_denom)
        
        # Parse response
        balance = response.get("balance", "0")
        
        result = GetBasketBalanceResponse(balance=balance)
        logger.info(f"Successfully retrieved basket balance: {balance}")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Failed to get basket balance for {basket_denom}/{batch_denom}: {e}")
        raise RegenClientError(f"Failed to get basket balance for {basket_denom}/{batch_denom}: {e}")


async def get_basket_fee() -> Dict[str, Any]:
    """Retrieve current fee required to create a new basket.
    
    Returns:
        Dict containing basket creation fee information
        
    Raises:
        RegenClientError: If the API request fails
    """
    client = get_regen_client()
    
    try:
        logger.info("Querying basket creation fee")
        response = await client.query_basket_fee()
        
        # Parse response
        fee_data = response.get("fee")
        
        result = BasketFee(
            fee=fee_data if fee_data else None
        )
        
        logger.info(f"Successfully retrieved basket fee: {fee_data}")
        return result.dict()
        
    except Exception as e:
        logger.error(f"Failed to get basket fee: {e}")
        raise RegenClientError(f"Failed to get basket fee: {e}")


def register_basket_tools(server: FastMCP) -> None:
    """Register all basket-related tools with the MCP server.
    
    Args:
        server: FastMCP server instance
    """
    
    @server.tool("list_baskets")
    async def _list_baskets(
        limit: int = 100,
        offset: int = 0,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """List all active ecocredit baskets on Regen Ledger.
        
        Args:
            limit: Number of baskets to return (1-1000, default: 100)
            offset: Number of baskets to skip (default: 0)
            count_total: Whether to return total count (default: True)
            reverse: Whether to reverse the order (default: False)
            
        Returns:
            Dictionary containing baskets list and pagination info
        """
        return await list_baskets(limit, offset, count_total, reverse)
    
    @server.tool("get_basket")
    async def _get_basket(basket_denom: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific basket.
        
        Args:
            basket_denom: Basket denomination (e.g., "eco.uC.NCT")
            
        Returns:
            Dictionary containing basket information
        """
        return await get_basket(basket_denom)
    
    @server.tool("list_basket_balances")
    async def _list_basket_balances(
        basket_denom: str,
        limit: int = 100,
        offset: int = 0,
        count_total: bool = True,
        reverse: bool = False
    ) -> Dict[str, Any]:
        """List all credit batches held in a specific basket.
        
        Args:
            basket_denom: Basket denomination
            limit: Number of balances to return (1-1000, default: 100)
            offset: Number of balances to skip (default: 0)
            count_total: Whether to return total count (default: True)
            reverse: Whether to reverse the order (default: False)
            
        Returns:
            Dictionary containing basket balances and pagination info
        """
        return await list_basket_balances(basket_denom, limit, offset, count_total, reverse)
    
    @server.tool("get_basket_balance")
    async def _get_basket_balance(
        basket_denom: str,
        batch_denom: str
    ) -> Dict[str, Any]:
        """Get balance of a specific credit batch in a basket.
        
        Args:
            basket_denom: Basket denomination
            batch_denom: Credit batch denomination
            
        Returns:
            Dictionary containing balance information
        """
        return await get_basket_balance(basket_denom, batch_denom)
    
    @server.tool("get_basket_fee")
    async def _get_basket_fee() -> Dict[str, Any]:
        """Retrieve current fee required to create a new basket.
        
        Returns:
            Dictionary containing basket creation fee information
        """
        return await get_basket_fee()
    
    logger.info("Registered 5 basket tools with MCP server")