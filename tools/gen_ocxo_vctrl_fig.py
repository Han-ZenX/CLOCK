#!/usr/bin/env python3
"""把 figures.py 里的 ocxo_vctrl 插图单独导出为 SVG 与 PDF。

用法: python gen_ocxo_vctrl_fig.py
输出: docs/hardware/ocxo-vctrl-trimpot-fig.svg / .pdf

文档内引用该图请用 md2pdf.py 的 `@fig:ocxo_vctrl 图题` 语法，本脚本只用于
需要单独一张矢量图的场合（例如贴进 KiCad 图框或邮件里）。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.graphics import renderPDF, renderSVG
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import figures
import md2pdf


def main():
    reg, bold = md2pdf.ensure_fonts()
    pdfmetrics.registerFont(TTFont(figures.FONT, reg))
    pdfmetrics.registerFont(TTFont(figures.BOLD, bold))

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, 'docs', 'hardware', 'ocxo-vctrl-trimpot-fig')
    d = figures.ocxo_vctrl()
    renderSVG.drawToFile(d, out + '.svg')
    renderPDF.drawToFile(d, out + '.pdf')
    print('[DONE] %s.svg / .pdf' % out)


if __name__ == '__main__':
    main()
