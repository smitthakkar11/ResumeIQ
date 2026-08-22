/** Centred loading spinner, used by lazy routes and the auth gate. */
export function Spinner() {
  return (
    <div className="flex justify-center py-24">
      <div className="size-6 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600" />
    </div>
  )
}
