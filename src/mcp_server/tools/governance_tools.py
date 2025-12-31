"""Governance module tools for Regen Network MCP server.

Note: Uses /cosmos/gov/v1 API (not v1beta1) because Regen Network upgraded
to gov v1 and some proposals can't be converted back to v1beta1 format.
"""

import logging
from typing import Dict, Any, Optional, Union

from ..client.regen_client import get_regen_client, Pagination, RegenClientError
from ..models.bank import validate_cosmos_address

logger = logging.getLogger(__name__)


class GovernanceToolsError(Exception):
    """Custom exception for governance tools errors."""
    pass


async def get_governance_proposal(proposal_id: Union[str, int]) -> Dict[str, Any]:
    """
    Get specific governance proposal.

    Args:
        proposal_id: Proposal ID (string or integer)

    Returns:
        Dict with proposal details or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        client = get_regen_client()
        response = await client.get_governance_proposal(proposal_str)
        return response

    except RegenClientError as e:
        logger.error(f"Governance proposal query failed: {e}")
        return {"error": f"Governance proposal query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_governance_proposal: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def list_governance_proposals(
    page: int = 1,
    limit: int = 100,
    proposal_status: Optional[str] = None,
    voter: Optional[str] = None,
    depositor: Optional[str] = None
) -> Dict[str, Any]:
    """
    List governance proposals with optional filters.

    Args:
        page: Page number for pagination
        limit: Number of results per page
        proposal_status: Filter by proposal status (optional)
        voter: Filter by voter address (optional)
        depositor: Filter by depositor address (optional)

    Returns:
        Dict with proposals list or error
    """
    try:
        pagination = Pagination(limit=limit, offset=(page - 1) * limit)

        client = get_regen_client()
        response = await client.list_governance_proposals(
            pagination, proposal_status, voter, depositor
        )
        return response

    except RegenClientError as e:
        logger.error(f"Governance proposals list query failed: {e}")
        return {"error": f"Governance proposals list query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_governance_proposals: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_governance_vote(proposal_id: Union[str, int], voter: str) -> Dict[str, Any]:
    """
    Get specific vote on a proposal.

    Args:
        proposal_id: Proposal ID (string or integer)
        voter: Voter account address

    Returns:
        Dict with vote details or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        if not validate_cosmos_address(voter):
            return {"error": f"Invalid voter address format: {voter}"}

        client = get_regen_client()
        response = await client.get_governance_vote(proposal_str, voter)
        return response

    except RegenClientError as e:
        logger.error(f"Governance vote query failed: {e}")
        return {"error": f"Governance vote query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_governance_vote: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def list_governance_votes(
    proposal_id: Union[str, int],
    page: int = 1,
    limit: int = 100
) -> Dict[str, Any]:
    """
    List votes for a specific proposal.

    Args:
        proposal_id: Proposal ID (string or integer)
        page: Page number for pagination
        limit: Number of results per page

    Returns:
        Dict with votes list or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        pagination = Pagination(limit=limit, offset=(page - 1) * limit)

        client = get_regen_client()
        response = await client.list_governance_votes(proposal_str, pagination)
        return response

    except RegenClientError as e:
        logger.error(f"Governance votes list query failed: {e}")
        return {"error": f"Governance votes list query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_governance_votes: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def list_governance_deposits(
    proposal_id: Union[str, int],
    page: int = 1,
    limit: int = 100
) -> Dict[str, Any]:
    """
    List deposits for a specific proposal.

    Args:
        proposal_id: Proposal ID (string or integer)
        page: Page number for pagination
        limit: Number of results per page

    Returns:
        Dict with deposits list or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        pagination = Pagination(limit=limit, offset=(page - 1) * limit)

        client = get_regen_client()
        response = await client.list_governance_deposits(proposal_str, pagination)
        return response

    except RegenClientError as e:
        logger.error(f"Governance deposits list query failed: {e}")
        return {"error": f"Governance deposits list query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in list_governance_deposits: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_governance_params(params_type: str) -> Dict[str, Any]:
    """
    Get governance parameters.

    Args:
        params_type: Type of parameters (voting, deposit, tally)

    Returns:
        Dict with governance parameters or error
    """
    try:
        valid_types = ["voting", "deposit", "tally"]
        if params_type not in valid_types:
            return {"error": f"Invalid params_type. Must be one of: {valid_types}"}

        client = get_regen_client()
        response = await client.get_governance_params(params_type)
        return response

    except RegenClientError as e:
        logger.error(f"Governance params query failed: {e}")
        return {"error": f"Governance params query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_governance_params: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_governance_deposit(proposal_id: Union[str, int], depositor: str) -> Dict[str, Any]:
    """
    Get specific deposit for a proposal.

    Args:
        proposal_id: Proposal ID (string or integer)
        depositor: Depositor account address

    Returns:
        Dict with deposit details or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        if not validate_cosmos_address(depositor):
            return {"error": f"Invalid depositor address format: {depositor}"}

        client = get_regen_client()
        response = await client.get_governance_deposit(proposal_str, depositor)
        return response

    except RegenClientError as e:
        logger.error(f"Governance deposit query failed: {e}")
        return {"error": f"Governance deposit query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_governance_deposit: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_governance_tally_result(proposal_id: Union[str, int]) -> Dict[str, Any]:
    """
    Get vote tally for a proposal.

    Args:
        proposal_id: Proposal ID (string or integer)

    Returns:
        Dict with tally results or error
    """
    try:
        # Convert to string if needed
        proposal_str = str(proposal_id)
        if not proposal_str.isdigit():
            return {"error": f"Invalid proposal ID format: {proposal_id}"}

        client = get_regen_client()
        response = await client.get_governance_tally_result(proposal_str)
        return response

    except RegenClientError as e:
        logger.error(f"Governance tally query failed: {e}")
        return {"error": f"Governance tally query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_governance_tally_result: {e}")
        return {"error": f"Unexpected error: {str(e)}"}