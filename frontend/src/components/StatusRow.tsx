type State = 'loading' | 'ok' | 'error'

const DOT: Record<State, string> = {
  loading: 'bg-slate-400 animate-pulse',
  ok: 'bg-emerald-500',
  error: 'bg-rose-500',
}

const LABEL: Record<State, string> = {
  loading: 'text-slate-500 dark:text-slate-400',
  ok: 'text-emerald-600 dark:text-emerald-400',
  error: 'text-rose-600 dark:text-rose-400',
}

export function StatusRow({ label, state, detail }: { label: string; state: State; detail: string }) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-0 dark:border-slate-800">
      <div className="flex items-center gap-3">
        <span className={`size-2 rounded-full ${DOT[state]}`} />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <span className={`font-mono text-xs ${LABEL[state]}`}>{detail}</span>
    </div>
  )
}

export type { State as StatusState }
