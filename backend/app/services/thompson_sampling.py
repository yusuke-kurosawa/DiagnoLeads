"""
Thompson Sampling Engine

Bayesian bandit algorithm for automatic A/B test optimization.
"""

import numpy as np
from typing import List, Dict, Tuple
from scipy import stats


class ThompsonSamplingEngine:
    """
    Thompson Sampling engine for multi-armed bandit optimization.

    Uses Beta distribution to model conversion rates and automatically
    allocates traffic to the best-performing variants.
    """

    def __init__(self, exploration_rate: float = 0.1):
        """
        Initialize Thompson Sampling engine.

        Args:
            exploration_rate: Balance between exploration and exploitation (0.0-1.0)
                             Higher = more exploration, Lower = more exploitation
        """
        self.exploration_rate = max(0.0, min(1.0, exploration_rate))

    def select_variant(
        self,
        variants: List[Dict],
        random_state: int = None
    ) -> Tuple[str, float]:
        """
        Select a variant using Thompson Sampling.

        Args:
            variants: List of variant dicts with 'id', 'alpha', 'beta' keys
            random_state: Random seed for reproducibility

        Returns:
            Tuple of (variant_id, thompson_score)
        """
        if not variants:
            raise ValueError("No variants provided")

        if random_state is not None:
            np.random.seed(random_state)

        # Sample from Beta distribution for each variant
        samples = []
        for variant in variants:
            alpha = variant.get("alpha", 1.0)
            beta = variant.get("beta", 1.0)

            # Add exploration bonus
            alpha_explore = alpha + self.exploration_rate
            beta_explore = beta + self.exploration_rate

            # Sample from Beta(alpha, beta)
            sample = np.random.beta(alpha_explore, beta_explore)

            samples.append({
                "variant_id": variant["id"],
                "variant_name": variant.get("name", "Unknown"),
                "sample": sample,
                "alpha": alpha,
                "beta": beta
            })

        # Select variant with highest sample
        winner = max(samples, key=lambda x: x["sample"])

        return winner["variant_id"], winner["sample"]

    def calculate_traffic_allocation(
        self,
        variants: List[Dict],
        min_sample_size: int = 100,
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate optimal traffic allocation for each variant.

        Args:
            variants: List of variant dicts
            min_sample_size: Minimum samples before optimization
            num_simulations: Number of Monte Carlo simulations

        Returns:
            Dict mapping variant_id to allocation ratio
        """
        if not variants:
            return {}

        # If not enough data, use equal allocation
        total_impressions = sum(v.get("impressions", 0) for v in variants)
        if total_impressions < min_sample_size * len(variants):
            equal_allocation = 1.0 / len(variants)
            return {v["id"]: equal_allocation for v in variants}

        # Run Monte Carlo simulations
        win_counts = {v["id"]: 0 for v in variants}

        for _ in range(num_simulations):
            samples = []
            for variant in variants:
                alpha = variant.get("alpha", 1.0)
                beta = variant.get("beta", 1.0)
                sample = np.random.beta(alpha, beta)
                samples.append((variant["id"], sample))

            # Find winner of this simulation
            winner_id = max(samples, key=lambda x: x[1])[0]
            win_counts[winner_id] += 1

        # Convert win counts to allocation ratios
        allocations = {
            variant_id: win_count / num_simulations
            for variant_id, win_count in win_counts.items()
        }

        return allocations

    def calculate_confidence_interval(
        self,
        alpha: float,
        beta: float,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate Bayesian credible interval for conversion rate.

        Args:
            alpha: Beta distribution alpha parameter
            beta: Beta distribution beta parameter
            confidence: Confidence level (0.0-1.0)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Calculate percentiles for credible interval
        lower_percentile = (1 - confidence) / 2
        upper_percentile = 1 - lower_percentile

        lower_bound = stats.beta.ppf(lower_percentile, alpha, beta)
        upper_bound = stats.beta.ppf(upper_percentile, alpha, beta)

        return lower_bound, upper_bound

    def determine_winner(
        self,
        variants: List[Dict],
        confidence_threshold: float = 0.95,
        min_sample_size: int = 100
    ) -> Dict:
        """
        Determine if there's a statistically significant winner.

        Args:
            variants: List of variant dicts
            confidence_threshold: Required confidence to declare winner
            min_sample_size: Minimum samples per variant

        Returns:
            Dict with winner info or None if no clear winner
        """
        # Check minimum sample size
        for variant in variants:
            if variant.get("impressions", 0) < min_sample_size:
                return {
                    "has_winner": False,
                    "reason": "insufficient_data",
                    "min_sample_size": min_sample_size
                }

        # Calculate probability that each variant is best
        probabilities = self.calculate_traffic_allocation(
            variants=variants,
            num_simulations=50000
        )

        # Find variant with highest probability
        best_variant_id = max(probabilities.items(), key=lambda x: x[1])[0]
        best_probability = probabilities[best_variant_id]

        # Check if it meets confidence threshold
        if best_probability >= confidence_threshold:
            # Find the actual variant
            winner = next(v for v in variants if v["id"] == best_variant_id)

            return {
                "has_winner": True,
                "winner_id": best_variant_id,
                "winner_name": winner.get("name", "Unknown"),
                "confidence": best_probability,
                "conversion_rate": winner.get("conversion_rate", 0.0),
                "probabilities": probabilities
            }
        else:
            return {
                "has_winner": False,
                "reason": "insufficient_confidence",
                "best_variant_id": best_variant_id,
                "confidence": best_probability,
                "threshold": confidence_threshold,
                "probabilities": probabilities
            }

    def calculate_expected_loss(
        self,
        variants: List[Dict],
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """
        Calculate expected loss for each variant.

        Expected loss = how much worse this variant is compared to the best.
        Lower expected loss = better variant.

        Args:
            variants: List of variant dicts
            num_simulations: Number of simulations

        Returns:
            Dict mapping variant_id to expected loss
        """
        losses = {v["id"]: [] for v in variants}

        for _ in range(num_simulations):
            # Sample conversion rates for all variants
            samples = []
            for variant in variants:
                alpha = variant.get("alpha", 1.0)
                beta = variant.get("beta", 1.0)
                sample = np.random.beta(alpha, beta)
                samples.append({
                    "id": variant["id"],
                    "rate": sample
                })

            # Find best rate in this simulation
            best_rate = max(s["rate"] for s in samples)

            # Calculate loss for each variant
            for sample in samples:
                loss = best_rate - sample["rate"]
                losses[sample["id"]].append(loss)

        # Calculate expected (mean) loss
        expected_losses = {
            variant_id: np.mean(loss_list)
            for variant_id, loss_list in losses.items()
        }

        return expected_losses

    def get_variant_statistics(
        self,
        alpha: float,
        beta: float,
        impressions: int,
        conversions: int,
        confidence: float = 0.95
    ) -> Dict:
        """
        Get comprehensive statistics for a variant.

        Args:
            alpha: Beta distribution alpha
            beta: Beta distribution beta
            impressions: Number of impressions
            conversions: Number of conversions
            confidence: Confidence level

        Returns:
            Dict with statistical metrics
        """
        # Conversion rate
        conversion_rate = conversions / impressions if impressions > 0 else 0.0

        # Bayesian estimate (mean of posterior)
        bayesian_estimate = alpha / (alpha + beta)

        # Confidence interval
        ci_lower, ci_upper = self.calculate_confidence_interval(
            alpha, beta, confidence
        )

        # Standard error
        variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
        std_error = np.sqrt(variance)

        return {
            "impressions": impressions,
            "conversions": conversions,
            "conversion_rate": conversion_rate,
            "bayesian_estimate": bayesian_estimate,
            "confidence_interval": {
                "lower": ci_lower,
                "upper": ci_upper,
                "confidence": confidence
            },
            "standard_error": std_error,
            "alpha": alpha,
            "beta": beta
        }


# Convenience functions
def select_ab_test_variant(variants_data: List[Dict], exploration_rate: float = 0.1) -> str:
    """
    Quick function to select an A/B test variant.

    Args:
        variants_data: List of dicts with variant info
        exploration_rate: Exploration rate

    Returns:
        Selected variant ID
    """
    engine = ThompsonSamplingEngine(exploration_rate=exploration_rate)
    variant_id, _ = engine.select_variant(variants_data)
    return variant_id


def calculate_ab_test_winner(
    variants_data: List[Dict],
    confidence_threshold: float = 0.95,
    min_sample_size: int = 100
) -> Dict:
    """
    Quick function to determine A/B test winner.

    Args:
        variants_data: List of dicts with variant info
        confidence_threshold: Required confidence
        min_sample_size: Minimum samples

    Returns:
        Winner analysis
    """
    engine = ThompsonSamplingEngine()
    return engine.determine_winner(
        variants=variants_data,
        confidence_threshold=confidence_threshold,
        min_sample_size=min_sample_size
    )
