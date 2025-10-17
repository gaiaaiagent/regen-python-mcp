"""Distribution module tools for Regen Network MCP server."""

import logging
from typing import Dict, Any, Optional, List

from ..client.regen_client import get_regen_client, Pagination, RegenClientError
from ..models.bank import validate_cosmos_address

logger = logging.getLogger(__name__)


class DistributionToolsError(Exception):
    """Custom exception for distribution tools errors."""
    pass


async def get_distribution_params() -> Dict[str, Any]:
    """
    Get distribution module parameters.

    Returns:
        Dict with distribution parameters or error
    """
    try:
        client = get_regen_client()
        response = await client.get_distribution_params()
        return response

    except RegenClientError as e:
        logger.error(f"Distribution params query failed: {e}")
        return {"error": f"Distribution query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_distribution_params: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_validator_outstanding_rewards(validator_address: str) -> Dict[str, Any]:
    """
    Get outstanding rewards for a validator.

    Args:
        validator_address: Validator operator address

    Returns:
        Dict with validator rewards or error
    """
    try:
        if not validator_address or not validator_address.startswith(("regenvaloper", "cosmosvaloper")):
            return {"error": f"Invalid validator address format: {validator_address}"}

        client = get_regen_client()
        response = await client.get_validator_outstanding_rewards(validator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Validator rewards query failed: {e}")
        return {"error": f"Validator rewards query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_validator_outstanding_rewards: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_validator_commission(validator_address: str) -> Dict[str, Any]:
    """
    Get commission for a validator.

    Args:
        validator_address: Validator operator address

    Returns:
        Dict with validator commission or error
    """
    try:
        if not validator_address or not validator_address.startswith(("regenvaloper", "cosmosvaloper")):
            return {"error": f"Invalid validator address format: {validator_address}"}

        client = get_regen_client()
        response = await client.get_validator_commission(validator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Validator commission query failed: {e}")
        return {"error": f"Validator commission query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_validator_commission: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_validator_slashes(
    validator_address: str,
    starting_height: Optional[int] = None,
    ending_height: Optional[int] = None,
    page: int = 1,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get slashing events for a validator.

    Args:
        validator_address: Validator operator address
        starting_height: Starting block height (optional)
        ending_height: Ending block height (optional)
        page: Page number for pagination
        limit: Number of results per page

    Returns:
        Dict with validator slashes or error
    """
    try:
        if not validator_address or not validator_address.startswith(("regenvaloper", "cosmosvaloper")):
            return {"error": f"Invalid validator address format: {validator_address}"}

        pagination = Pagination(limit=limit, offset=(page - 1) * limit)

        client = get_regen_client()
        response = await client.get_validator_slashes(
            validator_address, starting_height, ending_height, pagination
        )
        return response

    except RegenClientError as e:
        logger.error(f"Validator slashes query failed: {e}")
        return {"error": f"Validator slashes query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_validator_slashes: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_delegation_rewards(delegator_address: str, validator_address: str) -> Dict[str, Any]:
    """
    Get delegation rewards for specific delegator-validator pair.

    Args:
        delegator_address: Delegator account address
        validator_address: Validator operator address

    Returns:
        Dict with delegation rewards or error
    """
    try:
        if not validate_cosmos_address(delegator_address):
            return {"error": f"Invalid delegator address format: {delegator_address}"}

        if not validator_address or not validator_address.startswith(("regenvaloper", "cosmosvaloper")):
            return {"error": f"Invalid validator address format: {validator_address}"}

        client = get_regen_client()
        response = await client.get_delegation_rewards(delegator_address, validator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Delegation rewards query failed: {e}")
        return {"error": f"Delegation rewards query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_delegation_rewards: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_delegation_total_rewards(delegator_address: str) -> Dict[str, Any]:
    """
    Get total delegation rewards for a delegator.

    Args:
        delegator_address: Delegator account address

    Returns:
        Dict with total delegation rewards or error
    """
    try:
        if not validate_cosmos_address(delegator_address):
            return {"error": f"Invalid delegator address format: {delegator_address}"}

        client = get_regen_client()
        response = await client.get_delegation_total_rewards(delegator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Total delegation rewards query failed: {e}")
        return {"error": f"Total delegation rewards query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_delegation_total_rewards: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_delegator_validators(delegator_address: str) -> Dict[str, Any]:
    """
    Get validators that a delegator is bonded to.

    Args:
        delegator_address: Delegator account address

    Returns:
        Dict with delegator validators or error
    """
    try:
        if not validate_cosmos_address(delegator_address):
            return {"error": f"Invalid delegator address format: {delegator_address}"}

        client = get_regen_client()
        response = await client.get_delegator_validators(delegator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Delegator validators query failed: {e}")
        return {"error": f"Delegator validators query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_delegator_validators: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_delegator_withdraw_address(delegator_address: str) -> Dict[str, Any]:
    """
    Get withdraw address for a delegator.

    Args:
        delegator_address: Delegator account address

    Returns:
        Dict with withdraw address or error
    """
    try:
        if not validate_cosmos_address(delegator_address):
            return {"error": f"Invalid delegator address format: {delegator_address}"}

        client = get_regen_client()
        response = await client.get_delegator_withdraw_address(delegator_address)
        return response

    except RegenClientError as e:
        logger.error(f"Delegator withdraw address query failed: {e}")
        return {"error": f"Delegator withdraw address query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_delegator_withdraw_address: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


async def get_community_pool() -> Dict[str, Any]:
    """
    Get community pool balance.

    Returns:
        Dict with community pool balance or error
    """
    try:
        client = get_regen_client()
        response = await client.get_community_pool()
        return response

    except RegenClientError as e:
        logger.error(f"Community pool query failed: {e}")
        return {"error": f"Community pool query failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in get_community_pool: {e}")
        return {"error": f"Unexpected error: {str(e)}"}