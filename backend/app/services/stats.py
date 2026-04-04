from scipy.stats import norm
import math

def generate_summary(observed_lift, p_value, significant, alpha=0.05) -> str:
    """
    Generate plain-English summary of results.
    
    Input: results dict from z_test
    Output: string like "Variant B significantly outperforms A (p=0.032, lift=12.5%)"
    """
    
    if significant:
        if observed_lift > 0:
            return f"Variant B significantly outperforms A (p={p_value:.3f}, lift={observed_lift*100:.1f}%)"
        else:
            return f"Variant A significantly outperforms B (p={p_value:.3f}, lift={abs(observed_lift)*100:.1f}%)"
    else:
        return f"No significant difference detected (p={p_value:.3f}, lift={observed_lift*100:.1f}%)"

def z_test_two_proportions(n_a: int, conv_a: int, n_b: int, conv_b: int, two_sided: bool = True):
    if n_a <= 0:
        raise ValueError("n_a must be > 0")
    if n_b <= 0:
        raise ValueError("n_b must be > 0")
    if conv_a > n_a or conv_b > n_b:
        raise ValueError("Conversions cannot exceed samples")
    if conv_a < 0 or conv_b < 0:
        raise ValueError("Conversions cannot be negative")
    
    p_hat_a = conv_a / n_a
    p_hat_b = conv_b / n_b
    
    if p_hat_a == 0:
        observed_lift = float('inf')  # or use smoothing
    else:
        observed_lift = (p_hat_b - p_hat_a) / p_hat_a
    
    p_hat_pooled = (conv_a + conv_b) / (n_a + n_b)
    se = math.sqrt(p_hat_pooled * (1 - p_hat_pooled) * (1/n_a + 1/n_b))
    
    if se == 0:
        raise ValueError(
        "Cannot compute z-test: no variation in data. "
        "Both variants have identical conversion rates (0% or 100%). "
        "Need at least some variation to test."
        )
    """
    def z_test_two_proportions(...):
        # Smoothing: add pseudocounts
        # (like observing 1 conversion in each group, with 1 non-conversion)
        alpha = 0.5  # pseudocount
        
        conv_a_smooth = conv_a + alpha
        n_a_smooth = n_a + 2 * alpha
        
        conv_b_smooth = conv_b + alpha
        n_b_smooth = n_b + 2 * alpha
        
        p_hat_a = conv_a_smooth / n_a_smooth
        p_hat_b = conv_b_smooth / n_b_smooth
        
        # Now SE will never be 0
        # ... rest of z-test ..."""
    
    z = (p_hat_b - p_hat_a) / se
    
    if two_sided:
        p_value = 2 * (1 - norm.cdf(abs(z)))
    else: p_value = 1 - norm.cdf(abs(z))
    ci_low = p_hat_b - 1.96 * math.sqrt(p_hat_b * (1 - p_hat_b) / n_b)
    ci_high = p_hat_b + 1.96 * math.sqrt(p_hat_b * (1 - p_hat_b) / n_b)

    significant = p_value < 0.05
    
    return {
        "observed_lift": observed_lift,
        "p_value": float(p_value),
        "z_statistic": z,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "significant": bool(significant),
        "summary": generate_summary(observed_lift,p_value,significant)
        }

def compute_statistical_power(n_a, n_b, baseline_rate, effect_grid, 
                              alpha=0.05, n_sims=5000, method="ztest"):
    """
    Compute power for different effect sizes.
    Skeleton: return empty dict for now.
    Implement in Week 7.
    """
    return {}