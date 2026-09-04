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
  price_then: number;
  price_now: number;
  volume_then: number;
  volume_now: number;
}

export interface WatchlistChangeItem {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  pct_change: number;
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
    benchmark_change: number;
  };
  items: WatchlistChangeItem[];
}
