from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from pathlib import Path
import configparser

# -----------------------------
# Load project configuration
# -----------------------------
CONFIG_PATH = Path(__file__).parent / "project.conf"
PROJECT_NAME = "unknown"
if CONFIG_PATH.exists():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    PROJECT_NAME = config['DEFAULT'].get('PROJECT_NAME', 'unknown')

app = FastAPI(title=f"{PROJECT_NAME} Control")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Path to HTML file
HTML_FILE = Path(__file__).parent / "dashboard.html"

# ----------------------------
# Lifecycle hooks
# ----------------------------

@app.on_event("startup")
async def startup():
    print(f"{PROJECT_NAME} server starting up")
    # TODO:
    # - initialize MCU connection
    # - start telemetry tasks
    # - check battery / safety state

@app.on_event("shutdown")
async def shutdown():
    print(f"{PROJECT_NAME} server shutting down")
    # TODO:
    # - stop motors
    # - notify MCU
    # - flush logs

# ----------------------------
# Routes
# ----------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = HTML_FILE.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

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
