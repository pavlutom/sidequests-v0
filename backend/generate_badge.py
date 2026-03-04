import coverage
import sys

def get_color(pct):
    if pct >= 90: return "#4c1"
    if pct >= 80: return "#97ca00"
    if pct >= 70: return "#a4a61d"
    if pct >= 60: return "#dfb317"
    if pct >= 50: return "#fe7d37"
    return "#e05d44"

def generate_svg(pct):
    color = get_color(pct)
    # Simple, standard shields.io style SVG
    template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="104" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h61v20H0z"/>
    <path fill="{color}" d="M61 0h43v20H61z"/>
    <path fill="url(#b)" d="M0 0h104v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="30.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
    <text x="30.5" y="14">coverage</text>
    <text x="81.5" y="15" fill="#010101" fill-opacity=".3">{pct}%</text>
    <text x="81.5" y="14">{pct}%</text>
  </g>
</svg>"""
    return template

if __name__ == "__main__":
    cov = coverage.Coverage()
    cov.load()
    pct = int(cov.report(file=open('/dev/null', 'w')))
    
    svg = generate_svg(pct)
    with open("coverage.svg", "w") as f:
        f.write(svg)
    print(f"Generated coverage badge for {pct}%")
