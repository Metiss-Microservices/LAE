# routers/supplier.py

# PART 1

from fastapi import (
APIRouter,
Depends,
Header
)

from sqlalchemy.orm import Session

from uuid import UUID

from datetime import datetime

from database import get_db

from models import (

    Supplier,
    SupplierCategory,

    Lead,
    LeadMatch,
    Client,

    Category,
    SubCategory,
    Location,

    SupplierReview,

    WalletTransaction,

    CreditTransaction
)

from routers.auth import (
get_supplier_by_token
)

from services.bidding_service import (
place_bid
)

from services.claim_service import (
claim_lead
)

from scoring.service import (
calculate_supplier_reputation
)

from websocket.manager import (
manager
)

router = APIRouter(
prefix="/supplier"
)

# =========================================================

# AUTH

# =========================================================

def auth(
token: str
):

supplier_id = get_supplier_by_token(
    token
)

if not supplier_id:
    return None

return UUID(
    supplier_id
)

# =========================================================

# LOCATION HELPER

# =========================================================

def get_location_name(
db,
location_id
):

loc = db.query(
    Location
).filter_by(
    id=location_id
).first()

if not loc:
    return "-"

if loc.type == "district":

    parent = db.query(
        Location
    ).filter_by(
        id=loc.parent_id
    ).first()

    if parent:

        return (
            f"{parent.name} / "
            f"{loc.name}"
        )

return loc.name

# =========================================================

# PROFILE

# =========================================================

@router.get("/me")
def me(

token: str = Header(None),

db: Session = Depends(get_db)

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False,
        "error": "unauthorized"
    }

supplier = db.query(
    Supplier
).filter_by(
    id=supplier_id
).first()

if not supplier:

    return {
        "success": False,
        "error": "supplier_not_found"
    }

supplier_categories = (

    db.query(
        SupplierCategory
    )
    .filter_by(
        supplier_id=supplier.id
    )
    .all()
)

services = []

rows = (
    db.query(models.SupplierService)
    .filter_by(
        supplier_id=supplier.id
    )
    .all()
)

for row in rows:

    category = (
        db.query(Category)
        .filter_by(
            id=row.category_id
        )
        .first()
    )

    subcategory = (
        db.query(SubCategory)
        .filter_by(
            id=row.subcategory_id
        )
        .first()
    )

    services.append({

        "category_id":
            str(row.category_id),

        "category":
            category.name
            if category
            else None,

        "subcategory_id":
            str(row.subcategory_id),

        "subcategory":
            subcategory.name
            if subcategory
            else None
    })

reputation = (
    calculate_supplier_reputation(
        db,
        supplier.id
    )
)

return {

    "success": True,

    "supplier": {

        "id":
            str(supplier.id),

        "full_name":
            supplier.full_name,

        "phone":
            supplier.phone,

        "services":
            services,

        "location":
            get_location_name(
                db,
                supplier.location_id
            ),

        "credit_balance":
            supplier.credit_balance,

        "wallet_balance":
            supplier.wallet_balance,

        "score":
            supplier.score,

        "wins":
            supplier.wins,

        "verified":
            supplier.is_verified,

        "active":
            supplier.is_active,

        "online":

            str(supplier.id)
            in
            manager.suppliers,

        "rating_avg":
            reputation.get(
                "rating_avg"
            ),

        "review_count":
            reputation.get(
                "review_count"
            ),

        "success_rate":
            reputation.get(
                "success_rate"
            ),

        "trust_score":
            reputation.get(
                "trust_score"
            )
    }
}
 

# =========================================================

# UPDATE PROFILE

# =========================================================

@router.post("/profile")
def update_profile(

    payload: dict,

    token: str = Header(None),

    db: Session = Depends(get_db)
):

    supplier_id = auth(token)

    if not supplier_id:

        return {
            "success": False,
            "error": "unauthorized"
        }

    supplier = db.query(
        Supplier
    ).filter_by(
        id=supplier_id
    ).first()

    if not supplier:

        return {
            "success": False,
            "error": "supplier_not_found"
        }

    supplier.full_name = payload.get(
        "full_name",
        supplier.full_name
    )

    supplier.location_id = payload.get(
        "location_id",
        supplier.location_id
    )

    services = payload.get(
        "services"
    )

    if services is not None:

        db.query(
            SupplierCategory
        ).filter_by(
            supplier_id=supplier.id
        ).delete()

        for item in services:

            category_id = item.get(
                "category_id"
            )

            if not category_id:
                continue

            row = SupplierCategory(

                supplier_id=supplier.id,

                category_id=UUID(
                    category_id
                ),

                subcategory_id=(

                    UUID(
                        item["subcategory_id"]
                    )

                    if item.get(
                        "subcategory_id"
                    )

                    else None
                )
            )

            db.add(row)

    db.commit()

    return {
        "success": True
    }

# =========================================================

# LIVE LEADS

# =========================================================

@router.get("/leads")
def live_leads(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False,
        "error": "unauthorized"
    }

now = datetime.utcnow()

matches = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id
).all()

result = []

for match in matches:

    if (
        match.status == "pending"
        and
        match.expires_at
        and
        match.expires_at < now
    ):
        continue

    if match.status != "pending":
        continue

    lead = db.query(
        Lead
    ).filter_by(
        id=match.lead_id
    ).first()

    if not lead:
        continue

    category = db.query(
        Category
    ).filter_by(
        id=lead.category_id
    ).first()

    subcategory = db.query(
        SubCategory
    ).filter_by(
        id=lead.subcategory_id
    ).first()

    result.append({

        "match_id":
            str(match.id),

        "lead_id":
            str(lead.id),

        "category":
            category.name
            if category
            else None,

        "subcategory":
            subcategory.name
            if subcategory
            else None,

        "problem":
            lead.problem,

        "location":
            get_location_name(
                db,
                lead.location_id
            ),

        "score":
            match.final_score,

        "bid_price":
            match.bid_price,

        "expires_at":
            match.expires_at,

        "priority_mode":
            lead.priority_mode
    })

return {

    "success": True,

    "count":
        len(result),

    "items":
        result
}
 
# =========================================================

# PLACE BID

# =========================================================

@router.post("/bid")
def bid(

 
payload: dict,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False,
        "error": "unauthorized"
    }

lead_id = payload.get(
    "lead_id"
)

bid_price = payload.get(
    "bid_price"
)

if not lead_id:

    return {
        "success": False,
        "error": "missing_lead_id"
    }

return place_bid(

    db,

    supplier_id,

    UUID(lead_id),

    bid_price
)
 

# =========================================================

# CLAIM

# =========================================================

@router.post("/claim")
async def claim(

 
payload: dict,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False,
        "error": "unauthorized"
    }

match_id = payload.get(
    "match_id"
)

if not match_id:

    return {
        "success": False,
        "error": "missing_match_id"
    }

return await claim_lead(

    db=db,

    supplier_id=supplier_id,

    match_id=UUID(match_id)
)
 

# =========================================================

# WON LEADS

# =========================================================

@router.get("/won")
def won_leads(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

matches = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="won"
).order_by(
    LeadMatch.won_at.desc()
).all()

result = []

for match in matches:

    lead = db.query(
        Lead
    ).filter_by(
        id=match.lead_id
    ).first()

    if not lead:
        continue

    client = db.query(
        Client
    ).filter_by(
        id=lead.client_id
    ).first()

    result.append({

        "lead_id":
            str(lead.id),

        "problem":
            lead.problem,

        "phone":
            client.phone
            if client
            else None,

        "won_at":
            match.won_at
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# HISTORY

# =========================================================

@router.get("/history")
def history(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

matches = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id
).order_by(
    LeadMatch.created_at.desc()
).limit(100).all()

result = []

for match in matches:

    lead = db.query(
        Lead
    ).filter_by(
        id=match.lead_id
    ).first()

    if not lead:
        continue

    result.append({

        "match_id":
            str(match.id),

        "lead_id":
            str(lead.id),

        "problem":
            lead.problem,

        "status":
            match.status,

        "score":
            match.final_score,

        "bid_price":
            match.bid_price,

        "created_at":
            match.created_at
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# LEAD DETAILS

# =========================================================

@router.get("/lead/{lead_id}")
def lead_details(

 
lead_id: str,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

lead = db.query(
    Lead
).filter_by(
    id=UUID(lead_id)
).first()

if not lead:

    return {
        "success": False,
        "error": "lead_not_found"
    }

match = db.query(
    LeadMatch
).filter_by(
    lead_id=lead.id,
    supplier_id=supplier_id
).first()

if not match:

    return {
        "success": False,
        "error": "access_denied"
    }

return {

    "success": True,

    "lead": {

        "id":
            str(lead.id),

        "problem":
            lead.problem,

        "priority_mode":
            lead.priority_mode,

        "status":
            lead.status,

        "created_at":
            lead.created_at
    },

    "match": {

        "status":
            match.status,

        "score":
            match.final_score,

        "bid_price":
            match.bid_price
    }
}
 

# =========================================================

# RACE STATUS

# =========================================================

@router.get("/race/{match_id}")
def race_status(

 
match_id: str,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

match = db.query(
    LeadMatch
).filter_by(
    id=UUID(match_id),
    supplier_id=supplier_id
).first()

if not match:

    return {
        "success": False,
        "error": "not_found"
    }

return {

    "success": True,

    "status":
        match.status,

    "expires_at":
        match.expires_at,

    "score":
        match.final_score
}
 

# =========================================================

# AUCTION STATUS

# =========================================================

@router.get("/auction/{lead_id}")
def auction_status(

 
lead_id: str,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

matches = db.query(
    LeadMatch
).filter_by(
    lead_id=UUID(lead_id)
).all()

result = []

for item in matches:

    result.append({

        "supplier_id":
            str(item.supplier_id),

        "score":
            item.final_score,

        "bid_price":
            item.bid_price,

        "status":
            item.status
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# CONTACT UNLOCK CHECK

# =========================================================

@router.get("/contact/{lead_id}")
def contact_info(

 
lead_id: str,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

match = db.query(
    LeadMatch
).filter_by(
    lead_id=UUID(lead_id),
    supplier_id=supplier_id,
    status="won"
).first()

if not match:

    return {
        "success": False,
        "error": "not_winner"
    }

lead = db.query(
    Lead
).filter_by(
    id=UUID(lead_id)
).first()

if not lead:

    return {
        "success": False
    }

client = db.query(
    Client
).filter_by(
    id=lead.client_id
).first()

return {

    "success": True,

    "full_name":
        client.full_name
        if client
        else None,

    "phone":
        client.phone
        if client
        else None
}
 
# =========================================================

# WALLET HISTORY

# =========================================================

@router.get("/wallet")
def wallet_history(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

rows = db.query(
    WalletTransaction
).filter_by(
    supplier_id=supplier_id
).order_by(
    WalletTransaction.created_at.desc()
).limit(100).all()

result = []

for row in rows:

    result.append({

        "id":
            str(row.id),

        "amount":
            row.amount,

        "type":
            row.type,

        "status":
            row.status,

        "authority":
            row.authority,

        "created_at":
            row.created_at
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# CREDIT HISTORY

# =========================================================

@router.get("/credits")
def credit_history(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

rows = db.query(
    CreditTransaction
).filter_by(
    supplier_id=supplier_id
).order_by(
    CreditTransaction.created_at.desc()
).limit(100).all()

result = []

for row in rows:

    result.append({

        "id":
            str(row.id),

        "amount":
            row.amount,

        "type":
            row.type,

        "reference_id":
            row.reference_id,

        "created_at":
            row.created_at
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# REVIEWS

# =========================================================

@router.get("/reviews")
def reviews(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

rows = db.query(
    SupplierReview
).filter_by(
    supplier_id=supplier_id
).order_by(
    SupplierReview.created_at.desc()
).limit(100).all()

result = []

for row in rows:

    result.append({

        "id":
            str(row.id),

        "rating":
            row.rating,

        "review":
            row.review,

        "created_at":
            row.created_at
    })

return {

    "success": True,

    "items":
        result
}
 

# =========================================================

# STATISTICS

# =========================================================

@router.get("/stats")
def statistics(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

services_count = db.query(
    SupplierCategory
).filter_by(
    supplier_id=supplier_id
).count()

total_matches = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id
).count()

total_wins = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="won"
).count()

total_lost = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="lost"
).count()

total_pending = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="pending"
).count()

return {

    "success": True,

    "stats": {

        "services":
            services_count,
        
        "total_matches":
            total_matches,

        "total_wins":
            total_wins,

        "total_lost":
            total_lost,

        "total_pending":
            total_pending,

        "win_rate":

            round(
                (
                    total_wins /
                    total_matches
                ) * 100,
                2
            )

            if total_matches
            else 0
    }
}
 

# =========================================================

# DASHBOARD

# =========================================================

@router.get("/dashboard")
def dashboard(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

supplier = db.query(
    Supplier
).filter_by(
    id=supplier_id
).first()

if not supplier:

    return {
        "success": False
    }

open_leads = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="pending"
).count()

won_leads = db.query(
    LeadMatch
).filter_by(
    supplier_id=supplier_id,
    status="won"
).count()

services_count = db.query(
    SupplierCategory
).filter_by(
    supplier_id=supplier_id
).count()

reviews_count = db.query(
    SupplierReview
).filter_by(
    supplier_id=supplier_id
).count()

return {

    "success": True,

    "dashboard": {

        "credit_balance":
            supplier.credit_balance,

        "wallet_balance":
            supplier.wallet_balance,

        "score":
            supplier.score,

        "wins":
            supplier.wins,

        "open_leads":
            open_leads,

        "won_leads":
            won_leads,

        "services":
            services_count,
        "reviews":
            reviews_count
    }
}
 

# =========================================================

# NOTIFICATION SETTINGS

# =========================================================

@router.post("/notification-settings")
def notification_settings(

 
payload: dict,

token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

supplier = db.query(
    Supplier
).filter_by(
    id=supplier_id
).first()

if not supplier:

    return {
        "success": False
    }

supplier.notify_sms = payload.get(
    "notify_sms",
    supplier.notify_sms
)

supplier.notify_telegram = payload.get(
    "notify_telegram",
    supplier.notify_telegram
)

supplier.notify_bale = payload.get(
    "notify_bale",
    supplier.notify_bale
)

supplier.notify_rubika = payload.get(
    "notify_rubika",
    supplier.notify_rubika
)

db.commit()

return {
    "success": True
}
 

# =========================================================

# CHANNEL BINDINGS

# =========================================================

@router.get("/channels")
def channels(

 
token: str = Header(None),

db: Session = Depends(get_db)
 

):

 
supplier_id = auth(token)

if not supplier_id:

    return {
        "success": False
    }

supplier = db.query(
    Supplier
).filter_by(
    id=supplier_id
).first()

if not supplier:

    return {
        "success": False
    }

return {

    "success": True,

    "channels": {

        "telegram":
            supplier.telegram_chat_id,

        "bale":
            supplier.bale_chat_id,

        "rubika":
            supplier.rubika_chat_id
    }
}
 

# =========================================================

# END OF FILE

# =========================================================
