import { ref } from 'vue'
import { Capacitor } from '@capacitor/core'

const defaultSchoolLogo = '/logos/aura.png'
const DARK_MODE_STORAGE_KEY = 'aura_dark_mode'

function readStoredDarkModePreference() {
    try {
        return window?.localStorage?.getItem(DARK_MODE_STORAGE_KEY) === '1'
    } catch {
        return false
    }
}

function persistDarkModePreference(value) {
    try {
        window?.localStorage?.setItem(DARK_MODE_STORAGE_KEY, value ? '1' : '0')
    } catch {}
}

export const isDarkMode = ref(readStoredDarkModePreference())
export const activeAuraLogo = ref('/logos/aura_logo_black.png')
export const surfaceAuraLogo = ref('/logos/aura_logo_black.png')
export const secondaryAuraLogo = ref('/logos/aura_logo_black.png')

let currentActiveTheme = null

export const defaultTheme = {
    primaryColor: '#AAFF00',
    primaryDark: '#88CC00',
    primaryText: '#0A0A0A',

    secondaryColor: '#AAFF00',
    secondaryText: '#0A0A0A',

    background: '#EBEBEB',
    surfaceColor: '#FFFFFF',

    navColor: '#0A0A0A',
    navActiveColor: '#AAFF00',
}

// ================== HELPERS ==================

function darkenHex(hex, percent) {
    hex = hex.replace('#', '')
    let r = parseInt(hex.substring(0, 2), 16)
    let g = parseInt(hex.substring(2, 4), 16)
    let b = parseInt(hex.substring(4, 6), 16)

    const multiplier = 1 - percent / 100

    r = Math.floor(r * multiplier)
    g = Math.floor(g * multiplier)
    b = Math.floor(b * multiplier)

    return `#${[r, g, b].map(v => v.toString(16).padStart(2, '0')).join('')}`
}

function getContrastYIQ(hex) {
    hex = hex.replace('#', '')
    const r = parseInt(hex.substr(0, 2), 16)
    const g = parseInt(hex.substr(2, 2), 16)
    const b = parseInt(hex.substr(4, 2), 16)

    const yiq = (r * 299 + g * 587 + b * 114) / 1000
    return yiq >= 128 ? '#0A0A0A' : '#FFFFFF'
}

function mixHexColors(a, b, weight = 0.5) {
    const hexToRgb = (hex) => ({
        r: parseInt(hex.slice(1, 3), 16),
        g: parseInt(hex.slice(3, 5), 16),
        b: parseInt(hex.slice(5, 7), 16),
    })

    const rgbToHex = ({ r, g, b }) =>
        '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('')

    const c1 = hexToRgb(a)
    const c2 = hexToRgb(b)

    return rgbToHex({
        r: c1.r * weight + c2.r * (1 - weight),
        g: c1.g * weight + c2.g * (1 - weight),
        b: c1.b * weight + c2.b * (1 - weight),
    })
}

// ================== DARK MODE CONTROL ==================

export function toggleDarkMode() {
    setDarkMode(!isDarkMode.value)
}

export function setDarkMode(value) {
    isDarkMode.value = Boolean(value)
    persistDarkModePreference(isDarkMode.value)

    if (currentActiveTheme) {
        applyTheme(currentActiveTheme)
    }
}

// ================== MAIN THEME ==================

export function applyTheme(theme) {
    currentActiveTheme = theme
    const root = document.documentElement

    let bgColor = theme.background
    let surfaceColor = theme.surfaceColor

    if (isDarkMode.value) {
        bgColor = darkenHex(theme.primaryColor, 96)
    }

    const navPillBg = isDarkMode.value ? '#EBEBEB' : surfaceColor

    let textPrimary, textSecondary, textMuted
    let surfaceText, surfaceSecondary, surfaceMuted
    let navText, navSecondary

    if (isDarkMode.value) {
        // 🌙 DARK MODE (FIXED)
        textPrimary = '#FFFFFF'
        textSecondary = '#D1D5DB'
        textMuted = '#9CA3AF'

        surfaceText = '#0A0A0A'
        surfaceSecondary = '#555555'
        surfaceMuted = '#777777'

        navText = '#FFFFFF'
        navSecondary = '#A0A0A0'
    } else {
        // ☀️ LIGHT MODE (AUTO)
        const bgText = getContrastYIQ(bgColor)
        const surfText = getContrastYIQ(surfaceColor)
        const navTxt = getContrastYIQ(theme.navColor)

        textPrimary = bgText
        textSecondary = mixHexColors(bgText, bgColor, 0.7)
        textMuted = mixHexColors(bgText, bgColor, 0.5)

        surfaceText = surfText
        surfaceSecondary = mixHexColors(surfText, surfaceColor, 0.7)
        surfaceMuted = mixHexColors(surfText, surfaceColor, 0.5)

        navText = navTxt
        navSecondary = mixHexColors(navTxt, theme.navColor, 0.7)
    }

    root.style.setProperty('--color-bg', bgColor)
    root.style.setProperty('--color-surface', surfaceColor)
    root.style.setProperty('--color-nav', theme.navColor)
    root.style.setProperty('--color-nav-pill-bg', navPillBg)

    root.style.setProperty('--color-text-primary', textPrimary)
    root.style.setProperty('--color-text-secondary', textSecondary)
    root.style.setProperty('--color-text-muted', textMuted)

    root.style.setProperty('--color-surface-text', surfaceText)
    root.style.setProperty('--color-surface-text-secondary', surfaceSecondary)
    root.style.setProperty('--color-surface-text-muted', surfaceMuted)

    root.style.setProperty('--color-nav-text', navText)
    root.style.setProperty('--color-nav-text-secondary', navSecondary)

    root.style.setProperty('--color-primary', theme.primaryColor)
    root.style.setProperty('--color-primary-text', theme.primaryText)

    root.style.setProperty('color-scheme', isDarkMode.value ? 'dark' : 'light')

    activeAuraLogo.value = getContrastYIQ(theme.primaryColor) === '#FFFFFF'
        ? '/logos/aura_logo_white.png'
        : '/logos/aura_logo_black.png'
}