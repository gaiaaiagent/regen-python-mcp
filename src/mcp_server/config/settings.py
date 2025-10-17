"""Configuration settings for the Regen Python MCP server.

This module manages configuration from environment variables, defaults,
and provides type-safe access to settings throughout the application.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Information
    server_name: str = Field(default="regen-network-mcp", description="MCP server name")
    server_version: str = Field(default="0.1.0", description="Server version")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Regen Network Endpoints
    regen_rpc_endpoints: List[str] = Field(
        default=[
            "https://regen-rpc.polkachu.com",
            "https://rpc.cosmos.directory/regen",
            "https://rpc.regen.network",
        ],
        description="List of Regen Network RPC endpoints"
    )
    
    regen_rest_endpoints: List[str] = Field(
        default=[
            "https://regen-api.polkachu.com",
            "https://rest.cosmos.directory/regen", 
            "https://api.regen.network",
        ],
        description="List of Regen Network REST endpoints"
    )
    
    # Client Configuration
    request_timeout: float = Field(default=30.0, description="HTTP request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    
    # Pagination Defaults
    default_page_limit: int = Field(default=100, description="Default pagination limit")
    max_page_limit: int = Field(default=1000, description="Maximum pagination limit")
    
    # Caching (if implemented)
    enable_cache: bool = Field(default=False, description="Enable response caching")
    cache_ttl_seconds: int = Field(default=60, description="Cache TTL in seconds")
    
    # Security
    max_concurrent_requests: int = Field(default=100, description="Maximum concurrent requests")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable prefixes
        env_prefix = "REGEN_MCP_"
        
    @classmethod
    def parse_endpoint_list(cls, endpoints: str) -> List[str]:
        """Parse comma-separated endpoint list from environment variable."""
        if not endpoints:
            return []
        return [endpoint.strip() for endpoint in endpoints.split(",") if endpoint.strip()]
    
    def get_rpc_endpoints(self) -> List[str]:
        """Get RPC endpoints with environment override support."""
        env_endpoints = os.getenv("REGEN_RPC_ENDPOINTS") or os.getenv("RPC_ENDPOINTS")
        if env_endpoints:
            return self.parse_endpoint_list(env_endpoints)
        return self.regen_rpc_endpoints
    
    def get_rest_endpoints(self) -> List[str]:
        """Get REST endpoints with environment override support."""
        env_endpoints = os.getenv("REGEN_REST_ENDPOINTS") or os.getenv("REST_ENDPOINTS")
        if env_endpoints:
            return self.parse_endpoint_list(env_endpoints)
        return self.regen_rest_endpoints


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    This function uses LRU cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.
    
    Returns:
        Settings instance with configuration loaded from environment
    """
    return Settings()


def reload_settings() -> Settings:
    """Reload settings by clearing cache and creating new instance.
    
    Useful for testing or when configuration changes during runtime.
    
    Returns:
        Fresh Settings instance
    """
    get_settings.cache_clear()
    return get_settings()