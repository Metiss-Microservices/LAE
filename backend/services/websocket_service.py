from websocket.events import (
    emit_new_lead,
    emit_lead_claimed,
    emit_lead_lost,
    emit_wallet_update
)


async def push_new_lead(
    supplier_id,
    lead_data
):

    await emit_new_lead(
        supplier_id,
        lead_data
    )


async def push_claimed(
    supplier_id,
    lead_id
):

    await emit_lead_claimed(
        supplier_id,
        lead_id
    )


async def push_lost(
    supplier_id,
    lead_id
):

    await emit_lead_lost(
        supplier_id,
        lead_id
    )


async def push_wallet(
    supplier_id,
    wallet_balance,
    credit_balance
):

    await emit_wallet_update(

        supplier_id,

        wallet_balance,

        credit_balance
    )
