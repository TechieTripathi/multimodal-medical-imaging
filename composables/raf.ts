/**
 * Wrap a canvas draw so it runs at most once per screen refresh. Sliders fire many input events per
 * frame; drawing each one makes them lag on slower laptops, so only the latest state is drawn.
 */
export function rafThrottle(fn: () => void) {
  let id = 0
  return () => {
    if (id) return
    id = requestAnimationFrame(() => { id = 0; fn() })
  }
}
