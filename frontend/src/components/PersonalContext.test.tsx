import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PersonalContext } from './PersonalContext';

describe('PersonalContext', () => {
  it('renders nothing if context is missing', () => {
    const { container } = render(<PersonalContext />);
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing if context is empty', () => {
    const { container } = render(<PersonalContext context={{}} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders thesis context', () => {
    render(<PersonalContext context={{ thesis: { type: 'GROWTH', note: 'Strong outlook', status: 'OK', action: null } }} />);
    expect(screen.getByText(/Investment Thesis: GROWTH/)).toBeInTheDocument();
    expect(screen.getByText(/"Strong outlook"/)).toBeInTheDocument();
  });

  it('renders valuation context', () => {
    render(<PersonalContext context={{ valuation: { current_pe: 25.4, label: 'BELOW_HISTORICAL_RANGE', delta_pct: -15.2 } }} />);
    expect(screen.getByText(/Current P/)).toBeInTheDocument();
    expect(screen.getByText(/25.4/)).toBeInTheDocument();
    expect(screen.getByText(/BELOW HISTORICAL RANGE/)).toBeInTheDocument();
  });

  it('renders events context', () => {
    render(<PersonalContext context={{ events: [{ type: 'EARNINGS', title: 'Q3 Results', days_until: 10 }] }} />);
    expect(screen.getByText(/Upcoming Events/)).toBeInTheDocument();
    expect(screen.getByText(/EARNINGS/)).toBeInTheDocument();
    expect(screen.getByText(/Q3 Results/)).toBeInTheDocument();
  });

  it('renders fund overlap context', () => {
    render(<PersonalContext context={{ fund_overlap: [{ fund_name: 'Parag Parikh Flexi Cap', weight: 8.2 }] }} />);
    expect(screen.getByText(/Mutual Fund Overlap/)).toBeInTheDocument();
    expect(screen.getByText(/Parag Parikh Flexi Cap/)).toBeInTheDocument();
    expect(screen.getByText(/8.2%/)).toBeInTheDocument();
  });
});
