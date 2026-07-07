import redis
from config import REDIS_URL


# ---------------- CONNECTION ----------------
def create_redis():

    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )


r = create_redis()


# ---------------- SAFE SET (LOCK) ----------------
def acquire_lock(key: str, value: str, ttl: int = 120) -> bool:
    try:
        return r.set(key, value, nx=True, ex=ttl)
    except Exception:
        return False


# ---------------- SAFE GET ----------------
def get(key: str):
    try:
        return r.get(key)
    except Exception:
        return None


# ---------------- PUB/SUB (for realtime) ----------------
def publish(channel: str, message: str):
    try:
        r.publish(channel, message)
    except Exception:
        pass


def subscribe(channel: str):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub