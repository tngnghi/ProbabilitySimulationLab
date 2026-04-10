from fastapi.logger import logger
import logging

logger.setLevel(logging.WARNING)

def validate_sample_sizes(n_a,n_b) -> list[str]:
    warnings = []
    if n_a < 100 or n_b < 100:
        msg = f"Small sample size detected: n_a={n_a}, n_b={n_b}"
        logger.warning(msg)
        warnings.append(msg)
    if  n_a > 100000000 or n_b > 100000000:
        msg = f"Large sample size detected: n_a={n_a}, n_b={n_b}"
        logger.warning(msg)
        warnings.append(msg)
    return warnings

def validate_conversion_rates(conv_a, n_a, conv_b, n_b) -> list[str]:
    warnings = []
    conv_rate_a = conv_a / n_a
    conv_rate_b = conv_b / n_b
    if conv_rate_a > 0.5:
        msg = "Conversion rate A is unusually high"
        logger.warning(msg)
        warnings.append(msg)
    if conv_rate_b > 0.5:
        msg = "Conversion rate B is unusually high"
        logger.warning(msg)
        warnings.append(msg)
    if conv_rate_a < .001:
        msg = "Conversion rate A is very low"
        logger.warning(msg)
        warnings.append(msg)
    if conv_rate_b < .001:
        msg = "Conversion rate B is very low"
        logger.warning(msg)
        warnings.append(msg)
    return warnings

def validate_lift(conv_a, n_a, conv_b, n_b) -> list[str]:
    warnings = []
    rate_a = conv_a / n_a
    rate_b = conv_b / n_b
    if rate_a == 0: 
        msg = "can't compute lift"
        logger.warning(msg)
        warnings.append(msg)
        return []
    lift = (rate_b - rate_a) / rate_a
    if abs(lift) > 10: 
        msg = "Lift is very large, verify data"
        logger.warning(msg)
        warnings.append(msg)
    return warnings

def validate_aggregated_data(n_a, conv_a, n_b, conv_b) -> list[str]:
    warnings = []
    warnings += validate_sample_sizes(n_a, n_b)
    warnings += validate_conversion_rates(conv_a, n_a, conv_b, n_b)
    warnings += validate_lift(conv_a, n_a, conv_b, n_b)
    return warnings