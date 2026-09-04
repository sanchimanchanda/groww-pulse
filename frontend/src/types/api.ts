export type Freshness = 'LIVE' | 'DELAYED' | 'STALE' | 'UNAVAILABLE';
export type Verdict = 'needs_attention' | 'watch' | 'no_change' | 'unavailable';
export type Significance = 'HIGH' | 'MODERATE' | 'LOW' | 'NONE';
export type Confidence = 'HIGH' | 'MEDIUM' | 'LOW';
export type MarketContext = 'normal' | 'tracking_market' | 'outlier' | 'market_wide';

export interface Evidence {
  volatility_multiple: number;
  volume_multiple: number;
  relative_multiple: number;
  relative_delta_pp: number;
  pct_change: number;
  benchmark_pct_change: number;
}

export interface Signal {
  kind: string;
  value: number;
}

export interface SinceLastChecked {
  last_viewed_at: string;
  price_then: number | null;
  price_now: number | null;
  volume_then: number | null;
  volume_now: number | null;
}

export interface ThesisContext {
  type: string;
  note: string | null;
  status: "OK" | "REVIEW";
  action: string | null;
}

export interface ValuationContext {
  current_pe: number;
  label: "BELOW_HISTORICAL_RANGE" | "NEAR_MEDIAN" | "ABOVE_HISTORICAL_RANGE" | "DATA_UNAVAILABLE";
  delta_pct: number;
}

export interface EventContext {
  type: "EARNINGS" | "DIVIDEND";
  title: string;
  days_until: number;
}

export interface FundOverlapContext {
  fund_name: string;
  weight: number;
}

export interface PersonalContext {
  thesis?: ThesisContext;
  valuation?: ValuationContext;
  events?: EventContext[];
  fund_overlap?: FundOverlapContext[];
}

export interface WatchlistChangeItem {
  symbol: string;
  name: string;
  sector: string;
  price: number | null;
  pct_change: number | null;
  freshness: Freshness;
  verdict: Verdict;
  score: number;
  normalized_score: number;
  significance: Significance;
  confidence: Confidence;
  market_context: MarketContext;
  directionality: 'up' | 'down' | 'flat';
  headline: string;
  why_it_matters: string;
  evidence: Evidence;
  signals: Signal[];
  since_last_checked: SinceLastChecked | null;
  is_new_to_state: boolean;
  attention_rank: number | null;
  is_attention_budget: boolean;
  personal_context?: PersonalContext;
}

export interface WatchlistChangesResponse {
  watchlist_id: number;
  summary: {
    needs_attention: number;
    watch: number;
    no_change: number;
    unavailable: number;
  };
  market_data_available: boolean;
  market_context: {
    regime: MarketContext;
    headline: string;
    description: string;
    benchmark_change: number | null;
    coverage: number;
    outliers: string[];
    benchmark_freshness: string;
  };
  items: WatchlistChangeItem[];
}
