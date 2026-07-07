# =========================================================
# PRIORITY WEIGHTS
# =========================================================

PRIORITY_WEIGHTS = {

    "smart": {
        "location": 1.2,
        "reputation": 1.8,
        "speed": 1.2,
        "price": 1.0
    },

    "fastest": {
        "location": 0.4,
        "reputation": 0.9,
        "speed": 2.8,
        "price": 0.2
    },

    "experienced": {
        "location": 0.3,
        "reputation": 2.8,
        "speed": 0.8,
        "price": 0.2
    },

    "cheapest": {
        "location": 0.5,
        "reputation": 0.5,
        "speed": 0.2,
        "price": 2.8
    }
}


# =========================================================
# CALCULATE
# =========================================================

def calculate_priority_multiplier(

    priority_mode,

    loc_score,

    rep_score,

    speed_score,

    price_score
):

    mode = (
        priority_mode or "smart"
    ).lower()

    if mode not in PRIORITY_WEIGHTS:
        mode = "smart"

    weights = PRIORITY_WEIGHTS[mode]

    total = (

        loc_score *
        weights["location"]

        +

        rep_score *
        weights["reputation"]

        +

        speed_score *
        weights["speed"]

        +

        price_score *
        weights["price"]
    )

    return round(
        total,
        2
    )


# =========================================================
# PUBLIC
# =========================================================

def get_priority_modes():

    return list(
        PRIORITY_WEIGHTS.keys()
    )