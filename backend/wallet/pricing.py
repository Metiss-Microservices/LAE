# wallet/pricing.py

# =========================================================

# CREDIT PACKS

# =========================================================

CREDIT_PACKS = {

"starter": {

    "credits": 50,

    "price": 99000
},

"growth": {

    "credits": 150,

    "price": 249000
},

"pro": {

    "credits": 400,

    "price": 599000
}

}

# =========================================================

# MONTHLY FREE CREDIT

# =========================================================

MONTHLY_FREE_CREDIT = 5

# =========================================================

# CLAIM COST TABLE

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

# DEFAULT COSTS

# =========================================================

DEFAULT_SERVICE_CLAIM_COST = 2

DEFAULT_PRODUCT_CLAIM_COST = 4

# =========================================================

# CLAIM COST

# =========================================================

def get_claim_cost(

lead_type="service",

priority="medium"

):

lead_type = (
    lead_type
    or
    "service"
)

priority = (
    priority
    or
    "medium"
)

pricing = CLAIM_PRICING.get(
    lead_type
)

if not pricing:

    pricing = CLAIM_PRICING[
        "service"
    ]

return pricing.get(

    priority,

    pricing.get(
        "medium",
        2
    )
)

# =========================================================

# CREDIT PACK

# =========================================================

def get_pack(

pack_name

):

return CREDIT_PACKS.get(
    pack_name
)

# =========================================================

# VALIDATE PACK

# =========================================================

def is_valid_pack(

pack_name

):

return (
    pack_name
    in
    CREDIT_PACKS
)

# =========================================================

# PACK CREDITS

# =========================================================

def get_pack_credits(

pack_name

):

pack = get_pack(
    pack_name
)

if not pack:
    return 0

return pack[
    "credits"
]

# =========================================================

# PACK PRICE

# =========================================================

def get_pack_price(

pack_name

):

pack = get_pack(
    pack_name
)

if not pack:
    return 0

return pack[
    "price"
]

# =========================================================

# EXPORT

# =========================================================

**all** = [

"CREDIT_PACKS",

"CLAIM_PRICING",

"MONTHLY_FREE_CREDIT",

"DEFAULT_SERVICE_CLAIM_COST",

"DEFAULT_PRODUCT_CLAIM_COST",

"get_claim_cost",

"get_pack",

"get_pack_credits",

"get_pack_price",

"is_valid_pack"

]
