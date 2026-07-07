# services/notification.py

from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        # supplier_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    # ---------------- CONNECT ----------------
    async def connect(self, supplier_id: str, websocket: WebSocket):
        await websocket.accept()

        if supplier_id not in self.active_connections:
            self.active_connections[supplier_id] = []

        self.active_connections[supplier_id].append(websocket)

        print(f"🟢 WS CONNECTED: {supplier_id} ({len(self.active_connections[supplier_id])})")

    # ---------------- DISCONNECT ----------------
    def disconnect(self, supplier_id: str, websocket: WebSocket = None):

        if supplier_id not in self.active_connections:
            return

        if websocket:
            try:
                self.active_connections[supplier_id].remove(websocket)
            except ValueError:
                pass
        else:
            # remove all connections
            self.active_connections[supplier_id] = []

        # اگر لیست خالی شد → حذف کامل
        if not self.active_connections[supplier_id]:
            del self.active_connections[supplier_id]

        print(f"🔴 WS DISCONNECTED: {supplier_id}")

    # ---------------- SEND ----------------
    async def send_to_supplier(self, supplier_id: str, data: dict):

        connections = self.active_connections.get(supplier_id)

        if not connections:
            # ❗ مهم: این یعنی supplier آنلاین نیست
            print(f"⚠️ WS NOT FOUND: {supplier_id}")
            return

        dead_connections = []

        for ws in connections:
            try:
                await ws.send_json(data)
            except:
                dead_connections.append(ws)

        # پاکسازی کانکشن‌های مرده
        for ws in dead_connections:
            try:
                connections.remove(ws)
            except:
                pass

        # اگر خالی شد
        if not connections:
            self.active_connections.pop(supplier_id, None)

    # ---------------- BROADCAST (اختیاری ولی مهم برای آینده) ----------------
    async def broadcast(self, data: dict):
        for supplier_id in list(self.active_connections.keys()):
            await self.send_to_supplier(supplier_id, data)


manager = ConnectionManager()