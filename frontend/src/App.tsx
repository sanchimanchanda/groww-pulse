import { useEffect, useState } from 'react';
import type { WatchlistChangesResponse } from './types/api';
import { StockCard } from './components/StockCard';
import { StockDetail } from './components/StockDetail';
import { RefreshCw, AlertTriangle, ChevronRight, ChevronDown } from 'lucide-react';
import './App.css';

function App() {
  const [data, setData] = useState<WatchlistChangesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scenario, setScenario] = useState<string>('normal_market');
  const [availableScenarios, setAvailableScenarios] = useState<string[]>([]);
  const [noChangeExpanded, setNoChangeExpanded] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  const fetchScenarios = async () => {
    try {
      const res = await fetch('/demo/scenario');
      if (res.ok) {
        const json = await res.json();
        setAvailableScenarios(json.available_scenarios);
        setScenario(json.active_scenario);
      }
    } catch (e) {
      console.error('Failed to fetch scenarios', e);
    }
  };

  const fetchWatchlist = async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const res = await fetch('/watchlists/1/changes');
      if (!res.ok) throw new Error('API Error');
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch watchlist');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const changeScenario = async (newScenario: string) => {
    setScenario(newScenario);
    setLoading(true);
    try {
      await fetch('/demo/scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: newScenario })
      });
      await fetchWatchlist();
    } catch (e) {
      console.error(e);
    }
  };

  const handleAcknowledge = async (symbol: string) => {
    try {
      await fetch(`/stocks/${symbol}/acknowledge`, { method: 'POST' });
      // Refresh UI silently after acknowledgment
      await fetchWatchlist(true);
      // Navigate back to home
      setSelectedSymbol(null);
    } catch (e) {
      console.error('Failed to acknowledge', e);
    }
  };

  useEffect(() => {
    fetchScenarios().then(() => fetchWatchlist());
  }, []);

  const significantItems = data?.items.filter(item => item.verdict === 'needs_attention') || [];
  const watchItems = data?.items.filter(item => item.verdict === 'watch') || [];
  const noChangeItems = data?.items.filter(item => item.verdict === 'no_change' || item.verdict === 'unavailable') || [];

  // Determine "Since you last checked" timestamp
  const getLastCheckedString = () => {
    if (!data) return null;
    const dates = data.items
      .filter(i => i.since_last_checked?.last_viewed_at)
      .map(i => new Date(i.since_last_checked!.last_viewed_at).getTime());
    
    if (dates.length === 0) return "Your first market check";
    
    const maxDate = new Date(Math.max(...dates));
    const now = new Date();
    const isToday = maxDate.getDate() === now.getDate() && maxDate.getMonth() === now.getMonth() && maxDate.getFullYear() === now.getFullYear();
    const isYesterday = new Date(now.getTime() - 86400000).getDate() === maxDate.getDate();
    
    const timeStr = maxDate.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    
    if (isToday) return `Today · ${timeStr}`;
    if (isYesterday) return `Yesterday · ${timeStr}`;
    return `${maxDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} · ${timeStr}`;
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'GOOD MORNING';
    if (hour < 17) return 'GOOD AFTERNOON';
    return 'GOOD EVENING';
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="demo-controls">
          <select 
            value={scenario} 
            onChange={(e) => changeScenario(e.target.value)}
            disabled={loading}
            className="scenario-select"
          >
            {availableScenarios.map(s => (
              <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
            ))}
          </select>
          <button onClick={() => fetchWatchlist()} className="refresh-btn" disabled={loading} aria-label="Refresh">
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
          </button>
        </div>
      </header>

      <main className="main-content">
        {error ? (
          <div className="error-state">
            <AlertTriangle size={32} />
            <h2>Something went wrong</h2>
            <p>{error}</p>
            <button onClick={() => fetchWatchlist()} className="retry-btn">Try Again</button>
          </div>
        ) : loading && !data ? (
          <div className="loading-state">
            <div className="skeleton-title"></div>
            <div className="skeleton-card"></div>
            <div className="skeleton-card"></div>
          </div>
        ) : data && selectedSymbol ? (
          <StockDetail 
            item={data.items.find(i => i.symbol === selectedSymbol)!}
            onBack={() => setSelectedSymbol(null)}
            onAcknowledge={handleAcknowledge}
          />
        ) : data ? (
          <>
            <section className="greeting-section">
              <h1 className="greeting">{getGreeting()}</h1>
              <h2 className="tagline">Your market changed.</h2>
              <div className="last-checked">
                <span className="last-checked-label">Since you last checked</span>
                <span className="last-checked-time">{getLastCheckedString()}</span>
              </div>
            </section>

            <hr className="divider-line" />

            {data.market_context.regime === 'market_wide' && (
              <>
                <section className="market-context-section">
                  <h3 className="section-label">MARKET-WIDE MOVEMENT</h3>
                  <div className="benchmark-stat">
                    <span className="benchmark-name">NIFTY</span>
                    <span className={`benchmark-val ${data.market_context.benchmark_change > 0 ? 'text-green' : 'text-red'}`}>
                      {data.market_context.benchmark_change > 0 ? '+' : ''}{data.market_context.benchmark_change.toFixed(1)}%
                    </span>
                  </div>
                  <p className="market-desc">{data.market_context.description}</p>
                </section>
                <hr className="divider-line" />
              </>
            )}

            <section className="attention-section">
              <h3 className="section-label">
                {significantItems.length > 0 
                  ? `${significantItems.length} THING${significantItems.length > 1 ? 'S' : ''} WORTH YOUR ATTENTION`
                  : 'NOTHING REQUIRES IMMEDIATE ATTENTION'}
              </h3>
              
              <div className="card-list">
                {significantItems.map(item => (
                  <StockCard 
                    key={item.symbol} 
                    item={item} 
                    onClick={() => setSelectedSymbol(item.symbol)} 
                  />
                ))}
              </div>
            </section>

            <hr className="divider-line" />

            <section className="watch-section">
              <h3 className="section-label">WATCH</h3>
              {watchItems.length > 0 ? (
                <>
                  <p className="watch-desc">{watchItems.length} stock{watchItems.length > 1 ? 's' : ''} changed, but nothing unusual stood out.</p>
                  <div className="card-list">
                    {watchItems.map(item => (
                      <StockCard 
                        key={item.symbol} 
                        item={item} 
                        onClick={() => setSelectedSymbol(item.symbol)} 
                      />
                    ))}
                  </div>
                </>
              ) : (
                <p className="watch-desc">No secondary changes to monitor.</p>
              )}
            </section>

            <hr className="divider-line" />

            <section className="no-change-section">
              <button 
                className="collapse-btn" 
                onClick={() => setNoChangeExpanded(!noChangeExpanded)}
                aria-expanded={noChangeExpanded}
              >
                <span className="section-label">NO NOTABLE CHANGE</span>
                {noChangeExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
              <p className="no-change-desc">{noChangeItems.length} stocks</p>
              
              {noChangeExpanded && (
                <div className="card-list mt-3">
                  {noChangeItems.map(item => (
                    <StockCard 
                      key={item.symbol} 
                      item={item} 
                      onClick={() => setSelectedSymbol(item.symbol)} 
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}

export default App;
