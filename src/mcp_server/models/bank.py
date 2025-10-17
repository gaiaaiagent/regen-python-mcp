"""Pydantic models for Cosmos Bank module responses."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class Coin(BaseModel):
    """Represents a Cosmos Coin with denomination and amount."""
    
    denom: str = Field(..., description="Token denomination (e.g., uregen)")
    amount: str = Field(..., description="Token amount as string")


class PageRequest(BaseModel):
    """Pagination request parameters."""
    
    key: Optional[str] = Field(None, description="Key for pagination")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    limit: Optional[int] = Field(None, description="Limit for pagination")
    count_total: Optional[bool] = Field(None, description="Count total items")
    reverse: Optional[bool] = Field(None, description="Reverse order")


class PageResponse(BaseModel):
    """Pagination response metadata."""
    
    next_key: Optional[str] = Field(None, description="Next page key")
    total: Optional[str] = Field(None, description="Total items count")


class BalanceResponse(BaseModel):
    """Response model for balance queries."""
    
    balance: Coin = Field(..., description="Balance information")


class AllBalancesResponse(BaseModel):
    """Response model for all balances queries."""
    
    balances: List[Coin] = Field(..., description="List of all balances")
    pagination: Optional[PageResponse] = Field(None, description="Pagination info")


class SpendableBalancesResponse(BaseModel):
    """Response model for spendable balances queries."""
    
    balances: List[Coin] = Field(..., description="List of spendable balances") 
    pagination: Optional[PageResponse] = Field(None, description="Pagination info")


class TotalSupplyResponse(BaseModel):
    """Response model for total supply queries."""
    
    supply: List[Coin] = Field(..., description="Total supply of all tokens")
    pagination: Optional[PageResponse] = Field(None, description="Pagination info")


class SupplyOfResponse(BaseModel):
    """Response model for supply of specific denomination."""
    
    amount: Coin = Field(..., description="Supply amount of specific denomination")


class BankQueryParams(BaseModel):
    """Base parameters for bank queries."""
    
    address: str = Field(..., min_length=1, description="Cosmos account address")


class PaginatedBankQueryParams(BankQueryParams):
    """Bank query parameters with pagination."""
    
    limit: Optional[int] = Field(None, ge=1, le=200, description="Page size (default 100, max 200)")
    page: Optional[int] = Field(None, ge=1, description="Page number (1-based, default 1)") 
    count_total: Optional[bool] = Field(None, description="Return total count (default true)")
    reverse: Optional[bool] = Field(None, description="Descending order (default false)")


class BalanceQueryParams(BankQueryParams):
    """Parameters for balance queries."""
    
    denom: str = Field(..., min_length=1, description="Token denomination")


class SupplyQueryParams(BaseModel):
    """Parameters for supply queries."""
    
    limit: Optional[int] = Field(None, ge=1, le=200, description="Page size (default 100, max 200)")
    page: Optional[int] = Field(None, ge=1, description="Page number (1-based, default 1)")
    count_total: Optional[bool] = Field(None, description="Return total count (default true)")
    reverse: Optional[bool] = Field(None, description="Descending order (default false)")


class SupplyOfQueryParams(BaseModel):
    """Parameters for supply of specific denomination."""
    
    denom: str = Field(..., min_length=1, description="Token denomination")


def build_pagination_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Build pagination parameters for API requests."""
    pagination_params = {}
    
    # Handle page-based pagination conversion to offset-based
    limit = params.get("limit", 100)
    page = params.get("page", 1)
    
    pagination_params["pagination.limit"] = str(limit)
    pagination_params["pagination.offset"] = str((page - 1) * limit)
    
    if "count_total" in params and params["count_total"] is not None:
        pagination_params["pagination.count_total"] = str(params["count_total"]).lower()
        
    if "reverse" in params and params["reverse"] is not None:
        pagination_params["pagination.reverse"] = str(params["reverse"]).lower()
        
    return pagination_params


def validate_cosmos_address(address: str) -> bool:
    """Validate Cosmos bech32 address format."""
    if not address:
        return False
    
    # Basic validation: should start with regen and be appropriate length
    if not address.startswith("regen1"):
        return False
        
    # Cosmos addresses are typically 39-45 characters long
    if len(address) < 39 or len(address) > 45:
        return False
        
    return True


def validate_denomination(denom: str) -> bool:
    """Validate token denomination format."""
    if not denom:
        return False
    
    # Basic validation: non-empty string
    # Could be enhanced with more specific validation rules
    return len(denom) > 0