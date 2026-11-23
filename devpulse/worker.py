import asyncio

from devpulse.db import initialize_database
from devpulse.scheduler import monitor_loop


async def main() -> None:
    initialize_database()
    await monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())
