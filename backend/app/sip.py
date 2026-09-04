from datetime import datetime

PULLBACK_THRESHOLD_PCT = 5.0  # weekly benchmark decline

def evaluate_sip_context(benchmark_weekly_change: float, sip: dict) -> dict:
    """
    Returns: { "pullback_detected": bool, "benchmark_change": float, "sip": dict }
    Never says "buy more" or "invest now".
    """
    if not sip:
        return {
            "pullback_detected": False,
            "benchmark_change": benchmark_weekly_change,
            "sip": None
        }

    pullback_detected = benchmark_weekly_change <= -PULLBACK_THRESHOLD_PCT

    return {
        "pullback_detected": pullback_detected,
        "benchmark_change": benchmark_weekly_change,
        "sip": sip
    }
