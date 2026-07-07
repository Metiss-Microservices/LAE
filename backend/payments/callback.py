from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session

from database import get_db

from payments.service import verify_payment


router = APIRouter(
    prefix="/payment-callback",
    tags=["payment-callback"]
)


# =========================================================
# SUCCESS PAGE
# =========================================================

def success_html(balance):

    return HTMLResponse(
        f"""
        <html>
        <body>
            <h2>Payment Successful</h2>
            <p>Wallet Balance: {balance}</p>
        </body>
        </html>
        """
    )


# =========================================================
# FAILED PAGE
# =========================================================

def failed_html(message):

    return HTMLResponse(
        f"""
        <html>
        <body>
            <h2>Payment Failed</h2>
            <p>{message}</p>
        </body>
        </html>
        """
    )


# =========================================================
# ZARINPAL CALLBACK
# =========================================================

@router.get("/zarinpal")
def zarinpal_callback(
    Authority: str,
    Status: str = None,
    db: Session = Depends(get_db)
):

    if Status and Status.upper() != "OK":

        return failed_html(
            "payment_cancelled"
        )

    result = verify_payment(
        db=db,
        authority=Authority
    )

    if not result.get("success"):

        return failed_html(
            result.get(
                "error",
                "verify_failed"
            )
        )

    return success_html(
        result.get(
            "wallet_balance",
            0
        )
    )


# =========================================================
# MOCK CALLBACK
# =========================================================

@router.get("/mock")
def mock_callback(
    authority: str,
    db: Session = Depends(get_db)
):

    result = verify_payment(
        db=db,
        authority=authority
    )

    if not result.get("success"):

        return failed_html(
            result.get(
                "error",
                "verify_failed"
            )
        )

    return success_html(
        result.get(
            "wallet_balance",
            0
        )
    )