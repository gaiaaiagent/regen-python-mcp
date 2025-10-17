"""Pydantic models for advanced analytics and resource responses.

Type-safe models for analytics tools, resource responses, and performance metrics.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Set, Union
from pydantic import BaseModel, Field, validator

from .schemas import BaseRegenModel


# Analytics Models

class ImpactMetrics(BaseModel):
    """Environmental impact metrics."""
    total_co2_tons: float = Field(ge=0, description="Total CO2 impact in tons")
    verified_tons: float = Field(ge=0, description="Verified CO2 tons")
    additionality_score: float = Field(ge=0, le=100, description="Additionality score (0-100)")
    vintage_quality: float = Field(ge=0, description="Vintage quality score")
    geographic_diversity: List[str] = Field(default_factory=list, description="Geographic regions")
    methodology_diversity: List[str] = Field(default_factory=list, description="Methodologies used")


class BiodiversityMetrics(BaseModel):
    """Biodiversity impact metrics."""
    total_bio_units: float = Field(ge=0, description="Total biodiversity units")
    habitat_types: List[str] = Field(default_factory=list, description="Habitat types protected")
    species_protection: List[str] = Field(default_factory=list, description="Species protected")
    ecosystem_services: List[str] = Field(default_factory=list, description="Ecosystem services")
    conservation_area: float = Field(ge=0, description="Conservation area in hectares")


class CrossCuttingImpacts(BaseModel):
    """Cross-cutting social and economic impacts."""
    social_benefits: List[str] = Field(default_factory=list, description="Social benefits")
    economic_benefits: List[str] = Field(default_factory=list, description="Economic benefits")
    sdg_alignment: List[str] = Field(default_factory=list, description="SDG alignment")
    co_benefits_score: float = Field(ge=0, description="Co-benefits score")


class PortfolioComposition(BaseModel):
    """Portfolio composition breakdown."""
    credit_types: Dict[str, float] = Field(default_factory=dict, description="Credits by type")
    jurisdictions: Dict[str, float] = Field(default_factory=dict, description="Credits by jurisdiction")
    project_types: Dict[str, float] = Field(default_factory=dict, description="Credits by project type")
    vintage_distribution: Dict[int, float] = Field(default_factory=dict, description="Credits by vintage year")
    total_credits: float = Field(ge=0, description="Total credit amount")


class DiversificationMetrics(BaseModel):
    """Portfolio diversification metrics."""
    type_diversity: int = Field(ge=0, description="Number of credit types")
    geographic_diversity: int = Field(ge=0, description="Number of jurisdictions")
    temporal_diversity: int = Field(ge=0, description="Number of vintage years")
    methodology_diversity: int = Field(ge=0, description="Number of methodologies")
    concentration_risk: float = Field(ge=0, le=1, description="Concentration risk (HHI)")


class OptimizationRecommendation(BaseModel):
    """Portfolio optimization recommendation."""
    type: str = Field(description="Recommendation type")
    priority: Literal["high", "medium", "low"] = Field(description="Priority level")
    message: str = Field(description="Recommendation message")
    specific_action: Optional[str] = Field(None, description="Specific action to take")


class RiskAssessment(BaseModel):
    """Risk assessment metrics."""
    concentration_risk: Literal["high", "medium", "low"] = Field(description="Concentration risk level")
    diversification_score: float = Field(ge=0, description="Diversification score")
    liquidity_risk: Literal["high", "medium", "low"] = Field(description="Liquidity risk level")
    vintage_risk: Literal["high", "medium", "low"] = Field(description="Vintage risk level")


class PortfolioImpactAnalysis(BaseRegenModel):
    """Complete portfolio impact analysis response."""
    address: str = Field(description="Portfolio address analyzed")
    impact_analysis: Dict[str, Any] = Field(description="Impact analysis breakdown")
    portfolio_composition: PortfolioComposition = Field(description="Portfolio composition")
    diversification_metrics: DiversificationMetrics = Field(description="Diversification metrics")
    optimization_recommendations: List[OptimizationRecommendation] = Field(description="Optimization recommendations")
    risk_assessment: RiskAssessment = Field(description="Risk assessment")
    metadata: Dict[str, Any] = Field(description="Analysis metadata")


# Market Analytics Models

class CreditTypeStats(BaseModel):
    """Market statistics for a credit type."""
    orders: int = Field(ge=0, description="Number of active orders")
    volume: float = Field(ge=0, description="Total volume for sale")
    value: float = Field(ge=0, description="Total value in market")
    unique_batches: int = Field(ge=0, description="Number of unique batches")
    pricing: Dict[str, float] = Field(description="Price statistics")
    market_share: Dict[str, float] = Field(description="Market share metrics")


class MarketOverview(BaseModel):
    """Overall market overview metrics."""
    total_active_orders: int = Field(ge=0, description="Total active orders")
    total_credits_for_sale: float = Field(ge=0, description="Total credits for sale")
    unique_credit_types: int = Field(ge=0, description="Number of unique credit types")
    total_credit_classes: int = Field(ge=0, description="Total credit classes")
    total_credit_batches: int = Field(ge=0, description="Total credit batches")


class PriceRange(BaseModel):
    """Price range information."""
    range: str = Field(description="Price range description")
    min_price: float = Field(ge=0, description="Minimum price in range")
    max_price: float = Field(ge=0, description="Maximum price in range")
    order_count: int = Field(ge=0, description="Number of orders in range")


class MarketDepth(BaseModel):
    """Market depth analysis."""
    price_ranges: List[PriceRange] = Field(description="Price range breakdown")
    volume_distribution: Dict[str, Any] = Field(description="Volume distribution")


class LiquidityMetrics(BaseModel):
    """Market liquidity metrics."""
    average_order_size: float = Field(ge=0, description="Average order size")
    market_concentration: Dict[str, Any] = Field(description="Market concentration metrics")


class MarketSentiment(BaseModel):
    """Market sentiment indicators."""
    overall_sentiment: Literal["bullish", "neutral", "bearish"] = Field(description="Overall market sentiment")
    market_activity: Literal["high", "active", "moderate", "low"] = Field(description="Market activity level")
    price_discovery: Literal["healthy", "limited", "poor"] = Field(description="Price discovery quality")
    competition_level: Literal["competitive", "moderate", "limited"] = Field(description="Competition level")
    market_maturity: Literal["mature", "developing", "early"] = Field(description="Market maturity level")


class MarketTrendsAnalysis(BaseRegenModel):
    """Complete market trends analysis response."""
    analysis_period: Dict[str, Any] = Field(description="Analysis time period")
    current_market_snapshot: Dict[str, Any] = Field(description="Current market data")
    trend_analysis: Dict[str, Any] = Field(description="Trend analysis results")
    projections_and_insights: Dict[str, Any] = Field(description="Market projections")
    methodology: Dict[str, Any] = Field(description="Analysis methodology")
    metadata: Dict[str, Any] = Field(description="Analysis metadata")


# Credit Methodology Comparison Models

class MethodologyScores(BaseModel):
    """Methodology quality scores."""
    additionality: float = Field(ge=0, le=100, description="Additionality score")
    measurability: float = Field(ge=0, le=100, description="Measurability score")
    permanence: float = Field(ge=0, le=100, description="Permanence score")
    co_benefits: float = Field(ge=0, le=100, description="Co-benefits score")
    scalability: float = Field(ge=0, le=100, description="Scalability score")


class MarketPerformance(BaseModel):
    """Market performance metrics."""
    liquidity_score: float = Field(ge=0, le=100, description="Liquidity score")
    pricing_attractiveness: float = Field(ge=0, le=100, description="Pricing attractiveness")
    market_adoption: float = Field(ge=0, le=100, description="Market adoption score")
    supply_health: float = Field(ge=0, le=100, description="Supply health score")


class SupplyMetrics(BaseModel):
    """Credit supply metrics."""
    total_issued: float = Field(ge=0, description="Total credits issued")
    total_tradable: float = Field(ge=0, description="Total tradable credits")
    total_retired: float = Field(ge=0, description="Total retired credits")
    retirement_rate: float = Field(ge=0, le=100, description="Retirement rate percentage")


class AdoptionMetrics(BaseModel):
    """Adoption metrics."""
    total_projects: int = Field(ge=0, description="Total projects")
    total_batches: int = Field(ge=0, description="Total batches")
    active_market_orders: int = Field(ge=0, description="Active market orders")
    geographic_diversity: int = Field(ge=0, description="Geographic diversity")


class PricingInfo(BaseModel):
    """Pricing information."""
    average_price: float = Field(ge=0, description="Average price")
    market_volume: float = Field(ge=0, description="Market volume")
    market_value: float = Field(ge=0, description="Market value")


class InvestmentRecommendation(BaseModel):
    """Investment recommendation."""
    overall_score: float = Field(ge=0, description="Overall investment score")
    rating: Literal["Strong Buy", "Buy", "Hold", "Weak Hold", "Avoid"] = Field(description="Investment rating")


class ClassAnalysis(BaseModel):
    """Individual credit class analysis."""
    class_info: Dict[str, Any] = Field(description="Class information")
    methodology_scores: MethodologyScores = Field(description="Methodology scores")
    market_performance: MarketPerformance = Field(description="Market performance")
    supply_metrics: SupplyMetrics = Field(description="Supply metrics")
    adoption_metrics: AdoptionMetrics = Field(description="Adoption metrics")
    pricing_info: PricingInfo = Field(description="Pricing information")
    investment_recommendation: InvestmentRecommendation = Field(description="Investment recommendation")


class RecommendationRanking(BaseModel):
    """Investment recommendation ranking."""
    rank: int = Field(ge=1, description="Ranking position")
    class_id: str = Field(description="Credit class ID")
    overall_score: float = Field(ge=0, description="Overall score")
    rating: str = Field(description="Investment rating")
    key_strengths: List[str] = Field(description="Key strengths")
    key_weaknesses: List[str] = Field(description="Key weaknesses")


class ComparativeAnalysis(BaseModel):
    """Comparative analysis results."""
    methodology_comparison: Dict[str, Dict[str, float]] = Field(description="Methodology comparison")
    market_comparison: Dict[str, Dict[str, float]] = Field(description="Market comparison")
    risk_comparison: Dict[str, Dict[str, Any]] = Field(description="Risk comparison")
    recommendation_ranking: List[RecommendationRanking] = Field(description="Recommendation ranking")


class CreditMethodologyComparison(BaseRegenModel):
    """Complete credit methodology comparison response."""
    comparison_summary: Dict[str, Any] = Field(description="Comparison summary")
    detailed_class_analyses: Dict[str, ClassAnalysis] = Field(description="Detailed class analyses")
    comparative_analysis: ComparativeAnalysis = Field(description="Comparative analysis")
    methodology: Dict[str, Any] = Field(description="Analysis methodology")
    metadata: Dict[str, Any] = Field(description="Analysis metadata")


# Resource Response Models

class ChainConfig(BaseRegenModel):
    """Chain configuration response."""
    chain: Dict[str, Any] = Field(description="Chain information")
    endpoints: Dict[str, Any] = Field(description="Network endpoints")
    client_config: Dict[str, Any] = Field(description="Client configuration")
    modules: Dict[str, Any] = Field(description="Available modules")
    pagination: Dict[str, Any] = Field(description="Pagination settings")
    metadata: Dict[str, Any] = Field(description="Configuration metadata")


class EndpointStatus(BaseModel):
    """Individual endpoint status."""
    url: str = Field(description="Endpoint URL")
    type: Literal["rpc", "rest"] = Field(description="Endpoint type")
    healthy: bool = Field(description="Health status")
    response_time_ms: float = Field(ge=0, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


class EndpointsInfo(BaseRegenModel):
    """Endpoints health information."""
    rpc_endpoints: List[EndpointStatus] = Field(description="RPC endpoint statuses")
    rest_endpoints: List[EndpointStatus] = Field(description="REST endpoint statuses")
    summary: Dict[str, Any] = Field(description="Endpoint summary")
    metadata: Dict[str, Any] = Field(description="Check metadata")


class ChainStatus(BaseRegenModel):
    """Chain status response."""
    network: Dict[str, Any] = Field(description="Network information")
    endpoints: Dict[str, Any] = Field(description="Endpoint health")
    health: Dict[str, Any] = Field(description="Overall health status")
    metadata: Dict[str, Any] = Field(description="Status metadata")


class CreditClassSummary(BaseRegenModel):
    """Credit class summary response."""
    class_info: Dict[str, Any] = Field(description="Class information")
    statistics: Dict[str, Any] = Field(description="Class statistics")
    market_activity: Dict[str, Any] = Field(description="Market activity")
    project_distribution: Dict[str, Any] = Field(description="Project distribution")
    metadata: Dict[str, Any] = Field(description="Summary metadata")


class MarketStatistics(BaseRegenModel):
    """Market statistics response."""
    overview: MarketOverview = Field(description="Market overview")
    credit_type_breakdown: Dict[str, CreditTypeStats] = Field(description="Breakdown by credit type")
    market_depth: MarketDepth = Field(description="Market depth analysis")
    liquidity_metrics: LiquidityMetrics = Field(description="Liquidity metrics")
    metadata: Dict[str, Any] = Field(description="Statistics metadata")


class CreditTypesOverview(BaseRegenModel):
    """Credit types overview response."""
    summary: Dict[str, Any] = Field(description="Overview summary")
    credit_types: List[Dict[str, Any]] = Field(description="Credit type details")
    usage_statistics: Dict[str, Any] = Field(description="Usage statistics")
    metadata: Dict[str, Any] = Field(description="Overview metadata")


# Portfolio Resource Models

class HoldingDetail(BaseModel):
    """Individual holding detail."""
    batch_denom: str = Field(description="Batch denomination")
    amount_held: float = Field(ge=0, description="Amount held")
    batch_info: Dict[str, Any] = Field(description="Batch information")
    market_info: Dict[str, Any] = Field(description="Market information")
    vintage_info: Dict[str, Any] = Field(description="Vintage information")


class HoldingSummary(BaseModel):
    """Portfolio holdings summary."""
    total_holdings: int = Field(ge=0, description="Total number of holdings")
    total_credits: float = Field(ge=0, description="Total credit amount")
    total_estimated_value: float = Field(ge=0, description="Total estimated value")
    holdings_with_market_data: int = Field(ge=0, description="Holdings with market data")
    average_vintage: float = Field(description="Average vintage year")


class MarketSummary(BaseModel):
    """Market summary for portfolio."""
    tradeable_value: float = Field(ge=0, description="Tradeable value")
    high_liquidity_holdings: int = Field(ge=0, description="High liquidity holdings count")
    price_discovery_coverage: float = Field(ge=0, le=100, description="Price discovery coverage percentage")


class PortfolioHoldings(BaseRegenModel):
    """Portfolio holdings response."""
    address: str = Field(description="Portfolio address")
    summary: HoldingSummary = Field(description="Holdings summary")
    detailed_holdings: List[HoldingDetail] = Field(description="Detailed holdings")
    market_summary: MarketSummary = Field(description="Market summary")
    metadata: Dict[str, Any] = Field(description="Holdings metadata")


class PortfolioAnalysis(BaseRegenModel):
    """Portfolio analysis resource response."""
    address: str = Field(description="Portfolio address")
    summary: Dict[str, Any] = Field(description="Analysis summary")
    holdings_breakdown: Dict[str, Any] = Field(description="Holdings breakdown")
    diversification_metrics: DiversificationMetrics = Field(description="Diversification metrics")
    optimization_recommendations: List[OptimizationRecommendation] = Field(description="Optimization recommendations")
    impact_assessment: Dict[str, Any] = Field(description="Impact assessment")
    metadata: Dict[str, Any] = Field(description="Analysis metadata")


# Cache and Performance Models

class CacheMetrics(BaseModel):
    """Cache performance metrics."""
    hits: int = Field(ge=0, description="Cache hits")
    misses: int = Field(ge=0, description="Cache misses")
    evictions: int = Field(ge=0, description="Cache evictions")
    size_bytes: int = Field(ge=0, description="Cache size in bytes")
    entry_count: int = Field(ge=0, description="Number of cache entries")
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / max(1, total)) * 100
    
    @property
    def size_mb(self) -> float:
        """Get cache size in megabytes."""
        return self.size_bytes / (1024 * 1024)


class CacheStats(BaseRegenModel):
    """Detailed cache statistics."""
    performance: Dict[str, Any] = Field(description="Performance metrics")
    storage: Dict[str, Any] = Field(description="Storage metrics")
    age_distribution: Dict[str, int] = Field(description="Age distribution")
    configuration: Dict[str, Any] = Field(description="Cache configuration")
    ttl_configuration: Dict[str, int] = Field(description="TTL configuration")
    generated_at: str = Field(description="Statistics generation timestamp")