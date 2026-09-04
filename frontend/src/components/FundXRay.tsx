import { useEffect, useState } from 'react';
import styles from './FundXRay.module.css';

interface Holding {
  symbol: string;
  weight: number;
}

interface FundData {
  id: number;
  name: string;
  category: string;
  expense_ratio: number;
  top_holdings: Holding[];
}

interface Props {
  fundId: number;
}

export function FundXRay({ fundId }: Props) {
  const [data, setData] = useState<FundData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/funds/${fundId}/xray`)
      .then(r => {
        if (!r.ok) throw new Error('Failed to load fund data');
        return r.json();
      })
      .then(json => {
        setData(json);
        setError(null);
      })
      .catch(e => {
        setError(e.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [fundId]);

  if (loading) {
    return <div className={styles.loading}>Loading fund data…</div>;
  }

  if (error || !data) {
    return <div className={styles.error}>{error || 'Unavailable'}</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.title}>{data.name.toUpperCase()}</h3>
        <span className={styles.subtitle}>
          Expense Ratio: {data.expense_ratio.toFixed(2)}%
        </span>
      </div>

      <div className={styles.holdingsSection}>
        <h4 className={styles.holdingsTitle}>TOP HOLDINGS</h4>
        <ul className={styles.holdingsList}>
          {data.top_holdings.map((h, i) => (
            <li key={h.symbol} className={styles.holdingItem}>
              <span className={styles.holdingRank}>{i + 1}.</span>
              <span className={styles.holdingSymbol}>{h.symbol}</span>
              <span className={styles.holdingWeight}>{h.weight.toFixed(1)}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
