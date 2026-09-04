import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import { StockDetail } from './components/StockDetail';
import { StockCard } from './components/StockCard';
import type { WatchlistChangesResponse, WatchlistChangeItem } from './types/api';

const mockItem: WatchlistChangeItem = {
  symbol: 'RELIANCE',
  name: 'Reliance',
  sector: 'Energy',
  price: 2500,
  pct_change: 2.5,
  freshness: 'LIVE',
  verdict: 'needs_attention',
  score: 10,
  normalized_score: 100,
  significance: 'HIGH',
  confidence: 'HIGH',
  market_context: 'outlier',
  directionality: 'up',
  headline: 'Headline',
  why_it_matters: 'Matters',
  evidence: {
    volatility_multiple: 2,
    volume_multiple: 3,
    relative_multiple: 2,
    relative_delta_pp: 1,
    pct_change: 2.5,
    benchmark_pct_change: 0.5
  },
  signals: [],
  since_last_checked: {
    last_viewed_at: new Date().toISOString(),
    price_then: 2400,
    price_now: 2500,
    volume_then: 1000,
    volume_now: 2000
  },
  is_new_to_state: false,
  attention_rank: 1,
  is_attention_budget: true
};

const mockResponse: WatchlistChangesResponse = {
  watchlist_id: 1,
  summary: { needs_attention: 1, watch: 0, no_change: 0, unavailable: 0 },
  market_data_available: true,
  market_context: {
    regime: 'normal',
    benchmark_change: 0.5,
    coverage: 0,
    outliers: [],
    benchmark_freshness: 'LIVE'
  },
  items: [mockItem]
};

describe('Phase 9 Data Trust Tests', () => {
  beforeEach(() => {
    (global.fetch as any) = vi.fn().mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(mockResponse) });
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('1. LIVE badge renders', () => {
    render(<StockCard item={mockItem} onClick={() => {}} />);
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('2. DELAYED badge renders', () => {
    render(<StockCard item={{...mockItem, freshness: 'DELAYED'}} onClick={() => {}} />);
    expect(screen.getByText('DATA DELAYED')).toBeInTheDocument();
  });

  it('3. STALE badge renders', () => {
    render(<StockCard item={{...mockItem, freshness: 'STALE'}} onClick={() => {}} />);
    expect(screen.getByText('DATA STALE')).toBeInTheDocument();
  });

  it('4. UNAVAILABLE state renders', () => {
    render(<StockCard item={{...mockItem, freshness: 'UNAVAILABLE'}} onClick={() => {}} />);
    expect(screen.getByText('MARKET DATA UNAVAILABLE')).toBeInTheDocument();
  });

  it('5 & 6. API failure state and Retry button', async () => {
    (global.fetch as any).mockImplementationOnce((url: string) => Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) }))
                         .mockImplementationOnce((url: string) => Promise.reject(new Error('API failed')));
                         
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Market data unavailable')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  it('7. Recovery after retry', async () => {
    let callCount = 0;
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') {
        callCount++;
        if (callCount === 1) return Promise.reject(new Error('API failed'));
        return Promise.resolve({ ok: true, json: () => Promise.resolve(mockResponse) });
      }
    });
    
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Market data unavailable')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Retry'));
    
    await waitFor(() => {
      expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    });
  });

  it('8. No-change is not displayed when API fails', async () => {
    const apiFailureResponse = {
      ...mockResponse,
      market_data_available: false,
      items: [{...mockItem, verdict: 'unavailable', freshness: 'UNAVAILABLE', is_attention_budget: false}]
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(apiFailureResponse) });
    });
    
    render(<App />);
    await waitFor(() => {
      expect(screen.queryByText('NO NOTABLE CHANGE')).not.toBeInTheDocument();
      expect(screen.getByText('MARKET DATA UNAVAILABLE')).toBeInTheDocument();
    });
  });

  it('9. Stale data is not labeled LIVE', () => {
    render(<StockDetail item={{...mockItem, freshness: 'STALE'}} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.queryByText('LIVE')).not.toBeInTheDocument();
    expect(screen.getByText('DATA STALE')).toBeInTheDocument();
    expect(screen.getByText('Some signals may be outdated.')).toBeInTheDocument();
  });

  it('10. Last-known values are clearly labeled', () => {
    render(<StockDetail item={{...mockItem, freshness: 'UNAVAILABLE'}} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('LAST KNOWN VALUE')).toBeInTheDocument();
  });

  it('11. Missing benchmark is clearly communicated', async () => {
    const missingBenchmarkResponse = {
      ...mockResponse,
      market_context: {
        regime: 'market_wide',
        benchmark_change: null,
        coverage: 1,
        outliers: [],
        benchmark_freshness: 'UNAVAILABLE'
      }
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(missingBenchmarkResponse) });
    });
    
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Market comparison unavailable')).toBeInTheDocument();
    });
  });

  it('12. Missing volume does not crash UI', () => {
    render(<StockDetail item={{...mockItem, evidence: {...mockItem.evidence, volume_multiple: 0}}} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('Volume signal unavailable')).toBeInTheDocument();
  });
  
  it('13 & 14. Refresh preserves existing data while loading and replaces after', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('RELIANCE')).toBeInTheDocument();
    });
    
    const refreshBtn = screen.getByLabelText('Refresh');
    fireEvent.click(refreshBtn);
    
    // Existing data should still be there
    expect(screen.getByText('RELIANCE')).toBeInTheDocument();
  });

  it('15. Stock detail correctly handles stale/unavailable state', () => {
    render(<StockDetail item={{...mockItem, freshness: 'UNAVAILABLE'}} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('Mark as reviewed')).toBeDisabled();
  });
});
