
from services.auction_service import create_wave
from services.redis_client import r
import time

def dispatch(db, lead_id, suppliers):
    suppliers = sorted(suppliers, key=lambda s: s.priority, reverse=True)

    wave1 = suppliers[:3]
    wave2 = suppliers[3:5]

    create_wave(db, lead_id, wave1, 1)

    # schedule wave2
    r.zadd("jobs", {f"wave2:{lead_id}": time.time()+60})
