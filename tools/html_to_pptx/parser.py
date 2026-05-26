from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from bs4 import BeautifulSoup
from .chart_extractor import ChartInfo, extract_chart_info
from .utils import parse_numeric_weight, parse_px, parse_style_attribute

@dataclass
class TextBoxObject:
    left_px: float; top_px: float; width_px: float; height_px: float
    text: str; font_size_px: Optional[float]; font_weight: Optional[int]; text_align: Optional[str]; color: Optional[str]

@dataclass
class ChartObject:
    left_px: float; top_px: float; width_px: float; height_px: float; chart_info: ChartInfo

@dataclass
class SlideSpec:
    source_file: Path; textboxes: List[TextBoxObject]; chart: ChartObject

def parse_slide_html(path: Path) -> SlideSpec:
    html = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'lxml')
    textboxes=[]; chart_obj=None
    for obj in soup.find_all(attrs={'data-object':'true'}):
        typ=(obj.get('data-object-type') or '').strip().lower()
        st=parse_style_attribute(obj.get('style',''))
        left=parse_px(st.get('left')) or 0.0; top=parse_px(st.get('top')) or 0.0
        width=parse_px(st.get('width')) or 100.0; height=parse_px(st.get('height')) or 50.0
        if typ=='textbox':
            textboxes.append(TextBoxObject(left,top,width,height,' '.join(obj.stripped_strings),parse_px(st.get('font-size')),parse_numeric_weight(st.get('font-weight')),st.get('text-align'),st.get('color')))
        elif typ=='chart':
            chart_obj=ChartObject(left,top,width,height,extract_chart_info(html))
    if not chart_obj:
        raise ValueError(f'No chart in {path}')
    return SlideSpec(path,textboxes,chart_obj)
