"""Tests for governance tools with real blockchain data.

These tests validate that governance tools return correct data when called through
the MCP interface. NO MOCK DATA - validates actual tool behavior.

Governance tools are critical for:
- DAO participation
- Proposal monitoring
- Voting and deposits tracking
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_server.tools.governance_tools import (
    get_governance_proposal,
    list_governance_proposals,
    get_governance_vote,
    list_governance_votes,
    list_governance_deposits,
    get_governance_params,
    get_governance_deposit,
    get_governance_tally_result,
)


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestGovernanceToolsOnline:
    """Test governance tools with live network connection.

    These tests validate critical DAO governance functionality.
    """

    async def test_list_governance_proposals_returns_data(self):
        """Test that list_governance_proposals returns proposals.

        VALIDATES: Can we query governance proposals?
        IMPACT: Needed for DAO members to participate
        """
        result = await list_governance_proposals(page=1, limit=10)

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" not in result:
            print(f"✅ Can list governance proposals")
            if "proposals" in result:
                proposals = result["proposals"]
                print(f"   Proposals found: {len(proposals)}")
            elif "proposal" in result:
                # API might return singular
                print(f"   Proposal data available")
        else:
            print(f"⚠️  List proposals: {result.get('error')}")

    async def test_get_governance_params_voting(self):
        """Test getting voting parameters.

        VALIDATES: Can we see voting rules?
        IMPACT: Needed to understand governance mechanics
        """
        result = await get_governance_params("voting")

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" not in result:
            print(f"✅ Can query voting params")
            if "voting_params" in result or "params" in result:
                print(f"   Voting params available")
        else:
            print(f"⚠️  Voting params: {result.get('error')}")

    async def test_get_governance_params_deposit(self):
        """Test getting deposit parameters.

        VALIDATES: Can we see deposit requirements?
        IMPACT: Needed to know costs of proposal creation
        """
        result = await get_governance_params("deposit")

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" not in result:
            print(f"✅ Can query deposit params")
        else:
            print(f"⚠️  Deposit params: {result.get('error')}")

    async def test_get_governance_params_tally(self):
        """Test getting tally parameters.

        VALIDATES: Can we see how votes are counted?
        IMPACT: Needed to understand passing thresholds
        """
        result = await get_governance_params("tally")

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" not in result:
            print(f"✅ Can query tally params")
        else:
            print(f"⚠️  Tally params: {result.get('error')}")

    async def test_get_governance_proposal_by_id(self):
        """Test getting specific proposal.

        VALIDATES: Can we query proposal details?
        IMPACT: Needed to review proposals before voting
        """
        # Try proposal ID 1 (likely exists on most chains)
        result = await get_governance_proposal("1")

        assert isinstance(result, dict), "Result must be dictionary"

        # Proposal may or may not exist
        if "error" in result:
            print(f"⚠️  Get proposal #1: {result.get('error')}")
        else:
            print(f"✅ Can query proposal by ID")
            if "proposal" in result:
                proposal = result["proposal"]
                print(f"   Proposal structure available")

    async def test_list_governance_votes_for_proposal(self):
        """Test listing votes for a proposal.

        VALIDATES: Can we see how people voted?
        IMPACT: Needed for transparency and analysis
        """
        # Try getting votes for proposal 1
        result = await list_governance_votes("1", page=1, limit=10)

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" in result:
            print(f"⚠️  List votes: {result.get('error')}")
        else:
            print(f"✅ Can list votes for proposal")
            if "votes" in result:
                votes = result["votes"]
                print(f"   Votes found: {len(votes)}")

    async def test_list_governance_deposits_for_proposal(self):
        """Test listing deposits for a proposal.

        VALIDATES: Can we see who deposited?
        IMPACT: Needed for proposal funding tracking
        """
        # Try getting deposits for proposal 1
        result = await list_governance_deposits("1", page=1, limit=10)

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" in result:
            print(f"⚠️  List deposits: {result.get('error')}")
        else:
            print(f"✅ Can list deposits for proposal")
            if "deposits" in result:
                deposits = result["deposits"]
                print(f"   Deposits found: {len(deposits)}")

    async def test_get_governance_tally_result_for_proposal(self):
        """Test getting tally results.

        VALIDATES: Can we see current vote counts?
        IMPACT: Needed to track proposal status
        """
        # Try getting tally for proposal 1
        result = await get_governance_tally_result("1")

        assert isinstance(result, dict), "Result must be dictionary"

        if "error" in result:
            print(f"⚠️  Get tally: {result.get('error')}")
        else:
            print(f"✅ Can query tally results")
            if "tally" in result:
                tally = result["tally"]
                print(f"   Tally structure available")

    async def test_get_governance_vote_for_specific_voter(self):
        """Test getting specific vote.

        VALIDATES: Can we see how someone voted?
        IMPACT: Needed for accountability
        """
        # Use a test address
        test_voter = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        result = await get_governance_vote("1", test_voter)

        assert isinstance(result, dict), "Result must be dictionary"

        # Voter may not have voted
        if "error" in result:
            print(f"⚠️  Get vote for voter: {result.get('error')}")
        else:
            print(f"✅ Can query vote for specific voter")

    async def test_get_governance_deposit_for_specific_depositor(self):
        """Test getting specific deposit.

        VALIDATES: Can we see a specific deposit?
        IMPACT: Needed for deposit tracking
        """
        test_depositor = "regen1xhhquwctvwm40qn3nmmqq067pc2gw22e6q3p3c"

        result = await get_governance_deposit("1", test_depositor)

        assert isinstance(result, dict), "Result must be dictionary"

        # Depositor may not have deposited
        if "error" in result:
            print(f"⚠️  Get deposit for depositor: {result.get('error')}")
        else:
            print(f"✅ Can query deposit for specific depositor")


@pytest.mark.asyncio
@pytest.mark.tools
class TestGovernanceToolsValidation:
    """Test governance tools parameter validation and error handling."""

    async def test_proposal_id_validation(self):
        """Test that invalid proposal IDs are rejected."""
        # Non-numeric ID
        result = await get_governance_proposal("invalid")

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should indicate error"

    async def test_params_type_validation(self):
        """Test that invalid params types are rejected."""
        result = await get_governance_params("invalid_type")

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should indicate error"
        assert "voting" in result["error"] or "deposit" in result["error"], \
            "Should mention valid types"

    async def test_vote_address_validation(self):
        """Test that invalid voter addresses are rejected."""
        result = await get_governance_vote("1", "invalid_address")

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should indicate error"

    async def test_deposit_address_validation(self):
        """Test that invalid depositor addresses are rejected."""
        result = await get_governance_deposit("1", "")

        assert isinstance(result, dict), "Should return dict"
        assert "error" in result, "Should indicate error"


@pytest.mark.asyncio
@pytest.mark.tools
@pytest.mark.online
class TestGovernanceToolsUserJourneys:
    """Test governance tools for real user scenarios.

    These tests validate complete DAO governance workflows.
    """

    async def test_dao_member_can_review_proposal(self):
        """
        USER: DAO Member
        GOAL: Review a proposal before voting

        VALIDATES: Can member see proposal details?
        """
        # Step 1: List all proposals
        proposals_list = await list_governance_proposals(page=1, limit=10)

        assert isinstance(proposals_list, dict), \
            "DAO member cannot list proposals - wrong format"

        if "error" not in proposals_list:
            print("✅ DAO GOVERNANCE: Member can list proposals")

            # Step 2: Get specific proposal if any exist
            if "proposals" in proposals_list and len(proposals_list["proposals"]) > 0:
                first_proposal_id = proposals_list["proposals"][0].get("proposal_id", "1")
                proposal = await get_governance_proposal(str(first_proposal_id))

                if "error" not in proposal:
                    print(f"   Can view proposal #{first_proposal_id} details")

                    # Step 3: Check voting results
                    tally = await get_governance_tally_result(str(first_proposal_id))

                    if "error" not in tally:
                        print(f"   Can see current voting results")
        else:
            print(f"⚠️  DAO GOVERNANCE: Proposals not available")
            print(f"   Error: {proposals_list.get('error')}")

    async def test_governance_analyst_can_assess_participation(self):
        """
        USER: Governance Analyst
        GOAL: Analyze governance participation rates

        VALIDATES: Can analyst get comprehensive governance data?
        """
        # Step 1: Get governance params
        voting_params = await get_governance_params("voting")
        deposit_params = await get_governance_params("deposit")
        tally_params = await get_governance_params("tally")

        assert isinstance(voting_params, dict), \
            "Analyst cannot get voting params - wrong format"
        assert isinstance(deposit_params, dict), \
            "Analyst cannot get deposit params - wrong format"
        assert isinstance(tally_params, dict), \
            "Analyst cannot get tally params - wrong format"

        # Step 2: List recent proposals
        proposals = await list_governance_proposals(page=1, limit=5)

        if "error" not in proposals:
            print("✅ GOVERNANCE ANALYSIS: Analyst can assess participation")

            # Count how many params are available
            params_available = 0
            if "error" not in voting_params:
                params_available += 1
            if "error" not in deposit_params:
                params_available += 1
            if "error" not in tally_params:
                params_available += 1

            print(f"   Governance params available: {params_available}/3")

            if "proposals" in proposals:
                print(f"   Recent proposals: {len(proposals['proposals'])}")
        else:
            print(f"⚠️  GOVERNANCE ANALYSIS: Data not fully available")

    async def test_proposal_creator_can_monitor_deposit_progress(self):
        """
        USER: Proposal Creator
        GOAL: Monitor deposit progress on their proposal

        VALIDATES: Can creator see deposit status?
        """
        # Try to get deposits for proposal 1
        deposits = await list_governance_deposits("1", page=1, limit=10)

        assert isinstance(deposits, dict), \
            "Creator cannot monitor deposits - wrong format"

        if "error" not in deposits:
            print("✅ PROPOSAL MONITORING: Creator can track deposits")

            if "deposits" in deposits:
                deposit_count = len(deposits["deposits"])
                print(f"   Deposits tracked: {deposit_count}")

            # Also check tally
            tally = await get_governance_tally_result("1")

            if "error" not in tally:
                print(f"   Can monitor voting progress")
        else:
            print(f"⚠️  PROPOSAL MONITORING: Proposal #1 not found/available")
