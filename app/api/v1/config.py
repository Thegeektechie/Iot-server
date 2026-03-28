from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/config")
def get_config(request: Request):
    """
    Returns correct server configuration for both:
    - Local development
    - Public deployment (Render, Cloudflare, etc.)
    """

    # Detect protocol safely
    protocol = request.headers.get("x-forwarded-proto", "http")

    # Detect correct host (works behind proxies)
    host = request.headers.get("host")

    base_url = f"{protocol}://{host}"

    return {
        "device_id": "iot-server",
        "device_name": "Python IoT Command Center",

        # ✅ Primary API endpoint (THIS is what frontend should use)
        "api_url": base_url,

        # ✅ Sensor endpoint (important for your frontend pipeline)
        "sensor_endpoint": f"{base_url}/api/v1/sensor",

        # ✅ Stream endpoint (for real-time updates)
        "stream_endpoint": f"{base_url}/api/v1/stream"
    }