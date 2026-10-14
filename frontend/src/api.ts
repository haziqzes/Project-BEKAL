const DESKTOP_API_ORIGIN = 'http://127.0.0.1:8000'

function isPackagedDesktop(): boolean {
  return window.location.hostname === 'tauri.localhost'
    || window.location.protocol === 'tauri:'
}

export function apiUrl(path: string): string {
  if (/^[a-z][a-z\d+.-]*:\/\//i.test(path)) {
    return path
  }

  if (!path.startsWith('/api/')) {
    return path
  }

  return isPackagedDesktop()
    ? `${DESKTOP_API_ORIGIN}${path}`
    : path
}
