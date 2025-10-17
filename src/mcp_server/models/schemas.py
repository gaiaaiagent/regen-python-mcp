"""Base Pydantic models for Regen Network entities.

This module defines the core data models that represent entities on the Regen Network
blockchain, including baskets, credits, projects, and marketplace data. All models
provide validation, serialization, and type safety.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, root_validator


class BaseRegenModel(BaseModel):
    """Base model for all Regen Network entities."""
    
    class Config:
        # Allow extra fields for flexibility with blockchain data
        extra = "allow"
        # Use enum values
        use_enum_values = True
        # Validate assignment
        validate_assignment = True


class CosmosAddress(str):
    """Cosmos bech32 address string with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate Cosmos bech32 address format."""
        if not isinstance(value, str):
            raise TypeError("Address must be a string")
        
        if not value.startswith(("regen", "cosmos")):
            raise ValueError("Address must start with 'regen' or 'cosmos'")
        
        if len(value) < 39 or len(value) > 45:  # Typical bech32 length
            raise ValueError("Address length is invalid")
        
        return value


class TokenDenom(str):
    """Token denomination string with validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value: str) -> str:
        """Validate token denomination format."""
        if not isinstance(value, str):
            raise TypeError("Denomination must be a string")
        
        if not value:
            raise ValueError("Denomination cannot be empty")
        
        return value


class PaginationRequest(BaseModel):
    """Pagination parameters for blockchain queries."""
    
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    count_total: bool = Field(default=True, description="Whether to count total items")
    reverse: bool = Field(default=False, description="Whether to reverse sort order")


class PaginationResponse(BaseModel):
    """Pagination response metadata."""
    
    next_key: Optional[str] = Field(default=None, description="Key for next page")
    total: Optional[int] = Field(default=None, description="Total number of items")


class Coin(BaseModel):
    """Cosmos SDK coin representation."""
    
    denom: TokenDenom = Field(..., description="Token denomination")
    amount: str = Field(..., description="Token amount as string")
    
    @validator("amount")
    def validate_amount(cls, value: str) -> str:
        """Validate amount is a valid integer string."""
        try:
            int(value)
            return value
        except ValueError:
            raise ValueError("Amount must be a valid integer string")


class DateCriteria(BaseModel):
    """Date criteria for basket acceptance."""
    
    min_start_date: Optional[datetime] = Field(default=None, description="Minimum start date")
    start_date_window: Optional[str] = Field(default=None, description="Start date window duration")


class CreditType(BaseModel):
    """Credit type information."""
    
    abbreviation: str = Field(..., description="Credit type abbreviation (e.g., 'C')")
    name: str = Field(..., description="Full credit type name")
    unit: str = Field(..., description="Unit of measurement")
    precision: int = Field(..., description="Decimal precision")


class Location(BaseModel):
    """Geographic location information."""
    
    geometry: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON geometry")
    
    
class Basket(BaseModel):
    """Ecocredit basket model."""
    
    basket_denom: TokenDenom = Field(..., description="Basket denomination")
    name: str = Field(..., description="Human-readable basket name")
    disable_auto_retire: bool = Field(..., description="Whether auto-retirement is disabled")
    credit_type_abbrev: str = Field(..., description="Credit type abbreviation")
    date_criteria: Optional[DateCriteria] = Field(default=None, description="Date acceptance criteria")
    exponent: int = Field(..., description="Decimal exponent for display")
    curator: CosmosAddress = Field(..., description="Basket curator address")


class BasketBalance(BaseModel):
    """Balance of a credit batch in a basket."""
    
    batch_denom: str = Field(..., description="Credit batch denomination")
    balance: str = Field(..., description="Balance amount as string")


class CreditClass(BaseModel):
    """Credit class model."""
    
    key: str = Field(..., description="Unique class key")
    id: str = Field(..., description="Class ID")
    admin: CosmosAddress = Field(..., description="Class admin address")
    metadata: str = Field(..., description="Class metadata")
    credit_type: CreditType = Field(..., description="Credit type information")


class Project(BaseModel):
    """Ecological project model."""
    
    key: str = Field(..., description="Unique project key")
    id: str = Field(..., description="Project ID")
    admin: CosmosAddress = Field(..., description="Project admin address")
    class_key: str = Field(..., description="Associated credit class key")
    jurisdiction: str = Field(..., description="Project jurisdiction")
    metadata: str = Field(..., description="Project metadata")
    reference_id: Optional[str] = Field(default=None, description="External reference ID")


class CreditBatch(BaseModel):
    """Credit batch model."""
    
    key: str = Field(..., description="Unique batch key")
    issuer: CosmosAddress = Field(..., description="Batch issuer address")
    project_key: str = Field(..., description="Associated project key")
    denom: str = Field(..., description="Batch denomination")
    metadata: str = Field(..., description="Batch metadata")
    start_date: Optional[datetime] = Field(default=None, description="Monitoring start date")
    end_date: Optional[datetime] = Field(default=None, description="Monitoring end date")
    issuance_date: datetime = Field(..., description="Issuance date")
    open: bool = Field(..., description="Whether batch is open for additional issuance")


class CreditBatchSupply(BaseModel):
    """Credit batch supply information."""
    
    tradable_amount: str = Field(..., description="Tradable credit amount")
    retired_amount: str = Field(..., description="Retired credit amount")
    cancelled_amount: str = Field(..., description="Cancelled credit amount")


class SellOrderStatus(str, Enum):
    """Sell order status enumeration."""
    
    ACTIVE = "active"
    CANCELLED = "cancelled"
    FILLED = "filled"


class SellOrder(BaseModel):
    """Marketplace sell order model."""
    
    id: str = Field(..., description="Sell order ID")
    seller: CosmosAddress = Field(..., description="Seller address")
    batch_key: str = Field(..., description="Credit batch key")
    quantity: str = Field(..., description="Credit quantity for sale")
    market_id: str = Field(..., description="Market ID")
    ask_price: str = Field(..., description="Ask price as string")
    disable_auto_retire: bool = Field(..., description="Whether to disable auto-retirement")
    expiration: Optional[datetime] = Field(default=None, description="Order expiration")


class AllowedDenom(BaseModel):
    """Allowed denomination for marketplace payments."""
    
    bank_denom: TokenDenom = Field(..., description="Bank denomination")
    display_denom: str = Field(..., description="Display denomination")
    exponent: int = Field(..., description="Decimal exponent")


class MarketPlace(BaseModel):
    """Marketplace configuration."""
    
    id: str = Field(..., description="Market ID")
    credit_type_abbrev: str = Field(..., description="Credit type abbreviation")
    bank_denom: TokenDenom = Field(..., description="Bank denomination for payments")
    precision_modifier: int = Field(..., description="Precision modifier")


# Governance Models

class ProposalStatus(str, Enum):
    """Governance proposal status enumeration."""
    
    UNSPECIFIED = "PROPOSAL_STATUS_UNSPECIFIED"
    DEPOSIT_PERIOD = "PROPOSAL_STATUS_DEPOSIT_PERIOD"
    VOTING_PERIOD = "PROPOSAL_STATUS_VOTING_PERIOD"
    PASSED = "PROPOSAL_STATUS_PASSED"
    REJECTED = "PROPOSAL_STATUS_REJECTED"
    FAILED = "PROPOSAL_STATUS_FAILED"


class VoteOption(str, Enum):
    """Vote option enumeration."""
    
    UNSPECIFIED = "VOTE_OPTION_UNSPECIFIED"
    YES = "VOTE_OPTION_YES"
    ABSTAIN = "VOTE_OPTION_ABSTAIN"
    NO = "VOTE_OPTION_NO"
    NO_WITH_VETO = "VOTE_OPTION_NO_WITH_VETO"


class Proposal(BaseModel):
    """Governance proposal model."""
    
    proposal_id: str = Field(..., description="Proposal ID")
    content: Dict[str, Any] = Field(..., description="Proposal content")
    status: ProposalStatus = Field(..., description="Proposal status")
    final_tally_result: Dict[str, str] = Field(..., description="Final vote tally")
    submit_time: datetime = Field(..., description="Submission time")
    deposit_end_time: datetime = Field(..., description="Deposit end time")
    total_deposit: List[Coin] = Field(..., description="Total deposited amount")
    voting_start_time: datetime = Field(..., description="Voting start time")
    voting_end_time: datetime = Field(..., description="Voting end time")


class Vote(BaseModel):
    """Governance vote model."""
    
    proposal_id: str = Field(..., description="Proposal ID")
    voter: CosmosAddress = Field(..., description="Voter address")
    option: VoteOption = Field(..., description="Vote option")
    options: List[Dict[str, Any]] = Field(default=[], description="Weighted vote options")


class Deposit(BaseModel):
    """Governance deposit model."""
    
    proposal_id: str = Field(..., description="Proposal ID")
    depositor: CosmosAddress = Field(..., description="Depositor address")
    amount: List[Coin] = Field(..., description="Deposited amount")


# Response wrapper models

class BasketResponse(BaseModel):
    """Response wrapper for basket queries."""
    
    baskets: List[Basket] = Field(..., description="List of baskets")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class CreditClassResponse(BaseModel):
    """Response wrapper for credit class queries."""
    
    classes: List[CreditClass] = Field(..., description="List of credit classes")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class ProjectResponse(BaseModel):
    """Response wrapper for project queries."""
    
    projects: List[Project] = Field(..., description="List of projects")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class CreditBatchResponse(BaseModel):
    """Response wrapper for credit batch queries."""
    
    batches: List[CreditBatch] = Field(..., description="List of credit batches")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class SellOrderResponse(BaseModel):
    """Response wrapper for sell order queries."""
    
    sell_orders: List[SellOrder] = Field(..., description="List of sell orders")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class BasketBalanceResponse(BaseModel):
    """Response wrapper for basket balance queries."""
    
    balances: List[BasketBalance] = Field(..., description="List of basket balances")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


# Balance and bank models

class Balance(BaseModel):
    """Account balance model."""
    
    address: CosmosAddress = Field(..., description="Account address")
    coins: List[Coin] = Field(..., description="List of coin balances")


class BalanceResponse(BaseModel):
    """Response wrapper for balance queries."""
    
    balances: List[Coin] = Field(..., description="List of balances")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


class SupplyResponse(BaseModel):
    """Response wrapper for supply queries."""
    
    supply: List[Coin] = Field(..., description="Token supply amounts")
    pagination: Optional[PaginationResponse] = Field(default=None, description="Pagination info")


# Error models

class APIError(BaseModel):
    """API error response model."""
    
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


# Health check models

class EndpointHealth(BaseModel):
    """Health status for a single endpoint."""
    
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    chain_id: Optional[str] = Field(default=None, description="Chain ID if available")
    response_time_ms: Optional[float] = Field(default=None, description="Response time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")


class HealthCheckResponse(BaseModel):
    """Response wrapper for health check queries."""
    
    rpc_endpoints: Dict[str, EndpointHealth] = Field(..., description="RPC endpoint health")
    rest_endpoints: Dict[str, EndpointHealth] = Field(..., description="REST endpoint health")
    timestamp: float = Field(..., description="Timestamp of health check")


# Additional models for tools compatibility

class BatchInfo(BaseModel):
    """Basic batch information."""
    batch_denom: str = Field(..., description="Batch denomination")
    class_id: str = Field(..., description="Credit class ID")
    project_id: Optional[str] = Field(default=None, description="Project ID")
    issuer: Optional[str] = Field(default=None, description="Batch issuer")


class BatchKey(BaseModel):
    """Batch key for marketplace operations."""
    batch_denom: str = Field(..., description="Batch denomination")
    class_id: str = Field(..., description="Credit class ID")