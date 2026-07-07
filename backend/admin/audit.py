from datetime import datetime


_AUDIT_LOGS = []


# =========================================================
# WRITE
# =========================================================

def audit_log(

    actor_id,

    actor_role,

    action,

    resource,

    resource_id=None,

    payload=None
):

    _AUDIT_LOGS.append({

        "timestamp":
            datetime.utcnow(),

        "actor_id":
            actor_id,

        "actor_role":
            actor_role,

        "action":
            action,

        "resource":
            resource,

        "resource_id":
            resource_id,

        "payload":
            payload
    })


# =========================================================
# READ
# =========================================================

def get_audit_logs(

    limit=100
):

    return list(

        reversed(
            _AUDIT_LOGS[-limit:]
        )
    )


# =========================================================
# FILTER
# =========================================================

def find_logs(

    resource=None,

    actor_id=None,

    limit=100
):

    rows = get_audit_logs(
        limit=limit
    )

    result = []

    for row in rows:

        if resource:

            if row["resource"] != resource:

                continue

        if actor_id:

            if row["actor_id"] != actor_id:

                continue

        result.append(row)

    return result
