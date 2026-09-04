import type { WatchlistChangeItem } from '../types/api';
import { ChevronRight, AlertCircle, Clock } from 'lucide-react';
import styles from './StockCard.module.css';

interface Props {
  item: WatchlistChangeItem;
  onClick: () => void;
}

export function StockCard({ item, onClick }: Props) {
  const isSignificant = item.verdict === 'needs_attention';
  const isNoChange = item.verdict === 'no_change';

  // Format percent to display nicely (e.g. "+2.1%" or "-1.4%")
  const formattedPct = item.pct_change > 0 ? `+${item.pct_change.toFixed(1)}%` : `${item.pct_change.toFixed(1)}%`;
  const pctColor = item.pct_change > 0 ? 'text-green' : item.pct_change < 0 ? 'text-red' : 'text-secondary';

  const renderFreshness = () => {
    switch (item.freshness) {
      case 'LIVE': return <span className={styles.live}><span className={styles.liveDot}></span>LIVE</span>;
      case 'DELAYED': return <span className={styles.delayed}><Clock size={12}/> DELAYED</span>;
      case 'STALE': return <span className={styles.stale}><AlertCircle size={12}/> STALE</span>;
      case 'UNAVAILABLE': return <span className={styles.unavailable}><AlertCircle size={12}/> UNAVAILABLE</span>;
      default: return null;
    }
  };

  const renderConfidence = () => {
    return (
      <span className={styles.confidence}>
        {item.confidence} CONFIDENCE
      </span>
    );
  };

  return (
    <div 
      className={`${styles.card} ${isSignificant ? styles.significant : ''} ${isNoChange ? styles.noChange : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if(e.key === 'Enter') onClick(); }}
    >
      <div className={styles.header}>
        <div className={styles.topRow}>
          <div className={styles.titleInfo}>
            <h3 className={styles.symbol}>{item.symbol}</h3>
            <span className={styles.price}>₹{item.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
            <span className={`${styles.pctChange} ${pctColor}`}>{formattedPct}</span>
          </div>
          <ChevronRight size={20} className={styles.navArrow} />
        </div>
        
        {isSignificant && (
          <div className={styles.significantBadge}>
            SIGNIFICANT MOVEMENT
          </div>
        )}
        
        {item.freshness !== 'UNAVAILABLE' && (
          <div className={styles.summary}>
            <p className={styles.headline}>{item.headline}</p>
            <p className={styles.whyItMatters}>{item.why_it_matters}</p>
          </div>
        )}

        <div className={styles.footer}>
          {renderConfidence()}
          <span className={styles.divider}>·</span>
          {renderFreshness()}
        </div>
      </div>
    </div>
  );
}
