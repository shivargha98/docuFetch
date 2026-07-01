// Unit tests for the stripCitations utility in src/utils/sources.ts.

import { describe, it, expect } from 'vitest'
import { stripCitations } from '../../src/utils/sources'

describe('stripCitations', () => {
  it('strips a single citation from the middle of a sentence', () => {
    const result = stripCitations('See this [source: report.pdf] for details')
    expect(result).not.toContain('[source: report.pdf]')
    expect(result).not.toMatch(/\[.*\]/)
    expect(result).toBe('See this for details')
  })

  it('strips multiple citations scattered at arbitrary positions', () => {
    const input = 'First point [source: doc1.pdf] and second point [source: doc2.txt]'
    const result = stripCitations(input)
    expect(result).not.toContain('[source: doc1.pdf]')
    expect(result).not.toContain('[source: doc2.txt]')
    expect(result).toContain('First point')
    expect(result).toContain('and second point')
  })

  it('strips a citation with a filename containing spaces', () => {
    const result = stripCitations('Answer [source: my notes.txt] here')
    expect(result).not.toContain('[source: my notes.txt]')
    expect(result).not.toMatch(/\[.*\]/)
    expect(result).toBe('Answer here')
  })

  it('strips a citation with a filename containing hyphens and dots', () => {
    const result = stripCitations('See [source: project-brief.v2.pdf]')
    expect(result).not.toContain('[source: project-brief.v2.pdf]')
    expect(result).not.toMatch(/\[.*\]/)
  })

  it('returns an unchanged string when no citation is present', () => {
    const input = 'This is a plain answer with no citations.'
    const result = stripCitations(input)
    expect(result).toBe(input)
  })

  it('does not mutate the input string', () => {
    const input = 'Answer [source: report.pdf] here'
    stripCitations(input)
    expect(input).toBe('Answer [source: report.pdf] here')
  })
})
