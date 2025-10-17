"""Bank module tools for Regen Network MCP server."""

import logging
from typing import Dict, Any, Optional

from ..client.regen_client import get_regen_client, RegenClientError, Pagination
from ..models.bank import (
    BalanceQueryParams,
    PaginatedBankQueryParams,
    SupplyQueryParams,
    SupplyOfQueryParams,
    validate_cosmos_address,
    validate_denomination
)

logger = logging.getLogger(__name__)


class BankToolsError(Exception):
    """Custom exception for bank tools errors."""
    pass


async def get_balance(address: str, denom: str) -> Dict[str, Any]:
    """
    Get balance of specific token for address.
    
    Args:
        address: Cosmos account address (e.g., regen1...)
        denom: Token denomination (e.g., uregen, ibc/...)
        
    Returns:
        Dict with balance information or error
    """
    try:
        # Validate inputs
        if not validate_cosmos_address(address):
            return {"error": f"Invalid Cosmos address format: {address}"}
            
        if not validate_denomination(denom):
            return {"error": f"Invalid denomination format: {denom}"}
        
        # Create validated params object
        params = BalanceQueryParams(address=address, denom=denom)

        client = get_regen_client()
        response = await client.query_balance(params.address, params.denom)
        return response
            
    except RegenClientError as e:
        logger.error(f"Client error in get_balance: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_balance: {e}")
        return {"error": f"Internal error: {str(e)}"}


async def get_all_balances(
    address: str,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    count_total: Optional[bool] = None,
    reverse: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get all token balances for address.
    
    Args:
        address: Cosmos account address (e.g., regen1...)
        limit: Page size (default 100, max 200)
        page: Page number (1-based, default 1)
        count_total: Return total count (default true)
        reverse: Descending order (default false)
        
    Returns:
        Dict with all balances or error
    """
    try:
        # Validate address
        if not validate_cosmos_address(address):
            return {"error": f"Invalid Cosmos address format: {address}"}
        
        # Create validated params object
        params_dict = {"address": address}
        if limit is not None:
            params_dict["limit"] = limit
        if page is not None:
            params_dict["page"] = page
        if count_total is not None:
            params_dict["count_total"] = count_total
        if reverse is not None:
            params_dict["reverse"] = reverse
            
        params = PaginatedBankQueryParams(**params_dict)

        # Convert to API pagination parameters
        pagination = Pagination(
            limit=params.limit or 100,
            offset=((params.page or 1) - 1) * (params.limit or 100),
            count_total=params.count_total,
            reverse=params.reverse
        )

        client = get_regen_client()
        response = await client.query_all_balances(params.address, pagination)
        return response
            
    except ValueError as e:
        logger.error(f"Validation error in get_all_balances: {e}")
        return {"error": f"Validation error: {str(e)}"}
    except RegenClientError as e:
        logger.error(f"Client error in get_all_balances: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_all_balances: {e}")
        return {"error": f"Internal error: {str(e)}"}


async def get_spendable_balances(
    address: str,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    count_total: Optional[bool] = None,
    reverse: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get spendable (not locked/staked) balances for address.
    
    Args:
        address: Cosmos account address (e.g., regen1...)
        limit: Page size (default 100, max 200)
        page: Page number (1-based, default 1)
        count_total: Return total count (default true)
        reverse: Descending order (default false)
        
    Returns:
        Dict with spendable balances or error
    """
    try:
        # Validate address
        if not validate_cosmos_address(address):
            return {"error": f"Invalid Cosmos address format: {address}"}
        
        # Create validated params object
        params_dict = {"address": address}
        if limit is not None:
            params_dict["limit"] = limit
        if page is not None:
            params_dict["page"] = page
        if count_total is not None:
            params_dict["count_total"] = count_total
        if reverse is not None:
            params_dict["reverse"] = reverse
            
        params = PaginatedBankQueryParams(**params_dict)

        # Convert to API pagination parameters
        pagination = Pagination(
            limit=params.limit or 100,
            offset=((params.page or 1) - 1) * (params.limit or 100),
            count_total=params.count_total,
            reverse=params.reverse
        )

        client = get_regen_client()
        response = await client.query_spendable_balances(params.address, pagination)
        return response
            
    except ValueError as e:
        logger.error(f"Validation error in get_spendable_balances: {e}")
        return {"error": f"Validation error: {str(e)}"}
    except RegenClientError as e:
        logger.error(f"Client error in get_spendable_balances: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_spendable_balances: {e}")
        return {"error": f"Internal error: {str(e)}"}


async def get_total_supply(
    limit: Optional[int] = None,
    page: Optional[int] = None,
    count_total: Optional[bool] = None,
    reverse: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get total supply of all coin denominations.
    
    Args:
        limit: Page size (default 100, max 200)
        page: Page number (1-based, default 1)
        count_total: Return total count (default true)
        reverse: Descending order (default false)
        
    Returns:
        Dict with total supply data or error
    """
    try:
        # Create validated params object
        params_dict = {}
        if limit is not None:
            params_dict["limit"] = limit
        if page is not None:
            params_dict["page"] = page
        if count_total is not None:
            params_dict["count_total"] = count_total
        if reverse is not None:
            params_dict["reverse"] = reverse
            
        params = SupplyQueryParams(**params_dict)

        # Convert to API pagination parameters
        pagination = Pagination(
            limit=params.limit or 100,
            offset=((params.page or 1) - 1) * (params.limit or 100),
            count_total=params.count_total,
            reverse=params.reverse
        )

        client = get_regen_client()
        response = await client.query_total_supply(pagination)
        return response
            
    except ValueError as e:
        logger.error(f"Validation error in get_total_supply: {e}")
        return {"error": f"Validation error: {str(e)}"}
    except RegenClientError as e:
        logger.error(f"Client error in get_total_supply: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_total_supply: {e}")
        return {"error": f"Internal error: {str(e)}"}


async def get_supply_of(denom: str) -> Dict[str, Any]:
    """
    Get total supply of specific denomination.
    
    Args:
        denom: Token denomination (e.g., uregen, ibc/...)
        
    Returns:
        Dict with supply amount and metadata or error
    """
    try:
        # Validate denomination
        if not validate_denomination(denom):
            return {"error": f"Invalid denomination format: {denom}"}
        
        # Create validated params object
        params = SupplyOfQueryParams(denom=denom)

        client = get_regen_client()
        response = await client.query_supply_of(params.denom)
        return response
            
    except ValueError as e:
        logger.error(f"Validation error in get_supply_of: {e}")
        return {"error": f"Validation error: {str(e)}"}
    except RegenClientError as e:
        logger.error(f"Client error in get_supply_of: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in get_supply_of: {e}")
        return {"error": f"Internal error: {str(e)}"}


async def list_accounts(
    page: int = 1,
    limit: int = 100,
    count_total: bool = True,
    reverse: bool = False
) -> Dict[str, Any]:
    """
    List all accounts on Regen Network.

    Args:
        page: Page number for pagination
        limit: Number of results per page
        count_total: Return total count (default true)
        reverse: Descending order (default false)

    Returns:
        Dict with accounts list or error
    """
    try:
        pagination = Pagination(
            limit=limit,
            offset=(page - 1) * limit,
            count_total=count_total,
            reverse=reverse
        )

        client = get_regen_client()
        response = await client.query_accounts(pagination)
        return response

    except RegenClientError as e:
        logger.error(f"Accounts list query failed: {e}")
        return {"error": f"Accounts list query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_accounts: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_account(address: str) -> Dict[str, Any]:
    """
    Get detailed account information.

    Args:
        address: Cosmos account address (e.g., regen1...)

    Returns:
        Dict with account information or error
    """
    try:
        if not validate_cosmos_address(address):
            return {"error": f"Invalid Cosmos address format: {address}"}

        client = get_regen_client()
        response = await client.query_account(address)
        return response

    except RegenClientError as e:
        logger.error(f"Account query failed: {e}")
        return {"error": f"Account query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_account: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_bank_params() -> Dict[str, Any]:
    """
    Get bank module parameters.

    Returns:
        Dict with bank parameters or error
    """
    try:
        client = get_regen_client()
        response = await client.query_bank_params()
        return response

    except RegenClientError as e:
        logger.error(f"Bank params query failed: {e}")
        return {"error": f"Bank params query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_bank_params: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_denoms_metadata(
    page: int = 1,
    limit: int = 100,
    count_total: bool = True,
    reverse: bool = False
) -> Dict[str, Any]:
    """
    Get metadata for all tokens.

    Args:
        page: Page number for pagination
        limit: Number of results per page
        count_total: Return total count (default true)
        reverse: Descending order (default false)

    Returns:
        Dict with denominations metadata or error
    """
    try:
        pagination = Pagination(
            limit=limit,
            offset=(page - 1) * limit,
            count_total=count_total,
            reverse=reverse
        )

        client = get_regen_client()
        response = await client.query_denoms_metadata(pagination)
        return response

    except RegenClientError as e:
        logger.error(f"Denoms metadata query failed: {e}")
        return {"error": f"Denoms metadata query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_denoms_metadata: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_denom_metadata(denom: str) -> Dict[str, Any]:
    """
    Get metadata for specific token.

    Args:
        denom: Token denomination (e.g., uregen, ibc/...)

    Returns:
        Dict with denomination metadata or error
    """
    try:
        if not validate_denomination(denom):
            return {"error": f"Invalid denomination format: {denom}"}

        client = get_regen_client()
        response = await client.query_denom_metadata(denom)
        return response

    except RegenClientError as e:
        logger.error(f"Denom metadata query failed: {e}")
        return {"error": f"Denom metadata query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_denom_metadata: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_denom_owners(
    denom: str,
    page: int = 1,
    limit: int = 100,
    count_total: bool = True,
    reverse: bool = False
) -> Dict[str, Any]:
    """
    Get all holders of a token.

    Args:
        denom: Token denomination (e.g., uregen, ibc/...)
        page: Page number for pagination
        limit: Number of results per page
        count_total: Return total count (default true)
        reverse: Descending order (default false)

    Returns:
        Dict with token owners or error
    """
    try:
        if not validate_denomination(denom):
            return {"error": f"Invalid denomination format: {denom}"}

        pagination = Pagination(
            limit=limit,
            offset=(page - 1) * limit,
            count_total=count_total,
            reverse=reverse
        )

        client = get_regen_client()
        response = await client.query_denom_owners(denom, pagination)
        return response

    except RegenClientError as e:
        logger.error(f"Denom owners query failed: {e}")
        return {"error": f"Denom owners query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_denom_owners: {e}")
        return {"error": f"Unexpected error: {str(e)}"}