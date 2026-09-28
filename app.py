import os, secrets, time
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI(title="Nexus Railway Panel")
templates = Jinja2Templates(directory="templates")
security = HTTPBearer(auto_error=False)

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
SUB_PREFIX = os.getenv("SUB_PREFIX", "adminsubsub")
users = {}

class UserCreate(BaseModel):
    name: str
    traffic_limit_gb: float = 100
    expires_at: str | None = None

class ProxyCheck(BaseModel):
    host: str
    port: int = 443

def require_admin(creds: HTTPAuthorizationCredentials = Depends(security)):
    if not ADMIN_TOKEN or not creds or not secrets.compare_digest(creds.credentials, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": list(users.values())})

@app.post("/api/users")
def create_user(data: UserCreate, _: bool = Depends(require_admin)):
    slug = secrets.token_urlsafe(8).replace("-", "").replace("_", "").lower()
    while slug in users:
        slug = secrets.token_urlsafe(8).replace("-", "").replace("_", "").lower()

    credential = secrets.token_urlsafe(24)
    sub_url = f"/{SUB_PREFIX}/{slug}"
    users[slug] = {
        "slug": slug,
        "name": data.name,
        "credential": credential,
        "traffic_limit_gb": data.traffic_limit_gb,
        "expires_at": data.expires_at,
        "subscription_path": sub_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return users[slug]

@app.get("/api/users")
def list_users(_: bool = Depends(require_admin)):
    return list(users.values())

@app.get("/{prefix}/{slug}")
def subscription(prefix: str, slug: str):
    if prefix != SUB_PREFIX or slug not in users:
        raise HTTPException(status_code=404)
    # Placeholder subscription payload. Wire this to your own authorized
    # Xray/sing-box node configuration in production.
    u = users[slug]
    return PlainTextResponse(
        f"# subscription for {u['name']}\n"
        f"# credential={u['credential']}\n"
    )

@app.post("/api/proxy-scan")
def proxy_scan(data: ProxyCheck, _: bool = Depends(require_admin)):
    # Safe connectivity check only. No evasion or bypass logic.
    import socket
    started = time.perf_counter()
    try:
        with socket.create_connection((data.host, data.port), timeout=4):
            latency = round((time.perf_counter() - started) * 1000, 1)
        return {"healthy": True, "latency_ms": latency, "host": data.host, "port": data.port}
    except Exception as e:
        return {"healthy": False, "error": str(e), "host": data.host, "port": data.port}
