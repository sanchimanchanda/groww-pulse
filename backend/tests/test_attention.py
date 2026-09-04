from app.engine import calculate_attention

def test_highest_meaningful_signal_ranks_first():
    item1 = {"verdict": "needs_attention", "score": 3.0, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    item2 = {"verdict": "needs_attention", "score": 4.0, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(item2) > calculate_attention(item1)

def test_lower_meaningful_signal_ranks_lower():
    item1 = {"verdict": "needs_attention", "score": 2.5, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    item2 = {"verdict": "watch", "score": 1.5, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(item1) > calculate_attention(item2)

def test_no_change_items_never_enter_budget():
    item1 = {"verdict": "no_change", "score": 0.5, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(item1) == -1.0

def test_market_wide_tracking_stocks_receive_lower_priority_than_genuine_outliers():
    # Identical base score, but one is outlier, one is tracking
    tracking = {"verdict": "needs_attention", "score": 3.0, "market_context": "tracking_market", "confidence": "HIGH", "is_new_to_state": False}
    outlier = {"verdict": "needs_attention", "score": 3.0, "market_context": "outlier", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(outlier) > calculate_attention(tracking)

def test_genuine_outlier_remains_visible():
    outlier = {"verdict": "needs_attention", "score": 3.0, "market_context": "outlier", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(outlier) > 3.0 # Outlier gives a bonus (3.0 * 1.2 = 3.6)

def test_high_significance_low_confidence_remains_in_attention_candidates():
    item = {"verdict": "needs_attention", "score": 3.0, "market_context": "normal", "confidence": "LOW", "is_new_to_state": False}
    # It gets a penalty but doesn't get erased
    attention = calculate_attention(item)
    assert attention > 0 
    assert attention < 3.0

def test_reviewed_vs_unseen_equivalent_changes_unseen_ranks_higher():
    seen = {"verdict": "needs_attention", "score": 3.0, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    unseen = {"verdict": "needs_attention", "score": 3.0, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": True}
    assert calculate_attention(unseen) > calculate_attention(seen)

def test_normal_market_does_not_apply_market_wide_penalty():
    normal = {"verdict": "needs_attention", "score": 3.0, "market_context": "normal", "confidence": "HIGH", "is_new_to_state": False}
    assert calculate_attention(normal) == 3.0
