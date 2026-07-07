from pydantic import BaseModel
from typing import Optional
from uuid import UUID


# =========================================================
# AUTH
# =========================================================

class OTPRequest(BaseModel):

    phone: str


class OTPVerify(BaseModel):

    phone: str

    code: str


# =========================================================
# LEAD
# =========================================================

class LeadCreate(BaseModel):

    category_id: UUID

    subcategory_id: UUID

    location_id: UUID

    client_phone: str

    problem: str

    priority_mode: str = "smart"

    expected_budget: Optional[float] = 0


# =========================================================
# BID
# =========================================================

class BidCreate(BaseModel):

    lead_id: UUID

    amount: float


# =========================================================
# CLAIM
# =========================================================

class ClaimRequest(BaseModel):

    match_id: UUID


# =========================================================
# REVIEW
# =========================================================

class ReviewCreate(BaseModel):

    supplier_id: UUID

    lead_id: UUID

    rating: int

    review: Optional[str] = None


# =========================================================
# WALLET
# =========================================================

class WalletChargeRequest(BaseModel):

    amount: int


# =========================================================
# PAYMENT
# =========================================================

class PaymentVerifyRequest(BaseModel):

    authority: str


# =========================================================
# SUPPLIER
# =========================================================

class SupplierProfileOut(BaseModel):

    id: UUID

    name: str

    phone: str

    wallet_balance: float

    credit_balance: int

    score: float

    wins: int

    rating_avg: float

    review_count: int

    trust_score: float

    success_rate: float

    is_verified: bool

    is_active: bool


# =========================================================
# MATCH
# =========================================================

class MatchOut(BaseModel):

    lead_id: UUID

    match_id: UUID

    category: str

    problem: str

    location: str

    score: float

    bid: float

    remaining: int

    status: str