import { useState } from 'react';
import type { WatchlistChangeItem } from '../types/api';
import { ArrowLeft, AlertCircle, Clock } from 'lucide-react';
import styles from './StockDetail.module.css';

interface Props {
  item: WatchlistChangeItem;
  onBack: () => void;
  onAcknowledge: (symbol: string) => Promise<void>;
}

export function StockDetail({ item, onBack, onAcknowledge }: Props) {
  const [acknowledging, setAcknowledging] = useState(false);

  const formattedPct = item.pct_change !== null ? (item.pct_change > 0 ? `+${item.pct_change.toFixed(1)}%` : `${item.pct_change.toFixed(1)}%`) : '—';
  const pctColor = item.pct_change !== null ? (item.pct_change > 0 ? 'text-green' : item.pct_change < 0 ? 'text-red' : 'text-secondary') : 'text-secondary';
  const priceDisplay = item.price !== null ? `₹${item.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}` : 'Price unavailable';

  const renderFreshness = () => {
    switch (item.freshness) {
      case 'LIVE': return <span className={styles.live}><span className={styles.liveDot}></span>LIVE</span>;
      case 'DELAYED': return <span className={styles.delayed}><Clock size={12}/> DATA DELAYED</span>;
      case 'STALE': return <span className={styles.stale}><AlertCircle size={12}/> DATA STALE</span>;
      case 'UNAVAILABLE': return <span className={styles.unavailable}><AlertCircle size={12}/> MARKET DATA UNAVAILABLE</span>;
      default: return null;
    }
  };

  const handleAcknowledge = async () => {
    if (acknowledging || item.freshness === 'UNAVAILABLE') return;
    setAcknowledging(true);
    await onAcknowledge(item.symbol);
    setAcknowledging(false);
  };

  return (
    <div className={styles.container}>
      <button className={styles.backBtn} onClick={onBack} aria-label="Go back">
        <ArrowLeft size={20} /> Back
      </button>

      {/* HEADER */}
      <header className={styles.header}>
        <div className={styles.titleInfo}>
          <h2 className={styles.symbol}>{item.symbol}</h2>
          <div className="flex items-baseline gap-2">
            <span className={styles.price}>{priceDisplay}</span>
            {item.freshness === 'UNAVAILABLE' && item.price !== null && (
              <span className="text-xs text-yellow-600 font-medium">LAST KNOWN VALUE</span>
            )}
          </div>
          <span className={`${styles.pctChange} ${pctColor}`}>{formattedPct}</span>
        </div>

        <div className={styles.tags}>
          {item.verdict === 'needs_attention' && (
            <span className={styles.significantBadge}>SIGNIFICANT MOVEMENT</span>
          )}
        </div>
      </header>

      <hr className="divider-line" />

      {item.freshness === 'STALE' && (
        <div className="mx-6 mt-4 p-3 bg-yellow-900/20 border border-yellow-700/50 rounded-md text-yellow-500 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          Some signals may be outdated.
        </div>
      )}

      {/* WHY IT STANDS OUT */}
      <section className={styles.section}>
        <h3 className="section-label">WHY IT STANDS OUT</h3>
        <div className={styles.evidenceGrid}>
          {item.evidence.volatility_multiple > 0 && (
            <div className={styles.evidenceBlock}>
              <span className={styles.evidenceValue}>{item.evidence.volatility_multiple.toFixed(1)}×</span>
              <span className={styles.evidenceLabel}>normal volatility</span>
            </div>
          )}
          
          {item.evidence.volume_multiple > 0 ? (
            <div className={styles.evidenceBlock}>
              <span className={styles.evidenceValue}>{item.evidence.volume_multiple.toFixed(1)}×</span>
              <span className={styles.evidenceLabel}>average volume</span>
            </div>
          ) : (
            <div className={styles.evidenceBlock}>
              <span className={styles.evidenceLabel}>Volume signal unavailable</span>
            </div>
          )}
          
          {item.evidence.benchmark_pct_change !== null && item.evidence.relative_delta_pp > 0 ? (
            <div className={styles.evidenceBlock}>
              <span className={styles.evidenceValue}>+{item.evidence.relative_delta_pp.toFixed(1)} pp</span>
              <span className={styles.evidenceLabel}>vs NIFTY</span>
            </div>
          ) : item.evidence.benchmark_pct_change === null ? (
            <div className={styles.evidenceBlock}>
              <span className={styles.evidenceLabel}>Market comparison unavailable</span>
            </div>
          ) : null}
        </div>
      </section>

      <hr className="divider-line" />

      {/* SINCE YOUR LAST REVIEW */}
      <section className={styles.section}>
        <h3 className="section-label">SINCE YOUR LAST REVIEW</h3>
        {item.since_last_checked ? (
          <div className={styles.historyGrid}>
            <div className={styles.historyBlock}>
              <span className={styles.historyLabel}>Price</span>
              <div className={styles.historyValues}>
                <span className={styles.oldValue}>{item.since_last_checked.price_then !== null ? `₹${item.since_last_checked.price_then.toLocaleString('en-IN', {minimumFractionDigits: 2})}` : '—'}</span>
                <span className={styles.arrow}>→</span>
                <span className={styles.newValue}>{item.since_last_checked.price_now !== null ? `₹${item.since_last_checked.price_now.toLocaleString('en-IN', {minimumFractionDigits: 2})}` : '—'}</span>
                <span className={`${styles.historyPct} ${pctColor}`}>{formattedPct}</span>
              </div>
            </div>
            {item.since_last_checked.volume_then !== null && item.since_last_checked.volume_now !== null && (
              <div className={styles.historyBlock}>
                <span className={styles.historyLabel}>Volume</span>
                <div className={styles.historyValues}>
                  <span className={styles.oldValue}>{item.since_last_checked.volume_then.toLocaleString()}</span>
                  <span className={styles.arrow}>→</span>
                  <span className={styles.newValue}>{item.since_last_checked.volume_now.toLocaleString()}</span>
                </div>
              </div>
            )}
          </div>
        ) : item.is_new_to_state ? (
          <p className={styles.placeholderText}>First check</p>
        ) : (
          <p className={styles.placeholderText}>Previous snapshot unavailable</p>
        )}
      </section>

      <hr className="divider-line" />

      {/* MARKET CONTEXT */}
      <section className={styles.section}>
        <h3 className="section-label">MARKET CONTEXT</h3>
        <div className={styles.contextGrid}>
          {item.evidence.benchmark_pct_change !== null ? (
            <>
              <div className={styles.contextRow}>
                <span>NIFTY</span>
                <span className={item.evidence.benchmark_pct_change > 0 ? 'text-green' : item.evidence.benchmark_pct_change < 0 ? 'text-red' : 'text-secondary'}>
                  {item.evidence.benchmark_pct_change > 0 ? '+' : ''}{item.evidence.benchmark_pct_change.toFixed(1)}%
                </span>
              </div>
              <div className={styles.contextRow}>
                <span>{item.symbol}</span>
                <span className={pctColor}>{formattedPct}</span>
              </div>
              <div className={styles.contextVerdict}>
                {item.market_context === 'outlier' && <span className={styles.outlierBadge}>OUTLIER</span>}
                {item.market_context === 'tracking_market' && <span className={styles.trackingBadge}>TRACKING MARKET</span>}
                {item.market_context === 'normal' && <span className={styles.normalContextBadge}>NORMAL</span>}
              </div>
            </>
          ) : (
            <p className={styles.placeholderText}>Market comparison unavailable</p>
          )}
        </div>
      </section>

      <hr className="divider-line" />

      {/* DATA TRUST (CONFIDENCE/FRESHNESS) */}
      <section className={styles.section}>
        <h3 className="section-label">DATA QUALITY</h3>
        <div className={styles.trustGrid}>
          <span className={styles.confidenceBadge}>{item.confidence} CONFIDENCE</span>
          {renderFreshness()}
        </div>
      </section>

      <hr className="divider-line" />

      {/* ACTIONS */}
      <section className={styles.actions}>
        <button 
          className={styles.acknowledgeBtn} 
          onClick={handleAcknowledge}
          disabled={acknowledging || item.freshness === 'UNAVAILABLE'}
        >
          {acknowledging ? 'Reviewing...' : 'Mark as reviewed'}
        </button>
      </section>
    </div>
  );
}
