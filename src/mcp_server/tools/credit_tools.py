"""Credit-related tools for Regen Network MCP server."""

import logging
from typing import Dict, Any

from ..client.regen_client import get_regen_client
from ..models.schemas import PaginationRequest as Pagination
from ..models.credit import (
    CreditType, 
    CreditClass, 
    Project, 
    CreditBatch,
    CreditTypesResponse,
    CreditClassesResponse,
    ProjectsResponse,
    CreditBatchesResponse
)

logger = logging.getLogger(__name__)


async def list_credit_types() -> Dict[str, Any]:
    """List all credit types enabled via governance on Regen Network.
    
    Credit types represent the fundamental categories of ecological benefits
    that can be measured and tokenized (e.g., Carbon, Biodiversity).
    
    Returns:
        dict: Response containing list of credit types with their abbreviations,
              names, units, and precision settings.
    """
    try:
        client = get_regen_client()
        response = await client.query_credit_types()
        
        # Parse credit types from response
        credit_types = []
        for ct_data in response.get("credit_types", []):
            credit_type = CreditType(
                abbreviation=ct_data["abbreviation"],
                name=ct_data["name"],
                unit=ct_data["unit"],
                precision=int(ct_data["precision"])
            )
            credit_types.append(credit_type)
        
        result = CreditTypesResponse(credit_types=credit_types)
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing credit types: {str(e)}")
        error_result = CreditTypesResponse(
            success=False,
            error=f"Failed to query credit types: {str(e)}",
            credit_types=[]
        )
        return error_result.dict()


async def list_credit_classes(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all credit classes (methodologies) on Regen Network.
    
    Credit classes define specific methodologies for measuring and verifying
    ecological benefits within a credit type (e.g., C01, C02 for different
    carbon methodologies).
    
    Args:
        limit: Maximum number of classes to return (1-1000, default 100)
        offset: Number of classes to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of credit classes with their IDs,
              admins, metadata, and associated credit types.
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
        
        response = await client.query_credit_classes(pagination)
        
        # Parse credit classes from response
        classes = []
        for class_data in response.get("classes", []):
            credit_class = CreditClass(
                key=class_data["key"],
                id=class_data["id"],
                admin=class_data["admin"],
                metadata=class_data["metadata"],
                credit_type_abbrev=class_data["credit_type_abbrev"]
            )
            classes.append(credit_class)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)
        
        result = CreditClassesResponse(
            classes=classes,
            pagination=pagination_response
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing credit classes: {str(e)}")
        error_result = CreditClassesResponse(
            success=False,
            error=f"Failed to query credit classes: {str(e)}",
            classes=[]
        )
        return error_result.dict()


async def list_projects(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all registered projects on Regen Network.
    
    Projects represent specific ecological initiatives that generate credits
    under approved methodologies. Each project is linked to a credit class
    and has geographic and temporal boundaries.
    
    Args:
        limit: Maximum number of projects to return (1-1000, default 100)
        offset: Number of projects to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of projects with their IDs, class linkage,
              geographic metadata, and lifecycle state information.
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
        
        response = await client.query_projects(pagination)
        
        # Parse projects from response
        projects = []
        for project_data in response.get("projects", []):
            project = Project(
                key=project_data["key"],
                id=project_data["id"],
                admin=project_data["admin"],
                class_key=project_data["class_key"],
                jurisdiction=project_data["jurisdiction"],
                metadata=project_data["metadata"],
                reference_id=project_data["reference_id"]
            )
            projects.append(project)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)
        
        result = ProjectsResponse(
            projects=projects,
            pagination=pagination_response
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        error_result = ProjectsResponse(
            success=False,
            error=f"Failed to query projects: {str(e)}",
            projects=[]
        )
        return error_result.dict()


async def list_credit_batches(
    limit: int = 100,
    offset: int = 0,
    count_total: bool = True,
    reverse: bool = False,
    key: str = None
) -> Dict[str, Any]:
    """List all issued credit batches on Regen Network.
    
    Credit batches represent specific issuances of credits from projects.
    Each batch has a unique denomination, vintage period, and operational
    status (open/closed for additional issuance).
    
    Args:
        limit: Maximum number of batches to return (1-1000, default 100)
        offset: Number of batches to skip for pagination (default 0)
        count_total: Whether to return total count (default True)
        reverse: Whether to reverse the order of results (default False)
        key: Pagination key for next page (optional)
        
    Returns:
        dict: Response containing list of credit batches with their batch denoms,
              project IDs, issuers, status, and vintage information.
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
        
        response = await client.query_credit_batches(pagination)
        
        # Parse credit batches from response
        batches = []
        for batch_data in response.get("batches", []):
            batch = CreditBatch(
                key=batch_data["key"],
                issuer=batch_data["issuer"],
                project_key=batch_data["project_key"],
                denom=batch_data["denom"],
                metadata=batch_data["metadata"],
                start_date=batch_data.get("start_date"),
                end_date=batch_data.get("end_date"),
                issuance_date=batch_data["issuance_date"],
                open=batch_data["open"]
            )
            batches.append(batch)
        
        # Parse pagination
        pagination_response = client._parse_pagination_response(response)
        
        result = CreditBatchesResponse(
            batches=batches,
            pagination=pagination_response
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Error listing credit batches: {str(e)}")
        error_result = CreditBatchesResponse(
            success=False,
            error=f"Failed to query credit batches: {str(e)}",
            batches=[]
        )
        return error_result.dict()