"""Regen Network blockchain RPC client wrapper.

This module provides a high-level interface for interacting with the Regen Network
blockchain through REST and RPC endpoints. It handles connection pooling, retry logic,
endpoint fallbacks, and proper error handling.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
from pydantic import BaseModel, Field

from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class RegenClientError(Exception):
    """Base exception for Regen client errors."""
    pass


class NetworkError(RegenClientError):
    """Network-related errors."""
    pass


class ValidationError(RegenClientError):
    """Data validation errors."""
    pass


class Pagination(BaseModel):
    """Pagination parameters for blockchain queries."""

    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    count_total: Optional[bool] = Field(default=True, description="Whether to return total count")
    reverse: Optional[bool] = Field(default=False, description="Whether to reverse the order")

    def to_query_params(self) -> Dict[str, str]:
        """Convert pagination to query parameters."""
        params = {
            "pagination.limit": str(self.limit),
            "pagination.offset": str(self.offset),
        }
        if self.count_total is not None:
            params["pagination.count_total"] = str(self.count_total).lower()
        if self.reverse is not None:
            params["pagination.reverse"] = str(self.reverse).lower()
        return params


class PaginationResponse(BaseModel):
    """Pagination response metadata."""
    
    next_key: Optional[str] = Field(default=None, description="Key for next page")
    total: Optional[int] = Field(default=None, description="Total number of items")


class RegenClient:
    """High-level client for interacting with Regen Network blockchain.
    
    This client provides:
    - HTTP connection pooling and retry logic
    - Endpoint fallback mechanisms (RPC/REST)
    - Proper error handling and timeouts
    - Query methods for different Regen modules
    """
    
    def __init__(
        self,
        rpc_endpoints: Optional[List[str]] = None,
        rest_endpoints: Optional[List[str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize the Regen client.
        
        Args:
            rpc_endpoints: List of RPC endpoint URLs (for Tendermint queries)
            rest_endpoints: List of REST endpoint URLs (for gRPC-gateway queries)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        settings = get_settings()
        
        # Optimized endpoints based on reliability testing (2025-10-11)
        # All REST endpoints verified with working /classes, /projects, /batches APIs
        self.rpc_endpoints = rpc_endpoints or [
            "http://public-rpc.regen.vitwit.com:26657",      # Fastest: 94ms
            "http://mainnet.regen.network:26657",            # Fast: 185ms
            "https://regen-rpc.publicnode.com:443",          # Fast: 359ms
            "https://regen-rpc.polkachu.com",                # Reliable: 508ms
            "https://rpc-regen.ecostake.com",                # Reliable: 641ms
            "https://rpc.cosmos.directory/regen",            # Fallback: 1028ms
        ]

        self.rest_endpoints = rest_endpoints or [
            "http://public-rpc.regen.vitwit.com:1317",       # Fastest: 107ms ⚡
            "https://regen-rest.publicnode.com",             # Fast: 361ms
            "https://rest.cosmos.directory/regen",           # Fast: 567ms
            "https://regen-api.polkachu.com",                # Reliable: 635ms
            "https://rest-regen.ecostake.com",               # Reliable: 804ms
        ]
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # HTTP client with connection pooling
        self._http_client: Optional[httpx.AsyncClient] = None
        self._current_rpc_index = 0
        self._current_rest_index = 0
        
        logger.info(
            f"RegenClient initialized with {len(self.rpc_endpoints)} RPC and "
            f"{len(self.rest_endpoints)} REST endpoints (optimized for reliability)"
        )
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._http_client is None:
            limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
            timeout = httpx.Timeout(
                connect=10.0,
                read=self.timeout,
                write=10.0,
                pool=self.timeout + 5.0
            )
            
            self._http_client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                headers={"User-Agent": "regen-python-mcp/0.1.0"},
                follow_redirects=True,
            )
        
        return self._http_client
    
    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
            logger.info("RegenClient HTTP client closed")

    def _parse_pagination_response(self, response: Dict[str, Any]) -> Optional[PaginationResponse]:
        """Parse pagination information from API response.

        Args:
            response: API response dictionary

        Returns:
            PaginationResponse object or None if no pagination info present
        """
        pagination_data = response.get("pagination")
        if not pagination_data:
            return None

        return PaginationResponse(
            next_key=pagination_data.get("next_key"),
            total=int(pagination_data["total"]) if pagination_data.get("total") else None
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def _get_next_endpoint(self, endpoint_type: str = "rest") -> str:
        """Get next endpoint with round-robin fallback."""
        if endpoint_type == "rpc":
            endpoint = self.rpc_endpoints[self._current_rpc_index]
            self._current_rpc_index = (self._current_rpc_index + 1) % len(self.rpc_endpoints)
        else:
            endpoint = self.rest_endpoints[self._current_rest_index] 
            self._current_rest_index = (self._current_rest_index + 1) % len(self.rest_endpoints)
        
        return endpoint
    
    async def _make_request(
        self,
        path: str,
        endpoint_type: str = "rest",
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and endpoint fallback.
        
        Args:
            path: API path to append to base URL
            endpoint_type: Type of endpoint to use ("rest" or "rpc")
            params: Query parameters
            method: HTTP method
            
        Returns:
            Response JSON data
            
        Raises:
            NetworkError: If all endpoints fail
            ValidationError: If response validation fails
        """
        client = await self._get_http_client()
        last_exception = None
        
        # Try each endpoint with retries
        endpoints = self.rest_endpoints if endpoint_type == "rest" else self.rpc_endpoints
        
        for endpoint_idx in range(len(endpoints)):
            endpoint = self._get_next_endpoint(endpoint_type)
            url = urljoin(endpoint, path)
            
            for retry in range(self.max_retries):
                try:
                    logger.debug(f"Making request to {url} (attempt {retry + 1}/{self.max_retries})")
                    
                    response = await client.request(
                        method=method,
                        url=url,
                        params=params,
                    )
                    
                    # Check for HTTP errors
                    if response.status_code >= 400:
                        raise httpx.HTTPStatusError(
                            f"HTTP {response.status_code}", 
                            request=response.request, 
                            response=response
                        )
                    
                    # Parse JSON response
                    try:
                        data = response.json()
                        logger.debug(f"Successfully received response from {endpoint}")
                        return data
                    except Exception as e:
                        raise ValidationError(f"Failed to parse JSON response: {e}")
                
                except (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError) as e:
                    last_exception = e
                    logger.warning(f"Request failed for {url} (attempt {retry + 1}): {e}")
                    
                    if retry < self.max_retries - 1:
                        # Exponential backoff with jitter
                        delay = self.retry_delay * (2 ** retry) 
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    # Non-retryable error
                    raise NetworkError(f"Unexpected error for {url}: {e}")
        
        # All endpoints and retries failed
        raise NetworkError(f"All endpoints failed. Last error: {last_exception}")
    
    async def query_baskets(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query all ecocredit baskets on Regen Network.
        
        Args:
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing baskets and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                "/regen/ecocredit/basket/v1/baskets",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query baskets: {e}")
            raise
    
    async def query_basket(self, basket_denom: str) -> Dict[str, Any]:
        """Query specific ecocredit basket by denomination.
        
        Args:
            basket_denom: Basket denomination (e.g., "eco.uC.NCT")
            
        Returns:
            Dictionary containing basket information
        """
        try:
            response = await self._make_request(
                f"/regen/ecocredit/basket/v1/basket/{basket_denom}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query basket {basket_denom}: {e}")
            raise
    
    async def query_credit_classes(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query all credit classes on Regen Network.
        
        Args:
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing credit classes and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                "/regen/ecocredit/v1/classes",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query credit classes: {e}")
            raise
    
    async def query_credit_types(self) -> Dict[str, Any]:
        """Query all enabled credit types on Regen Network.
        
        Returns:
            Dictionary containing credit types
        """
        try:
            response = await self._make_request(
                "/regen/ecocredit/v1/credit-types",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query credit types: {e}")
            raise
    
    async def query_projects(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query all projects on Regen Network.
        
        Args:
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing projects and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                "/regen/ecocredit/v1/projects",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query projects: {e}")
            raise
    
    async def query_credit_batches(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query all credit batches on Regen Network.
        
        Args:
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing credit batches and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                "/regen/ecocredit/v1/batches",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query credit batches: {e}")
            raise
    
    async def query_sell_orders(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query all marketplace sell orders on Regen Network.
        
        Args:
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing sell orders and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                "/regen/ecocredit/marketplace/v1/sell-orders",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query sell orders: {e}")
            raise
    
    async def query_sell_order(self, sell_order_id: Union[int, str]) -> Dict[str, Any]:
        """Query specific sell order by ID.

        Args:
            sell_order_id: Sell order ID

        Returns:
            Dictionary containing sell order information
        """
        try:
            response = await self._make_request(
                f"/regen/ecocredit/marketplace/v1/sell-order/{sell_order_id}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query sell order {sell_order_id}: {e}")
            raise

    async def query_sell_orders_by_batch(
        self,
        batch_denom: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query sell orders for a specific credit batch.

        Args:
            batch_denom: Credit batch denomination
            pagination: Pagination parameters

        Returns:
            Dictionary containing sell orders for the batch
        """
        params = {"batch_denom": batch_denom}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/regen/ecocredit/marketplace/v1/sell-orders-by-batch",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query sell orders for batch {batch_denom}: {e}")
            raise

    async def query_sell_orders_by_seller(
        self,
        seller: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query sell orders by seller address.

        Args:
            seller: Seller address
            pagination: Pagination parameters

        Returns:
            Dictionary containing sell orders from the seller
        """
        params = {"seller": seller}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/regen/ecocredit/marketplace/v1/sell-orders-by-seller",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query sell orders for seller {seller}: {e}")
            raise

    async def query_allowed_denoms(self, pagination: Optional[Pagination] = None) -> Dict[str, Any]:
        """Query allowed payment denominations in marketplace.

        Args:
            pagination: Pagination parameters

        Returns:
            Dictionary containing allowed denominations
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/regen/ecocredit/marketplace/v1/allowed-denoms",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query allowed denoms: {e}")
            raise
    
    async def query_basket_balances(
        self, 
        basket_denom: str, 
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query all credit batch balances in a basket.
        
        Args:
            basket_denom: Basket denomination
            pagination: Pagination parameters
            
        Returns:
            Dictionary containing basket balances and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        
        try:
            response = await self._make_request(
                f"/regen/ecocredit/basket/v1/basket/{basket_denom}/balances",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query basket balances for {basket_denom}: {e}")
            raise
    
    async def query_basket_balance(
        self, 
        basket_denom: str, 
        batch_denom: str
    ) -> Dict[str, Any]:
        """Query balance of specific credit batch in a basket.
        
        Args:
            basket_denom: Basket denomination
            batch_denom: Credit batch denomination
            
        Returns:
            Dictionary containing specific basket balance information
        """
        try:
            response = await self._make_request(
                f"/regen/ecocredit/basket/v1/basket/{basket_denom}/balance/{batch_denom}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query basket balance for {basket_denom}/{batch_denom}: {e}")
            raise
    
    async def query_basket_fee(self) -> Dict[str, Any]:
        """Query current fee required to create a new basket.
        
        Returns:
            Dictionary containing basket creation fee information
        """
        try:
            response = await self._make_request(
                "/regen/ecocredit/basket/v1/basket-fee",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query basket fee: {e}")
            raise
    
    async def query_balance(self, address: str, denom: str) -> Dict[str, Any]:
        """Query balance of specific denom for an address.
        
        Args:
            address: Cosmos address
            denom: Token denomination
            
        Returns:
            Dictionary containing balance information
        """
        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/balances/{address}/by_denom",
                endpoint_type="rest",
                params={"denom": denom}
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query balance for {address}/{denom}: {e}")
            raise
    
    async def query_all_balances(
        self,
        address: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query all token balances for an address.

        Args:
            address: Cosmos address
            pagination: Pagination parameters

        Returns:
            Dictionary containing all balances and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/balances/{address}",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query all balances for {address}: {e}")
            raise

    async def query_spendable_balances(
        self,
        address: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query spendable balances for an address.

        Args:
            address: Cosmos address
            pagination: Pagination parameters

        Returns:
            Dictionary containing spendable balances and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/spendable_balances/{address}",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query spendable balances for {address}: {e}")
            raise

    async def query_total_supply(
        self,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query total supply of all tokens.

        Args:
            pagination: Pagination parameters

        Returns:
            Dictionary containing total supply and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/cosmos/bank/v1beta1/supply",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query total supply: {e}")
            raise

    async def query_supply_of(self, denom: str) -> Dict[str, Any]:
        """Query supply of specific denomination.

        Args:
            denom: Token denomination

        Returns:
            Dictionary containing supply information
        """
        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/supply/by_denom",
                endpoint_type="rest",
                params={"denom": denom}
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query supply of {denom}: {e}")
            raise

    async def query_denoms_metadata(
        self,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query metadata for all denominations.

        Args:
            pagination: Pagination parameters

        Returns:
            Dictionary containing denoms metadata and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/cosmos/bank/v1beta1/denoms_metadata",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query denoms metadata: {e}")
            raise

    async def query_denom_metadata(self, denom: str) -> Dict[str, Any]:
        """Query metadata for specific denomination.

        Args:
            denom: Token denomination

        Returns:
            Dictionary containing denom metadata
        """
        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/denoms_metadata/{denom}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query denom metadata for {denom}: {e}")
            raise

    async def query_denom_owners(
        self,
        denom: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query all holders of a denomination.

        Args:
            denom: Token denomination
            pagination: Pagination parameters

        Returns:
            Dictionary containing denom owners and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                f"/cosmos/bank/v1beta1/denom_owners/{denom}",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query denom owners for {denom}: {e}")
            raise

    async def query_bank_params(self) -> Dict[str, Any]:
        """Query bank module parameters.

        Returns:
            Dictionary containing bank parameters
        """
        try:
            response = await self._make_request(
                "/cosmos/bank/v1beta1/params",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query bank params: {e}")
            raise

    async def query_accounts(
        self,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query all accounts on the blockchain.

        Args:
            pagination: Pagination parameters

        Returns:
            Dictionary containing accounts and pagination info
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                "/cosmos/auth/v1beta1/accounts",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query accounts: {e}")
            raise

    async def query_account(self, address: str) -> Dict[str, Any]:
        """Query specific account by address.

        Args:
            address: Cosmos account address

        Returns:
            Dictionary containing account information
        """
        try:
            response = await self._make_request(
                f"/cosmos/auth/v1beta1/accounts/{address}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query account {address}: {e}")
            raise

    # Distribution module queries

    async def get_distribution_params(self) -> Dict[str, Any]:
        """Query distribution module parameters.

        Returns:
            Dictionary containing distribution parameters
        """
        try:
            response = await self._make_request(
                "/cosmos/distribution/v1beta1/params",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query distribution params: {e}")
            raise

    async def get_validator_outstanding_rewards(self, validator_address: str) -> Dict[str, Any]:
        """Query outstanding rewards for a validator.

        Args:
            validator_address: Validator operator address

        Returns:
            Dictionary containing validator outstanding rewards
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/validators/{validator_address}/outstanding_rewards",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query validator outstanding rewards for {validator_address}: {e}")
            raise

    async def get_validator_commission(self, validator_address: str) -> Dict[str, Any]:
        """Query commission for a validator.

        Args:
            validator_address: Validator operator address

        Returns:
            Dictionary containing validator commission
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/validators/{validator_address}/commission",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query validator commission for {validator_address}: {e}")
            raise

    async def get_validator_slashes(
        self,
        validator_address: str,
        starting_height: Optional[int] = None,
        ending_height: Optional[int] = None,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query slashing events for a validator.

        Args:
            validator_address: Validator operator address
            starting_height: Starting block height (optional)
            ending_height: Ending block height (optional)
            pagination: Pagination parameters

        Returns:
            Dictionary containing validator slashes
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        if starting_height is not None:
            params["starting_height"] = str(starting_height)
        if ending_height is not None:
            params["ending_height"] = str(ending_height)

        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/validators/{validator_address}/slashes",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query validator slashes for {validator_address}: {e}")
            raise

    async def get_delegation_rewards(
        self,
        delegator_address: str,
        validator_address: str
    ) -> Dict[str, Any]:
        """Query delegation rewards for specific delegator-validator pair.

        Args:
            delegator_address: Delegator account address
            validator_address: Validator operator address

        Returns:
            Dictionary containing delegation rewards
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/rewards/{validator_address}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query delegation rewards for {delegator_address}/{validator_address}: {e}")
            raise

    async def get_delegation_total_rewards(self, delegator_address: str) -> Dict[str, Any]:
        """Query total delegation rewards for a delegator.

        Args:
            delegator_address: Delegator account address

        Returns:
            Dictionary containing total delegation rewards
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/rewards",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query total delegation rewards for {delegator_address}: {e}")
            raise

    async def get_delegator_validators(self, delegator_address: str) -> Dict[str, Any]:
        """Query validators that a delegator is bonded to.

        Args:
            delegator_address: Delegator account address

        Returns:
            Dictionary containing delegator validators
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/validators",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query delegator validators for {delegator_address}: {e}")
            raise

    async def get_delegator_withdraw_address(self, delegator_address: str) -> Dict[str, Any]:
        """Query withdraw address for a delegator.

        Args:
            delegator_address: Delegator account address

        Returns:
            Dictionary containing delegator withdraw address
        """
        try:
            response = await self._make_request(
                f"/cosmos/distribution/v1beta1/delegators/{delegator_address}/withdraw_address",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query delegator withdraw address for {delegator_address}: {e}")
            raise

    async def get_community_pool(self) -> Dict[str, Any]:
        """Query community pool balance.

        Returns:
            Dictionary containing community pool balance
        """
        try:
            response = await self._make_request(
                "/cosmos/distribution/v1beta1/community_pool",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query community pool: {e}")
            raise

    # Governance module queries

    async def get_governance_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Query specific governance proposal.

        Args:
            proposal_id: Proposal ID

        Returns:
            Dictionary containing proposal details
        """
        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance proposal {proposal_id}: {e}")
            raise

    async def list_governance_proposals(
        self,
        pagination: Optional[Pagination] = None,
        proposal_status: Optional[str] = None,
        voter: Optional[str] = None,
        depositor: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query list of governance proposals with optional filters.

        Args:
            pagination: Pagination parameters
            proposal_status: Filter by proposal status (optional)
            voter: Filter by voter address (optional)
            depositor: Filter by depositor address (optional)

        Returns:
            Dictionary containing proposals list
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())
        if proposal_status:
            params["proposal_status"] = proposal_status
        if voter:
            params["voter"] = voter
        if depositor:
            params["depositor"] = depositor

        try:
            response = await self._make_request(
                "/cosmos/gov/v1beta1/proposals",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance proposals: {e}")
            raise

    async def get_governance_vote(self, proposal_id: str, voter: str) -> Dict[str, Any]:
        """Query specific vote on a proposal.

        Args:
            proposal_id: Proposal ID
            voter: Voter account address

        Returns:
            Dictionary containing vote details
        """
        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}/votes/{voter}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance vote for {proposal_id}/{voter}: {e}")
            raise

    async def list_governance_votes(
        self,
        proposal_id: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query list of votes for a specific proposal.

        Args:
            proposal_id: Proposal ID
            pagination: Pagination parameters

        Returns:
            Dictionary containing votes list
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}/votes",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance votes for {proposal_id}: {e}")
            raise

    async def list_governance_deposits(
        self,
        proposal_id: str,
        pagination: Optional[Pagination] = None
    ) -> Dict[str, Any]:
        """Query list of deposits for a specific proposal.

        Args:
            proposal_id: Proposal ID
            pagination: Pagination parameters

        Returns:
            Dictionary containing deposits list
        """
        params = {}
        if pagination:
            params.update(pagination.to_query_params())

        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}/deposits",
                endpoint_type="rest",
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance deposits for {proposal_id}: {e}")
            raise

    async def get_governance_params(self, params_type: str) -> Dict[str, Any]:
        """Query governance parameters.

        Args:
            params_type: Type of parameters (voting, deposit, tally)

        Returns:
            Dictionary containing governance parameters
        """
        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/params/{params_type}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance params {params_type}: {e}")
            raise

    async def get_governance_deposit(self, proposal_id: str, depositor: str) -> Dict[str, Any]:
        """Query specific deposit for a proposal.

        Args:
            proposal_id: Proposal ID
            depositor: Depositor account address

        Returns:
            Dictionary containing deposit details
        """
        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}/deposits/{depositor}",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance deposit for {proposal_id}/{depositor}: {e}")
            raise

    async def get_governance_tally_result(self, proposal_id: str) -> Dict[str, Any]:
        """Query vote tally for a proposal.

        Args:
            proposal_id: Proposal ID

        Returns:
            Dictionary containing tally results
        """
        try:
            response = await self._make_request(
                f"/cosmos/gov/v1beta1/proposals/{proposal_id}/tally",
                endpoint_type="rest"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to query governance tally for {proposal_id}: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of available endpoints.

        Returns:
            Dictionary containing health status of all endpoints
        """
        results = {
            "rpc_endpoints": {},
            "rest_endpoints": {},
            "timestamp": None,
        }

        import time
        results["timestamp"] = time.time()

        # Check REST endpoints
        for endpoint in self.rest_endpoints:
            try:
                url = urljoin(endpoint, "/cosmos/base/tendermint/v1beta1/node_info")
                client = await self._get_http_client()
                response = await client.get(url, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    results["rest_endpoints"][endpoint] = {
                        "status": "healthy",
                        "chain_id": data.get("default_node_info", {}).get("network"),
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                    }
                else:
                    results["rest_endpoints"][endpoint] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}"
                    }

            except Exception as e:
                results["rest_endpoints"][endpoint] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

        # Check RPC endpoints
        for endpoint in self.rpc_endpoints:
            try:
                url = urljoin(endpoint, "/status")
                client = await self._get_http_client()
                response = await client.get(url, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    results["rpc_endpoints"][endpoint] = {
                        "status": "healthy",
                        "chain_id": data.get("result", {}).get("node_info", {}).get("network"),
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                    }
                else:
                    results["rpc_endpoints"][endpoint] = {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status_code}"
                    }

            except Exception as e:
                results["rpc_endpoints"][endpoint] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

        return results


# Singleton client instance
_client_instance: Optional[RegenClient] = None


def get_regen_client() -> RegenClient:
    """Get singleton Regen client instance.

    Note: The client will lazily initialize its HTTP client on first use.
    This allows the client to be created outside of an async context,
    while the actual HTTP client is created when needed in async context.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = RegenClient()
    return _client_instance


async def close_regen_client() -> None:
    """Close singleton Regen client instance."""
    global _client_instance
    if _client_instance is not None:
        await _client_instance.close()
        _client_instance = None