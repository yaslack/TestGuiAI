"""Helper client for interacting with an LM Studio HTTP server."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


class LMStudioError(RuntimeError):
    """Base exception for LM Studio client errors."""


class LMStudioConnectionError(LMStudioError):
    """Raised when the LM Studio server cannot be reached."""


class LMStudioResponseError(LMStudioError):
    """Raised when the LM Studio server returns an unexpected response."""


@dataclass
class ModelInfo:
    """Represents a single LM Studio model entry."""

    name: str
    description: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "ModelInfo":
        name = payload.get("name") or payload.get("id") or payload.get("model")
        if not name:
            raise LMStudioResponseError("LM Studio model payload does not contain an identifier")
        description = payload.get("description") or payload.get("details") or payload.get("path")
        return cls(name=name, description=description)


class LMStudioClient:
    """Async client used to talk with an LM Studio HTTP server."""

    def __init__(self, base_url: str, *, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def list_models(self) -> List[ModelInfo]:
        """Return the list of available models."""
        try:
            response = await self._client.get("/api/models")
            response.raise_for_status()
        except httpx.RequestError as exc:  # pragma: no cover - networking errors
            raise LMStudioConnectionError(str(exc)) from exc
        except httpx.HTTPStatusError as exc:  # pragma: no cover - server errors
            raise LMStudioResponseError(str(exc)) from exc

        payload = response.json()
        entries: List[Dict[str, Any]]
        if isinstance(payload, dict):
            if "models" in payload and isinstance(payload["models"], list):
                entries = payload["models"]
            elif "data" in payload and isinstance(payload["data"], list):
                entries = payload["data"]
            else:
                raise LMStudioResponseError("Unexpected LM Studio model response format")
        elif isinstance(payload, list):
            entries = payload
        else:
            raise LMStudioResponseError("Unexpected LM Studio model response format")

        return [ModelInfo.from_payload(entry) for entry in entries]

    async def select_model(self, model_name: str) -> Dict[str, Any]:
        """Select the model that should be active in LM Studio."""
        try:
            response = await self._client.post("/api/select-model", json={"model": model_name})
            response.raise_for_status()
        except httpx.RequestError as exc:  # pragma: no cover - networking errors
            raise LMStudioConnectionError(str(exc)) from exc
        except httpx.HTTPStatusError as exc:  # pragma: no cover - server errors
            raise LMStudioResponseError(str(exc)) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise LMStudioResponseError("LM Studio returned a non-JSON response") from exc

    async def __aenter__(self) -> "LMStudioClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()


async def list_models(base_url: str) -> List[ModelInfo]:
    """Convenience helper for quickly fetching the list of models."""
    async with LMStudioClient(base_url) as client:
        return await client.list_models()


async def select_model(base_url: str, model_name: str) -> Dict[str, Any]:
    """Convenience helper for selecting a model."""
    async with LMStudioClient(base_url) as client:
        return await client.select_model(model_name)
