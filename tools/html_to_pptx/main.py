from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None,''):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from html_to_pptx.parser import parse_slide_html
    from html_to_pptx.ppt_builder import build_pptx
else:
    from .parser import parse_slide_html
    from .ppt_builder import build_pptx

def discover_html_files(root: Path):
    return sorted([p for p in root.glob('*.html') if p.name!='index.html'])

def main():
    root=Path(__file__).resolve().parents[2]
    files=discover_html_files(root)
    slides=[parse_slide_html(p) for p in files]
    out=root/'output'/'output.pptx'
    build_pptx(slides,out)
    print(f'Generated {out} with {len(slides)} slides')

if __name__=='__main__':
    main()
