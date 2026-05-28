from scipy.stats import norm
import math


def generate_summary(
    conversion_rate_a: float,
    conversion_rate_b: float,
    absolute_lift: float,
    relative_lift: float | None,
    p_value: float,
    significant: bool,
    alpha: float = 0.05,
) -> str:
    """
    Generate a plain-English summary of A/B test results.

    absolute_lift = conversion_rate_b - conversion_rate_a
    relative_lift = absolute_lift / conversion_rate_a
    """

    absolute_lift_pp = absolute_lift * 100

    if relative_lift is None:
        relative_lift_text = "undefined relative lift because Variant A has a 0% conversion rate"
    else:
        relative_lift_text = f"{relative_lift * 100:.1f}% relative lift"

    if significant:
        if absolute_lift > 0:
            return (
                f"Variant B significantly outperforms Variant A "
                f"(p={p_value:.3f}, +{absolute_lift_pp:.2f} percentage points, "
                f"{relative_lift_text}, alpha={alpha})."
            )
        elif absolute_lift < 0:
            return (
                f"Variant A significantly outperforms Variant B "
                f"(p={p_value:.3f}, {absolute_lift_pp:.2f} percentage points, "
                f"{relative_lift_text}, alpha={alpha})."
            )
        else:
            return (
                f"No practical difference detected "
                f"(p={p_value:.3f}, 0.00 percentage point lift, alpha={alpha})."
            )

    return (
        f"No statistically significant difference detected "
        f"(p={p_value:.3f}, {absolute_lift_pp:.2f} percentage points, "
        f"{relative_lift_text}, alpha={alpha})."
    )


def z_test_two_proportions(
    n_a: int,
    conv_a: int,
    n_b: int,
    conv_b: int,
    alpha: float = 0.05,
    two_sided: bool = True,
) -> dict:
    """
    Two-proportion z-test for A/B conversion data.

    Tests whether conversion_rate_b differs from conversion_rate_a.

    Returns:
        conversion rates, absolute lift, relative lift, z-statistic,
        p-value, confidence interval for absolute lift, and significance.
    """

    # -----------------------------
    # Input validation
    # -----------------------------
    if n_a <= 0:
        raise ValueError("n_a must be greater than 0.")

    if n_b <= 0:
        raise ValueError("n_b must be greater than 0.")

    if conv_a < 0 or conv_b < 0:
        raise ValueError("Conversions cannot be negative.")

    if conv_a > n_a:
        raise ValueError("conv_a cannot exceed n_a.")

    if conv_b > n_b:
        raise ValueError("conv_b cannot exceed n_b.")

    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1.")

    # -----------------------------
    # Conversion rates and lift
    # -----------------------------
    conversion_rate_a = conv_a / n_a
    conversion_rate_b = conv_b / n_b

    absolute_lift = conversion_rate_b - conversion_rate_a

    if conversion_rate_a == 0:
        relative_lift = None
    else:
        relative_lift = absolute_lift / conversion_rate_a

    # -----------------------------
    # Z-test calculation
    # -----------------------------
    pooled_rate = (conv_a + conv_b) / (n_a + n_b)

    pooled_se = math.sqrt(
        pooled_rate
        * (1 - pooled_rate)
        * ((1 / n_a) + (1 / n_b))
    )

    if pooled_se == 0:
        raise ValueError(
            "Cannot compute z-test because the pooled standard error is 0. "
            "This usually happens when both groups have 0% conversions or 100% conversions."
        )

    z_statistic = absolute_lift / pooled_se

    if two_sided:
        p_value = 2 * (1 - norm.cdf(abs(z_statistic)))
    else:
        # One-sided test assumes the alternative hypothesis is B > A.
        p_value = 1 - norm.cdf(z_statistic)

    # -----------------------------
    # Confidence interval for absolute lift
    # -----------------------------
    # This CI is for conversion_rate_b - conversion_rate_a.
    unpooled_se = math.sqrt(
        (conversion_rate_a * (1 - conversion_rate_a) / n_a)
        + (conversion_rate_b * (1 - conversion_rate_b) / n_b)
    )

    z_critical = norm.ppf(1 - alpha / 2)

    absolute_lift_ci_low = absolute_lift - z_critical * unpooled_se
    absolute_lift_ci_high = absolute_lift + z_critical * unpooled_se

    significant = p_value < alpha

    summary = generate_summary(
        conversion_rate_a=conversion_rate_a,
        conversion_rate_b=conversion_rate_b,
        absolute_lift=absolute_lift,
        relative_lift=relative_lift,
        p_value=p_value,
        significant=significant,
        alpha=alpha,
    )

    return {
        "conversion_rate_a": conversion_rate_a,
        "conversion_rate_b": conversion_rate_b,
        "absolute_lift": absolute_lift,
        "relative_lift": relative_lift,
        "z_statistic": z_statistic,
        "p_value": p_value,
        "absolute_lift_ci_low": absolute_lift_ci_low,
        "absolute_lift_ci_high": absolute_lift_ci_high,
        "alpha": alpha,
        "significant": significant,
        "summary": summary,
    }