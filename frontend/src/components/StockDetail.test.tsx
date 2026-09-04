/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { StockDetail } from './StockDetail';
import type { WatchlistChangeItem } from '../types/api';

const mockItem: WatchlistChangeItem = {
  symbol: 'GENERIC',
  name: 'Generic Stock',
  sector: 'IT',
  price: 1500.5,
  pct_change: 2.5,
  freshness: 'LIVE',
  verdict: 'needs_attention',
  score: 3.5,
  normalized_score: 80,
  significance: 'HIGH',
  confidence: 'HIGH',
  market_context: 'outlier',
  directionality: 'up',
  headline: 'Test',
  why_it_matters: 'Test',
  evidence: {
    volatility_multiple: 3.5,
    volume_multiple: 3.2,
    relative_multiple: 2.0,
    relative_delta_pp: 2.0,
    pct_change: 2.5,
    benchmark_pct_change: 0.5,
  },
  signals: [],
  since_last_checked: {
    last_viewed_at: '2023-10-27T10:00:00Z',
    price_then: 1450.0,
    price_now: 1500.5,
    volume_then: 100000,
    volume_now: 320000
  },
  is_new_to_state: false,
};

describe('StockDetail Component', () => {
  it('1 & 19. Generic stock detail renders with generic symbols working', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getAllByText('GENERIC').length).toBeGreaterThan(0);
  });

  it('2. Price and percentage render correctly', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getAllByText('₹1,500.50').length).toBeGreaterThan(0);
    expect(screen.getAllByText('+2.5%').length).toBeGreaterThan(0);
  });

  it('3. Significance renders correctly', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('SIGNIFICANT MOVEMENT')).toBeInTheDocument();
  });

  it('4. Confidence renders correctly', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('HIGH CONFIDENCE')).toBeInTheDocument();
  });

  it('5. Freshness renders correctly', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('6 & 7 & 8. Evidence components render correctly', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('3.5×')).toBeInTheDocument();
    expect(screen.getByText('normal volatility')).toBeInTheDocument();
    expect(screen.getByText('3.2×')).toBeInTheDocument();
    expect(screen.getByText('average volume')).toBeInTheDocument();
    expect(screen.getByText('+2.0 pp')).toBeInTheDocument();
    expect(screen.getByText('vs NIFTY')).toBeInTheDocument();
  });

  it('9. Since-last-checked values render when available', () => {
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('₹1,450.00')).toBeInTheDocument();
    expect(screen.getByText('100,000')).toBeInTheDocument();
    expect(screen.getByText('320,000')).toBeInTheDocument();
  });

  it('10. First-check state renders when no previous state exists', () => {
    const firstCheckItem = { ...mockItem, since_last_checked: null, is_new_to_state: true };
    render(<StockDetail item={firstCheckItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('First check')).toBeInTheDocument();
  });

  it('11. Missing volume does not crash the page', () => {
    const missingVol = { ...mockItem, evidence: { ...mockItem.evidence, volume_multiple: 0 } };
    render(<StockDetail item={missingVol} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('Volume signal unavailable')).toBeInTheDocument();
  });

  it('12. Missing benchmark does not crash the page', () => {
    const missingBench = { ...mockItem, evidence: { ...mockItem.evidence, benchmark_pct_change: null as any } };
    render(<StockDetail item={missingBench} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getAllByText('Market comparison unavailable').length).toBeGreaterThan(0);
  });

  it('13. Stale data is clearly marked stale', () => {
    const staleItem = { ...mockItem, freshness: 'STALE' as any };
    render(<StockDetail item={staleItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('DATA STALE')).toBeInTheDocument();
  });

  it('14. Unavailable data displays correctly and disables acknowledge', () => {
    const unavItem = { ...mockItem, freshness: 'UNAVAILABLE' as any };
    render(<StockDetail item={unavItem} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('MARKET DATA UNAVAILABLE')).toBeInTheDocument();
    const btn = screen.getByRole('button', { name: /mark as reviewed/i });
    expect(btn).toBeDisabled();
  });

  it('15 & 16. Market tracking context and Outlier context render correctly', () => {
    const { unmount } = render(<StockDetail item={{ ...mockItem, market_context: 'tracking_market' }} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('TRACKING MARKET')).toBeInTheDocument();
    unmount();
    render(<StockDetail item={{ ...mockItem, market_context: 'outlier' }} onBack={() => {}} onAcknowledge={async () => {}} />);
    expect(screen.getByText('OUTLIER')).toBeInTheDocument();
  });

  it('17 & 18. Mark-as-reviewed calls backend and prevents duplicate submissions', async () => {
    let resolveAck: any;
    const ackPromise = new Promise<void>(res => { resolveAck = res; });
    const mockAck = vi.fn().mockReturnValue(ackPromise);
    
    render(<StockDetail item={mockItem} onBack={() => {}} onAcknowledge={mockAck} />);
    const btn = screen.getByRole('button', { name: /mark as reviewed/i });
    
    fireEvent.click(btn);
    expect(mockAck).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Reviewing...')).toBeInTheDocument();
    expect(btn).toBeDisabled();
    
    fireEvent.click(btn);
    expect(mockAck).toHaveBeenCalledTimes(1); // duplicate prevented
    
    resolveAck();
  });
});
