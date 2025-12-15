#!/usr/bin/env python3
"""Automated test suite for ChatGPT REST API v2.

Tests all 26 endpoints with various parameter combinations.
"""

import asyncio
import httpx
import json
from dataclasses import dataclass
from typing import Optional, Any

BASE_URL = "http://localhost:8006"

# Known valid test data from Regen Network
TEST_ADDRESS = "regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2"
TEST_VALIDATOR = "regenvaloper1qr8vwvh5yzf7t3cuu3xwfp46860c05qhx9ywhj"
TEST_BATCH_DENOM = "C02-001-20180101-20181231-001"  # Batch with active sell orders
TEST_BASKET_DENOM = "eco.uC.NCT"
TEST_DENOM = "uregen"
TEST_SELL_ORDER_ID = 33  # Known existing sell order


@dataclass
class TestResult:
    endpoint: str
    method: str
    params: dict
    success: bool
    status_code: int
    error: Optional[str] = None
    response_preview: Optional[str] = None


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    params: dict = None,
    json_body: dict = None,
    description: str = ""
) -> TestResult:
    """Test a single endpoint."""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = await client.get(url, params=params, timeout=30.0)
        elif method == "POST":
            response = await client.post(url, json=json_body, timeout=30.0)
        else:
            raise ValueError(f"Unknown method: {method}")

        success = response.status_code == 200
        error = None
        preview = None

        if not success:
            try:
                error = response.text[:200]
            except:
                error = f"HTTP {response.status_code}"
        else:
            try:
                data = response.json()
                preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
            except:
                preview = response.text[:100]

        return TestResult(
            endpoint=f"{method} {path}" + (f" ({description})" if description else ""),
            method=method,
            params=params or json_body or {},
            success=success,
            status_code=response.status_code,
            error=error,
            response_preview=preview
        )

    except httpx.TimeoutException:
        return TestResult(
            endpoint=f"{method} {path}" + (f" ({description})" if description else ""),
            method=method,
            params=params or json_body or {},
            success=False,
            status_code=0,
            error="TIMEOUT"
        )
    except Exception as e:
        return TestResult(
            endpoint=f"{method} {path}" + (f" ({description})" if description else ""),
            method=method,
            params=params or json_body or {},
            success=False,
            status_code=0,
            error=str(e)
        )


async def run_all_tests() -> list[TestResult]:
    """Run all endpoint tests."""
    results = []

    async with httpx.AsyncClient() as client:
        # =====================================================================
        # 1. ROOT
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/", description="API info"))

        # =====================================================================
        # 2-5. ECOCREDITS (4 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/ecocredits/types", description="credit types"))
        results.append(await test_endpoint(client, "GET", "/ecocredits/classes", params={"limit": 5}, description="credit classes"))
        results.append(await test_endpoint(client, "GET", "/ecocredits/projects", params={"limit": 5}, description="projects"))
        results.append(await test_endpoint(client, "GET", "/ecocredits/batches", params={"limit": 5}, description="batches"))

        # =====================================================================
        # 6-7. MARKETPLACE (2 endpoints)
        # =====================================================================
        # Test marketplace orders with different query params
        results.append(await test_endpoint(client, "GET", "/marketplace/orders", params={"limit": 5}, description="list all orders"))
        results.append(await test_endpoint(client, "GET", "/marketplace/orders", params={"id": TEST_SELL_ORDER_ID}, description="order by ID"))
        # NOTE: The following two tests fail with HTTP 501 - the Regen REST API doesn't implement these endpoints
        results.append(await test_endpoint(client, "GET", "/marketplace/orders", params={"batch": TEST_BATCH_DENOM, "limit": 5}, description="orders by batch [EXPECTED FAIL: upstream 501]"))
        results.append(await test_endpoint(client, "GET", "/marketplace/orders", params={"seller": TEST_ADDRESS, "limit": 5}, description="orders by seller [EXPECTED FAIL: upstream 501]"))
        results.append(await test_endpoint(client, "GET", "/marketplace/denoms", description="allowed denoms"))

        # =====================================================================
        # 8-10. BASKETS (3 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/baskets", params={"limit": 5}, description="list baskets"))
        results.append(await test_endpoint(client, "GET", "/baskets/fee", description="basket fee"))
        results.append(await test_endpoint(client, "GET", f"/baskets/{TEST_BASKET_DENOM}", description="get basket"))
        results.append(await test_endpoint(client, "GET", f"/baskets/{TEST_BASKET_DENOM}", params={"include_balances": True, "limit": 5}, description="basket with balances"))

        # =====================================================================
        # 11-15. BANK (5 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/bank/accounts", params={"limit": 5}, description="list accounts"))
        results.append(await test_endpoint(client, "GET", "/bank/accounts", params={"address": TEST_ADDRESS}, description="get account"))
        results.append(await test_endpoint(client, "GET", f"/bank/balances/{TEST_ADDRESS}", description="all balances"))
        results.append(await test_endpoint(client, "GET", f"/bank/balances/{TEST_ADDRESS}", params={"denom": TEST_DENOM}, description="specific balance"))
        results.append(await test_endpoint(client, "GET", f"/bank/balances/{TEST_ADDRESS}", params={"spendable": True}, description="spendable balances"))
        results.append(await test_endpoint(client, "GET", "/bank/supply", params={"limit": 5}, description="total supply"))
        results.append(await test_endpoint(client, "GET", "/bank/supply", params={"denom": TEST_DENOM}, description="specific supply"))
        results.append(await test_endpoint(client, "GET", "/bank/metadata", params={"limit": 5}, description="all metadata"))
        results.append(await test_endpoint(client, "GET", "/bank/metadata", params={"denom": TEST_DENOM}, description="specific metadata"))
        results.append(await test_endpoint(client, "GET", "/bank/metadata", params={"denom": TEST_DENOM, "include_owners": True, "limit": 5}, description="metadata with owners"))
        results.append(await test_endpoint(client, "GET", "/bank/params", description="bank params"))

        # =====================================================================
        # 16-19. DISTRIBUTION (4 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/distribution/params", description="distribution params"))
        results.append(await test_endpoint(client, "GET", "/distribution/pool", description="community pool"))
        results.append(await test_endpoint(client, "GET", f"/distribution/validator/{TEST_VALIDATOR}", description="validator distribution"))
        results.append(await test_endpoint(client, "GET", f"/distribution/delegator/{TEST_ADDRESS}", description="delegator all info"))
        # NOTE: This test fails because the test address has no delegations to this validator
        results.append(await test_endpoint(client, "GET", f"/distribution/delegator/{TEST_ADDRESS}", params={"validator": TEST_VALIDATOR}, description="delegator specific validator [EXPECTED FAIL: no delegation]"))

        # =====================================================================
        # 20-23. GOVERNANCE (4 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", "/governance/params", description="all gov params"))
        results.append(await test_endpoint(client, "GET", "/governance/params", params={"type": "voting"}, description="voting params"))
        results.append(await test_endpoint(client, "GET", "/governance/params", params={"type": "deposit"}, description="deposit params"))
        results.append(await test_endpoint(client, "GET", "/governance/params", params={"type": "tally"}, description="tally params"))
        results.append(await test_endpoint(client, "GET", "/governance/proposals", params={"limit": 5}, description="list proposals"))
        results.append(await test_endpoint(client, "GET", "/governance/proposals", params={"id": 1}, description="get proposal by ID"))
        results.append(await test_endpoint(client, "GET", "/governance/proposal/1/full", description="full proposal details"))
        results.append(await test_endpoint(client, "GET", "/governance/pool", description="community pool (gov alias)"))

        # =====================================================================
        # 24-26. ANALYTICS (3 endpoints)
        # =====================================================================
        results.append(await test_endpoint(client, "GET", f"/analytics/portfolio/{TEST_ADDRESS}", description="portfolio analysis"))
        results.append(await test_endpoint(client, "GET", "/analytics/trends", description="market trends"))
        results.append(await test_endpoint(client, "POST", "/analytics/compare", json_body={"class_ids": ["C01", "C02"]}, description="compare methodologies"))

    return results


def print_results(results: list[TestResult]):
    """Print test results in a formatted table."""
    print("\n" + "=" * 100)
    print("CHATGPT REST API v2 - TEST RESULTS")
    print("=" * 100)

    passed = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    expected_failures = [r for r in failed if "EXPECTED FAIL" in r.endpoint]
    unexpected_failures = [r for r in failed if "EXPECTED FAIL" not in r.endpoint]

    print(f"\nTotal: {len(results)} | Passed: {len(passed)} | Failed: {len(failed)} (expected: {len(expected_failures)}, unexpected: {len(unexpected_failures)})")
    print("-" * 100)

    # Print passed tests
    if passed:
        print("\n✅ PASSED TESTS:")
        for r in passed:
            print(f"  ✓ {r.endpoint}")

    # Print expected failures (upstream limitations)
    if expected_failures:
        print("\n⚠️  EXPECTED FAILURES (upstream API limitations):")
        for r in expected_failures:
            print(f"  ⚠ {r.endpoint}")

    # Print unexpected failures with details
    if unexpected_failures:
        print("\n❌ UNEXPECTED FAILURES:")
        for r in unexpected_failures:
            print(f"\n  ✗ {r.endpoint}")
            print(f"    Status: {r.status_code}")
            print(f"    Error: {r.error}")

    print("\n" + "=" * 100)

    # Only return False for unexpected failures
    return len(unexpected_failures) == 0


if __name__ == "__main__":
    print("Starting API endpoint tests...")
    results = asyncio.run(run_all_tests())
    all_passed = print_results(results)
    exit(0 if all_passed else 1)
