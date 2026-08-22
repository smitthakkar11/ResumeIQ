import { PolarAngleAxis, RadialBar, RadialBarChart, ResponsiveContainer } from 'recharts'
import { useTheme } from '@/lib/theme'

/** Colour follows the score so the number and the visual agree. */
function bandColour(score) {
  if (score >= 70) return '#10b981' // emerald
  if (score >= 45) return '#f59e0b' // amber
  return '#f43f5e' // rose
}
export function ScoreGauge({ score }) {
  const { theme } = useTheme()
  const colour = bandColour(score)
  // Recharts takes SVG fills, not CSS classes, so the track colour is picked
  // from the theme rather than a dark: variant.
  const track = theme === 'dark' ? '#1e293b' : '#e2e8f0'
  return (
    <div className="relative h-52 w-full">
      <ResponsiveContainer>
        <RadialBarChart
          innerRadius="72%"
          outerRadius="100%"
          data={[
            {
              value: score,
            },
          ]}
          startAngle={220}
          endAngle={-40}
        >
          {/* Fixes the scale to 0-100 so the arc length means something. */}
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar
            dataKey="value"
            cornerRadius={999}
            fill={colour}
            background={{
              fill: track,
            }}
          />
        </RadialBarChart>
      </ResponsiveContainer>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-4xl font-bold tabular-nums"
          style={{
            color: colour,
          }}
        >
          {score}%
        </span>
        <span className="mt-0.5 text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Overall match
        </span>
      </div>
    </div>
  )
}
