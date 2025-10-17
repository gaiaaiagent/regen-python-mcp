"""Pydantic models for marketplace functionality."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field

from .schemas import BaseRegenModel, BatchKey, Coin


class SellOrder(BaseRegenModel):
    """Marketplace sell order model."""

    id: str = Field(description="Sell order ID")
    seller: str = Field(description="Seller address")
    batch_denom: str = Field(description="Credit batch denomination")
    quantity: str = Field(description="Quantity for sale")
    ask_denom: str = Field(description="Payment denomination")
    ask_amount: str = Field(description="Ask amount in payment denom")
    disable_auto_retire: bool = Field(description="Whether to disable auto-retire")
    expiration: Optional[datetime] = Field(default=None, description="Order expiration")
    market_id: Optional[str] = Field(default=None, description="Market ID (if available)")


class AllowedDenom(BaseRegenModel):
    """Allowed denomination in marketplace."""

    bank_denom: str = Field(description="Bank denomination")
    display_denom: str = Field(description="Display name for denomination")
    exponent: int = Field(description="Decimal exponent")


class BuyOrder(BaseRegenModel):
    """Buy order information."""
    
    id: str = Field(description="Buy order ID")
    buyer: str = Field(description="Buyer address")
    selection: dict = Field(description="Credit selection criteria")
    quantity: str = Field(description="Quantity to buy")
    bid_price: Coin = Field(description="Bid price")
    disable_auto_retire: bool = Field(description="Whether to disable auto-retire")
    expiration: Optional[datetime] = Field(default=None, description="Order expiration")


class MarketInfo(BaseRegenModel):
    """Market information."""
    
    id: str = Field(description="Market ID")
    credit_type_abbrev: str = Field(description="Credit type abbreviation")
    bank_denom: str = Field(description="Bank denomination for payments")
    precision_modifier: int = Field(description="Precision modifier")


class OrderBook(BaseRegenModel):
    """Order book information."""
    
    sell_orders: List[SellOrder] = Field(description="Active sell orders")
    buy_orders: List[BuyOrder] = Field(description="Active buy orders")


# Response models for API endpoints

class GetSellOrderResponse(BaseRegenModel):
    """Response for get sell order query."""
    
    sell_order: Optional[SellOrder] = Field(default=None, description="Sell order information")


class ListSellOrdersResponse(BaseRegenModel):
    """Response for list sell orders query."""
    
    sell_orders: List[SellOrder] = Field(description="List of sell orders")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class ListAllowedDenomsResponse(BaseRegenModel):
    """Response for list allowed denoms query."""
    
    allowed_denoms: List[AllowedDenom] = Field(description="List of allowed denominations")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class GetMarketResponse(BaseRegenModel):
    """Response for get market query."""
    
    market: Optional[MarketInfo] = Field(default=None, description="Market information")


# Additional response types for tools

class SellOrderResponse(BaseRegenModel):
    """Response for get sell order query."""
    sell_order: Optional[SellOrder] = Field(default=None, description="Sell order information")


class SellOrdersResponse(BaseRegenModel):
    """Response for list sell orders query."""
    sell_orders: List[SellOrder] = Field(default_factory=list, description="List of sell orders")
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="Pagination info")


class AllowedDenomsResponse(BaseRegenModel):
    """Response for list allowed denoms query."""
    allowed_denoms: List[AllowedDenom] = Field(default_factory=list, description="List of allowed denoms")
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="Pagination info")