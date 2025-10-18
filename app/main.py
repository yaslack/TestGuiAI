"""FastAPI application exposing a small UI for LM Studio model selection."""
from __future__ import annotations

import os
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .lmstudio import (
    LMStudioConnectionError,
    LMStudioResponseError,
    list_models,
    select_model,
)

LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234")

app = FastAPI(title="LM Studio Model Selector")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> HTMLResponse:
    """Serve the HTML interface."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "lm_studio_url": LM_STUDIO_URL,
        },
    )


@app.get("/api/config")
async def get_config() -> Dict[str, str]:
    """Return runtime configuration used by the UI."""
    return {"lmStudioUrl": LM_STUDIO_URL}


@app.get("/api/models")
async def get_models() -> Dict[str, List[Dict[str, str]]]:
    """Return the list of models exposed by LM Studio."""
    try:
        models = await list_models(LM_STUDIO_URL)
    except LMStudioConnectionError as exc:
        raise HTTPException(status_code=503, detail=f"LM Studio unreachable: {exc}") from exc
    except LMStudioResponseError as exc:
        raise HTTPException(status_code=502, detail=f"LM Studio returned an invalid response: {exc}") from exc

    return {
        "models": [
            {
                "name": model.name,
                "description": model.description or "",
            }
            for model in models
        ]
    }


@app.post("/api/select")
async def select_model_endpoint(payload: Dict[str, str]) -> Dict[str, str]:
    """Select a model in LM Studio."""
    model_name = (payload or {}).get("model") or (payload or {}).get("model_id")
    if not model_name:
        raise HTTPException(status_code=400, detail="The 'model' field is required")

    try:
        response = await select_model(LM_STUDIO_URL, model_name)
    except LMStudioConnectionError as exc:
        raise HTTPException(status_code=503, detail=f"LM Studio unreachable: {exc}") from exc
    except LMStudioResponseError as exc:
        raise HTTPException(status_code=502, detail=f"LM Studio returned an invalid response: {exc}") from exc

    message = response.get("message") if isinstance(response, dict) else None
    return {"status": "ok", "message": message or f"Model '{model_name}' selected"}
