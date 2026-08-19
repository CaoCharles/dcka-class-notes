"""Generate architect-level Draw.io and SVG views for the DCKA project.

The Draw.io file is the editable source of truth.  The SVG exports mirror the
three pages and are converted to PNG for Markdown/Word consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
IMAGE_DIR = HERE.parent / "images"
DRAWIO_OUT = HERE / "dcka-system-architecture.drawio"

FONT = "Arial, PingFang TC, Microsoft JhengHei, sans-serif"
COLORS = {
    "ink": "#0F172A",
    "muted": "#475569",
    "line": "#64748B",
    "canvas": "#F8FAFC",
    "zone": "#F1F5F9",
    "zone_stroke": "#CBD5E1",
    "blue_fill": "#DBEAFE",
    "blue": "#2563EB",
    "purple_fill": "#EDE9FE",
    "purple": "#7C3AED",
    "green_fill": "#DCFCE7",
    "green": "#059669",
    "amber_fill": "#FEF3C7",
    "amber": "#D97706",
    "red_fill": "#FEE2E2",
    "red": "#DC2626",
    "white": "#FFFFFF",
}


@dataclass
class Node:
    id: str
    x: int
    y: int
    w: int
    h: int
    title: str
    lines: list[str] = field(default_factory=list)
    fill: str = COLORS["white"]
    stroke: str = COLORS["line"]
    shape: str = "rounded"
    title_size: int = 18
    body_size: int = 14
    dashed: bool = False
    title_color: str = COLORS["ink"]
    body_color: str = COLORS["muted"]
    stroke_width: int = 2


@dataclass
class Zone:
    id: str
    x: int
    y: int
    w: int
    h: int
    title: str
    subtitle: str = ""
    fill: str = COLORS["zone"]
    stroke: str = COLORS["zone_stroke"]
    dashed: bool = False
    rounded: bool = True


@dataclass
class Edge:
    id: str
    points: list[tuple[int, int]]
    label: str = ""
    color: str = COLORS["line"]
    dashed: bool = False
    width: int = 2
    bidirectional: bool = False
    label_x: int | None = None
    label_y: int | None = None


@dataclass
class Text:
    id: str
    x: int
    y: int
    text: str
    size: int = 15
    color: str = COLORS["muted"]
    bold: bool = False
    anchor: str = "start"
    rotation: int = 0


@dataclass
class Page:
    id: str
    name: str
    width: int
    height: int
    title: str
    subtitle: str
    zones: list[Zone] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    texts: list[Text] = field(default_factory=list)
    svg_name: str = ""


def node_label(node: Node) -> str:
    parts = [f'<font color="{node.title_color}"><b>{escape(node.title)}</b></font>']
    parts.extend(f'<font color="{node.body_color}">{escape(line)}</font>' for line in node.lines)
    return "<br>".join(parts)


def drawio_style(node: Node) -> str:
    shape = "rounded=1;arcSize=12;" if node.shape == "rounded" else ""
    if node.shape == "cylinder":
        shape = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=12;"
    if node.shape == "hexagon":
        shape = "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;"
    if node.shape == "diamond":
        shape = "rhombus;perimeter=rhombusPerimeter;"
    if node.shape == "ellipse":
        shape = "ellipse;perimeter=ellipsePerimeter;"
    if node.shape == "parallelogram":
        shape = "shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;"
    return (
        f"{shape}whiteSpace=wrap;html=1;fillColor={node.fill};"
        f"strokeColor={node.stroke};strokeWidth={node.stroke_width};fontColor={node.title_color};"
        f"fontSize={node.body_size};align=center;verticalAlign=middle;spacing=8;"
        + ("dashed=1;" if node.dashed else "")
    )


def add_vertex(root: ET.Element, node: Node) -> None:
    cell = ET.SubElement(
        root,
        "mxCell",
        {
            "id": node.id,
            "value": node_label(node),
            "style": drawio_style(node),
            "vertex": "1",
            "parent": "1",
        },
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        {"x": str(node.x), "y": str(node.y), "width": str(node.w), "height": str(node.h), "as": "geometry"},
    )


def add_zone(root: ET.Element, zone: Zone) -> None:
    value = f"<b>{escape(zone.title)}</b>"
    if zone.subtitle:
        value += f"<br><font color=\"{COLORS['muted']}\">{escape(zone.subtitle)}</font>"
    style = (
        f"rounded={1 if zone.rounded else 0};arcSize=8;whiteSpace=wrap;html=1;fillColor={zone.fill};"
        f"strokeColor={zone.stroke};strokeWidth=2;verticalAlign=top;align=left;"
        "spacingTop=12;spacingLeft=14;fontSize=15;fontStyle=1;"
        + ("dashed=1;" if zone.dashed else "")
    )
    cell = ET.SubElement(root, "mxCell", {"id": zone.id, "value": value, "style": style, "vertex": "1", "parent": "1"})
    ET.SubElement(cell, "mxGeometry", {"x": str(zone.x), "y": str(zone.y), "width": str(zone.w), "height": str(zone.h), "as": "geometry"})


def add_edge(root: ET.Element, edge: Edge) -> None:
    style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;"
        f"strokeColor={edge.color};strokeWidth={edge.width};endArrow=block;endFill=1;"
        + ("startArrow=block;startFill=1;" if edge.bidirectional else "")
        + ("dashed=1;" if edge.dashed else "")
    )
    cell = ET.SubElement(root, "mxCell", {"id": edge.id, "value": escape(edge.label), "style": style, "edge": "1", "parent": "1"})
    geom = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(geom, "mxPoint", {"x": str(edge.points[0][0]), "y": str(edge.points[0][1]), "as": "sourcePoint"})
    ET.SubElement(geom, "mxPoint", {"x": str(edge.points[-1][0]), "y": str(edge.points[-1][1]), "as": "targetPoint"})
    if len(edge.points) > 2:
        arr = ET.SubElement(geom, "Array", {"as": "points"})
        for x, y in edge.points[1:-1]:
            ET.SubElement(arr, "mxPoint", {"x": str(x), "y": str(y)})


def add_text(root: ET.Element, item: Text) -> None:
    style = (
        "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;verticalAlign=middle;"
        f"fontSize={item.size};fontColor={item.color};align={'center' if item.anchor == 'middle' else 'left'};"
        + ("fontStyle=1;" if item.bold else "")
        + (f"rotation={item.rotation};" if item.rotation else "")
    )
    # ElementTree escapes XML attributes. Passing pre-escaped text would turn
    # an ampersand into "&amp;amp;" inside the editable Draw.io source.
    cell = ET.SubElement(root, "mxCell", {"id": item.id, "value": item.text, "style": style, "vertex": "1", "parent": "1"})
    width = 720 if item.anchor == "start" else 500
    x = item.x if item.anchor == "start" else item.x - width // 2
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(item.y - item.size), "width": str(width), "height": str(item.size + 12), "as": "geometry"})


def write_drawio(pages: list[Page]) -> None:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2026-08-19T12:00:00.000Z",
            "agent": "Codex",
            "version": "24.7.17",
            "type": "device",
            "compressed": "false",
        },
    )
    for page in pages:
        diagram = ET.SubElement(mxfile, "diagram", {"id": page.id, "name": page.name})
        graph = ET.SubElement(
            diagram,
            "mxGraphModel",
            {
                "dx": str(page.width),
                "dy": str(page.height),
                "grid": "1",
                "gridSize": "10",
                "guides": "1",
                "tooltips": "1",
                "connect": "1",
                "arrows": "1",
                "fold": "1",
                "page": "1",
                "pageScale": "1",
                "pageWidth": str(page.width),
                "pageHeight": str(page.height),
                "math": "0",
                "shadow": "0",
            },
        )
        root = ET.SubElement(graph, "root")
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
        add_text(root, Text(f"{page.id}-title", 55, 56, page.title, 28, COLORS["ink"], True))
        add_text(root, Text(f"{page.id}-subtitle", 55, 91, page.subtitle, 15, COLORS["muted"]))
        for zone in page.zones:
            add_zone(root, zone)
        for edge in page.edges:
            add_edge(root, edge)
        for node in page.nodes:
            add_vertex(root, node)
        for item in page.texts:
            add_text(root, item)

    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(DRAWIO_OUT, encoding="utf-8", xml_declaration=True)


def svg_text(x: int, y: int, text: str, size: int, color: str, bold: bool = False, anchor: str = "start") -> str:
    weight = "700" if bold else "400"
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(text)}</text>'


def svg_zone(zone: Zone) -> str:
    dash = ' stroke-dasharray="9 7"' if zone.dashed else ""
    radius = 18 if zone.rounded else 0
    out = [f'<rect x="{zone.x}" y="{zone.y}" width="{zone.w}" height="{zone.h}" rx="{radius}" fill="{zone.fill}" stroke="{zone.stroke}" stroke-width="2"{dash}/>']
    out.append(svg_text(zone.x + 16, zone.y + 28, zone.title, 15, COLORS["ink"], True))
    if zone.subtitle:
        out.append(svg_text(zone.x + 16, zone.y + 50, zone.subtitle, 12, COLORS["muted"]))
    return "\n".join(out)


def svg_node(node: Node) -> str:
    dash = ' stroke-dasharray="8 6"' if node.dashed else ""
    if node.shape == "cylinder":
        shape = (
            f'<path d="M {node.x} {node.y + 12} C {node.x} {node.y - 4}, {node.x + node.w} {node.y - 4}, {node.x + node.w} {node.y + 12} '
            f'L {node.x + node.w} {node.y + node.h - 12} C {node.x + node.w} {node.y + node.h + 4}, {node.x} {node.y + node.h + 4}, {node.x} {node.y + node.h - 12} Z" '
            f'fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"{dash}/>'
            f'<ellipse cx="{node.x + node.w / 2}" cy="{node.y + 12}" rx="{node.w / 2}" ry="12" fill="none" stroke="{node.stroke}" stroke-width="2"/>'
        )
    elif node.shape == "hexagon":
        points = f"{node.x + 18},{node.y} {node.x + node.w - 18},{node.y} {node.x + node.w},{node.y + node.h / 2} {node.x + node.w - 18},{node.y + node.h} {node.x + 18},{node.y + node.h} {node.x},{node.y + node.h / 2}"
        shape = f'<polygon points="{points}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"{dash}/>'
    elif node.shape == "diamond":
        points = f"{node.x + node.w / 2},{node.y} {node.x + node.w},{node.y + node.h / 2} {node.x + node.w / 2},{node.y + node.h} {node.x},{node.y + node.h / 2}"
        shape = f'<polygon points="{points}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"{dash}/>'
    elif node.shape == "ellipse":
        shape = f'<ellipse cx="{node.x + node.w / 2}" cy="{node.y + node.h / 2}" rx="{node.w / 2}" ry="{node.h / 2}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="2"{dash}/>'
    elif node.shape == "parallelogram":
        skew = min(22, node.w // 5)
        points = f"{node.x + skew},{node.y} {node.x + node.w},{node.y} {node.x + node.w - skew},{node.y + node.h} {node.x},{node.y + node.h}"
        shape = f'<polygon points="{points}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="{node.stroke_width}"{dash}/>'
    else:
        radius = 14 if node.shape == "rounded" else 0
        shape = f'<rect x="{node.x}" y="{node.y}" width="{node.w}" height="{node.h}" rx="{radius}" fill="{node.fill}" stroke="{node.stroke}" stroke-width="{node.stroke_width}"{dash}/>'
    center = node.x + node.w / 2
    total_lines = 1 + len(node.lines)
    gap = 22
    first_y = node.y + node.h / 2 - (total_lines - 1) * gap / 2
    parts = [shape, svg_text(int(center), int(first_y), node.title, node.title_size, node.title_color, True, "middle")]
    for idx, line in enumerate(node.lines, start=1):
        parts.append(svg_text(int(center), int(first_y + idx * gap), line, node.body_size, node.body_color, False, "middle"))
    return "\n".join(parts)


def svg_edge(edge: Edge) -> str:
    points = " ".join(f"{x},{y}" for x, y in edge.points)
    dash = ' stroke-dasharray="9 7"' if edge.dashed else ""
    start = ' marker-start="url(#arrow-start)"' if edge.bidirectional else ""
    out = [f'<polyline points="{points}" fill="none" stroke="{edge.color}" stroke-width="{edge.width}" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#arrow)"{start}{dash}/>']
    if edge.label:
        if edge.label_x is not None and edge.label_y is not None:
            lx, ly = edge.label_x, edge.label_y
        else:
            x1, y1 = edge.points[0]
            x2, y2 = edge.points[-1]
            lx, ly = (x1 + x2) // 2, (y1 + y2) // 2 - 8
        pad = max(54, len(edge.label) * 7)
        out.append(f'<rect x="{lx - pad / 2}" y="{ly - 15}" width="{pad}" height="22" rx="5" fill="{COLORS["canvas"]}" opacity="0.96"/>')
        out.append(svg_text(lx, ly, edge.label, 12, COLORS["muted"], False, "middle"))
    return "\n".join(out)


def write_svg(page: Page) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{page.width}" height="{page.height}" viewBox="0 0 {page.width} {page.height}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748B"/></marker><marker id="arrow-start" markerWidth="10" markerHeight="10" refX="1" refY="3" orient="auto"><path d="M9,0 L9,6 L0,3 z" fill="#64748B"/></marker></defs>',
        f'<rect width="{page.width}" height="{page.height}" fill="{COLORS["canvas"]}"/>',
        svg_text(55, 56, page.title, 30, COLORS["ink"], True),
        svg_text(55, 89, page.subtitle, 15, COLORS["muted"]),
    ]
    parts.extend(svg_zone(zone) for zone in page.zones)
    parts.extend(svg_edge(edge) for edge in page.edges)
    parts.extend(svg_node(node) for node in page.nodes)
    for item in page.texts:
        rendered = svg_text(item.x, item.y, item.text, item.size, item.color, item.bold, item.anchor)
        if item.rotation:
            rendered = rendered.replace("<text ", f'<text transform="rotate({item.rotation} {item.x} {item.y})" ', 1)
        parts.append(rendered)
    parts.append("</svg>")
    (IMAGE_DIR / page.svg_name).write_text("\n".join(parts), encoding="utf-8")


def system_page() -> Page:
    p = Page(
        "system-container",
        "01 System Component & Deployment Architecture",
        1800,
        1120,
        "DCKA System Component & Deployment Architecture (Current State)",
        "C4 Container / Deployment View｜實線：Runtime data flow　虛線：Build / Deploy control flow",
        svg_name="overall-architecture.svg",
    )
    p.zones = [
        Zone("z-client", 40, 120, 360, 900, "CLIENT & DEVELOPER ZONE", "本機與使用者瀏覽器"),
        Zone("z-github", 430, 120, 610, 900, "GITHUB CONTROL / DELIVERY PLANE", "Repository、Actions、Pages"),
        Zone("z-gcp", 1070, 120, 500, 900, "GOOGLE CLOUD PROJECT", "Managed build、serverless runtime 與 persistence", fill="#F0FDF4", stroke="#86EFAC"),
        Zone("z-ai", 1600, 120, 160, 900, "EXTERNAL AI", "Google API", fill="#FFFBEB", stroke="#FCD34D"),
        Zone("z-run", 1100, 425, 440, 440, "CLOUD RUN SERVICE: dcka-chatbot-backend", "asia-east1｜public ingress｜stateless revision", fill="#ECFDF5", stroke="#34D399"),
    ]
    p.nodes = [
        Node("developer", 75, 175, 290, 90, "Author / Developer", ["VS Code · Git · uv"], COLORS["blue_fill"], COLORS["blue"]),
        Node("local-repo", 75, 315, 290, 100, "Local working tree", ["docs/ · mkdocs.yml", "backend/ · hooks/"], COLORS["blue_fill"], COLORS["blue"]),
        Node("mkdocs", 75, 475, 290, 130, "MkDocs build process", ["Markdown → static site", "hook → content.json", "local preview / fallback"], COLORS["purple_fill"], COLORS["purple"]),
        Node("browser", 75, 700, 290, 220, "Browser runtime", ["HTML / CSS / Material UI", "chatbot.js + marked.js", "content.json in memory", "history → sessionStorage"], COLORS["blue_fill"], COLORS["blue"]),
        Node("main", 470, 175, 230, 105, "main branch", ["source of truth", "docs + frontend + backend"], COLORS["purple_fill"], COLORS["purple"]),
        Node("actions", 760, 175, 240, 105, "GitHub Actions", ["deploy-pages.yml", "deploy-backend.yml"], COLORS["purple_fill"], COLORS["purple"]),
        Node("secrets", 760, 330, 240, 130, "GitHub configuration", ["Variables: project + WIF", "Secret: GEMINI_API_KEY", "no GCP JSON key"], COLORS["red_fill"], COLORS["red"], "cylinder"),
        Node("gh-pages", 470, 505, 230, 110, "Pages artifact", ["built site bundle", "HTML / CSS / JS / JSON"], COLORS["purple_fill"], COLORS["purple"]),
        Node("pages", 760, 505, 240, 125, "GitHub Pages", ["static hosting / CDN", "caocharles.github.io", "/dcka-class-notes/"], COLORS["purple_fill"], COLORS["purple"]),
        Node("cloud-build", 1110, 175, 200, 105, "Cloud Build", ["source deploy", "uses Dockerfile"], COLORS["green_fill"], COLORS["green"]),
        Node("artifact", 1340, 175, 190, 105, "Artifact Registry", ["managed image", "versioned artifact"], COLORS["green_fill"], COLORS["green"], "cylinder"),
        Node("wif", 1110, 315, 200, 80, "Workload Identity", ["GitHub OIDC federation", "repo + main trust"], COLORS["green_fill"], COLORS["green"], "hexagon", 15, 11),
        Node("deployer", 1340, 315, 190, 80, "Deployer SA", ["short-lived credential", "source deploy only"], COLORS["green_fill"], COLORS["green"], "rounded", 15, 11),
        Node("ingress", 1130, 480, 170, 90, "HTTPS ingress", ["GET /", "POST /api/chat"], COLORS["green_fill"], COLORS["green"]),
        Node("fastapi", 1330, 480, 180, 105, "FastAPI / Uvicorn", ["body + Pydantic limits", "CORS + rate limiting"], COLORS["green_fill"], COLORS["green"]),
        Node("adapter", 1130, 635, 170, 105, "Request adapter", ["role mapping", "history + message"], COLORS["green_fill"], COLORS["green"]),
        Node("genai", 1330, 635, 180, 105, "google-genai SDK", ["GenerateContentConfig", "thinking_level=low"], COLORS["green_fill"], COLORS["green"]),
        Node("runtime-sa", 1110, 780, 200, 70, "Runtime identity", ["dcka-chatbot-runtime", "roles/datastore.user"], COLORS["green_fill"], COLORS["green"], "rounded", 15, 11),
        Node("env", 1330, 780, 180, 70, "Runtime secret", ["GEMINI_API_KEY · PORT"], COLORS["red_fill"], COLORS["red"], "cylinder", 15, 11),
        Node("firestore", 1190, 900, 300, 90, "Cloud Firestore", ["masked chat_logs · expires_at", "TTL ACTIVE · 90-day retention"], "#FCE7F3", "#DB2777", "cylinder", 17, 13),
        Node("gemini", 1608, 505, 144, 185, "Gemini API", ["model:", "gemini-3.5-flash", "request / response"], COLORS["amber_fill"], COLORS["amber"], "hexagon", 17, 13),
    ]
    p.edges = [
        Edge("e-dev-local", [(220, 265), (220, 305)], "edit"),
        Edge("e-local-main", [(365, 365), (420, 365), (420, 228), (470, 228)], "git push main", dashed=True, label_x=430, label_y=323),
        Edge("e-local-build", [(220, 415), (220, 465)], "uv run", dashed=True),
        Edge("e-build-gh", [(365, 540), (420, 540), (420, 560), (470, 560)], "manual fallback", dashed=True, label_x=425, label_y=520),
        Edge("e-gh-pages", [(700, 560), (750, 560)], "publish", dashed=True),
        Edge("e-pages-browser", [(760, 585), (680, 585), (680, 670), (220, 670), (220, 700)], "GET HTML / assets / content.json", bidirectional=False, label_x=505, label_y=652),
        Edge("e-main-actions", [(700, 225), (750, 225)], "docs/** | backend/**", dashed=True),
        Edge("e-actions-pages-artifact", [(800, 280), (800, 480), (700, 480), (700, 550)], "MkDocs build + upload", dashed=True, label_x=750, label_y=465),
        Edge("e-secrets-actions", [(880, 330), (880, 290)], "workflow inputs", dashed=True),
        Edge("e-actions-wif", [(1000, 225), (1060, 225), (1060, 355), (1100, 355)], "OIDC token", dashed=True, label_x=1050, label_y=305),
        Edge("e-wif-deployer", [(1310, 355), (1330, 355)], "impersonate", dashed=True),
        Edge("e-deployer-build", [(1435, 315), (1435, 295), (1210, 295), (1210, 290)], "deploy source", dashed=True, label_x=1320, label_y=290),
        Edge("e-build-artifact", [(1310, 225), (1330, 225)], "image", dashed=True),
        Edge("e-artifact-run", [(1435, 280), (1435, 395), (1320, 395), (1320, 425)], "new revision", dashed=True),
        Edge("e-secrets-env", [(1000, 395), (1050, 395), (1050, 815), (1320, 815)], "--set-env-vars", COLORS["red"], True, label_x=1190, label_y=795),
        Edge("e-browser-ingress", [(365, 810), (1070, 810), (1070, 525), (1120, 525)], "HTTPS JSON · origin allowlist · anonymous", label_x=760, label_y=790),
        Edge("e-ingress-fastapi", [(1300, 525), (1320, 525)], "route"),
        Edge("e-fastapi-adapter", [(1420, 585), (1420, 610), (1215, 610), (1215, 625)], "validated ChatRequest", label_x=1325, label_y=600),
        Edge("e-adapter-genai", [(1300, 685), (1320, 685)], "contents + config", label_x=1310, label_y=665),
        Edge("e-env-genai", [(1420, 780), (1420, 750)], "API key", COLORS["red"], True),
        Edge("e-genai-gemini", [(1510, 685), (1585, 685), (1585, 600), (1598, 600)], "HTTPS generate_content", bidirectional=True, label_x=1560, label_y=728),
        Edge("e-fastapi-firestore", [(1510, 545), (1550, 545), (1550, 945), (1500, 945)], "BackgroundTasks · masked", "#DB2777", True, 2, False, 1510, 885),
        Edge("e-runtime-firestore", [(1210, 850), (1210, 890)], "runtime IAM", "#DB2777", True),
    ]
    p.texts = [
        Text("note-current", 450, 950, "CURRENT-STATE CONTROLS / CONSTRAINTS", 14, COLORS["red"], True),
        Text("note-state", 450, 978, "• Anonymous API   • Exact CORS allowlist   • Per-instance rate limit + request size limits", 13),
        Text("note-rag", 450, 1002, "• Cloud Run remains stateless compute   • Persistence lives in Firestore   • Context is still full-site, not retrieval RAG", 13),
    ]
    return p


def runtime_page() -> Page:
    bp_lane = "#E8EEF4"
    bp_lane_alt = "#EFF3F7"
    bp_grid = "#AAB5C0"
    bp_line = "#34414C"
    bp_node = "#FBFCFD"
    bp_number = "#F2B632"
    bp_note = "#FFF8DF"

    p = Page(
        "runtime-swimlane",
        "02 AI Assistant Runtime Interaction Architecture",
        1800,
        1160,
        "DCKA AI Assistant | Runtime Interaction Architecture",
        "Current-state technical blueprint｜Vertical swimlanes = responsibility boundary｜Numbered circles = execution order",
        svg_name="ai-chatbot-integration.svg",
    )
    p.zones = [
        Zone("lane-user", 30, 125, 145, 900, "I", "USER", fill=bp_lane, stroke=bp_grid, rounded=False),
        Zone("lane-browser", 175, 125, 255, 900, "II", "BROWSER / SESSION", fill=bp_lane_alt, stroke=bp_grid, rounded=False),
        Zone("lane-pages", 430, 125, 245, 900, "III", "CONTENT DELIVERY", fill=bp_lane, stroke=bp_grid, rounded=False),
        Zone("lane-api", 675, 125, 380, 900, "IV", "API / ORCHESTRATION", fill=bp_lane_alt, stroke=bp_grid, rounded=False),
        Zone("lane-ai", 1055, 125, 250, 900, "V", "GENERATION", fill=bp_lane, stroke=bp_grid, rounded=False),
        Zone("lane-response", 1305, 125, 245, 900, "VI", "RESPONSE", fill=bp_lane_alt, stroke=bp_grid, rounded=False),
        Zone("lane-data", 1550, 125, 220, 900, "VII", "DATA / AUDIT", fill=bp_lane, stroke=bp_grid, rounded=False),
    ]

    p.nodes = [
        Node("sw-start", 55, 195, 95, 52, "開始", ["Open site"], bp_node, bp_line, "ellipse", 14, 10, stroke_width=1),
        Node("sw-session", 205, 185, 190, 82, "Session bootstrap", ["sessionStorage", "missing → randomUUID()"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-pages", 458, 185, 188, 82, "GitHub Pages", ["HTML / JS / CSS", "content.json"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-cache", 205, 320, 190, 90, "Browser context", ["session_id + history", "allDocsContent in memory"], bp_node, bp_line, "cylinder", 14, 10, stroke_width=1),
        Node("sw-schema", 1568, 190, 184, 132, "ChatLog schema", ["session_id · question", "answer · model", "latency_ms · status", "error · created_at", "expires_at · masked"], bp_note, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-iam", 1568, 360, 184, 95, "IAM boundary", ["Cloud Run service account", "roles/datastore.user", "Browser has no DB access"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-question", 45, 472, 115, 76, "輸入 Request", ["question", "Click Send"], bp_node, bp_line, "parallelogram", 14, 10, stroke_width=1),
        Node("sw-assemble", 205, 455, 190, 110, "Request assembly", ["session_id · history", "message · system rules", "+ full site context"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-post", 708, 452, 160, 92, "POST /api/chat", ["JSON over HTTPS", "exact-origin CORS", "public ingress"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-validate", 902, 445, 125, 105, "Request valid?", ["body / Pydantic", "rate limit"], bp_node, bp_line, "diamond", 13, 10, stroke_width=1),
        Node("sw-adapter", 758, 620, 220, 88, "Context / role adapter", ["map user / model roles", "append current message"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-sdk", 1086, 620, 188, 88, "google-genai SDK", ["GenerateContentConfig", "thinking_level = low"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-model", 1086, 772, 188, 95, "Gemini 3.5 Flash", ["generate_content", "text / exception"], bp_node, bp_line, "hexagon", 14, 10, stroke_width=1),
        Node("sw-result", 1350, 620, 145, 100, "Generation", ["success?", "latency_ms"], bp_node, bp_line, "diamond", 13, 10, stroke_width=1),
        Node("sw-envelope", 1328, 790, 190, 100, "Response envelope", ["answer / generic error", "status · Retry-After", "latency_ms"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-log", 1568, 640, 184, 88, "log_chat()", ["BackgroundTasks", "mask · try/except"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-db-decision", 1592, 785, 136, 95, "Firestore", ["write OK?"], bp_node, bp_line, "diamond", 13, 10, stroke_width=1),
        Node("sw-firestore", 1568, 925, 184, 78, "chat_logs", ["created_at + expires_at", "TTL · persistent Q&A"], bp_node, bp_line, "cylinder", 14, 10, stroke_width=1),
        Node("sw-render", 205, 800, 190, 95, "Render / persist UI", ["fixBrokenLinks", "marked.parse", "history → sessionStorage"], bp_node, bp_line, "rect", 14, 10, stroke_width=1),
        Node("sw-response", 45, 805, 115, 78, "輸出 Response", ["answer / error", "show in widget"], bp_node, bp_line, "parallelogram", 14, 10, stroke_width=1),
        Node("sw-end", 55, 940, 95, 52, "結束", ["Ready"], bp_node, bp_line, "ellipse", 14, 10, stroke_width=1),
    ]

    def flow(num: int, points: list[tuple[int, int]], label: str, *, color: str = COLORS["line"], dashed: bool = False, label_x: int | None = None, label_y: int | None = None):
        p.edges.append(Edge(f"sw-e{num}", points, label, color, dashed, 2, False, label_x, label_y))
        x, y = points[0]
        p.nodes.append(
            Node(
                f"sw-n{num}", x - 14, y - 14, 28, 28, str(num), [], bp_number, bp_number,
                "ellipse", 12, 10, title_color=COLORS["white"], body_color=COLORS["white"], stroke_width=1,
            )
        )

    flow(1, [(150, 221), (195, 221)], "", color=bp_line)
    flow(2, [(395, 221), (448, 221)], "", color=bp_line, dashed=True)
    flow(3, [(552, 267), (552, 300), (405, 300), (405, 365)], "content.json → memory", color=bp_line, dashed=True, label_x=470, label_y=292)
    flow(4, [(160, 510), (195, 510)], "", color=bp_line)
    flow(5, [(395, 510), (698, 510)], "{session_id, history, message, system_instruction}", color=bp_line, label_x=545, label_y=490)
    flow(6, [(868, 498), (892, 498)], "validate", color=bp_line)
    flow(7, [(965, 550), (965, 600), (868, 600), (868, 610)], "normal request", color=bp_line, label_x=925, label_y=590)
    flow(8, [(395, 365), (430, 365), (430, 665), (748, 665)], "history + full site context", color=bp_line, label_x=575, label_y=645)
    flow(9, [(978, 665), (1076, 665)], "contents + config", color=bp_line)
    flow(10, [(1180, 708), (1180, 762)], "generate_content", color=bp_line)
    flow(11, [(1274, 820), (1305, 820), (1305, 670), (1340, 670)], "text / exception", color=bp_line, dashed=True, label_x=1305, label_y=745)
    flow(12, [(1422, 720), (1422, 780)], "success / error", color=bp_line)
    flow(13, [(1328, 850), (1305, 850), (1305, 920), (410, 920), (410, 848), (405, 848)], "HTTP 200 answer / generic 4xx–5xx", color=bp_line, dashed=True, label_x=855, label_y=904)
    flow(14, [(1518, 820), (1540, 820), (1540, 684), (1558, 684)], "after response · background task", color=bp_line, dashed=True, label_x=1535, label_y=760)
    flow(15, [(1660, 728), (1660, 775)], "masked document", color=bp_line)
    flow(16, [(1660, 880), (1660, 915)], "Yes", color=bp_line)
    flow(17, [(1592, 833), (1540, 833), (1540, 905), (1518, 905), (1518, 880)], "No → Cloud Logging", color=COLORS["red"], dashed=True, label_x=1520, label_y=930)
    flow(18, [(195, 848), (170, 848)], "render", color=bp_line)
    flow(19, [(102, 883), (102, 930)], "ready", color=bp_line)

    p.edges.extend([
        Edge("sw-boundary", [(675, 175), (675, 1010)], "", COLORS["red"], True, 2),
        Edge("sw-iam-access", [(1660, 455), (1660, 630)], "service account / IAM", bp_line, True, 1, False, 1660, 560),
    ])

    p.texts.extend([
        Text("sw-lane-user", 52, 1000, "使用者", 12, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-browser", 197, 1000, "SESSION / HISTORY", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-content", 452, 1000, "STATIC CONTENT", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-api", 697, 1000, "STATELESS COMPUTE", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-ai", 1077, 1000, "MODEL API", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-response", 1327, 1000, "RESPONSE CONTRACT", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-lane-data", 1572, 1000, "PERSISTENT STORE", 11, COLORS["muted"], True, rotation=-90),
        Text("sw-boundary-label", 690, 285, "SERVER TRUST BOUNDARY", 10, COLORS["red"], True, rotation=90),
        Text("sw-legend-title", 45, 1075, "ARCHITECTURE LEGEND", 12, bp_line, True),
        Text("sw-legend", 220, 1075, "Oval: start/end  •  Parallelogram: I/O  •  Rectangle: process  •  Diamond: decision  •  Cylinder: state/store  •  Dashed: control/failure", 12, COLORS["muted"]),
        Text("sw-note-state", 45, 1112, "State ownership｜Browser: session_id + history   •   Cloud Run: stateless compute   •   Firestore: persistent anonymous Q&A records", 12, bp_line, True),
        Text("sw-note-sync", 1035, 1112, "Security｜Exact CORS allowlist + bounded input + per-instance rate limit; detailed exceptions stay in Cloud Logging.", 11, COLORS["red"], True),
    ])
    return p


def delivery_page() -> Page:
    p = Page(
        "delivery-pipelines",
        "03 Frontend & Backend Delivery Architecture",
        1800,
        1180,
        "Frontend & Backend Delivery Architecture",
        "同一個 repository、兩條獨立發布路徑｜Frontend + Backend path-triggered automation",
        svg_name="github-pages-deployment.svg",
    )
    p.zones = [
        Zone("front-zone", 45, 125, 1710, 430, "PIPELINE A — STATIC FRONTEND", "Current: GitHub Actions builds and deploys Pages after push main", fill="#EFF6FF", stroke="#93C5FD"),
        Zone("back-zone", 45, 590, 1710, 500, "PIPELINE B — CLOUD RUN BACKEND", "Current: GitHub Actions on push main when backend/** changes", fill="#F0FDF4", stroke="#86EFAC"),
    ]
    p.nodes = [
        Node("f-edit", 85, 220, 220, 105, "Source content", ["docs/**/*.md", "mkdocs.yml · assets"], COLORS["blue_fill"], COLORS["blue"]),
        Node("f-local", 360, 220, 240, 105, "GitHub main", ["commit + push", "source of truth"], COLORS["purple_fill"], COLORS["purple"]),
        Node("f-hook", 655, 205, 250, 135, "Pages build job", ["uv sync --locked", "MkDocs + post-build hook", "generate site/content.json"], COLORS["purple_fill"], COLORS["purple"]),
        Node("f-artifact", 960, 220, 220, 105, "Pages artifact", ["deployable static bundle", "HTML / CSS / JS / JSON"], COLORS["purple_fill"], COLORS["purple"], "cylinder"),
        Node("f-pages", 1235, 220, 220, 105, "GitHub Pages", ["static hosting / CDN", "TLS + public URL"], COLORS["purple_fill"], COLORS["purple"]),
        Node("f-user", 1510, 220, 200, 105, "Browser clients", ["GET static files", "cacheable delivery"], COLORS["blue_fill"], COLORS["blue"]),
        Node("b-edit", 85, 720, 220, 105, "Backend source", ["backend/**", "Dockerfile · Python"], COLORS["blue_fill"], COLORS["blue"]),
        Node("b-main", 360, 720, 220, 105, "GitHub main", ["commit + push", "source of truth"], COLORS["purple_fill"], COLORS["purple"], "cylinder"),
        Node("b-trigger", 635, 695, 250, 155, "GitHub Actions", ["paths filter: backend/**", "checkout", "google-github-actions/auth", "setup-gcloud"], COLORS["purple_fill"], COLORS["purple"]),
        Node("b-secrets", 635, 905, 250, 120, "GitHub configuration", ["Variables: project + WIF + SAs", "Secret: GEMINI_API_KEY", "no JSON deploy key"], COLORS["red_fill"], COLORS["red"], "cylinder", 15, 11),
        Node("b-build", 940, 720, 220, 105, "Cloud Build", ["gcloud run deploy", "--source backend"], COLORS["green_fill"], COLORS["green"]),
        Node("b-reg", 1215, 720, 220, 105, "Artifact Registry", ["container image", "managed build artifact"], COLORS["green_fill"], COLORS["green"], "cylinder"),
        Node("b-run", 1490, 695, 220, 155, "Cloud Run revision", ["asia-east1 · public /api/chat", "SA: dcka-chatbot-runtime", "env: GEMINI_API_KEY", "automatic traffic switch"], COLORS["green_fill"], COLORS["green"]),
        Node("b-firestore", 1490, 915, 220, 110, "Cloud Firestore", ["Native mode · chat_logs", "runtime IAM: datastore.user", "TTL ACTIVE · 90 days"], "#FCE7F3", "#DB2777", "cylinder", 16, 12),
    ]
    p.edges = [
        Edge("fe1", [(305, 272), (350, 272)], "author"),
        Edge("fe2", [(600, 272), (645, 272)], "trigger deploy-pages.yml", dashed=True),
        Edge("fe3", [(905, 272), (950, 272)], "upload-pages-artifact", dashed=True),
        Edge("fe4", [(1180, 272), (1225, 272)], "deploy-pages", dashed=True),
        Edge("fe5", [(1455, 272), (1500, 272)], "HTTPS GET"),
        Edge("be1", [(305, 772), (350, 772)], "git push"),
        Edge("be2", [(580, 772), (625, 772)], "trigger on path", dashed=True),
        Edge("be3", [(885, 772), (930, 772)], "OIDC / WIF → deploy", dashed=True),
        Edge("be4", [(1160, 772), (1205, 772)], "push image", dashed=True),
        Edge("be5", [(1435, 772), (1480, 772)], "new revision", dashed=True),
        Edge("be-secret-action", [(760, 905), (760, 860)], "variables + secret", COLORS["red"], True),
        Edge("be-secret-run", [(885, 965), (1455, 965), (1455, 825), (1480, 825)], "inject runtime env", COLORS["red"], True, label_x=1210, label_y=940),
        Edge("be-run-firestore", [(1600, 850), (1600, 905)], "runtime IAM", "#DB2777", True),
    ]
    p.texts = [
        Text("front-note", 85, 390, "Artifact contract: HTML/CSS/JS/images + content.json are immutable static outputs deployed by GitHub Pages Actions.", 13),
        Text("front-future", 85, 430, "Repository setting confirmed: Settings → Pages → Source = GitHub Actions.", 13, COLORS["green"], True),
        Text("back-note", 940, 1040, "Cloud Build / Artifact Registry are deployment services; Firestore is a separately provisioned runtime dependency.", 13),
        Text("back-security", 940, 1070, "Deploy auth: GitHub OIDC → WIF → github-actions-deployer; short-lived credentials, no Service Account JSON key.", 13, COLORS["green"], True),
    ]
    return p


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    pages = [system_page(), runtime_page(), delivery_page()]
    write_drawio(pages)
    for page in pages:
        write_svg(page)
    print(DRAWIO_OUT)
    for page in pages:
        print(IMAGE_DIR / page.svg_name)


if __name__ == "__main__":
    main()
