// Utility for stripping [source: filename] citation patterns from answer text.
// This is the single place in the codebase responsible for transforming raw
// answer text before display.

/**
 * Removes all [source: <filename>] citation patterns from the given text,
 * collapses any resulting double spaces to single spaces, and trims leading
 * and trailing whitespace from the result.
 *
 * Handles filenames containing spaces, hyphens, dots, and other valid
 * filename characters. Returns the original string unchanged if no citation
 * pattern is present.
 */
export function stripCitations(text: string): string {
  const stripped = text.replace(/\[source:[^\]]+\]/g, '')
  return stripped.replace(/  +/g, ' ').trim()
}
