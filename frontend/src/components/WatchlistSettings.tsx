import { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import styles from './WatchlistSettings.module.css';

const GOALS = [
  { value: 'GENERAL', label: 'General' },
  { value: 'LONG_TERM_WEALTH', label: 'Long-term wealth' },
  { value: 'RETIREMENT', label: 'Retirement' },
  { value: 'GROWTH', label: 'Growth' },
  { value: 'DIVIDEND', label: 'Dividend income' },
  { value: 'VALUE', label: 'Value investing' },
  { value: 'SECTOR_THEME', label: 'Sector / Theme' },
] as const;

const HORIZONS = [
  { value: 'SHORT_TERM', label: 'Short term' },
  { value: 'MEDIUM_TERM', label: 'Medium term' },
  { value: 'LONG_TERM', label: 'Long term' },
] as const;

interface Props {
  watchlistId: number;
  onClose: () => void;
}

export function WatchlistSettings({ watchlistId, onClose }: Props) {
  const [goal, setGoal] = useState<string | null>(null);
  const [horizon, setHorizon] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/watchlists/${watchlistId}/context`)
      .then(r => r.json())
      .then(data => {
        setGoal(data.goal ?? null);
        setHorizon(data.horizon ?? null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [watchlistId]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`/api/watchlists/${watchlistId}/context`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, horizon }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // Silent fail for demo
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true" aria-label="Watchlist settings">
      <div className={styles.panel}>
        <div className={styles.panelHeader}>
          <h2 className={styles.panelTitle}>WATCHLIST INTENT</h2>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close settings">
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <p className={styles.loadingText}>Loading…</p>
        ) : (
          <>
            <section className={styles.section}>
              <p className={styles.sectionLabel}>What are you tracking this watchlist for?</p>
              <div className={styles.optionGrid} role="radiogroup" aria-label="Investment goal">
                {GOALS.map(g => (
                  <button
                    key={g.value}
                    id={`goal-${g.value}`}
                    role="radio"
                    aria-checked={goal === g.value}
                    className={`${styles.optionBtn} ${goal === g.value ? styles.selected : ''}`}
                    onClick={() => setGoal(g.value === goal ? null : g.value)}
                  >
                    {g.label}
                  </button>
                ))}
              </div>
            </section>

            <section className={styles.section}>
              <p className={styles.sectionLabel}>Investment horizon</p>
              <div className={styles.optionRow} role="radiogroup" aria-label="Investment horizon">
                {HORIZONS.map(h => (
                  <button
                    key={h.value}
                    id={`horizon-${h.value}`}
                    role="radio"
                    aria-checked={horizon === h.value}
                    className={`${styles.optionBtn} ${horizon === h.value ? styles.selected : ''}`}
                    onClick={() => setHorizon(h.value === horizon ? null : h.value)}
                  >
                    {h.label}
                  </button>
                ))}
              </div>
            </section>

            <div className={styles.actions}>
              <button
                className={styles.saveBtn}
                onClick={handleSave}
                disabled={saving}
                aria-label="Save watchlist intent"
              >
                {saved ? (
                  <><Check size={16} /> Saved</>
                ) : saving ? (
                  'Saving…'
                ) : (
                  'Save'
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
