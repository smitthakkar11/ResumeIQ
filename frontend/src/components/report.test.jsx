import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SkillBadges } from '@/components/SkillBadges'
import { SectionChecklist } from '@/components/SectionChecklist'
import { Recommendations } from '@/components/Recommendations'
import { ScorePill } from '@/components/ScorePill'
import { band } from '@/lib/score'

describe('SkillBadges', () => {
  it('groups skills under their category', () => {
    render(
      <SkillBadges
        skills={[
          { name: 'Python', category: 'Language' },
          { name: 'React', category: 'Frontend' },
          { name: 'C++', category: 'Language' },
        ]}
      />,
    )
    expect(screen.getByText('Language')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('C++')).toBeInTheDocument()
  })

  it('shows an empty state rather than nothing at all', () => {
    render(<SkillBadges skills={[]} />)
    expect(screen.getByText(/no skills.*were detected/i)).toBeInTheDocument()
  })
})

describe('SectionChecklist', () => {
  const sections = { Contact: true, Education: true, Experience: false }

  it('marks detected and undetected sections differently', () => {
    render(<SectionChecklist sections={sections} />)
    expect(screen.getAllByText('detected')).toHaveLength(2)
    expect(screen.getAllByText('not detected')).toHaveLength(1)
  })

  it('says section detection can be wrong', () => {
    // Spec §20: never claim a resume is bad because a heuristic missed something.
    render(<SectionChecklist sections={sections} />)
    expect(screen.getByText(/can hide a section that is genuinely there/i)).toBeInTheDocument()
  })
})

describe('Recommendations', () => {
  it('renders each message with its category label', () => {
    render(
      <Recommendations
        items={[
          { category: 'skills', message: 'Docker was not detected.' },
          { category: 'content', message: 'No figures were detected.' },
        ]}
      />,
    )
    expect(screen.getByText('Skills')).toBeInTheDocument()
    expect(screen.getByText('Content')).toBeInTheDocument()
    expect(screen.getByText('Docker was not detected.')).toBeInTheDocument()
  })

  it('says so when there is nothing to suggest', () => {
    render(<Recommendations items={[]} />)
    expect(screen.getByText(/no suggestions/i)).toBeInTheDocument()
  })
})

describe('score bands', () => {
  // Assert the banding logic, not the Tailwind class names — restyling should
  // not break tests, and it did the first time these were written that way.
  it.each([
    [100, 'strong'],
    [70, 'strong'],
    [69.9, 'partial'],
    [45, 'partial'],
    [44.9, 'weak'],
    [0, 'weak'],
  ])('bands %s%% as %s', (score, expected) => {
    expect(band(score).key).toBe(expected)
  })

  it('gives each band a distinct human label', () => {
    const labels = [90, 55, 10].map((s) => band(s).label)
    expect(new Set(labels).size).toBe(3)
  })
})

describe('ScorePill', () => {
  it('renders the score as a percentage', () => {
    render(<ScorePill score={78.4} />)
    expect(screen.getByText('78.4%')).toBeInTheDocument()
  })
})
