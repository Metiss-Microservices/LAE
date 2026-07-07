from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from websocket.manager import (
    manager
)


router = APIRouter()


# =========================================================
# SUPPLIER SOCKET
# =========================================================

@router.websocket(
    "/ws/supplier/{supplier_id}"
)
async def supplier_socket(
    websocket: WebSocket,
    supplier_id: str
):

    await manager.connect_supplier(

        supplier_id,
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await manager.disconnect_supplier(
            supplier_id
        )


# =========================================================
# ADMIN SOCKET
# =========================================================

@router.websocket(
    "/ws/admin"
)
async def admin_socket(
    websocket: WebSocket
):

    await manager.connect_admin(
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        await manager.disconnect_admin(
            websocket
        )