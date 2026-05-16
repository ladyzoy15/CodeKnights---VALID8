"""Use: Marks `routers` as a Python package and groups related backend files.
Where to use: Used automatically when Python imports modules from `routers`.
Role: Package layer. It helps the backend treat this folder as one importable package.
"""

from . import (
    users,
    events,
    programs,
    departments,
    auth,
    google_auth,
    attendance,
    school_settings,
    admin_placeholder,
    admin_import,
    school,
    audit_logs,
    notifications,
    security_center,
    subscription,
    governance,
    governance_hierarchy,
    face_recognition,
    public_attendance,
    health,
    sanctions,
)
