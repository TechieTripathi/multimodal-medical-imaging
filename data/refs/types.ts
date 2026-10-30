// A single bibliographic source. Every factual claim on a slide must trace to one of these.
export interface Ref {
  /** Stable citation key, e.g. 'vaswani2017'. Unique across all files in data/refs/. */
  key: string
  /** Authors or organisation, e.g. 'Vaswani, A. et al.' or 'OWASP Foundation'. */
  authors: string
  year: number | string
  title: string
  /** Journal, conference, publisher or website. */
  venue: string
  /** Canonical URL (DOI or arXiv abs page preferred). Must have been opened and checked. */
  url: string
  /** Date the URL was checked, ISO format. */
  accessed?: string
  /** What the source supports, in a few words (shown on the sources slides). */
  supports?: string
}
