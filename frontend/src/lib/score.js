/**
 * Score banding, shared by every component that colours a number.
 *
 * Thresholds are judgement calls, not fitted values — 70 and 45 were chosen so
 * that "strong" means most required skills are present.
 */
export function band(score) {
  if (score >= 70)
    return { key: 'strong', label: 'Strong match', fill: 'bg-acid-400', text: 'text-acid-600 dark:text-acid-400' }
  if (score >= 45)
    return { key: 'partial', label: 'Partial match', fill: 'bg-warn', text: 'text-warn' }
  return { key: 'weak', label: 'Weak match', fill: 'bg-alert', text: 'text-alert' }
}
