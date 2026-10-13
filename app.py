"""Stateless live JSON endpoint; works with Vercel, Render, and a VPS."""
import json
import os
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sync import synchronize

SOURCE_URL = os.environ.get("ORDERS_URL", "https://test.ooobs.ru/api/orders")
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/")
@app.get("/api/orders")
def orders():
    try:
        request = Request(SOURCE_URL, headers={"Accept": "application/json"})
        with urlopen(request, timeout=10) as response:
            raw_orders = json.load(response)
        if not isinstance(raw_orders, list):
            raise ValueError("The source must return a JSON array")
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Upstream orders unavailable") from exc
    result = synchronize(raw_orders)
    return JSONResponse(content=result, headers={"Cache-Control": "no-store"})
