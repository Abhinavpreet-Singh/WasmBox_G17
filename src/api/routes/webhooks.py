"""Webhook ingress - Week 4 Day 18."""

import hmac
import hashlib
from fastapi import APIRouter, Header, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from src.storage.db import SessionLocal
from src.storage.models import Plugin
from src.api.routes.run import run_plugin, RunRequest

router = APIRouter(prefix="/hooks", tags=["Webhooks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# For a real implementation, this would be fetched from the plugin/tenant settings
WEBHOOK_SECRET = b"wasmbox-super-secret"

@router.post("/{plugin_id}")
async def trigger_webhook(
    plugin_id: str,
    request: Request,
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db)
):
    """Trigger a plugin via webhook with HMAC verification."""
    
    # Verify HMAC
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")
        
    payload = await request.body()
    expected_signature = "sha256=" + hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # Check if plugin exists
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    if not plugin.active_version_id:
        raise HTTPException(status_code=400, detail="Plugin has no active version")
        
    # Run the plugin
    run_req = RunRequest(
        artifact=f"{plugin.active_version_id}.wasm",
        stdin=payload.decode('utf-8', errors='replace'),
        allow_db_bridge=True
    )
    
    result = run_plugin(run_req, db=db)
    
    if result.status == "error":
        raise HTTPException(status_code=500, detail=result.stderr)
        
    return {"status": "ok", "execution_id": result.id, "output": result.stdout}
