# =========================================================
# CREDIT PACKAGES
# =========================================================

CREDIT_PACKAGES = [

    {
        "id": "starter",
        "credits": 20,
        "price": 200000
    },

    {
        "id": "growth",
        "credits": 60,
        "price": 500000
    },

    {
        "id": "pro",
        "credits": 150,
        "price": 1000000
    }
]


# =========================================================
# MONTHLY FREE CREDIT
# =========================================================

MONTHLY_FREE_CREDIT = 5


# =========================================================
# CLAIM COST
# =========================================================

CLAIM_PRICING = {

    "service": {

        "low": 1,

        "medium": 2,

        "high": 4
    },

    "product": {

        "low": 2,

        "medium": 4,

        "high": 7
    }
}


# =========================================================
# AUCTION COST
# =========================================================

AUCTION_WIN_COST = {

    "low": 2,

    "medium": 4,

    "high": 6
}


def get_claim_cost(
    lead_type="service",
    priority="medium"
):

    lead_type = lead_type or "service"

    priority = priority or "medium"

    table = CLAIM_PRICING.get(
        lead_type,
        CLAIM_PRICING["service"]
    )

    return table.get(priority, 2)


def get_auction_cost(
    priority="medium"
):

    return AUCTION_WIN_COST.get(
        priority,
        4
    )


def get_packages():

    return CREDIT_PACKAGES