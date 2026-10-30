// The seven sections of the deck (IDEA.md §2). Slide ranges are core slide numbers.
export interface Section {
  no: number
  name: string
  slides: [number, number]
  minutes: number
}

export const SECTIONS: Section[] = [
  { no: 1, name: 'The problem', slides: [1, 8], minutes: 12 },
  { no: 2, name: 'How multimodal AI works', slides: [9, 18], minutes: 22 },
  { no: 3, name: 'Training, evaluation and models', slides: [19, 28], minutes: 20 },
  { no: 4, name: 'DICOM and imaging data', slides: [29, 36], minutes: 16 },
  { no: 5, name: 'Applications', slides: [37, 44], minutes: 14 },
  { no: 6, name: 'Demonstrations', slides: [45, 53], minutes: 22 },
  { no: 7, name: 'Responsible use', slides: [54, 58], minutes: 14 },
]

export const CORE_SLIDES = 58
/** Unnumbered slides before slide 1 (the institutional cover). */
export const FRONT_SLIDES = 1

export function sectionFor(no: number | undefined): Section | undefined {
  return SECTIONS.find(s => s.no === no)
}
