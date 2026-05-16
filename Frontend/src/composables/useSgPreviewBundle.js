import { computed, unref } from 'vue'

/**
 * Provides mock data for the governance workspace when in preview mode.
 * This is used to display a functional UI even when the user is not logged in
 * or when viewing a school's public portal.
 */
export function useSgPreviewBundle(previewSource) {
  const previewBundle = computed(() => {
    if (!unref(previewSource)) return null

    return {
      activeUnit: {
        id: 1,
        governance_unit_id: 1,
        unit_code: 'SSG',
        unit_name: 'Supreme Student Government',
        unit_type: 'SSG',
        position_title: 'Officer',
        permission_codes: [],
        members: []
      },
      events: [],
      announcements: [],
      schoolSettings: {
        school_name: 'Aura Integrated School',
        logo_url: null,
        primary_color: '#4f46e5',
        secondary_color: '#1e1b4b'
      },
      attendance: {
        summary: {
          total_participants: 0,
          total_present: 0,
          total_late: 0,
          total_absent: 0
        },
        records: []
      }
    }
  })

  return {
    previewBundle
  }
}
