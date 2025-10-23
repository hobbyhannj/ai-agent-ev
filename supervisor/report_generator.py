"""PDF report generation utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional
import platform
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def _register_korean_font():
    """Register Korean fonts from system."""
    if not REPORTLAB_AVAILABLE:
        return

    font_paths = []
    system = platform.system()

    if system == "Darwin":
        font_paths = [
            "/Library/Fonts/NotoSansKR-Regular.otf",
            "/System/Library/Fonts/AppleGothic.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    elif system == "Windows":
        font_paths = [
            "C:\\Windows\\Fonts\\malgun.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]
    elif system == "Linux":
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansKR-Regular.otf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    for font_path in font_paths:
        try:
            if Path(font_path).exists():
                font_name = Path(font_path).stem
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
        except Exception:
            continue

    return "Helvetica"


def _setup_matplotlib_korean():
    """Setup matplotlib for Korean text."""
    if not MATPLOTLIB_AVAILABLE:
        return

    system = platform.system()

    if system == "Darwin":
        rcParams['font.sans-serif'] = ['AppleGothic', 'Arial Unicode MS', 'DejaVu Sans']
    elif system == "Windows":
        rcParams['font.sans-serif'] = ['Malgun Gothic', 'Arial', 'DejaVu Sans']
    elif system == "Linux":
        rcParams['font.sans-serif'] = ['Noto Sans CJK KR', 'DejaVu Sans']

    rcParams['axes.unicode_minus'] = False


def _generate_market_graph() -> Optional[Image]:
    """Generate EV market trends graph."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    _setup_matplotlib_korean()

    try:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        regions = ['Global', 'China', 'Europe', 'US']
        growth_rates = [28, 32, 16, 19]
        colors_list = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        ax.bar(regions, growth_rates, color=colors_list, alpha=0.7, edgecolor='black')
        ax.set_ylabel('YoY Growth Rate (%)', fontsize=11)
        ax.set_title('EV Market Growth by Region', fontsize=13, fontweight='bold')
        ax.set_ylim(0, 40)

        for i, v in enumerate(growth_rates):
            ax.text(i, v + 1, f'{v}%', ha='center', fontsize=10, fontweight='bold')

        plt.tight_layout()

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        return Image(img_buffer, width=4.5*inch, height=3*inch)
    except Exception:
        return None


def _generate_supply_chain_graph() -> Optional[Image]:
    """Generate supply chain component status graph."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    _setup_matplotlib_korean()

    try:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        components = ['Battery', 'Semiconductor', 'Motor']
        status = [7, 8, 7]
        colors_list = ['#2ca02c', '#ff7f0e', '#1f77b4']

        bars = ax.barh(components, status, color=colors_list, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Health Score (0-10)', fontsize=11)
        ax.set_title('Supply Chain Component Health', fontsize=13, fontweight='bold')
        ax.set_xlim(0, 10)

        for i, v in enumerate(status):
            ax.text(v + 0.2, i, f'{v}/10', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        return Image(img_buffer, width=4.5*inch, height=3*inch)
    except Exception:
        return None


def _generate_oem_production_graph() -> Optional[Image]:
    """Generate OEM production capacity graph."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    _setup_matplotlib_korean()

    try:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        oems = ['Tesla', 'BYD', 'VW', 'GM']
        capacity = [2.2, 3.0, 1.5, 1.0]
        colors_list = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e']

        bars = ax.bar(oems, capacity, color=colors_list, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Production Capacity (M units/year)', fontsize=11)
        ax.set_title('OEM EV Production Capacity', fontsize=13, fontweight='bold')
        ax.set_ylim(0, 3.5)

        for i, v in enumerate(capacity):
            ax.text(i, v + 0.1, f'{v}M', ha='center', fontsize=10, fontweight='bold')

        plt.tight_layout()

        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        return Image(img_buffer, width=4.5*inch, height=3*inch)
    except Exception:
        return None


def generate_pdf_report(
    report_text: str,
    output_path: Optional[str] = None,
    title: str = "EV Market Intelligence Report",
) -> str:
    """Generate PDF report from text content."""

    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab not installed. Install with: pip install reportlab"
        )

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reports/ev_market_report_{timestamp}.pdf"

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    font_name = _register_korean_font()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1a3a52"),
        spaceAfter=30,
        alignment=1,
        fontName=font_name,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c5aa0"),
        spaceAfter=12,
        spaceBefore=12,
        fontName=font_name,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        fontName=font_name,
    )

    elements = []

    elements.append(Paragraph(title, title_style))
    elements.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 0.3 * inch))

    sections = report_text.split("\n\n")

    for idx, section in enumerate(sections):
        lines = section.split("\n")

        for line in lines:
            if not line.strip():
                continue

            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.")):
                elements.append(Paragraph(line.strip(), heading_style))

                if line.startswith("2."):
                    graph = _generate_market_graph()
                    if graph:
                        elements.append(Spacer(1, 0.2 * inch))
                        elements.append(graph)
                        elements.append(Spacer(1, 0.3 * inch))

                elif line.startswith("4."):
                    graph = _generate_oem_production_graph()
                    if graph:
                        elements.append(Spacer(1, 0.2 * inch))
                        elements.append(graph)
                        elements.append(Spacer(1, 0.3 * inch))

                elif line.startswith("5."):
                    graph = _generate_supply_chain_graph()
                    if graph:
                        elements.append(Spacer(1, 0.2 * inch))
                        elements.append(graph)
                        elements.append(Spacer(1, 0.3 * inch))

            elif line.strip().startswith("-"):
                elements.append(Paragraph(line.strip(), body_style))
            else:
                elements.append(Paragraph(line.strip(), body_style))

        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

    return str(Path(output_path).absolute())


def generate_text_report(
    report_text: str,
    output_path: Optional[str] = None,
) -> str:
    """Generate text report file."""

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"reports/ev_market_report_{timestamp}.txt"

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"EV Market Intelligence Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(report_text)

    return str(Path(output_path).absolute())
