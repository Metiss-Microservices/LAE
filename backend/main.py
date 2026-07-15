# backend/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from identity.dependencies import admin_required
from config import (
    PROJECT_NAME,
    PROJECT_VERSION,
)

# =========================================================
# CORE ROUTERS
# =========================================================

from routers.auth import router as auth_router
from otp.router import router as otp_router

from routers.request import router as request_router
from routers.output import router as output_router
from routers.meta import router as meta_router
from routers.priority import router as priority_router

from routers.supplier import router as supplier_router
from routers.claim import router as claim_router

from wallet.router import router as wallet_router
from payments.router import router as payment_router

from scoring.router import router as scoring_router
from rating.router import router as rating_router

from websocket.router import router as websocket_router

# =========================================================
# IDENTITY
# =========================================================

#from identity.dependencies import router as identity_router

# =========================================================
# ADMIN ROUTERS
# =========================================================

from routers.admin.dashboard import (
    router as admin_dashboard_router,
)
from routers.admin.suppliers import (
    router as admin_suppliers_router,
)
from routers.admin.clients import (
    router as admin_clients_router,
)
from routers.admin.leads import (
    router as admin_leads_router,
)
from routers.admin.matches import (
    router as admin_matches_router,
)
from routers.admin.payments import (
    router as admin_payments_router,
)
from routers.admin.settings import (
    router as admin_settings_router,
)
from routers.admin.channels import (
    router as admin_channels_router,
)
from routers.admin.campaigns import (
    router as admin_campaigns_router,
)
from routers.admin.reports import (
    router as admin_reports_router,
)

# =========================================================
# SERVICES
# =========================================================

from notifications.service import startup_notifications
from websocket.manager import ws_manager

API_PREFIX = "/api/v1"

# =========================================================
# LIFESPAN
# =========================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"🚀 {PROJECT_NAME} v{PROJECT_VERSION} starting"
    )

    try:
        await startup_notifications()

        print("✅ notifications")
        print("✅ websocket")
        print("✅ wallet")
        print("✅ payments")
        print("✅ scoring")
        print("✅ rating")
        print("✅ identity")
        print("✅ admin")

    except Exception as e:
        print(f"❌ startup error: {e}")

    yield

    print(
        f"🛑 {PROJECT_NAME} stopping"
    )

    try:
        await ws_manager.shutdown()
    except Exception:
        pass

    print("✅ shutdown complete")


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title=PROJECT_NAME,
    version=PROJECT_VERSION,
    lifespan=lifespan,
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": PROJECT_NAME,
        "version": PROJECT_VERSION,
    }


# =========================================================
# IDENTITY
# =========================================================

#app.include_router(
#    identity_router,
#    prefix=API_PREFIX,
#)

# =========================================================
# AUTH
# =========================================================

app.include_router(
    auth_router,
    prefix=API_PREFIX,
)

app.include_router(
    otp_router,
    prefix=API_PREFIX,
)

# =========================================================
# CLIENT FLOW
# =========================================================

app.include_router(
    request_router,
    prefix=API_PREFIX,
)

app.include_router(
    output_router,
    prefix=API_PREFIX,
)

app.include_router(
    meta_router,
    prefix=API_PREFIX,
)

app.include_router(
    priority_router,
    prefix=API_PREFIX,
)

# =========================================================
# SUPPLIER FLOW
# =========================================================

app.include_router(
    supplier_router,
    prefix=API_PREFIX,
)

app.include_router(
    claim_router,
    prefix=API_PREFIX,
)

# =========================================================
# WALLET + PAYMENTS
# =========================================================

app.include_router(
    wallet_router,
    prefix=API_PREFIX,
)

app.include_router(
    payment_router,
    prefix=API_PREFIX,
)

# =========================================================
# SCORING + RATING
# =========================================================

app.include_router(
    scoring_router,
    prefix=API_PREFIX,
)

app.include_router(
    rating_router,
    prefix=API_PREFIX,
)

# =========================================================
# WEBSOCKET
# =========================================================

app.include_router(
    websocket_router,
)

# =========================================================
# ADMIN
# =========================================================

app.include_router(
    admin_dashboard_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_suppliers_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_clients_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_leads_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_matches_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_payments_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_settings_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_channels_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_campaigns_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)

app.include_router(
    admin_reports_router,
    prefix=API_PREFIX,
    dependencies=[
        Depends(admin_required),
    ],
)