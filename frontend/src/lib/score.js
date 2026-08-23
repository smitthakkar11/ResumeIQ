/**
 * Score banding, shared by every component that colours a number.
 *
 * Thresholds are judgement calls, not fitted values — 70 and 45 were chosen so
 * that "strong" means most required skills are present.
 */
export function band(score) {
  if (score >= 70)
    return {
      key: 'strong',
      label: 'Strong match',
      fill: 'bg-brand-500',
      text: 'text-brand-600 dark:text-brand-400',
      soft: 'bg-brand-50 dark:bg-brand-500/12',
    }
  if (score >= 45)
    return {
      key: 'partial',
      label: 'Partial match',
      fill: 'bg-warn',
      text: 'text-warn',
      soft: 'bg-warn-soft dark:bg-warn/12',
    }
  return {
    key: 'weak',
    label: 'Weak match',
    fill: 'bg-alert',
    text: 'text-alert',
    soft: 'bg-alert-soft dark:bg-alert/12',
  }
}
