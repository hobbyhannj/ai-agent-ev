"""Convenience entry point for running the PDF FastAPI service with uvicorn."""

from __future__ import annotations

import uvicorn

from .app import create_app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("print.main:app", host="0.0.0.0", port=8080, reload=False)
