import { onMounted, shallowRef } from 'vue'

/** Fetch a bundled binary file (imported with `?url`) once the component mounts. */
export function useBinary(url: string) {
  const buf = shallowRef<ArrayBuffer | null>(null)
  onMounted(async () => { buf.value = await (await fetch(url)).arrayBuffer() })
  return buf
}
