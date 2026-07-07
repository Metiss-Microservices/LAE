from fastapi import HTTPException


# =========================================================
# ROLES
# =========================================================

ROLE_SUPER_ADMIN = "super_admin"

ROLE_ADMIN = "admin"

ROLE_OPERATOR = "operator"

ROLE_SUPPORT = "support"

ROLE_FINANCE = "finance"

ROLE_MARKETING = "marketing"


# =========================================================
# PERMISSIONS
# =========================================================

PERMISSIONS = {

    ROLE_SUPER_ADMIN: [

        "*"
    ],

    ROLE_ADMIN: [

        "dashboard",

        "suppliers",

        "clients",

        "leads",

        "matches",

        "payments",

        "settings",

        "channels",

        "campaigns",

        "reports"
    ],

    ROLE_OPERATOR: [

        "dashboard",

        "suppliers",

        "clients",

        "leads",

        "matches"
    ],

    ROLE_SUPPORT: [

        "clients",

        "leads",

        "matches"
    ],

    ROLE_FINANCE: [

        "payments",

        "reports"
    ],

    ROLE_MARKETING: [

        "campaigns",

        "channels",

        "reports"
    ]
}


# =========================================================
# CHECK
# =========================================================

def has_permission(
    role,
    permission
):

    allowed = PERMISSIONS.get(
        role,
        []
    )

    if "*" in allowed:

        return True

    return permission in allowed


# =========================================================
# ENFORCE
# =========================================================

def require_permission(
    role,
    permission
):

    if has_permission(
        role,
        permission
    ):

        return True

    raise HTTPException(

        status_code=403,

        detail="permission_denied"
    )
