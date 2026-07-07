# websocket/events.py

from websocket.manager import ws_manager


# =========================================================
# NEW LEAD
# =========================================================

async def emit_new_lead(
    supplier_id,
    payload
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "new_lead",
            "data": payload
        }
    )


# =========================================================
# BID UPDATE
# =========================================================

async def emit_bid_update(
    supplier_id,
    payload
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "bid_update",
            "data": payload
        }
    )


# =========================================================
# LEAD CLAIMED
# =========================================================

async def emit_lead_claimed(
    supplier_id,
    lead_id
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "lead_claimed",
            "lead_id": str(lead_id)
        }
    )


# =========================================================
# LEAD LOST
# =========================================================

async def emit_lead_lost(
    supplier_id,
    lead_id
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "lead_lost",
            "lead_id": str(lead_id)
        }
    )


# =========================================================
# CLAIM RESULT
# =========================================================

async def emit_claim_result(
    supplier_id,
    payload
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "claim_result",
            "data": payload
        }
    )


# =========================================================
# CREDIT UPDATE
# =========================================================

async def emit_credit_update(
    supplier_id,
    credit_balance
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "credit_update",
            "credit_balance": credit_balance
        }
    )


# =========================================================
# WALLET UPDATE
# =========================================================

async def emit_wallet_update(
    supplier_id,
    wallet_balance,
    credit_balance=None
):

    payload = {

        "type": "wallet_update",

        "wallet_balance":
            wallet_balance
    }

    if credit_balance is not None:

        payload[
            "credit_balance"
        ] = credit_balance

    await ws_manager.send_to_supplier(

        str(supplier_id),

        payload
    )


# =========================================================
# AUCTION WINNER
# =========================================================

async def emit_auction_winner(
    supplier_id,
    lead_id,
    bid_price
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "auction_winner",

            "lead_id":
                str(lead_id),

            "bid_price":
                bid_price
        }
    )


# =========================================================
# AUCTION LOST
# =========================================================

async def emit_auction_lost(
    supplier_id,
    lead_id
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "auction_lost",

            "lead_id":
                str(lead_id)
        }
    )


# =========================================================
# SYSTEM MESSAGE
# =========================================================

async def emit_system_message(
    supplier_id,
    message
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "system_message",
            "message": message
        }
    )


# =========================================================
# CLIENT EVENT
# =========================================================

async def emit_client_event(
    client_id,
    payload
):

    await ws_manager.send_to_client(

        str(client_id),

        {
            "type": "client_event",
            "data": payload
        }
    )


# =========================================================
# ADMIN EVENT
# =========================================================

async def emit_admin_event(
    payload
):

    await ws_manager.send_to_admins(

        {
            "type": "admin_event",
            "data": payload
        }
    )


# =========================================================
# BROADCAST SYSTEM
# =========================================================

async def emit_system_broadcast(
    message
):

    await ws_manager.broadcast_suppliers(

        {
            "type": "system_broadcast",
            "message": message
        }
    )


# =========================================================
# ONLINE STATUS
# =========================================================

async def emit_online_status(
    supplier_id,
    online=True
):

    await ws_manager.send_to_supplier(

        str(supplier_id),

        {
            "type": "online_status",
            "online": online
        }
    )