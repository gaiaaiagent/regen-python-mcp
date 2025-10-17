"""Pydantic models for credit classes and batches."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field

from .schemas import BaseRegenModel, CreditType, Location, BatchInfo


class CreditClass(BaseRegenModel):
    """Credit class model matching actual API response."""

    id: str = Field(description="Class ID")
    admin: str = Field(description="Class administrator address")
    metadata: str = Field(description="Class metadata")
    credit_type_abbrev: str = Field(description="Credit type abbreviation")


class Project(BaseRegenModel):
    """Ecological project model matching actual API response."""

    id: str = Field(description="Project ID")
    admin: str = Field(description="Project administrator address")
    class_id: str = Field(description="Associated credit class ID")
    jurisdiction: str = Field(description="Jurisdiction code")
    metadata: str = Field(description="Project metadata")
    reference_id: Optional[str] = Field(default="", description="Reference ID")


class CreditBatch(BaseRegenModel):
    """Credit batch model matching actual API response."""

    issuer: str = Field(description="Batch issuer address")
    project_id: str = Field(description="Associated project ID")
    denom: str = Field(description="Batch denomination")
    metadata: str = Field(description="Batch metadata")
    start_date: Optional[str] = Field(default=None, description="Monitoring start date")
    end_date: Optional[str] = Field(default=None, description="Monitoring end date")
    issuance_date: Optional[str] = Field(default=None, description="Issuance date")
    open: bool = Field(description="Whether batch is open for additional issuance")


class CreditBalance(BaseRegenModel):
    """Credit balance for an address."""
    
    batch_denom: str = Field(description="Batch denomination")
    tradable_amount: str = Field(description="Tradable amount")
    retired_amount: str = Field(description="Retired amount")
    escrowed_amount: str = Field(description="Escrowed amount")


class Supply(BaseRegenModel):
    """Credit batch supply information."""
    
    batch_denom: str = Field(description="Batch denomination")
    tradable_amount: str = Field(description="Total tradable supply")
    retired_amount: str = Field(description="Total retired supply")
    cancelled_amount: str = Field(description="Total cancelled supply")


# Response models for API endpoints

class ListCreditClassesResponse(BaseRegenModel):
    """Response for list credit classes query."""
    
    classes: List[CreditClass] = Field(description="List of credit classes")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class ListProjectsResponse(BaseRegenModel):
    """Response for list projects query."""
    
    projects: List[Project] = Field(description="List of projects")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class ListCreditBatchesResponse(BaseRegenModel):
    """Response for list credit batches query."""
    
    batches: List[CreditBatch] = Field(description="List of credit batches")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class ListCreditTypesResponse(BaseRegenModel):
    """Response for list credit types query."""
    
    credit_types: List[CreditType] = Field(description="List of credit types")
    pagination: Optional[dict] = Field(default=None, description="Pagination info")


class GetProjectResponse(BaseRegenModel):
    """Response for get project query."""
    
    project: Optional[Project] = Field(default=None, description="Project information")


class GetCreditClassResponse(BaseRegenModel):
    """Response for get credit class query."""
    
    class_info: Optional[CreditClass] = Field(default=None, description="Credit class information")


# Additional response types for tools

class CreditTypesResponse(BaseRegenModel):
    """Response for list credit types query."""
    credit_types: List[CreditType] = Field(default_factory=list, description="List of credit types")
    

class CreditClassesResponse(BaseRegenModel):
    """Response for list credit classes query."""
    classes: List[CreditClass] = Field(default_factory=list, description="List of credit classes")
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="Pagination info")


class ProjectsResponse(BaseRegenModel):
    """Response for list projects query."""
    projects: List[Project] = Field(default_factory=list, description="List of projects")
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="Pagination info")


class CreditBatchesResponse(BaseRegenModel):
    """Response for list credit batches query."""
    batches: List[CreditBatch] = Field(default_factory=list, description="List of credit batches")
    pagination: Optional[Dict[str, Any]] = Field(default=None, description="Pagination info")