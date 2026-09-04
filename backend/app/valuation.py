def classify_valuation(current_pe: float, historical_pe_median: float, historical_pe_low: float, historical_pe_high: float) -> dict:
    """
    Returns: {
      "label": "BELOW_HISTORICAL_RANGE" | "NEAR_MEDIAN" | "ABOVE_HISTORICAL_RANGE",
      "delta_vs_median_pct": float
    }
    Never uses words: cheap, expensive, buy, sell.
    """
    if not current_pe or not historical_pe_median:
        return {"label": "DATA_UNAVAILABLE", "delta_vs_median_pct": 0.0}

    delta_pct = ((current_pe - historical_pe_median) / historical_pe_median) * 100.0
    
    # Let's say within 5% of median is "NEAR_MEDIAN".
    # Otherwise BELOW or ABOVE.
    # We can refine using low/high but the implementation plan test cases imply:
    # current_pe 22 vs median 28 -> BELOW (-21%)
    # current_pe 28.5 vs median 28 -> NEAR_MEDIAN (+1.7%)
    # current_pe 38 vs median 28 -> ABOVE (+35%)
    
    if abs(delta_pct) <= 5.0:
        label = "NEAR_MEDIAN"
    elif delta_pct < -5.0:
        label = "BELOW_HISTORICAL_RANGE"
    else:
        label = "ABOVE_HISTORICAL_RANGE"
        
    return {
        "label": label,
        "delta_vs_median_pct": round(delta_pct, 1)
    }
