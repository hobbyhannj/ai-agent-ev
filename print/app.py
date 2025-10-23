"""FastAPI service for rendering EV Market Supervisor reports as HTML and PDF."""

from __future__ import annotations

import io
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
from pydantic import BaseModel, Field
from weasyprint import HTML

TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

_SECTION_HEADER_PATTERN = re.compile(r"^(?P<index>\d+)\.\s+(?P<title>.+)$")
_LABEL_PATTERN = re.compile(r"^(?P<label>[^:]+):\s*(?P<value>.+)$")
_URL_PATTERN = re.compile(r"(https?://[^\s)]+)")


class ReportRequest(BaseModel):
    """Payload describing how to render the final supervisor report."""

    report: str = Field(..., description="Supervisor final report text")
    title: str = Field(
        default="EV Market Supervisor Report",
        description="Title displayed at the top of the document",
        max_length=200,
    )
    subtitle: str | None = Field(
        default=None,
        description="Optional subtitle shown beneath the main title",
        max_length=250,
    )
    prepared_for: str | None = Field(
        default=None,
        description="Name of the audience or recipient of the report",
        max_length=200,
    )
    prepared_by: str | None = Field(
        default=None,
        description="Name of the report author",
        max_length=200,
    )
    summary: str | None = Field(
        default=None,
        description="Short highlight paragraph shown near the beginning",
        max_length=1000,
    )
    generated_at: datetime | None = Field(
        default=None,
        description="Timestamp representing when the report was generated",
    )


def create_app() -> FastAPI:
    """Construct and return an application instance."""

    app = FastAPI(title="EV Market Supervisor PDF Service", version="1.0.0")

    @app.get("/health", response_class=JSONResponse)
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/render", response_class=HTMLResponse)
    async def render_html(payload: ReportRequest) -> HTMLResponse:
        html = _render_report(payload)
        return HTMLResponse(content=html)

    @app.post("/pdf")
    async def render_pdf(payload: ReportRequest) -> StreamingResponse:
        html = _render_report(payload)
        try:
            pdf_bytes = HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf()
        except Exception as exc:  # pragma: no cover - defensive guard around renderer
            raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc
        filename = _build_filename(payload.title)
        headers = {
            "Content-Disposition": f"attachment; filename={filename}.pdf",
            "Content-Type": "application/pdf",
        }
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)

    return app


def _render_report(payload: ReportRequest) -> str:
    """Render the report as an HTML document."""

    sections = _format_sections(payload.report)
    generated_at = _format_generated_at(payload.generated_at)
    template = _env.get_template("report.html")
    html = template.render(
        title=payload.title,
        subtitle=payload.subtitle,
        prepared_for=payload.prepared_for,
        prepared_by=payload.prepared_by,
        summary=payload.summary,
        sections=sections,
        generated_at=generated_at,
    )
    return html


def _format_sections(report_text: str) -> List[Dict[str, Any]]:
    """Split the raw report into structured sections for templating."""

    sections: List[Dict[str, Any]] = []
    current_section: Dict[str, Any] | None = None
    list_buffer: List[str] = []

    for raw_line in report_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            if current_section and list_buffer:
                current_section["blocks"].append({"type": "list", "items": list_buffer.copy()})
                list_buffer.clear()
            continue

        if stripped.startswith("==="):
            continue

        header_match = _SECTION_HEADER_PATTERN.match(stripped)
        if header_match:
            if current_section:
                if list_buffer:
                    current_section["blocks"].append({"type": "list", "items": list_buffer.copy()})
                    list_buffer.clear()
                sections.append(current_section)
            current_section = {
                "index": header_match.group("index"),
                "title": header_match.group("title"),
                "blocks": [],
            }
            continue

        if not current_section:
            # Skip lines before the first numbered section.
            continue

        if stripped.startswith("- "):
            list_buffer.append(stripped[2:].strip())
            continue

        if list_buffer:
            current_section["blocks"].append({"type": "list", "items": list_buffer.copy()})
            list_buffer.clear()

        current_section["blocks"].append({"type": "paragraph", "text": stripped})

    if current_section:
        if list_buffer:
            current_section["blocks"].append({"type": "list", "items": list_buffer.copy()})
            list_buffer.clear()
        sections.append(current_section)

    for section in sections:
        section["blocks"] = _format_blocks(section["blocks"])

    return sections


def _format_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted: List[Dict[str, Any]] = []
    for block in blocks:
        if block["type"] == "list":
            items = [_format_list_item(item) for item in block.get("items", []) if item]
            if items:
                formatted.append({"type": "list", "items": items})
        elif block["type"] == "paragraph":
            text = block.get("text", "").strip()
            if text:
                formatted.append({"type": "paragraph", "html": _format_paragraph(text)})
    return formatted


def _format_paragraph(text: str) -> Markup:
    label_match = _LABEL_PATTERN.match(text)
    if label_match:
        label = escape(label_match.group("label"))
        value = _escape_and_linkify(label_match.group("value"))
        return Markup(f"<strong>{label}:</strong> ") + value
    return _escape_and_linkify(text)


def _format_list_item(text: str) -> Markup:
    return _escape_and_linkify(text)


def _escape_and_linkify(text: str) -> Markup:
    text = text.strip()
    if not text:
        return Markup("")

    matches = list(_URL_PATTERN.finditer(text))
    if not matches:
        return escape(text)

    last_index = 0
    parts: List[Markup] = []
    for match in matches:
        if match.start() > last_index:
            parts.append(escape(text[last_index : match.start()]))
        url = match.group(0)
        escaped_url = escape(url)
        link = Markup(f'<a href="{escaped_url}" class="external-link">{escaped_url}</a>')
        parts.append(link)
        last_index = match.end()

    if last_index < len(text):
        parts.append(escape(text[last_index:]))

    result = Markup("")
    for fragment in parts:
        result += fragment
    return result


def _format_generated_at(timestamp: datetime | None) -> str:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    elif timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    else:
        timestamp = timestamp.astimezone(timezone.utc)

    return timestamp.astimezone().strftime("%B %d, %Y • %H:%M %Z")


def _build_filename(title: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9]+", "-", title).strip("-")
    return sanitized.lower() or "ev-market-report"
