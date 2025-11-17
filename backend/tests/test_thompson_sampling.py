"""
Tests for Thompson Sampling A/B testing engine
"""
import pytest
from backend.app.services.thompson_sampling import ThompsonSamplingEngine


class TestThompsonSamplingEngine:
    """Test Thompson Sampling algorithm implementation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = ThompsonSamplingEngine()

    def test_select_variant_with_equal_performance(self):
        """Test variant selection when all variants have equal performance"""
        variants = [
            {
                "id": "variant_a",
                "name": "A",
                "alpha": 10.0,
                "beta": 90.0,
                "impressions": 100,
            },
            {
                "id": "variant_b",
                "name": "B",
                "alpha": 10.0,
                "beta": 90.0,
                "impressions": 100,
            },
        ]

        # Select variant multiple times
        selections = []
        for _ in range(100):
            variant_id, score = self.engine.select_variant(
                variants, exploration_rate=0.1
            )
            selections.append(variant_id)

        # Both variants should be selected roughly equally
        a_count = selections.count("variant_a")
        b_count = selections.count("variant_b")

        # Allow some variance but both should be selected
        assert a_count > 20
        assert b_count > 20
        assert a_count + b_count == 100

    def test_select_variant_with_clear_winner(self):
        """Test variant selection when one variant clearly performs better"""
        variants = [
            {
                "id": "variant_a",
                "name": "A",
                "alpha": 50.0,  # 50 conversions
                "beta": 50.0,   # 50 failures (50% CVR)
                "impressions": 100,
            },
            {
                "id": "variant_b",
                "name": "B",
                "alpha": 10.0,  # 10 conversions
                "beta": 90.0,   # 90 failures (10% CVR)
                "impressions": 100,
            },
        ]

        # Select variant multiple times
        selections = []
        for _ in range(100):
            variant_id, score = self.engine.select_variant(
                variants, exploration_rate=0.1
            )
            selections.append(variant_id)

        # Variant A should be selected more often
        a_count = selections.count("variant_a")
        assert a_count > 70  # A should win most of the time

    def test_calculate_traffic_allocation(self):
        """Test traffic allocation calculation"""
        variants = [
            {
                "id": "variant_a",
                "alpha": 30.0,
                "beta": 70.0,
                "impressions": 100,
            },
            {
                "id": "variant_b",
                "alpha": 20.0,
                "beta": 80.0,
                "impressions": 100,
            },
        ]

        allocation = self.engine.calculate_traffic_allocation(
            variants, min_sample_size=50, num_simulations=1000
        )

        # All variants should have allocation
        assert "variant_a" in allocation
        assert "variant_b" in allocation

        # Allocations should sum to 1.0
        total = sum(allocation.values())
        assert abs(total - 1.0) < 0.01

        # Variant A should have higher allocation (better performance)
        assert allocation["variant_a"] > allocation["variant_b"]

    def test_calculate_confidence_interval(self):
        """Test confidence interval calculation"""
        # Test with alpha=30, beta=70 (30% conversion rate)
        lower, upper = self.engine.calculate_confidence_interval(
            alpha=30.0, beta=70.0, confidence=0.95
        )

        # Confidence interval should contain the point estimate
        point_estimate = (30 - 1) / (30 + 70 - 2)  # ~0.293
        assert lower < point_estimate < upper

        # Interval should be reasonable width
        assert 0.0 <= lower < upper <= 1.0
        assert upper - lower < 0.2  # Not too wide

    def test_determine_winner_with_clear_winner(self):
        """Test winner determination with statistically significant difference"""
        variants = [
            {
                "id": "variant_a",
                "alpha": 100.0,  # 100 conversions
                "beta": 100.0,   # 100 failures (50% CVR)
                "impressions": 200,
                "conversions": 100,
            },
            {
                "id": "variant_b",
                "alpha": 20.0,   # 20 conversions
                "beta": 180.0,   # 180 failures (10% CVR)
                "impressions": 200,
                "conversions": 20,
            },
        ]

        result = self.engine.determine_winner(
            variants, confidence_threshold=0.95, min_sample_size=100
        )

        # Should have a clear winner
        assert result["has_winner"] is True
        assert result["winner_id"] == "variant_a"
        assert result["confidence"] >= 0.95

    def test_determine_winner_insufficient_data(self):
        """Test winner determination with insufficient sample size"""
        variants = [
            {
                "id": "variant_a",
                "alpha": 10.0,
                "beta": 10.0,
                "impressions": 20,
                "conversions": 10,
            },
            {
                "id": "variant_b",
                "alpha": 5.0,
                "beta": 15.0,
                "impressions": 20,
                "conversions": 5,
            },
        ]

        result = self.engine.determine_winner(
            variants, confidence_threshold=0.95, min_sample_size=100
        )

        # Should not have winner due to insufficient data
        assert result["has_winner"] is False
        assert result["reason"] == "insufficient_data"

    def test_determine_winner_insufficient_confidence(self):
        """Test winner determination when confidence threshold not met"""
        variants = [
            {
                "id": "variant_a",
                "alpha": 105.0,  # Slightly better
                "beta": 95.0,
                "impressions": 200,
                "conversions": 105,
            },
            {
                "id": "variant_b",
                "alpha": 100.0,
                "beta": 100.0,
                "impressions": 200,
                "conversions": 100,
            },
        ]

        result = self.engine.determine_winner(
            variants, confidence_threshold=0.95, min_sample_size=100
        )

        # Difference is too small for 95% confidence
        if not result["has_winner"]:
            assert result["reason"] == "insufficient_confidence"

    def test_calculate_expected_loss(self):
        """Test expected loss calculation"""
        variants = [
            {
                "id": "variant_a",
                "alpha": 50.0,
                "beta": 50.0,
            },
            {
                "id": "variant_b",
                "alpha": 30.0,
                "beta": 70.0,
            },
        ]

        expected_losses = self.engine.calculate_expected_loss(
            variants, num_simulations=1000
        )

        # Both variants should have expected loss values
        assert "variant_a" in expected_losses
        assert "variant_b" in expected_losses

        # All losses should be non-negative
        assert expected_losses["variant_a"] >= 0
        assert expected_losses["variant_b"] >= 0

        # Variant B should have higher expected loss (worse performance)
        assert expected_losses["variant_b"] > expected_losses["variant_a"]

    def test_get_variant_statistics(self):
        """Test variant statistics calculation"""
        stats = self.engine.get_variant_statistics(
            alpha=30.0,
            beta=70.0,
            impressions=100,
            conversions=30,
            confidence=0.95,
        )

        # Should return all expected statistics
        assert "conversion_rate" in stats
        assert "bayesian_estimate" in stats
        assert "confidence_interval_lower" in stats
        assert "confidence_interval_upper" in stats
        assert "standard_error" in stats

        # Conversion rate should be accurate
        assert abs(stats["conversion_rate"] - 0.30) < 0.01

        # Bayesian estimate should be close to conversion rate
        assert abs(stats["bayesian_estimate"] - 0.293) < 0.01

        # Confidence interval should contain the estimate
        assert (
            stats["confidence_interval_lower"]
            < stats["bayesian_estimate"]
            < stats["confidence_interval_upper"]
        )

    def test_exploration_rate_effect(self):
        """Test that exploration rate affects variant selection"""
        variants = [
            {
                "id": "variant_a",
                "name": "A",
                "alpha": 100.0,
                "beta": 100.0,
                "impressions": 200,
            },
            {
                "id": "variant_b",
                "name": "B",
                "alpha": 10.0,
                "beta": 190.0,
                "impressions": 200,
            },
        ]

        # With low exploration, variant A should dominate
        low_exploration_selections = []
        for _ in range(100):
            variant_id, _ = self.engine.select_variant(
                variants, exploration_rate=0.01
            )
            low_exploration_selections.append(variant_id)

        # With high exploration, variant B should get more chances
        high_exploration_selections = []
        for _ in range(100):
            variant_id, _ = self.engine.select_variant(
                variants, exploration_rate=0.5
            )
            high_exploration_selections.append(variant_id)

        low_b_count = low_exploration_selections.count("variant_b")
        high_b_count = high_exploration_selections.count("variant_b")

        # High exploration should give variant B more selections
        assert high_b_count > low_b_count
