"""
Utilidades para generar reportes HTML (tablas + diagramas SVG) a partir de
los resultados de des.py, en lugar de imprimir todo por consola.

No depende de librerias externas (solo la libreria estandar de Python), por
lo que el HTML generado es un archivo autocontenido que se abre en cualquier
navegador.
"""

CSS = """
:root {
    --bg: #0f1420;
    --panel: #161d2e;
    --border: #2a3450;
    --text: #e7ebf3;
    --muted: #9aa5bd;
    --accent: #5fb3ff;
    --accent2: #7ee0a8;
    --accent3: #ffb454;
    --mono-bg: #0b101c;
}
@media (prefers-color-scheme: light) {
    :root {
        --bg: #f4f6fb;
        --panel: #ffffff;
        --border: #dbe1ee;
        --text: #1b2230;
        --muted: #566079;
        --accent: #1266d1;
        --accent2: #1a8a53;
        --accent3: #b56a00;
        --mono-bg: #eef1f7;
    }
}
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 2rem 1.2rem 4rem;
    background: var(--bg);
    color: var(--text);
    font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.5;
}
.wrap { max-width: 980px; margin: 0 auto; }
h1 {
    font-size: 1.6rem;
    margin-bottom: .1rem;
}
h2 {
    font-size: 1.15rem;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: .4rem;
    margin-top: 2.4rem;
}
.subtitle { color: var(--muted); margin-top: 0; margin-bottom: 2rem; }
.card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
}
.mono {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background: var(--mono-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: .55rem .7rem;
    word-break: break-all;
    font-size: .82rem;
    display: block;
    margin: .3rem 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    font-size: .85rem;
    margin: .6rem 0 1.2rem;
    overflow-x: auto;
    display: block;
}
thead { display: table-header-group; }
tbody { display: table-row-group; }
tr { display: table-row; }
th, td { display: table-cell; }
th, td {
    border: 1px solid var(--border);
    padding: .45rem .6rem;
    text-align: left;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    white-space: nowrap;
}
th { background: var(--mono-bg); color: var(--muted); font-family: inherit; }
tr:nth-child(even) td { background: rgba(127,127,127,.06); }
.badge {
    display: inline-block;
    padding: .15rem .55rem;
    border-radius: 999px;
    font-size: .75rem;
    font-weight: 600;
}
.badge.ok { background: rgba(126,224,168,.18); color: var(--accent2); }
.grid8 {
    border-collapse: collapse;
    margin: .6rem 0;
    width: auto;
}
.grid8 td {
    width: 34px; height: 34px;
    text-align: center;
    font-weight: 700;
    font-family: "SFMono-Regular", Consolas, monospace;
    background: var(--mono-bg);
    white-space: normal;
}
.flow { display: flex; align-items: center; flex-wrap: wrap; gap: .4rem; margin: 1rem 0; }
.flow .box {
    background: var(--mono-bg);
    border: 1px solid var(--accent);
    color: var(--accent);
    border-radius: 8px;
    padding: .5rem .8rem;
    font-family: monospace;
    font-size: .85rem;
    text-align: center;
}
.flow .op {
    color: var(--muted);
    font-size: 1.1rem;
}
.section-note { color: var(--muted); font-size: .88rem; }
svg { max-width: 100%; height: auto; display: block; margin: .6rem auto; }
.toc { color: var(--muted); font-size: .9rem; }
.toc a { color: var(--accent); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
footer { color: var(--muted); font-size: .8rem; margin-top: 3rem; text-align: center; }
"""


def page(title, subtitle, sections):
    body = "\n".join(sections)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<h1>{title}</h1>
<p class="subtitle">{subtitle}</p>
{body}
<footer>Generado automaticamente por el script de Python de la actividad DES / Triple DES.</footer>
</div>
</body>
</html>"""


def section(titulo, contenido_html, nota=""):
    nota_html = f'<p class="section-note">{nota}</p>' if nota else ""
    return f'<h2>{titulo}</h2>\n{nota_html}\n{contenido_html}'


def card(html_inner):
    return f'<div class="card">{html_inner}</div>'


def mono(texto):
    return f'<span class="mono">{texto}</span>'


def bit_grid(bits, cols=8):
    """Dibuja una cadena de bits como una cuadrilla (igual que las matrices del PDF)."""
    rows_html = []
    for i in range(0, len(bits), cols):
        fila = bits[i:i + cols]
        celdas = "".join(f"<td>{b}</td>" for b in fila)
        rows_html.append(f"<tr>{celdas}</tr>")
    return f'<table class="grid8">{"".join(rows_html)}</table>'


def table(headers, rows):
    thead = "".join(f"<th>{h}</th>" for h in headers)
    tbody = ""
    for r in rows:
        celdas = "".join(f"<td>{c}</td>" for c in r)
        tbody += f"<tr>{celdas}</tr>"
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>"


def flow(items):
    """items: lista de strings; se dibujan como cajas conectadas por flechas ->"""
    partes = []
    for i, it in enumerate(items):
        if i > 0:
            partes.append('<span class="op">&#8594;</span>')
        partes.append(f'<div class="box">{it}</div>')
    return f'<div class="flow">{"".join(partes)}</div>'


def badge_ok(texto_si_ok, ok):
    clase = "ok" if ok else ""
    return f'<span class="badge {clase}">{texto_si_ok}</span>'


# ---------------------------------------------------------------------------
# Diagrama SVG: una ronda del esquema Feistel de DES
# ---------------------------------------------------------------------------

def svg_feistel_round():
    return """
<svg viewBox="0 0 640 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Esquema de una ronda Feistel">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
    </marker>
  </defs>
  <g fill="none" stroke="currentColor" stroke-width="1.6" font-family="monospace" font-size="14">
    <text x="130" y="24" text-anchor="middle" fill="currentColor" stroke="none">L(i-1)</text>
    <text x="440" y="24" text-anchor="middle" fill="currentColor" stroke="none">R(i-1)</text>

    <line x1="130" y1="34" x2="130" y2="250" marker-end="url(#arrow)"/>
    <line x1="440" y1="34" x2="440" y2="90" marker-end="url(#arrow)"/>
    <line x1="440" y1="34" x2="440" y2="270" marker-end="url(#arrow)"/>

    <line x1="440" y1="90" x2="470" y2="90"/>
    <rect x="380" y="70" width="120" height="45" rx="6"/>
    <text x="440" y="98" text-anchor="middle" fill="currentColor" stroke="none">f (R, Ki)</text>
    <line x1="440" y1="115" x2="440" y2="150"/>

    <line x1="500" y1="92" x2="560" y2="92" marker-end="url(#arrow)"/>
    <text x="580" y="96" text-anchor="middle" fill="currentColor" stroke="none">Ki</text>

    <circle cx="240" cy="150" r="18"/>
    <text x="240" y="156" text-anchor="middle" fill="currentColor" stroke="none">XOR</text>
    <line x1="148" y1="150" x2="222" y2="150" marker-end="url(#arrow)"/>
    <line x1="410" y1="150" x2="258" y2="150" marker-end="url(#arrow)"/>

    <line x1="240" y1="168" x2="240" y2="270" marker-end="url(#arrow)"/>

    <text x="130" y="290" text-anchor="middle" fill="currentColor" stroke="none">L(i) = R(i-1)</text>
    <text x="240" y="310" text-anchor="middle" fill="currentColor" stroke="none">R(i) = L(i-1) XOR f(R(i-1),Ki)</text>
  </g>
</svg>
"""


# ---------------------------------------------------------------------------
# Diagrama SVG: esquema 3DES EDE (cifrado y descifrado)
# ---------------------------------------------------------------------------

def svg_3des_scheme(k1_hex, k2_hex, k3_hex):
    return f"""
<svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Esquema 3DES EDE">
  <defs>
    <marker id="arrow2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
    </marker>
  </defs>
  <g font-family="monospace" font-size="13">
    <text x="10" y="55" fill="currentColor">M</text>
    <line x1="30" y1="50" x2="70" y2="50" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="75" y="25" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="145" y="45" text-anchor="middle" fill="currentColor">E ( K1 )</text>
    <text x="145" y="16" text-anchor="middle" fill="currentColor" font-size="11">K1={k1_hex}</text>
    <line x1="215" y1="50" x2="255" y2="50" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="260" y="25" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="330" y="45" text-anchor="middle" fill="currentColor">D ( K2 )</text>
    <text x="330" y="16" text-anchor="middle" fill="currentColor" font-size="11">K2={k2_hex}</text>
    <line x1="400" y1="50" x2="440" y2="50" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="445" y="25" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="515" y="45" text-anchor="middle" fill="currentColor">E ( K3 )</text>
    <text x="515" y="16" text-anchor="middle" fill="currentColor" font-size="11">K3={k3_hex}</text>
    <line x1="585" y1="50" x2="625" y2="50" stroke="currentColor" marker-end="url(#arrow2)"/>
    <text x="650" y="55" fill="currentColor">C  (cifrado)</text>

    <text x="10" y="175" fill="currentColor">C</text>
    <line x1="30" y1="170" x2="70" y2="170" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="75" y="145" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="145" y="165" text-anchor="middle" fill="currentColor">D ( K3 )</text>
    <line x1="215" y1="170" x2="255" y2="170" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="260" y="145" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="330" y="165" text-anchor="middle" fill="currentColor">E ( K2 )</text>
    <line x1="400" y1="170" x2="440" y2="170" stroke="currentColor" marker-end="url(#arrow2)"/>

    <rect x="445" y="145" width="140" height="50" rx="8" fill="none" stroke="currentColor"/>
    <text x="515" y="165" text-anchor="middle" fill="currentColor">D ( K1 )</text>
    <line x1="585" y1="170" x2="625" y2="170" stroke="currentColor" marker-end="url(#arrow2)"/>
    <text x="650" y="175" fill="currentColor">M  (recuperado)</text>

    <text x="75" y="230" fill="currentColor" font-size="12">Cifrado:    C = E(K3, D(K2, E(K1, M)))</text>
    <text x="75" y="250" fill="currentColor" font-size="12">Descifrado: M = D(K1, E(K2, D(K3, C)))</text>
  </g>
</svg>
"""


def write(path, html):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
