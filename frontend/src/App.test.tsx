/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import type { WatchlistChangesResponse } from './types/api';

const mockBaseResponse: WatchlistChangesResponse = {
  watchlist_id: 1,
  summary: { needs_attention: 1, watch: 1, no_change: 1, unavailable: 0 },
  market_data_available: true,
  market_context: {
    regime: 'normal',
    headline: 'Normal Market',
    description: 'The market is normal.',
    benchmark_change: 0.5,
    coverage: 0,
    outliers: [],
    benchmark_freshness: 'LIVE',
  },
  items: [
    {
      symbol: 'ATTENTION',
      name: 'ATTN',
      sector: 'IT',
      price: 100,
      pct_change: 5,
      freshness: 'LIVE',
      verdict: 'needs_attention',
      score: 10,
      normalized_score: 100,
      significance: 'HIGH',
      confidence: 'HIGH',
      market_context: 'outlier',
      directionality: 'up',
      headline: 'test',
      why_it_matters: 'test',
      evidence: { volatility_multiple: 2, volume_multiple: 2, relative_multiple: 2, relative_delta_pp: 2, pct_change: 5, benchmark_pct_change: 0.5 },
      signals: [],
      since_last_checked: {
        last_viewed_at: '2023-10-27T10:00:00Z',
        price_then: 95,
        price_now: 100,
        volume_then: 1000,
        volume_now: 2000
      },
      is_new_to_state: false,
      attention_rank: 1,
      is_attention_budget: true
    },
    {
      symbol: 'WATCH',
      name: 'WTCH',
      sector: 'IT',
      price: 100,
      pct_change: 1,
      freshness: 'LIVE',
      verdict: 'watch',
      score: 5,
      normalized_score: 50,
      significance: 'MODERATE',
      confidence: 'HIGH',
      market_context: 'normal',
      directionality: 'up',
      headline: 'test',
      why_it_matters: 'test',
      evidence: { volatility_multiple: 1, volume_multiple: 1, relative_multiple: 1, relative_delta_pp: 1, pct_change: 1, benchmark_pct_change: 0.5 },
      signals: [],
      since_last_checked: null,
      is_new_to_state: true,
      attention_rank: null,
      is_attention_budget: false
    },
    {
      symbol: 'NOCHANGE',
      name: 'NOCH',
      sector: 'IT',
      price: 100,
      pct_change: 0,
      freshness: 'LIVE',
      verdict: 'no_change',
      score: 0,
      normalized_score: 0,
      significance: 'NONE',
      confidence: 'HIGH',
      market_context: 'normal',
      directionality: 'flat',
      headline: 'test',
      why_it_matters: 'test',
      evidence: { volatility_multiple: 0, volume_multiple: 0, relative_multiple: 0, relative_delta_pp: 0, pct_change: 0, benchmark_pct_change: 0.5 },
      signals: [],
      since_last_checked: null,
      is_new_to_state: true,
      attention_rank: null,
      is_attention_budget: false
    }
  ]
};

beforeEach(() => {
  global.fetch = vi.fn((url: string) => {
    if (url === '/demo/scenario') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ available_scenarios: ['normal'], active_scenario: 'normal' })
      } as Response);
    }
    if (url === '/watchlists/1/changes') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockBaseResponse)
      } as Response);
    }
    if (url.includes('/acknowledge')) {
      return Promise.resolve({ ok: true } as Response);
    }
    return Promise.reject(new Error('not mocked'));
  });
});

describe('App Component - Phase 6', () => {
  it('1. Existing user with last_seen timestamp renders correctly', async () => {
    render(<App />);
    await waitFor(() => {
      // Because we used 2023-10-27, it should format as "Oct 27"
      expect(screen.getByText(/Oct 27/i)).toBeInTheDocument();
    });
  });

  it('2. First-time user shows no fabricated timestamp', async () => {
    const firstTimeResponse = {
      ...mockBaseResponse,
      items: mockBaseResponse.items.map(i => ({ ...i, since_last_checked: null }))
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(firstTimeResponse) });
    });
    
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('Your first market check')).toBeInTheDocument();
    });
  });

  it('3. Meaningful changes appear in attention section', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('THINGS WORTH YOUR ATTENTION')).toBeInTheDocument();
      expect(screen.getByText('ATTENTION')).toBeInTheDocument();
    });
  });

  it('4. No-change stocks are collapsed', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('NO NOTABLE CHANGE')).toBeInTheDocument();
    });
    // NOCHANGE symbol should NOT be visible initially
    expect(screen.queryByText('NOCHANGE')).not.toBeInTheDocument();
    
    // Click expand
    fireEvent.click(screen.getByText('NO NOTABLE CHANGE'));
    expect(screen.getByText('NOCHANGE')).toBeInTheDocument();
  });

  it('5 & 6. Market-wide banner appears only when market_wide', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.queryByText('MARKET CONTEXT')).not.toBeInTheDocument();
    });

    const marketWideResponse = {
      ...mockBaseResponse,
      market_context: { ...mockBaseResponse.market_context, regime: 'market_wide' }
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(marketWideResponse) });
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('MARKET CONTEXT')).toBeInTheDocument();
    });
  });

  it('7. Stale data is not presented as live', async () => {
    const staleResponse = {
      ...mockBaseResponse,
      items: [{ ...mockBaseResponse.items[0], freshness: 'STALE', verdict: 'watch' }]
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(staleResponse) });
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('DATA STALE')).toBeInTheDocument();
    });
  });

  it('8. Unavailable data is not presented as "no change" without distinction', async () => {
    const unavResponse = {
      ...mockBaseResponse,
      items: [{ ...mockBaseResponse.items[2], verdict: 'unavailable', freshness: 'UNAVAILABLE' }]
    };
    (global.fetch as any).mockImplementation((url: string) => {
      if (url === '/demo/scenario') return Promise.resolve({ ok: true, json: () => Promise.resolve({ available_scenarios: [], active_scenario: '' }) });
      if (url === '/watchlists/1/changes') return Promise.resolve({ ok: true, json: () => Promise.resolve(unavResponse) });
    });

    render(<App />);
    await waitFor(() => {
      fireEvent.click(screen.getByText('NO NOTABLE CHANGE'));
      expect(screen.getByText('MARKET DATA UNAVAILABLE')).toBeInTheDocument();
    });
  });

  it('9 & 10 & 11. Acknowledgement calls backend and refreshes', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText('ATTENTION')).toBeInTheDocument();
    });
    
    // Navigate to detail view
    fireEvent.click(screen.getByText('ATTENTION'));
    
    const ackBtn = screen.getByText('Mark as reviewed');
    fireEvent.click(ackBtn);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/stocks/ATTENTION/acknowledge', expect.objectContaining({ method: 'POST' }));
      // Should have re-fetched
      expect(global.fetch).toHaveBeenCalledWith('/watchlists/1/changes');
    });
  });
});
