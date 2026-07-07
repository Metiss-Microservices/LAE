import asyncio

from workers.expired_matches import (
    run_expired_matches
)


async def loop():

    while True:

        try:

            run_expired_matches()

        except Exception as e:

            print("worker error", e)

        await asyncio.sleep(15)


if __name__ == "__main__":

    asyncio.run(loop())
