from fastapi import APIRouter

router = APIRouter(
    prefix="/priority",
    tags=["priority"]
)


# =========================================================
# MODES
# =========================================================

@router.get("/modes")
def priority_modes():

    return {

        "success": True,

        "modes": [

            {
                "code": "smart",
                "title": "هوشمند",
                "engine": "race"
            },

            {
                "code": "fastest",
                "title": "سریع‌ترین",
                "engine": "race"
            },

            {
                "code": "experienced",
                "title": "باتجربه‌ترین",
                "engine": "race"
            },

            {
                "code": "cheapest",
                "title": "ارزان‌ترین",
                "engine": "auction"
            }
        ]
    }


# =========================================================
# EXPLAIN
# =========================================================

@router.get("/explain/{mode}")
def explain_mode(
    mode: str
):

    descriptions = {

        "smart":
            "ترکیب اعتبار، سرعت پاسخ و موقعیت جغرافیایی",

        "fastest":
            "اولویت با تامین‌کننده‌های سریع‌تر",

        "experienced":
            "اولویت با تامین‌کننده‌های با سابقه و امتیاز بالاتر",

        "cheapest":
            "برگزاری مزایده و انتخاب بهترین پیشنهاد قیمت"
    }

    return {

        "success": True,

        "mode": mode,

        "description":
            descriptions.get(
                mode,
                "-"
            )
    }