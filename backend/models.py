from sqlalchemy import (

    Column,

    String,

    Integer,

    DateTime,

    ForeignKey,

    Float,

    Boolean,

    Text
)

from sqlalchemy.orm import relationship

from sqlalchemy.orm import session

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from database import Base


def now():

    return datetime.utcnow()


# =========================================================
# IDENTITY
# =========================================================

class UserIdentity(Base):

    __tablename__ = "user_identities"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    phone = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# SESSION
# =========================================================

class UserSession(Base):

    __tablename__ = "user_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    identity_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_identities.id"
        ),
        nullable=False
    )

    token = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    role = Column(
        String,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# ADMIN USER
# =========================================================

class AdminUser(Base):

    __tablename__ = "admin_users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="operator"
    )

    permissions = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    last_login_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# SETTINGS
# =========================================================

class SystemSetting(Base):

    __tablename__ = "system_settings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    key = Column(
        String,
        unique=True,
        nullable=False
    )

    value = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# PAYMENT SETTINGS
# =========================================================

class PaymentProviderSetting(Base):

    __tablename__ = "payment_provider_settings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    provider = Column(
        String,
        unique=True,
        nullable=False
    )

    merchant_id = Column(
        String,
        nullable=True
    )

    callback_url = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# AUDIT LOG
# =========================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    actor_type = Column(
        String
    )

    actor_id = Column(
        String
    )

    action = Column(
        String
    )

    entity_type = Column(
        String
    )

    entity_id = Column(
        String
    )

    payload = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )



# =========================================================
# CAMPAIGNS
# =========================================================

class BroadcastCampaign(Base):

    __tablename__ = "broadcast_campaigns"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title = Column(String)

    message = Column(Text)

    audience_type = Column(String)

    channel = Column(String)

    status = Column(
        String,
        default="draft"
    )

    created_at = Column(
        DateTime,
        default=now
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )


class BroadcastRecipient(Base):

    __tablename__ = "broadcast_recipients"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    campaign_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "broadcast_campaigns.id"
        )
    )

    recipient_type = Column(
        String
    )

    recipient_id = Column(
        String
    )

    status = Column(
        String,
        default="pending"
    )

    delivered_at = Column(
        DateTime,
        nullable=True
    )

# =========================================================
# CATEGORY
# =========================================================

class Category(Base):

    __tablename__ = "categories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        nullable=False
    )

    type = Column(
        String,
        nullable=True
    )


class SubCategory(Base):

    __tablename__ = "subcategories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        nullable=False
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "categories.id"
        )
    )


# =========================================================
# LOCATION
# =========================================================

class Location(Base):

    __tablename__ = "locations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        nullable=False
    )

    type = Column(
        String,
        nullable=False
    )

    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id"
        ),
        nullable=True
    )


# =========================================================
# SUPPLIER
# =========================================================

class Supplier(Base):

    __tablename__ = "suppliers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    identity_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_identities.id"
        )
    )

    full_name = Column(
        String
    )

    phone = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String
    )

    location_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id"
        )
    )

    credit_balance = Column(
        Integer,
        default=0
    )

    wallet_balance = Column(
        Float,
        default=0
    )

    score = Column(
        Float,
        default=5
    )

    wins = Column(
        Integer,
        default=0
    )

    rating_count = Column(
        Integer,
        default=0
    )

    completed_jobs = Column(
        Integer,
        default=0
    )

    cancelled_jobs = Column(
        Integer,
        default=0
    )

    response_speed = Column(
        Integer,
        default=60
    )

    monthly_free_credit_used = Column(
        Integer,
        default=0
    )

    last_free_credit_at = Column(
        DateTime,
        nullable=True
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    is_blocked = Column(
        Boolean,
        default=False
    )

    telegram_chat_id = Column(
        String
    )

    bale_chat_id = Column(
        String
    )

    rubika_chat_id = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=now
    )

    categories = relationship(
        "SupplierCategory",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )


# =========================================================
# SUPPLIER CATEGORY
# =========================================================

class SupplierCategory(Base):

    __tablename__ = "supplier_categories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "suppliers.id"
        )
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "categories.id"
        )
    )

    created_at = Column(
        DateTime,
        default=now
    )

    supplier = relationship(
        "Supplier",
        back_populates="categories"
    )


# =========================================================
# SUPPLIER SUBCATEGORY
# =========================================================

class SupplierSubCategory(Base):

    __tablename__ = "supplier_subcategories"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "suppliers.id"
        )
    )

    subcategory_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "subcategories.id"
        )
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# SUPPLIER CHANNEL LINK
# =========================================================

class SupplierChannelLink(Base):

    __tablename__ = "supplier_channel_links"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "suppliers.id"
        )
    )

    channel_name = Column(
        String
    )

    channel_url = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# CLIENT
# =========================================================

class Client(Base):

    __tablename__ = "clients"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    identity_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_identities.id"
        )
    )

    full_name = Column(
        String
    )

    phone = Column(
        String,
        unique=True
    )

    requests_count = Column(
        Integer,
        default=0
    )

    telegram_chat_id = Column(
        String
    )

    bale_chat_id = Column(
        String
    )

    rubika_chat_id = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=now
    )

# =========================================================
# LEAD
# =========================================================

class Lead(Base):

    __tablename__ = "leads"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        nullable=False
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=False
    )

    subcategory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("subcategories.id"),
        nullable=False
    )

    location_id = Column(
        UUID(as_uuid=True),
        ForeignKey("locations.id"),
        nullable=False
    )

    problem = Column(
        Text,
        nullable=False
    )

    expected_budget = Column(
        Float,
        default=0
    )

    priority_mode = Column(
        String,
        default="smart"
    )

    status = Column(
        String,
        default="open"
    )

    winner_supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=True
    )

    matched_count = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime,
        default=now
    )

    closed_at = Column(
        DateTime,
        nullable=True
    )


# =========================================================
# LEAD MATCH
# =========================================================

class LeadMatch(Base):

    __tablename__ = "lead_matches"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id"),
        nullable=False
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=False
    )

    distance_score = Column(
        Float,
        default=0
    )

    reputation_score = Column(
        Float,
        default=0
    )

    speed_score = Column(
        Float,
        default=0
    )

    price_score = Column(
        Float,
        default=0
    )

    base_score = Column(
        Float,
        default=0
    )

    final_score = Column(
        Float,
        default=0
    )

    status = Column(
        String,
        default="pending"
    )

    bid_price = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime,
        default=now
    )

    expires_at = Column(
        DateTime,
        nullable=True
    )

    won_at = Column(
        DateTime,
        nullable=True
    )


# =========================================================
# RACE LOCK
# =========================================================

class RaceLock(Base):

    __tablename__ = "race_locks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id"),
        unique=True
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    locked_at = Column(
        DateTime,
        default=now
    )

    expires_at = Column(
        DateTime
    )


# =========================================================
# LEAD EVENT
# =========================================================

class LeadEvent(Base):

    __tablename__ = "lead_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id")
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id"),
        nullable=True
    )

    event_type = Column(
        String
    )

    payload = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )

# =========================================================
# CREDIT TRANSACTION
# =========================================================

class CreditTransaction(Base):

    __tablename__ = "credit_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    amount = Column(
        Integer
    )

    type = Column(
        String
    )

    description = Column(
        Text
    )

    reference_id = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# WALLET TRANSACTION
# =========================================================

class WalletTransaction(Base):

    __tablename__ = "wallet_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    amount = Column(
        Float
    )

    type = Column(
        String
    )

    authority = Column(
        String,
        nullable=True
    )

    description = Column(
        Text
    )

    status = Column(
        String,
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=now
    )


# =========================================================
# PAYMENT TRANSACTION
# =========================================================

class PaymentTransaction(Base):

    __tablename__ = "payment_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    amount = Column(
        Integer,
        nullable=False
    )

    gateway = Column(
        String,
        default="zarinpal"
    )

    authority = Column(
        String,
        unique=True
    )

    ref_id = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        default="pending"
    )

    callback_payload = Column(
        Text,
        nullable=True
    )

    verify_payload = Column(
        Text,
        nullable=True
    )

    failure_reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )


# =========================================================
# SUPPLIER REVIEW
# =========================================================

class SupplierReview(Base):

    __tablename__ = "supplier_reviews"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id")
    )

    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id")
    )

    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("leads.id")
    )

    rating = Column(
        Float,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=now
    )

