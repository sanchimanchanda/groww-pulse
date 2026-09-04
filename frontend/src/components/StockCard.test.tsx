/// <reference types="vitest/globals" />
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { StockCard } from './StockCard';
import type { WatchlistChangeItem } from '../types/api';

const mockItem: WatchlistChangeItem = {
  symbol: 'TESTSYM',
  name: 'Test Symbol',
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
  headline: 'Test headline',
  why_it_matters: 'Test why it matters',
  evidence: {
    volatility_multiple: 2.0,
    volume_multiple: 3.0,
    relative_multiple: 1.5,
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
    volume_now: 300000
  },
  is_new_to_state: false,
};

describe('StockCard Component', () => {
  it('renders generic stock data correctly', () => {
    render(<StockCard item={mockItem} onClick={() => {}} />);
    expect(screen.getByText('TESTSYM')).toBeInTheDocument();
    expect(screen.getByText('₹1,500.50')).toBeInTheDocument();
    expect(screen.getByText('+2.5%')).toBeInTheDocument();
  });

  it('renders significance correctly', () => {
    render(<StockCard item={mockItem} onClick={() => {}} />);
    expect(screen.getByText('SIGNIFICANT MOVEMENT')).toBeInTheDocument();
  });

  it('renders confidence correctly', () => {
    render(<StockCard item={mockItem} onClick={() => {}} />);
    expect(screen.getByText('HIGH CONFIDENCE')).toBeInTheDocument();
  });

  it('renders freshness correctly', () => {
    render(<StockCard item={mockItem} onClick={() => {}} />);
    expect(screen.getByText('LIVE')).toBeInTheDocument();
  });

  it('fires onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<StockCard item={mockItem} onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });

  it('handles unavailable/stale state distinction from no-change', () => {
    const staleItem: WatchlistChangeItem = {
      ...mockItem,
      freshness: 'STALE',
      verdict: 'no_change',
    };
    render(<StockCard item={staleItem} onClick={() => {}} />);
    expect(screen.getByText('DATA STALE')).toBeInTheDocument();
    expect(screen.queryByText('SIGNIFICANT MOVEMENT')).not.toBeInTheDocument();
  });
});
