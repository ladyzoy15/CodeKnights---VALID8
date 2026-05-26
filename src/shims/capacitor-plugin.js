/**
 * Generic web shim for individual Capacitor plugins.
 * On web builds, all plugin calls become no-ops so existing
 * code paths that guard with Capacitor.isNativePlatform() stay safe.
 */
const noop = () => Promise.resolve()
const noopSync = () => {}

const handler = {
  get: (_target, prop) => {
    if (prop === 'then') return undefined // not a Promise
    return noop
  },
}

const pluginProxy = new Proxy({}, handler)

// Named exports that plugins typically expose
export const Camera = pluginProxy
export const Geolocation = pluginProxy
export const Haptics = pluginProxy
export const StatusBar = pluginProxy
export const Style = {}
export const SplashScreen = pluginProxy
export const App = pluginProxy
export const Keyboard = pluginProxy
export const Network = pluginProxy

export default pluginProxy
