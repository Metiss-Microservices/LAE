# websocket/manager.py

from collections import defaultdict
from datetime import datetime

from fastapi import WebSocket

import asyncio
import logging


logger = logging.getLogger(__name__)


class WSManager:

    def __init__(self):

        self.supplier_connections = defaultdict(set)

        self.client_connections = defaultdict(set)

        self.admin_connections = set()

        self.last_seen = {}

        self.lock = asyncio.Lock()

    # =====================================================
    # CONNECT
    # =====================================================

    async def connect_supplier(
        self,
        supplier_id,
        websocket: WebSocket
    ):

        await websocket.accept()

        supplier_id = str(
            supplier_id
        )

        async with self.lock:

            self.supplier_connections[
                supplier_id
            ].add(websocket)

            self.last_seen[
                f"supplier:{supplier_id}"
            ] = datetime.utcnow()

        logger.info(
            f"WS supplier connected {supplier_id}"
        )

    async def connect_client(
        self,
        client_id,
        websocket: WebSocket
    ):

        await websocket.accept()

        client_id = str(
            client_id
        )

        async with self.lock:

            self.client_connections[
                client_id
            ].add(websocket)

            self.last_seen[
                f"client:{client_id}"
            ] = datetime.utcnow()

        logger.info(
            f"WS client connected {client_id}"
        )

    async def connect_admin(
        self,
        websocket: WebSocket
    ):

        await websocket.accept()

        async with self.lock:

            self.admin_connections.add(
                websocket
            )

        logger.info(
            "WS admin connected"
        )

    # =====================================================
    # DISCONNECT
    # =====================================================

    async def disconnect_supplier(
        self,
        supplier_id,
        websocket
    ):

        supplier_id = str(
            supplier_id
        )

        async with self.lock:

            if (
                supplier_id
                not in self.supplier_connections
            ):
                return

            self.supplier_connections[
                supplier_id
            ].discard(websocket)

            if not self.supplier_connections[
                supplier_id
            ]:

                del self.supplier_connections[
                    supplier_id
                ]

    async def disconnect_client(
        self,
        client_id,
        websocket
    ):

        client_id = str(
            client_id
        )

        async with self.lock:

            if (
                client_id
                not in self.client_connections
            ):
                return

            self.client_connections[
                client_id
            ].discard(websocket)

            if not self.client_connections[
                client_id
            ]:

                del self.client_connections[
                    client_id
                ]

    async def disconnect_admin(
        self,
        websocket
    ):

        async with self.lock:

            self.admin_connections.discard(
                websocket
            )

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def touch(
        self,
        key
    ):

        self.last_seen[
            key
        ] = datetime.utcnow()

    # =====================================================
    # INTERNAL SEND
    # =====================================================

    async def _safe_send(
        self,
        websocket,
        payload
    ):

        try:

            await websocket.send_json(
                payload
            )

            return True

        except Exception:

            return False

    # =====================================================
    # SEND SUPPLIER
    # =====================================================

    async def send_to_supplier(
        self,
        supplier_id,
        payload
    ):

        supplier_id = str(
            supplier_id
        )

        sockets = list(

            self.supplier_connections.get(
                supplier_id,
                []
            )
        )

        if not sockets:
            return False

        dead = []

        for ws in sockets:

            ok = await self._safe_send(
                ws,
                payload
            )

            if not ok:
                dead.append(ws)

        for ws in dead:

            await self.disconnect_supplier(
                supplier_id,
                ws
            )

        self.touch(
            f"supplier:{supplier_id}"
        )

        return True

    # =====================================================
    # SEND CLIENT
    # =====================================================

    async def send_to_client(
        self,
        client_id,
        payload
    ):

        client_id = str(
            client_id
        )

        sockets = list(

            self.client_connections.get(
                client_id,
                []
            )
        )

        if not sockets:
            return False

        dead = []

        for ws in sockets:

            ok = await self._safe_send(
                ws,
                payload
            )

            if not ok:
                dead.append(ws)

        for ws in dead:

            await self.disconnect_client(
                client_id,
                ws
            )

        self.touch(
            f"client:{client_id}"
        )

        return True

    # =====================================================
    # SEND ADMINS
    # =====================================================

    async def send_to_admins(
        self,
        payload
    ):

        dead = []

        for ws in list(
            self.admin_connections
        ):

            ok = await self._safe_send(
                ws,
                payload
            )

            if not ok:
                dead.append(ws)

        for ws in dead:

            await self.disconnect_admin(
                ws
            )

        return True

    # =====================================================
    # ALIAS
    # =====================================================

    async def broadcast_admin(
        self,
        payload
    ):

        return await self.send_to_admins(
            payload
        )

    # =====================================================
    # BROADCAST SUPPLIERS
    # =====================================================

    async def broadcast_suppliers(
        self,
        payload
    ):

        for supplier_id in list(
            self.supplier_connections.keys()
        ):

            await self.send_to_supplier(
                supplier_id,
                payload
            )

    # =====================================================
    # BROADCAST CLIENTS
    # =====================================================

    async def broadcast_clients(
        self,
        payload
    ):

        for client_id in list(
            self.client_connections.keys()
        ):

            await self.send_to_client(
                client_id,
                payload
            )

    # =====================================================
    # ONLINE
    # =====================================================

    def is_supplier_online(
        self,
        supplier_id
    ):

        return (
            str(supplier_id)
            in
            self.supplier_connections
        )

    def is_client_online(
        self,
        client_id
    ):

        return (
            str(client_id)
            in
            self.client_connections
        )

    # =====================================================
    # STATS
    # =====================================================

    def stats(self):

        supplier_connections = sum(

            len(v)

            for v in self.supplier_connections.values()
        )

        client_connections = sum(

            len(v)

            for v in self.client_connections.values()
        )

        return {

            "supplier_connections":
                supplier_connections,

            "client_connections":
                client_connections,

            "admin_connections":
                len(
                    self.admin_connections
                ),

            "suppliers_online":
                len(
                    self.supplier_connections
                ),

            "clients_online":
                len(
                    self.client_connections
                )
        }

    # =====================================================
    # SHUTDOWN
    # =====================================================

    async def shutdown(self):

        for sockets in self.supplier_connections.values():

            for ws in sockets:

                try:
                    await ws.close()
                except Exception:
                    pass

        for sockets in self.client_connections.values():

            for ws in sockets:

                try:
                    await ws.close()
                except Exception:
                    pass

        for ws in self.admin_connections:

            try:
                await ws.close()
            except Exception:
                pass

        self.supplier_connections.clear()

        self.client_connections.clear()

        self.admin_connections.clear()

        self.last_seen.clear()


manager = WSManager()
ws_manager = manager