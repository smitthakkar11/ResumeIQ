import { ComponentBars } from '@/components/ComponentBars'
import { JobIntelligence } from '@/components/JobIntelligence'
import { PartialSkills } from '@/components/PartialSkills'
import { QualityScore } from '@/components/QualityScore'
import { Recommendations } from '@/components/Recommendations'
import { ScoreMeter } from '@/components/ScoreMeter'
import { SectionChecklist } from '@/components/SectionChecklist'
import { SemanticComparison } from '@/components/SemanticComparison'
import { SkillBadges } from '@/components/SkillBadges'
import { SectionHead } from '@/components/ui'

/** The full results view. Shared by /analyze and /results/:id. */
export function AnalysisReport({ result, divider = false }) {
  const hasSemantic =
    result.semantic_similarity !== null && result.semantic_similarity !== undefined

  return (
    <div className={divider ? 'rule pt-10' : ''}>
      <div className="mb-8 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 className="font-display text-2xl font-bold tracking-tight">
          {result.job_title || 'Results'}
        </h2>
        <span className="num text-[11px] text-ink-400 dark:text-ink-600">
          {result.resume_filename}
        </span>
      </div>

      {/* ---- the readout: score left, breakdown right ---- */}
      <div className="panel grid gap-10 p-6 lg:grid-cols-[1.1fr_1fr] lg:p-8">
        <ScoreMeter score={result.match_score} />
        <div className="lg:border-l lg:border-paper-line lg:pl-10 dark:lg:border-ink-800">
          <h3 className="font-display text-lg font-bold tracking-tight">Breakdown</h3>
          <div className="mt-3">
            <ComponentBars result={result} />
          </div>
          <p className="mt-4 text-[13px] leading-relaxed text-ink-400 dark:text-ink-600">
            Each part is weighted and combined into the overall figure.
          </p>
        </div>
      </div>

      {hasSemantic && (
        <div className="mt-10">
          <SemanticComparison result={result} />
        </div>
      )}

      {/* ---- skill gap: have / partial / missing ---- */}
      <div className="mt-12 grid gap-10 lg:grid-cols-3">
        <section>
          <SectionHead
            right={<span className="num text-xs text-ink-400">{result.matched_skills.length}</span>}
          >
            Matched skills
          </SectionHead>
          <SkillBadges skills={result.matched_skills} tone="matched" />
        </section>

        <section>
          <SectionHead
            right={
              <span className="num text-xs text-ink-400">{result.partial_skills.length}</span>
            }
          >
            Partial matches
          </SectionHead>
          <PartialSkills partials={result.partial_skills} />
        </section>

        <section>
          <SectionHead
            right={<span className="num text-xs text-ink-400">{result.missing_skills.length}</span>}
          >
            Missing skills
          </SectionHead>
          {result.missing_skills.length === 0 ? (
            <p className="text-sm text-ink-500 dark:text-ink-400">
              Nothing missing — the resume names every skill the job asked for.
            </p>
          ) : (
            <SkillBadges skills={result.missing_skills} tone="missing" />
          )}
        </section>
      </div>

      {/* ---- keywords ---- */}
      <section className="mt-12">
        <SectionHead
          right={
            <span className="num text-xs text-ink-400">
              {result.keywords.filter((k) => k.found).length}/{result.keywords.length} found
            </span>
          }
        >
          Keywords from the job post
        </SectionHead>
        <div className="flex flex-wrap gap-1.5">
          {result.keywords.map((k) => (
            <span
              key={k.term}
              className={`rounded-md border px-2 py-1 font-mono text-[11px] ${
                k.found
                  ? 'border-brand-500/30 bg-brand-500/10 text-brand-700 dark:text-brand-300'
                  : 'border-paper-line text-ink-500 line-through decoration-alert dark:border-ink-700 dark:text-ink-400'
              }`}
            >
              {k.term}
            </span>
          ))}
        </div>
      </section>

      {result.resume_quality_score !== null &&
        result.quality_breakdown?.length > 0 && (
          <section className="mt-12">
            <SectionHead>Your resume on its own</SectionHead>
            <QualityScore
              overall={result.resume_quality_score}
              components={result.quality_breakdown}
            />
          </section>
        )}

      {result.requirements && (
        <section className="mt-12">
          <SectionHead>What the job asks for</SectionHead>
          <JobIntelligence requirements={result.requirements} />
        </section>
      )}

      {/* ---- structure + recommendations ---- */}
      <div className="mt-12 grid gap-10 lg:grid-cols-[1fr_1.6fr]">
        <section>
          <SectionHead>Resume structure</SectionHead>
          <SectionChecklist sections={result.sections} />
        </section>

        <section>
          <SectionHead>Recommendations</SectionHead>
          <Recommendations items={result.recommendations} />
        </section>
      </div>
    </div>
  )
}
