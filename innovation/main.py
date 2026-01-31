from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import signal
import sys

app = FastAPI(title="Innovation Control")

# ----------------------------
# Lifecycle hooks
# ----------------------------

@app.on_event("startup")
async def startup():
    print("Innovation server starting up")
    # TODO:
    # - initialize MCU connection
    # - start telemetry tasks
    # - check battery / safety state


@app.on_event("shutdown")
async def shutdown():
    print("Innovation server shutting down")
    # TODO:
    # - stop motors
    # - notify MCU
    # - flush logs


# ----------------------------
# Routes
# ----------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head><title>Innovation</title></head>
        <body>
            <h1>Innovation Control</h1>
            <p>Status: OK</p>
        </body>
    </html>
    """


@app.get("/api/status")
async def status():
    return {
        "server": "running",
        "mode": "pi",
        "battery": "unknown",
    }


@app.post("/api/motors/stop")
async def stop_motors():
    # TODO: send stop command to MCU
    return {"result": "motors stopped"}


# ----------------------------
# Optional: background task example
# ----------------------------

async def telemetry_loop():
    while True:
        # TODO: poll MCU, sensors, etc.
        await asyncio.sleep(1)


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(telemetry_loop())
