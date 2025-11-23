const API_BASE_URL = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const apiURL = new URL(API_BASE_URL)
const wsProtocol = apiURL.protocol === 'https:' ? 'wss:' : 'ws:'
const WS_BASE_URL = `${wsProtocol}//${apiURL.host}${apiURL.pathname.replace(/\/$/, '')}`

export { API_BASE_URL, WS_BASE_URL }
