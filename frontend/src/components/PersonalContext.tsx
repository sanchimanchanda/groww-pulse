import type { PersonalContext as PersonalContextType } from '../types/api';
import styles from './PersonalContext.module.css';

interface Props {
  context?: PersonalContextType;
}

export function PersonalContext({ context }: Props) {
  if (!context) return null;

  const hasContent = context.thesis || context.valuation || (context.events && context.events.length > 0) || (context.fund_overlap && context.fund_overlap.length > 0);
  if (!hasContent) return null;

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>PERSONAL CONTEXT</h3>
      
      {context.thesis && (
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.icon}>🎯</span>
            <h4>Investment Thesis: {context.thesis.type}</h4>
          </div>
          {context.thesis.note && <p className={styles.note}>"{context.thesis.note}"</p>}
          {context.thesis.status === "REVIEW" && (
            <div className={styles.alert}>
              <strong>⚠️ Thesis Challenged:</strong> {context.thesis.action}
            </div>
          )}
        </div>
      )}

      {context.valuation && (
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.icon}>⚖️</span>
            <h4>Valuation</h4>
          </div>
          <p className={styles.detail}>
            Current P/E: <strong>{context.valuation.current_pe.toFixed(1)}</strong> 
            {' '}({context.valuation.delta_pct > 0 ? '+' : ''}{context.valuation.delta_pct.toFixed(1)}% vs historical median)
            — <span className={styles.label}>{context.valuation.label.replace(/_/g, ' ')}</span>
          </p>
        </div>
      )}

      {context.events && context.events.length > 0 && (
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.icon}>📅</span>
            <h4>Upcoming Events</h4>
          </div>
          <ul className={styles.list}>
            {context.events.map((e, i) => (
              <li key={i}>
                <strong>{e.type}</strong>: {e.title} (in {e.days_until} days)
              </li>
            ))}
          </ul>
        </div>
      )}

      {context.fund_overlap && context.fund_overlap.length > 0 && (
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <span className={styles.icon}>🧩</span>
            <h4>Mutual Fund Overlap</h4>
          </div>
          <ul className={styles.list}>
            {context.fund_overlap.map((f, i) => (
              <li key={i}>
                Found in <strong>{f.fund_name}</strong> ({f.weight.toFixed(1)}% weight)
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
