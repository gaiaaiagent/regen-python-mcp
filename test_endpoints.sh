#!/bin/bash
# Quick endpoint test script

BASE="http://localhost:8006"
PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" --max-time 15 "$url" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" --max-time 15 "$url" 2>&1)
    fi

    code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)

    if [ "$code" = "200" ]; then
        echo "✓ $name"
        ((PASS++))
    else
        echo "✗ $name [HTTP $code]"
        echo "  Error: $(echo "$body" | head -c 150)"
        ((FAIL++))
    fi
}

echo "========================================"
echo "Testing ChatGPT REST API v2 Endpoints"
echo "========================================"
echo ""

# Root
echo "--- INFO ---"
test_endpoint "GET /" "$BASE/"

# Ecocredits
echo ""
echo "--- ECOCREDITS ---"
test_endpoint "GET /ecocredits/types" "$BASE/ecocredits/types"
test_endpoint "GET /ecocredits/classes" "$BASE/ecocredits/classes?limit=3"
test_endpoint "GET /ecocredits/projects" "$BASE/ecocredits/projects?limit=3"
test_endpoint "GET /ecocredits/batches" "$BASE/ecocredits/batches?limit=3"

# Marketplace
echo ""
echo "--- MARKETPLACE ---"
test_endpoint "GET /marketplace/orders (list)" "$BASE/marketplace/orders?limit=3"
test_endpoint "GET /marketplace/orders?id=1" "$BASE/marketplace/orders?id=1"
test_endpoint "GET /marketplace/denoms" "$BASE/marketplace/denoms"

# Baskets
echo ""
echo "--- BASKETS ---"
test_endpoint "GET /baskets" "$BASE/baskets?limit=3"
test_endpoint "GET /baskets/fee" "$BASE/baskets/fee"
test_endpoint "GET /baskets/{denom}" "$BASE/baskets/eco.uC.NCT"

# Bank
echo ""
echo "--- BANK ---"
test_endpoint "GET /bank/accounts (list)" "$BASE/bank/accounts?limit=3"
test_endpoint "GET /bank/accounts?address=" "$BASE/bank/accounts?address=regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2"
test_endpoint "GET /bank/balances/{addr}" "$BASE/bank/balances/regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2"
test_endpoint "GET /bank/balances/{addr}?denom=" "$BASE/bank/balances/regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2?denom=uregen"
test_endpoint "GET /bank/balances/{addr}?spendable=" "$BASE/bank/balances/regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2?spendable=true"
test_endpoint "GET /bank/supply (all)" "$BASE/bank/supply?limit=3"
test_endpoint "GET /bank/supply?denom=" "$BASE/bank/supply?denom=uregen"
test_endpoint "GET /bank/metadata (all)" "$BASE/bank/metadata?limit=3"
test_endpoint "GET /bank/metadata?denom=" "$BASE/bank/metadata?denom=uregen"
test_endpoint "GET /bank/params" "$BASE/bank/params"

# Distribution
echo ""
echo "--- DISTRIBUTION ---"
test_endpoint "GET /distribution/params" "$BASE/distribution/params"
test_endpoint "GET /distribution/pool" "$BASE/distribution/pool"
test_endpoint "GET /distribution/validator/{addr}" "$BASE/distribution/validator/regenvaloper1qr8vwvh5yzf7t3cuu3xwfp46860c05qhx9ywhj"
test_endpoint "GET /distribution/delegator/{addr}" "$BASE/distribution/delegator/regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2"

# Governance
echo ""
echo "--- GOVERNANCE ---"
test_endpoint "GET /governance/params (all)" "$BASE/governance/params"
test_endpoint "GET /governance/params?type=voting" "$BASE/governance/params?type=voting"
test_endpoint "GET /governance/proposals (list)" "$BASE/governance/proposals?limit=3"
test_endpoint "GET /governance/proposals?id=1" "$BASE/governance/proposals?id=1"
test_endpoint "GET /governance/proposal/{id}/full" "$BASE/governance/proposal/1/full"
test_endpoint "GET /governance/pool" "$BASE/governance/pool"

# Analytics
echo ""
echo "--- ANALYTICS ---"
test_endpoint "GET /analytics/portfolio/{addr}" "$BASE/analytics/portfolio/regen1qqpcnttgs84wzfsm8jjht6dn27u0qpnexxqzy2"
test_endpoint "GET /analytics/trends" "$BASE/analytics/trends"
test_endpoint "POST /analytics/compare" "$BASE/analytics/compare" "POST" '{"class_ids":["C01","C02"]}'

echo ""
echo "========================================"
echo "Results: $PASS passed, $FAIL failed"
echo "========================================"
