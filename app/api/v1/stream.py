from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import Any, Dict

router = APIRouter()

# Queue-based SSE to avoid polling over deque indices (which can make streams unstable).
# Each sensor POST pushes a single event dict into this queue.
_sse_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()


def push_sse_event(event: Dict[str, Any]) -> None:
    """Push an event into the global SSE queue."""
    try:
        _sse_queue.put_nowait(event)
    except asyncio.QueueFull:
        # If a client is slow, drop events to keep the stream alive.
        pass


async def event_stream():
    """Real-time Server Sent Events stream (queue-based + heartbeats)."""

    retry_ms = 2000
    loop = asyncio.get_event_loop()
    last_ping = loop.time()

    while True:
        # Send heartbeat every ~15s so proxies/load balancers keep the connection.
        now = loop.time()
        if now - last_ping >= 15:
            # Optional ping event helps clients/debug.
            yield (
                "event: ping\n"
                f"data: {{\"ts\": {int(loop.time() * 1000)}}}\n\n"
            )
            yield f"retry: {retry_ms}\n\n"
            last_ping = now

        try:
            event = await asyncio.wait_for(_sse_queue.get(), timeout=15.0)
        except asyncio.TimeoutError:
            continue

        yield f"data: {json.dumps(event)}\n\n"


@router.get("/stream")
async def stream():
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

