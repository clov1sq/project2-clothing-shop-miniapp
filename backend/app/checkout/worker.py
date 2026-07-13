import asyncio
import logging

from app.checkout.service import expire_reservations
from app.db.session import get_sessionmaker

logger = logging.getLogger(__name__)


async def reservation_expiry_loop(stop_event: asyncio.Event, interval_seconds: int = 60) -> None:
    maker = get_sessionmaker()
    while not stop_event.is_set():
        try:
            async with maker() as session:
                count = await expire_reservations(session)
                if count:
                    logger.info("Expired inventory reservations", extra={"count": count})
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Reservation expiry iteration failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except TimeoutError:
            continue
