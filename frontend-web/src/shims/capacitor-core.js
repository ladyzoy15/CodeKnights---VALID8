/**
 * Web shim for @capacitor/core
 * This stub replaces Capacitor on web builds so all existing
 * Capacitor-aware code continues to work — isNativePlatform()
 * always returns false, which activates the web-only code paths.
 */
export const Capacitor = {
  isNativePlatform: () => false,
  isPluginAvailable: () => false,
  getPlatform: () => 'web',
  convertFileSrc: (src) => src,
}

export default Capacitor
