import { Bar, BarChart, Cell, LabelList, ResponsiveContainer, XAxis, YAxis } from 'recharts'
const COLOURS = ['#6366f1', '#8b5cf6', '#a78bfa']

/**
 * The three score components side by side. This is the point of a transparent
 * score: you can see which part is dragging the total down.
 */
export function ComponentBars({ result }) {
  const data = [
    {
      name: 'Text similarity',
      value: result.text_similarity,
      weight: result.weights.text_similarity,
    },
    {
      name: 'Skill match',
      value: result.skill_match ?? 0,
      weight: result.weights.skill_match,
    },
    {
      name: 'Keyword match',
      value: result.keyword_match,
      weight: result.weights.keyword_match,
    },
  ].filter((d) => d.weight !== undefined)
  return (
    <div className="h-44 w-full">
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{
            left: 0,
            right: 44,
            top: 4,
            bottom: 4,
          }}
        >
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            axisLine={false}
            tickLine={false}
            tick={{
              fontSize: 12,
              fill: 'currentColor',
            }}
            className="text-slate-600 dark:text-slate-400"
          />
          <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((entry, i) => (
              <Cell key={entry.name} fill={COLOURS[i % COLOURS.length]} />
            ))}
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v) => `${v ?? 0}%`}
              className="fill-slate-700 dark:fill-slate-300"
              style={{
                fontSize: 12,
                fontWeight: 600,
              }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">
        {data.map((d) => `${d.name} x${d.weight}`).join('  ·  ')}
      </p>
    </div>
  )
}
