import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const rawProxyTarget = String(env.VITE_BACKEND_PROXY_TARGET || "")
    .trim()
    .replace(/\/+$/, "");
  const proxyTarget = normalizeProxyTarget(rawProxyTarget);
  const strictBuildWarnings =
    String(env.CI_STRICT_BUILD_WARNINGS || "")
      .trim()
      .toLowerCase() === "true";
  const chunkSizeWarningLimit = readPositiveInteger(
    env.CI_CHUNK_SIZE_WARNING_LIMIT_KB,
    1400,
  );

  return {
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        '@capacitor/core': fileURLToPath(new URL('./src/shims/capacitor-core.js', import.meta.url)),
        '@capacitor/camera': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/geolocation': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/haptics': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/status-bar': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/splash-screen': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/app': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/keyboard': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/network': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/local-notifications': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/filesystem': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
        '@capacitor/share': fileURLToPath(new URL('./src/shims/capacitor-plugin.js', import.meta.url)),
      },
    },
    server: proxyTarget
      ? {
          host: "0.0.0.0",
          allowedHosts: [".ngrok-free.app", ".ngrok-free.dev"],
          proxy: {
            "/__backend__": {
              target: proxyTarget,
              changeOrigin: true,
              secure: true,
              rewrite: (path) => path.replace(/^\/__backend__/, ""),
              headers: {
                "ngrok-skip-browser-warning": "true",
              },
            },
          },
        }
      : {
          host: "0.0.0.0",
          allowedHosts: [".ngrok-free.app", ".ngrok-free.dev"],
        },
    build: {
      chunkSizeWarningLimit,
      rollupOptions: strictBuildWarnings
        ? {
            onwarn(warning) {
              throw new Error(formatRollupWarning(warning));
            },
          }
        : undefined,
    },
  };
});

function normalizeProxyTarget(target) {
  if (!target) return "";

  try {
    const url = new URL(target);
    if (url.pathname === "/api") {
      url.pathname = "";
      return url.toString().replace(/\/+$/, "");
    }
    return url.toString().replace(/\/+$/, "");
  } catch {
    return target;
  }
}

function readPositiveInteger(value, fallbackValue) {
  const numericValue = Number(value);
  return Number.isInteger(numericValue) && numericValue > 0
    ? numericValue
    : fallbackValue;
}

function formatRollupWarning(warning) {
  const location = warning.loc
    ? `${warning.loc.file}:${warning.loc.line}:${warning.loc.column}`
    : warning.id || "unknown location";
  const code = warning.code || "ROLLUP_WARNING";
  const frame = warning.frame ? `\n${warning.frame}` : "";
  return `CI strict build warning [${code}] at ${location}: ${warning.message}${frame}`;
}
