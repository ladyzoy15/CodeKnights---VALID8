export function resolveGoogleWebClientId() {
    const runtime = typeof window !== 'undefined' ? window.__NEXUS_RUNTIME_CONFIG__ : null
    const fromRuntime = runtime?.googleWebClientId
    if (fromRuntime && !fromRuntime.startsWith('${')) {
        return String(fromRuntime).trim()
    }
    const fromEnv = import.meta?.env?.VITE_GOOGLE_WEB_CLIENT_ID || '1059104622372-jn3avucjr34lht8o6r99i9t57npbv0tt.apps.googleusercontent.com'
    return String(fromEnv).trim()
}

export function isGoogleLoginAvailable() {
    return resolveGoogleWebClientId().length > 0
}
