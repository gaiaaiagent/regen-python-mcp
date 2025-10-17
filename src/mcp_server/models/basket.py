"""Pydantic models for ecocredit baskets."""

from typing import Optional, List
from pydantic import Field

from .schemas import BaseRegenModel, DateCriteria, Coin


class BasketInfo(BaseRegenModel):
    """Ecocredit basket information."""
    
    basket_denom: str = Field(description="Unique basket denomination")
    name: str = Field(description="Basket name")
    disable_auto_retire: bool = Field(description="Whether auto-retire is disabled")
    credit_type_abbrev: str = Field(description="Credit type abbreviation")
    date_criteria: Optional[DateCriteria] = Field(default=None, description="Date criteria")
    exponent: int = Field(description="Decimal exponent")
    curator: str = Field(description="Basket curator address")


class BasketBalance(BaseRegenModel):
    """Balance of credits in a basket."""
    
    basket_denom: str = Field(description="Basket denomination")
    batch_denom: str = Field(description="Batch denomination")
    balance: str = Field(description="Balance amount")


class BasketFee(BaseRegenModel):
    """Fee required to create a basket."""
    
    fee: Optional[dict] = Field(default=None, description="Creation fee (None if no fee)")


class BasketCriteria(BaseRegenModel):
    """Criteria for basket eligibility."""
    
    allowed_classes: Optional[List[str]] = Field(default=None, description="Allowed credit classes")
    date_criteria: Optional[DateCriteria] = Field(default=None, description="Date requirements")
    min_start_date: Optional[str] = Field(default=None, description="Minimum start date")
    start_date_window: Optional[str] = Field(default=None, description="Start date window")


# Response models for API endpoints

class ListBasketsResponse(BaseRegenModel):
    """Response for list baskets query."""
    
    baskets: List[BasketInfo] = Field(description="List of baskets")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class GetBasketResponse(BaseRegenModel):
    """Response for get basket query."""
    
    basket: Optional[BasketInfo] = Field(default=None, description="Basket information")


class ListBasketBalancesResponse(BaseRegenModel):
    """Response for list basket balances query."""
    
    balances: List[BasketBalance] = Field(description="List of basket balances")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class GetBasketBalanceResponse(BaseRegenModel):
    """Response for get basket balance query."""
    
    balance: str = Field(description="Balance amount")