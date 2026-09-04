from typing import Optional, Dict

def evaluate_thesis(thesis_type: str, evidence: dict) -> dict:
    """
    Evaluates whether the given thesis type is challenged by the current market evidence.
    Returns: { "status": "OK" | "REVIEW", "reason": str | None }
    
    Rules:
    - GROWTH thesis + relative_delta_pp < -5.0 (significantly underperformed benchmark) → REVIEW
    - GROWTH thesis + volatility_multiple < -2.0 (persistent down trend) → REVIEW
    - DIVIDEND thesis + pct_change < -10.0 → REVIEW
    - VALUE thesis + volatility_multiple > 3.0 (high volatility) → REVIEW
    All other cases → OK
    """
    if thesis_type == "GROWTH":
        # Underperformance vs benchmark
        relative_delta = evidence.get("relative_delta_pp")
        if relative_delta is not None and relative_delta < -5.0:
            return {
                "status": "REVIEW",
                "reason": f"Significantly underperformed benchmark by {abs(relative_delta):.1f} percentage points."
            }
        
        # Volatility/Price drop
        # The prompt says "volatility_multiple < -2.0". Wait, volatility_multiple is positive (e.g., 2.7x average move).
        # We need a combination of negative price change and high volatility, OR we can use the z_price (volatility multiple with sign).
        # In engine.py, `volatility_multiple` is `abs(z_price)`.
        # However, `pct_change` is available. Let's use `pct_change < 0` and `volatility_multiple > 2.0` as a proxy for "persistent down trend".
        pct_change = evidence.get("pct_change")
        vol_multiple = evidence.get("volatility_multiple")
        if pct_change is not None and vol_multiple is not None and pct_change < 0 and vol_multiple > 2.0:
            return {
                "status": "REVIEW",
                "reason": f"Persistent downward trend: {abs(pct_change):.1f}% drop with {vol_multiple:.1f}x normal volatility."
            }

    elif thesis_type == "DIVIDEND":
        pct_change = evidence.get("pct_change")
        if pct_change is not None and pct_change < -10.0:
            return {
                "status": "REVIEW",
                "reason": f"Large capital loss ({pct_change:.1f}%) may offset dividend yield."
            }

    elif thesis_type == "VALUE":
        vol_multiple = evidence.get("volatility_multiple")
        if vol_multiple is not None and vol_multiple > 3.0:
            return {
                "status": "REVIEW",
                "reason": f"High volatility ({vol_multiple:.1f}x normal) challenges stable value assumption."
            }
            
    return {"status": "OK", "reason": None}
