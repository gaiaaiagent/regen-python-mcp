"""Credit-related tools for Regen Network MCP server."""

import asyncio
import logging
from typing import Dict, Any

from ..client.regen_client import get_regen_client, Pagination
from ..client.metadata_graph_client import resolve_metadata_summary
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
                abbreviation=ct_data.get("abbreviation", ""),
                name=ct_data.get("name", ""),
                unit=ct_data.get("unit", ""),
                precision=int(ct_data.get("precision", 0))
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
    reverse: bool = False
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
            reverse=reverse
        )
        
        response = await client.query_credit_classes(pagination)
        
        # Parse credit classes from response
        class_rows = response.get("classes", [])
        summaries = await asyncio.gather(
            *[
                resolve_metadata_summary((class_data or {}).get("metadata", ""))
                for class_data in class_rows
            ],
            return_exceptions=True,
        )

        classes = []
        for class_data, summary_result in zip(class_rows, summaries):
            summary = summary_result if isinstance(summary_result, dict) else None
            credit_class = CreditClass(
                id=class_data.get("id", ""),
                admin=class_data.get("admin", ""),
                metadata=class_data.get("metadata", ""),
                credit_type_abbrev=class_data.get("credit_type_abbrev", ""),
                name=(summary.get("name") if summary else None),
                source_registry=(summary.get("source_registry") if summary else None),
            )
            classes.append(credit_class)

        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = CreditClassesResponse(
            classes=classes,
            pagination=pagination_response.dict() if pagination_response else None
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
    reverse: bool = False
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
            reverse=reverse
        )
        
        response = await client.query_projects(pagination)
        
        # Parse projects from response
        projects = []
        for project_data in response.get("projects", []):
            project = Project(
                id=project_data.get("id", ""),
                admin=project_data.get("admin", ""),
                class_id=project_data.get("class_id", ""),
                jurisdiction=project_data.get("jurisdiction", ""),
                metadata=project_data.get("metadata", ""),
                reference_id=project_data.get("reference_id", "")
            )
            projects.append(project)

        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = ProjectsResponse(
            projects=projects,
            pagination=pagination_response.dict() if pagination_response else None
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
    reverse: bool = False
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
            reverse=reverse
        )
        
        response = await client.query_credit_batches(pagination)
        
        # Parse credit batches from response
        batches = []
        for batch_data in response.get("batches", []):
            batch = CreditBatch(
                issuer=batch_data.get("issuer", ""),
                project_id=batch_data.get("project_id", ""),
                denom=batch_data.get("denom", ""),
                metadata=batch_data.get("metadata", ""),
                start_date=batch_data.get("start_date"),
                end_date=batch_data.get("end_date"),
                issuance_date=batch_data.get("issuance_date"),
                open=batch_data.get("open", False)
            )
            batches.append(batch)

        # Parse pagination
        pagination_response = client._parse_pagination_response(response)

        result = CreditBatchesResponse(
            batches=batches,
            pagination=pagination_response.dict() if pagination_response else None
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


async def get_credit_class_supply(class_id: str) -> Dict[str, Any]:
    """Get aggregated supply/retirement data for all batches in a credit class.

    Args:
        class_id: Credit class ID (e.g., "MBS01", "C01", "BT01")

    Returns:
        dict: Aggregated totals (total_issued, total_tradable, total_retired,
              retirement_rate_pct) plus per-batch breakdown.
    """
    try:
        client = get_regen_client()
        pagination = Pagination(limit=1000, offset=0)

        # Get all projects and filter to this class
        projects_response = await client.query_projects(pagination)
        class_projects = [
            p for p in projects_response.get("projects", [])
            if p.get("class_id") == class_id
        ]
        if not class_projects:
            return {"error": f"Credit class '{class_id}' not found or has no projects"}

        # Get all batches and filter to this class via project_id
        batches_response = await client.query_credit_batches(pagination)
        project_ids = {p["id"] for p in class_projects}
        class_batches = [
            b for b in batches_response.get("batches", [])
            if b.get("project_id") in project_ids
        ]

        # Aggregate supply (raw batch response includes tradable_amount, retired_amount, etc.)
        total_issued = sum(float(b.get("total_amount", 0)) for b in class_batches)
        total_tradable = sum(float(b.get("tradable_amount", 0)) for b in class_batches)
        total_retired = sum(float(b.get("retired_amount", 0)) for b in class_batches)
        total_cancelled = sum(float(b.get("cancelled_amount", 0)) for b in class_batches)
        retirement_rate = (total_retired / total_issued * 100) if total_issued > 0 else 0

        return {
            "class_id": class_id,
            "project_count": len(class_projects),
            "batch_count": len(class_batches),
            "supply": {
                "total_issued": total_issued,
                "total_tradable": total_tradable,
                "total_retired": total_retired,
                "total_cancelled": total_cancelled,
                "retirement_rate_pct": round(retirement_rate, 2),
            },
            "batches": [
                {
                    "denom": b.get("denom"),
                    "project_id": b.get("project_id"),
                    "total_amount": float(b.get("total_amount", 0)),
                    "tradable_amount": float(b.get("tradable_amount", 0)),
                    "retired_amount": float(b.get("retired_amount", 0)),
                    "cancelled_amount": float(b.get("cancelled_amount", 0)),
                    "start_date": b.get("start_date"),
                    "end_date": b.get("end_date"),
                }
                for b in class_batches
            ],
        }

    except Exception as e:
        logger.error(f"Error getting credit class supply for {class_id}: {str(e)}")
        return {"error": f"Failed to query credit class supply: {str(e)}"}
