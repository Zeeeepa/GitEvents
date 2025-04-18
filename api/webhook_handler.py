import os
import logging
import hmac
import hashlib
import json
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware

from handlers.github_event_handler import GitHub

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GitHub Webhook Handler", description="Webhook handler for GitHub events")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GitHub event handler
github_handler = GitHub(app)

def verify_webhook_signature(request: Request, x_hub_signature_256: Optional[str] = Header(None)) -> bool:
    """Verify the webhook signature from GitHub"""
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    # If no secret is configured, skip verification (not recommended for production)
    if not webhook_secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True
    
    # If no signature is provided, reject the request
    if not x_hub_signature_256:
        logger.warning("No X-Hub-Signature-256 header provided")
        return False
    
    # Get the raw request body
    body = request.body
    
    # Compute the expected signature
    expected_signature = "sha256=" + hmac.new(
        webhook_secret.encode(), 
        msg=body, 
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Compare signatures using a constant-time comparison
    return hmac.compare_digest(expected_signature, x_hub_signature_256)

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events"""
    # Verify the webhook signature
    if not verify_webhook_signature(request):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Parse the request body
    body = await request.body()
    event_data = json.loads(body)
    
    # Handle the event
    try:
        result = await github_handler.handle(event_data, request)
        return result
    except Exception as e:
        logger.exception(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WEBHOOK_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
