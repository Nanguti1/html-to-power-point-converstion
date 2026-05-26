from __future__ import annotations
import re
from typing import Dict, Optional
from pptx.dml.color import RGBColor
PX_PER_INCH = 96.0

def px_to_inches(px_value: float) -> float:
    return px_value / PX_PER_INCH

def parse_px(style_value: Optional[str]) -> Optional[float]:
    if not style_value:
        return None
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)px\s*", style_value)
    return float(m.group(1)) if m else None

def parse_style_attribute(style_attr: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in style_attr.split(';'):
        if ':' in part:
            k,v = part.split(':',1)
            out[k.strip().lower()] = v.strip()
    return out

def parse_hex_color(value: Optional[str]) -> Optional[RGBColor]:
    if not value:
        return None
    s = value.strip().lstrip('#')
    if len(s)==3:
        s=''.join(c*2 for c in s)
    if len(s)!=6:
        return None
    return RGBColor.from_string(s.upper())

def parse_numeric_weight(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    v = value.strip().lower()
    if v == 'bold': return 700
    if v == 'normal': return 400
    try:
        return int(float(v))
    except ValueError:
        return None

def parse_js_array_literal(script_text: str, var_name: str) -> Optional[str]:
    m = re.search(rf"const\s+{re.escape(var_name)}\s*=\s*(\[[\s\S]*?\]);", script_text)
    return m.group(1) if m else None

def parse_chart_type(script_text: str) -> str:
    m = re.search(r"type\s*:\s*['\"]([a-zA-Z]+)['\"]", script_text)
    return m.group(1).lower() if m else 'bar'

def parse_index_axis(script_text: str) -> Optional[str]:
    m = re.search(r"indexAxis\s*:\s*['\"]([xy])['\"]", script_text)
    return m.group(1).lower() if m else None
