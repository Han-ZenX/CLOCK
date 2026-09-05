#!/usr/bin/env python3
"""
md2pdf.py 的配套绘图模块：为硬件文档生成矢量示意图。

在 Markdown 中用 `@fig:名称 图题` 单独一行引用，例如:
    @fig:stackup 图 2　四层板叠层剖面（1.6 mm）

纯 reportlab.graphics 矢量绘制，不依赖外部图片文件。
"""

from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

W = 170 * mm  # 与正文同宽

FONT, BOLD = 'NotoSC', 'NotoSC-Bold'
ACCENT = colors.HexColor('#1a5f9c')
DARK = colors.HexColor('#1a1a1a')
GREY = colors.HexColor('#666666')
COPPER = colors.HexColor('#c8801f')
DIEL = colors.HexColor('#d9e6c9')
CORE_C = colors.HexColor('#c3d6ae')
MASK = colors.HexColor('#2f7a4f')
RED = colors.HexColor('#c0392b')
AMBER = colors.HexColor('#d68910')
GREEN = colors.HexColor('#1e8449')

CAP = ParagraphStyle('cap', fontName=FONT, fontSize=8.5, leading=12.5,
                     textColor=GREY, alignment=1, spaceBefore=3, spaceAfter=10)


def _txt(d, x, y, s, size=8, font=FONT, fill=DARK, anchor='start'):
    d.add(String(x, y, s, fontName=font, fontSize=size,
                 fillColor=fill, textAnchor=anchor))


def _box(d, x, y, w, h, fill, stroke=None, sw=0.6, r=None):
    kw = dict(fillColor=fill, strokeColor=stroke or colors.HexColor('#94a7b8'),
              strokeWidth=sw)
    if r:
        kw['rx'] = kw['ry'] = r
    d.add(Rect(x, y, w, h, **kw))


def _arrow(d, x1, y1, x2, y2, color=ACCENT, sw=1.0, head=4):
    """带箭头的直线（仅支持水平/垂直方向的箭头）。"""
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=sw))
    if abs(x2 - x1) < 0.01:                       # 垂直
        s = -head if y2 < y1 else head
        d.add(Polygon([x2, y2, x2 - head * 0.6, y2 - s, x2 + head * 0.6, y2 - s],
                      fillColor=color, strokeColor=color))
    else:                                          # 水平
        s = -head if x2 < x1 else head
        d.add(Polygon([x2, y2, x2 - s, y2 - head * 0.6, x2 - s, y2 + head * 0.6],
                      fillColor=color, strokeColor=color))


# ---------------------------------------------------------------- 图：流程总览

def flow():
    """十阶段流程总览，边框颜色表示返工代价。"""
    d = Drawing(W, 268)
    stages = [
        ('一', '开工前决策', '层数 / 板厂 / 板框', RED),
        ('二', '原理图收尾', '批注 / 封装 / ERC', AMBER),
        ('三', '电路板配置', '叠层 / 规则 / 网络类', RED),
        ('四', '更新 PCB', '从原理图导入', GREEN),
        ('五', '板框与结构', 'Edge.Cuts / 安装孔', AMBER),
        ('六', '布局', '摆放 / 分区 / 锁定', RED),
        ('七', '布线', '优先级 / 阻抗 / 等长', AMBER),
        ('八', '铺铜与回流', '平面 / 缝合过孔', GREEN),
        ('九', '检查', 'DRC / 目视 / 3D', ACCENT),
        ('十', '制造输出', 'Gerber / 钻孔 / BOM', GREEN),
    ]
    bw, bh, gx, gy = 218, 38, 24, 8
    x0, y0 = 4, 268 - bh - 16
    for i, (num, name, sub, col) in enumerate(stages):
        cx = x0 + (i % 2) * (bw + gx)
        cy = y0 - (i // 2) * (bh + gy)
        _box(d, cx, cy, bw, bh, colors.white, col, 1.1, r=4)
        d.add(Rect(cx, cy, 4, bh, fillColor=col, strokeColor=col))
        _txt(d, cx + 12, cy + bh - 15, '阶段' + num, 8.5, BOLD, col)
        _txt(d, cx + 52, cy + bh - 15, name, 9.5, BOLD, DARK)
        _txt(d, cx + 12, cy + 8, sub, 7.5, FONT, GREY)
        if i % 2 == 0:                              # 左 -> 右
            _arrow(d, cx + bw + 3, cy + bh / 2, cx + bw + gx - 3, cy + bh / 2, GREY, .8)
        elif i < len(stages) - 1:                   # 右 -> 下一行左
            _arrow(d, cx + bw / 2, cy - 1, cx + bw / 2, cy - gy + 1, GREY, .8)

    ly = 12
    _txt(d, 4, ly, '返工代价：', 8, BOLD, DARK)
    for i, (c, t) in enumerate(((RED, '极高 / 高'), (AMBER, '高 / 中'),
                                (GREEN, '低'), (ACCENT, '检查环节'))):
        bx = 52 + i * 96
        d.add(Rect(bx, ly - 1, 16, 7, fillColor=colors.white, strokeColor=c, strokeWidth=1.1))
        _txt(d, bx + 21, ly, t, 8, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：叠层剖面

def stackup():
    """四层板 1.6 mm 叠层剖面（嘉立创 JLC04161H-7628）。"""
    d = Drawing(W, 232)
    layers = [
        ('阻焊 / Solder Mask', '0.01 mm', MASK, 7, ''),
        ('F.Cu  (1 oz)', '0.035 mm', COPPER, 11, '信号层：射频、差分时钟'),
        ('Prepreg 7628', '0.2104 mm', DIEL, 26, 'Dk 4.4　← 决定 F.Cu 阻抗'),
        ('In1.Cu  (0.5 oz)', '0.0152 mm', COPPER, 9, 'GND 完整平面（不可分割）'),
        ('Core', '1.065 mm', CORE_C, 52, 'Dk 4.2'),
        ('In2.Cu  (0.5 oz)', '0.0152 mm', COPPER, 9, 'PWR 电源平面'),
        ('Prepreg 7628', '0.2104 mm', DIEL, 26, 'Dk 4.4'),
        ('B.Cu  (1 oz)', '0.035 mm', COPPER, 11, '次信号层'),
        ('阻焊 / Solder Mask', '0.01 mm', MASK, 7, ''),
    ]
    lx, lw = 92, 210
    y = 232 - 26
    for name, th, col, h, note in layers:
        y -= h
        _box(d, lx, y, lw, h, col, colors.HexColor('#7d8f9e'), 0.5)
        _txt(d, lx - 6, y + h / 2 - 3, name, 7.5, FONT, DARK, 'end')
        _txt(d, lx + lw + 8, y + h / 2 - 3, th, 7.5, BOLD, ACCENT)
        if note:
            _txt(d, lx + lw + 62, y + h / 2 - 3, note, 7.5, FONT, GREY)

    top, bot = 232 - 26, y
    d.add(Line(lx - 76, top, lx - 76, bot, strokeColor=ACCENT, strokeWidth=0.8))
    for yy in (top, bot):
        d.add(Line(lx - 80, yy, lx - 72, yy, strokeColor=ACCENT, strokeWidth=0.8))
    _txt(d, lx - 84, (top + bot) / 2 - 3, '1.6 mm', 8, BOLD, ACCENT, 'end')

    # 高亮 F.Cu 与 In1.Cu 之间的关键间距
    ky1 = top - 7 - 11
    ky2 = ky1 - 26
    d.add(Line(lx + lw + 168, ky1, lx + lw + 168, ky2, strokeColor=RED, strokeWidth=0.9))
    for yy in (ky1, ky2):
        d.add(Line(lx + lw + 164, yy, lx + lw + 172, yy, strokeColor=RED, strokeWidth=0.9))
    _txt(d, lx + lw + 176, (ky1 + ky2) / 2 - 3, 'H', 8.5, BOLD, RED)

    _txt(d, 4, 8, '计算阻抗时 H 填这一段（0.2104 mm），不是板厚 1.6 mm', 8, BOLD, RED)
    return d


# ---------------------------------------------------------------- 图：微带线截面

def microstrip():
    """微带线截面与计算器参数对应关系。"""
    d = Drawing(W, 165)
    bx, bw2, by = 60, 300, 46
    d.add(Rect(bx, by, bw2, 42, fillColor=DIEL, strokeColor=colors.HexColor('#7d8f9e')))
    d.add(Rect(bx, by - 10, bw2, 10, fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e')))
    tw, tx = 54, bx + 120
    d.add(Rect(tx, by + 42, tw, 11, fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e')))

    _txt(d, bx - 6, by - 8, 'In1.Cu', 8, BOLD, DARK, 'end')
    _txt(d, bx - 6, by + 18, 'Prepreg', 8, FONT, DARK, 'end')
    _txt(d, bx + bw2 + 8, by - 8, '参考平面（完整 GND）', 8, FONT, GREY)
    _txt(d, tx + tw + 10, by + 57, '走线 (F.Cu)', 8, FONT, GREY)

    # W 标注
    d.add(Line(tx, by + 68, tx + tw, by + 68, strokeColor=ACCENT, strokeWidth=0.9))
    for xx in (tx, tx + tw):
        d.add(Line(xx, by + 64, xx, by + 72, strokeColor=ACCENT, strokeWidth=0.9))
    _txt(d, tx + tw / 2, by + 74, 'W 线宽', 8.5, BOLD, ACCENT, 'middle')
    # H 标注
    hx = bx + 40
    d.add(Line(hx, by, hx, by + 42, strokeColor=RED, strokeWidth=0.9))
    for yy in (by, by + 42):
        d.add(Line(hx - 4, yy, hx + 4, yy, strokeColor=RED, strokeWidth=0.9))
    _txt(d, hx + 8, by + 18, 'H 介质厚度', 8.5, BOLD, RED)
    # T 标注
    d.add(Line(tx + tw + 4, by + 42, tx + tw + 4, by + 53, strokeColor=GREEN, strokeWidth=0.9))
    _txt(d, tx + tw + 8, by + 44, 'T 铜厚', 8, BOLD, GREEN)

    _txt(d, 4, 22, 'KiCad 计算器对应：εr = 介质 Dk　|　H = 介质厚度（非板厚）　|　'
                   'T = 铜厚　|　W = 合成结果', 8, FONT, DARK)
    _txt(d, 4, 8, 'H(top) 保持 1e+20，表示走线上方为空气、无金属盖板', 8, FONT, GREY)
    return d


# ---------------------------------------------------------------- 图：布线优先级

def priority():
    """布线优先级阶梯。"""
    d = Drawing(W, 248)
    items = [
        ('1', '去耦电容 → 电源/地引脚', '环路面积最小'),
        ('2', '晶振、时钟源', '最短最直，远离干扰'),
        ('3', '阻抗控制线：射频、差分时钟', '线宽固定，无腾挪余地'),
        ('4', '其他差分对：以太网、USB', '需成对等距'),
        ('5', '敏感模拟信号', '远离数字与开关电源'),
        ('6', '高速数字总线', '需等长、成组'),
        ('7', '普通数字 I/O、LED、按键', '最灵活，随便绕'),
        ('8', '电源走线', '加宽即可，最后填空隙'),
    ]
    bh, gy = 20, 3.5
    y = 248 - 26
    for i, (n, name, why) in enumerate(items):
        y -= bh
        ratio = 1 - i * 0.055
        bw2 = 300 * ratio
        col = RED if i < 4 else (AMBER if i < 6 else GREEN)
        _box(d, 40, y, bw2, bh, colors.white, col, 1.0, r=3)
        d.add(Rect(40, y, 3.5, bh, fillColor=col, strokeColor=col))
        _txt(d, 22, y + 6, n, 10, BOLD, col, 'middle')
        _txt(d, 50, y + 6, name, 8.5, FONT, DARK)
        _txt(d, 352, y + 6, why, 7.5, FONT, GREY)
        y -= gy

    _arrow(d, 12, 248 - 30, 12, y + 14, ACCENT, 1.0)
    _txt(d, 4, 248 - 18, '先', 8, BOLD, ACCENT)
    _txt(d, 4, y + 4, '后', 8, BOLD, ACCENT)
    _txt(d, 40, 8, '越敏感、越难改的越先走；LED 按键这类线多晚布都能绕过去', 8, BOLD, DARK)
    return d


# ---------------------------------------------------------------- 图：回流路径

def refplane():
    """参考平面完整 vs 被割断时的回流路径对比。"""
    d = Drawing(W, 175)
    pw, ph = 218, 88
    for k, (px, title, ok) in enumerate((
            (6, '完整参考平面', True),
            (6 + pw + 24, '平面被走线割断', False))):
        py = 58
        _box(d, px, py, pw, ph, colors.HexColor('#f4f7fa'),
             GREEN if ok else RED, 1.1, r=3)
        # 信号走线（上方）
        sy = py + ph - 22
        d.add(Line(px + 20, sy, px + pw - 20, sy, strokeColor=COPPER, strokeWidth=2.4))
        _txt(d, px + 20, sy + 7, '信号走线 (F.Cu)', 7.5, FONT, GREY)
        # 参考平面（下方）
        gy2 = py + 26
        if ok:
            d.add(Rect(px + 14, gy2, pw - 28, 9, fillColor=COPPER,
                       strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
        else:
            gap = 34
            midx = px + pw / 2
            d.add(Rect(px + 14, gy2, midx - gap / 2 - (px + 14), 9, fillColor=COPPER,
                       strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
            d.add(Rect(midx + gap / 2, gy2, (px + pw - 14) - (midx + gap / 2), 9,
                       fillColor=COPPER, strokeColor=colors.HexColor('#7d8f9e'), strokeWidth=0.4))
            _txt(d, midx, gy2 - 12, '割缝', 7.5, BOLD, RED, 'middle')
        _txt(d, px + 14, gy2 + 14, 'In1.Cu (GND)', 7.5, FONT, GREY)

        # 回流路径
        if ok:
            d.add(PolyLine([px + 60, sy - 4, px + 60, gy2 + 13,
                            px + pw - 60, gy2 + 13, px + pw - 60, sy - 4],
                           strokeColor=GREEN, strokeWidth=1.3,
                           strokeDashArray=[3, 2]))
            _txt(d, px + pw / 2, gy2 + 18, '回流路径短', 7.5, BOLD, GREEN, 'middle')
        else:
            midx = px + pw / 2
            d.add(PolyLine([px + 60, sy - 4, px + 60, gy2 + 13, midx - 20, gy2 + 13,
                            midx - 20, py + 8, midx + 20, py + 8,
                            midx + 20, gy2 + 13, px + pw - 60, gy2 + 13,
                            px + pw - 60, sy - 4],
                           strokeColor=RED, strokeWidth=1.3, strokeDashArray=[3, 2]))
            _txt(d, midx, py + 1, '回流被迫绕行 → 阻抗突变、辐射、串扰', 7.5, BOLD, RED, 'middle')

        _txt(d, px + pw / 2, py + ph + 8, title, 9, BOLD,
             GREEN if ok else RED, 'middle')

    _txt(d, 6, 30, '高频回流电流总是走信号线正下方的最短路径。参考平面上任何割缝都会迫使回流绕行，',
         8, FONT, DARK)
    _txt(d, 6, 17, '同时破坏阻抗连续性并显著增加辐射。这是 In1.Cu 不允许走线的根本原因。',
         8, FONT, DARK)
    return d


# ---------------------------------------------------------------- 图：布局分区

def layout():
    """CORE 底板的布局分区示意。"""
    d = Drawing(W, 215)
    bx, by, bw2, bh2 = 30, 34, 420, 160
    _box(d, bx, by, bw2, bh2, colors.white, DARK, 1.2, r=3)
    _txt(d, bx, by + bh2 + 8, '板框 (Edge.Cuts)', 8, FONT, GREY)

    zones = [
        (bx + 8, by + 8, 130, 144, '#fdeaea', RED, '射频区', 'SMA ×8 输入\n50Ω 控制\n最短路径'),
        (bx + 146, by + 8, 150, 144, '#eaf1f8', ACCENT, '数字区', 'ZYNQ 核心板座\n差分时钟\n高速总线'),
        (bx + 304, by + 78, 108, 74, '#eaf6ee', GREEN, '电源区', '稳压器\n大电容'),
        (bx + 304, by + 8, 108, 62, '#fdf6e6', AMBER, '接口区', 'RJ45 / USB-C'),
    ]
    for zx, zy, zw, zh, fill, col, name, items in zones:
        _box(d, zx, zy, zw, zh, colors.HexColor(fill), col, 0.9, r=3)
        _txt(d, zx + 6, zy + zh - 13, name, 9, BOLD, col)
        for j, ln in enumerate(items.split('\n')):
            _txt(d, zx + 6, zy + zh - 27 - j * 11, ln, 7.5, FONT, GREY)

    # 板边接口标记
    for cy, lbl in ((by + 130, 'SMA'), (by + 100, 'SMA'), (by + 70, 'SMA'), (by + 40, 'SMA')):
        d.add(Rect(bx - 7, cy, 7, 12, fillColor=COPPER, strokeColor=DARK, strokeWidth=0.5))
    _txt(d, bx - 12, by + 12, 'SMA ×8', 7.5, BOLD, DARK, 'end')
    for cx, lbl in ((bx + 330, 'RJ45'), (bx + 386, 'USB-C')):
        d.add(Rect(cx, by - 7, 34, 7, fillColor=COPPER, strokeColor=DARK, strokeWidth=0.5))
        _txt(d, cx + 17, by - 17, lbl, 7.5, BOLD, DARK, 'middle')

    _txt(d, 6, 16, '三条原则：就近（去耦电容贴紧电源脚）　|　分区（模拟/数字/电源/射频分开）　|　'
                   '信号流向（避免来回穿越）', 8, FONT, DARK)
    return d


# ------------------------------------------------------- 图：原理图流程总览

def sch_flow():
    """原理图设计八阶段。"""
    d = Drawing(W, 212)
    stages = [
        ('一', '工程与图纸准备', '新建工程 / 页面设置 / 图框', GREEN),
        ('二', '符号库准备', '标准库 / 自建符号 / 库路径', AMBER),
        ('三', '绘制电路', '放符号 / 连线 / 标签', ACCENT),
        ('四', '层次化拆分', '按功能分图纸 / 层次标签', AMBER),
        ('五', '批注位号', '分配唯一 R1 C2 U3', GREEN),
        ('六', '分配封装', '与实际采购件对应', RED),
        ('七', 'ERC 检查', '引脚冲突 / 未连接 / 电源', RED),
        ('八', '输出', 'BOM / 网表 / 更新 PCB', GREEN),
    ]
    bw, bh, gx, gy = 218, 38, 24, 8
    x0, y0 = 4, 212 - bh - 14
    for i, (num, name, sub, col) in enumerate(stages):
        cx = x0 + (i % 2) * (bw + gx)
        cy = y0 - (i // 2) * (bh + gy)
        _box(d, cx, cy, bw, bh, colors.white, col, 1.1, r=4)
        d.add(Rect(cx, cy, 4, bh, fillColor=col, strokeColor=col))
        _txt(d, cx + 12, cy + bh - 15, '阶段' + num, 8.5, BOLD, col)
        _txt(d, cx + 52, cy + bh - 15, name, 9.5, BOLD, DARK)
        _txt(d, cx + 12, cy + 8, sub, 7.5, FONT, GREY)
        if i % 2 == 0:
            _arrow(d, cx + bw + 3, cy + bh / 2, cx + bw + gx - 3, cy + bh / 2, GREY, .8)
        elif i < len(stages) - 1:
            _arrow(d, cx + bw / 2, cy - 1, cx + bw / 2, cy - gy + 1, GREY, .8)
    _txt(d, 4, 10, '阶段六、七出错会直接导致板子报废或返工，是全流程的两个卡点',
         8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：六种连接方式

def sch_connect():
    """原理图中六种建立连接的方式对比。"""
    d = Drawing(W, 268)
    rows = [
        ('导线 / Wire', 'W', '直接画线相连', '同一图纸内看得见的物理连接'),
        ('结点 / Junction', 'J', '交叉处的实心圆点', '无圆点的交叉线不相连'),
        ('网络标签 / Label', 'L', '同名 = 相连', '仅在本张图纸内生效'),
        ('全局标签 / Global Label', 'Ctrl+L', '同名 = 相连', '跨所有图纸生效'),
        ('层次标签 / Hier. Label', 'H', '对应父图纸的图纸引脚', '子图与父图的接口'),
        ('电源符号 / Power', 'P', '同名 = 自动相连', 'GND、+3V3 等全局连通'),
    ]
    rh = 38
    y = 268 - 24
    for name, key, how, note in rows:
        y -= rh
        _box(d, 4, y, W - 8, rh - 4, colors.HexColor('#f8fafb'),
             colors.HexColor('#d5dee7'), 0.6, r=3)
        _txt(d, 12, y + rh - 18, name, 9, BOLD, ACCENT)
        d.add(Rect(150, y + rh - 22, 34, 13, fillColor=colors.white,
                   strokeColor=ACCENT, strokeWidth=0.8, rx=2, ry=2))
        _txt(d, 167, y + rh - 18, key, 8, BOLD, ACCENT, 'middle')
        _txt(d, 12, y + 8, how, 7.5, FONT, DARK)
        _txt(d, 150, y + 8, note, 7.5, FONT, GREY)

        # 右侧小示意
        gx0, gy0 = 340, y + rh / 2 - 2
        if name.startswith('导线'):
            d.add(Line(gx0, gy0, gx0 + 60, gy0, strokeColor=GREEN, strokeWidth=1.4))
            for xx in (gx0, gx0 + 60):
                d.add(Rect(xx - 3, gy0 - 3, 6, 6, fillColor=DARK, strokeColor=DARK))
        elif name.startswith('结点'):
            d.add(Line(gx0, gy0, gx0 + 60, gy0, strokeColor=GREEN, strokeWidth=1.4))
            d.add(Line(gx0 + 30, gy0 - 14, gx0 + 30, gy0 + 14, strokeColor=GREEN, strokeWidth=1.4))
            d.add(Polygon([gx0 + 30, gy0 + 3.2, gx0 + 33.2, gy0, gx0 + 30, gy0 - 3.2,
                           gx0 + 26.8, gy0], fillColor=DARK, strokeColor=DARK))
        elif name.startswith('网络标签'):
            for k, off in ((0, 0), (1, 76)):
                d.add(Line(gx0 + off, gy0, gx0 + off + 26, gy0,
                           strokeColor=GREEN, strokeWidth=1.4))
                _txt(d, gx0 + off + 28, gy0 - 3, 'SDA', 7.5, BOLD, ACCENT)
            _txt(d, gx0 + 56, gy0 + 8, '=', 9, BOLD, GREY)
        elif name.startswith('全局标签'):
            for off, lbl in ((0, '图纸 A'), (76, '图纸 B')):
                d.add(Rect(gx0 + off, gy0 - 10, 52, 20, fillColor=colors.white,
                           strokeColor=GREY, strokeWidth=0.5, rx=2, ry=2))
                _txt(d, gx0 + off + 26, gy0 - 3, lbl, 7, FONT, GREY, 'middle')
            _arrow(d, gx0 + 54, gy0, gx0 + 74, gy0, ACCENT, 1.0, 3.5)
        elif name.startswith('层次标签'):
            d.add(Rect(gx0, gy0 - 12, 56, 24, fillColor=colors.white,
                       strokeColor=ACCENT, strokeWidth=0.9, rx=2, ry=2))
            _txt(d, gx0 + 28, gy0 - 3, '父图纸', 7, FONT, ACCENT, 'middle')
            d.add(Rect(gx0 + 54, gy0 - 3, 6, 6, fillColor=AMBER, strokeColor=AMBER))
            _arrow(d, gx0 + 62, gy0, gx0 + 84, gy0, AMBER, 1.0, 3.5)
            _txt(d, gx0 + 88, gy0 - 3, '子图', 7, FONT, AMBER)
        else:
            for off in (0, 60):
                d.add(Line(gx0 + off + 12, gy0 + 10, gx0 + off + 12, gy0,
                           strokeColor=GREEN, strokeWidth=1.4))
                d.add(Line(gx0 + off + 4, gy0, gx0 + off + 20, gy0,
                           strokeColor=GREEN, strokeWidth=1.6))
                _txt(d, gx0 + off + 12, gy0 - 11, 'GND', 7, BOLD, ACCENT, 'middle')
            _txt(d, gx0 + 40, gy0 + 2, '=', 9, BOLD, GREY)

    _txt(d, 4, 8, '常见错误：交叉处漏放结点导致该连的没连；用网络标签跨图纸连接（不生效，'
                  '需用全局标签）', 8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：层次化结构

def sch_hierarchy():
    """层次化原理图的父子对应关系。"""
    d = Drawing(W, 226)
    # 顶层
    tx, ty, tw, th = 90, 150, 300, 60
    _box(d, tx, ty, tw, th, colors.HexColor('#eaf1f8'), ACCENT, 1.2, r=4)
    _txt(d, tx + 8, ty + th - 15, '顶层图纸 / Root Sheet', 9, BOLD, ACCENT)
    sheets = [('电源.kicad_sch', tx + 14), ('射频前端.kicad_sch', tx + 108),
              ('接口.kicad_sch', tx + 214)]
    pins = []
    for name, sx in sheets:
        d.add(Rect(sx, ty + 8, 78, 28, fillColor=colors.white,
                   strokeColor=DARK, strokeWidth=0.8))
        _txt(d, sx + 39, ty + 24, '图纸符号', 7, FONT, GREY, 'middle')
        _txt(d, sx + 39, ty + 13, name.replace('.kicad_sch', ''), 7.5, BOLD, DARK, 'middle')
        px, py = sx + 78, ty + 22
        d.add(Rect(px - 3, py - 3, 6, 6, fillColor=AMBER, strokeColor=AMBER))
        pins.append((px, py, sx + 39))
    _txt(d, tx + tw + 8, ty + 22, '图纸引脚', 7.5, BOLD, AMBER)
    _txt(d, tx + tw + 8, ty + 11, 'Sheet Pin', 7, FONT, GREY)

    # 子图
    cy = 44
    for i, (name, sx) in enumerate(sheets):
        cx = 24 + i * 152
        _box(d, cx, cy, 132, 62, colors.HexColor('#fdf6e6'), AMBER, 1.0, r=4)
        _txt(d, cx + 8, cy + 48, name.replace('.kicad_sch', '') + ' 子图', 8, BOLD, AMBER)
        d.add(Rect(cx + 8, cy + 26, 6, 6, fillColor=AMBER, strokeColor=AMBER))
        _txt(d, cx + 20, cy + 26, '层次标签 (H)', 7.5, FONT, DARK)
        _txt(d, cx + 8, cy + 10, '名称必须与图纸引脚一致', 7, FONT, GREY)
        _arrow(d, pins[i][2], ty - 2, cx + 66, cy + 64, ACCENT, 0.8, 3.5)

    _txt(d, 4, 20, '层次标签 (H) 与父图纸上的图纸引脚 **同名即相连**，是子图对外的唯一接口。',
         8, FONT, DARK)
    _txt(d, 4, 8, '快捷键：S 放置图纸　|　Ctrl+H 层次导航　|　Alt+Back 离开图纸　|　'
                  'PgUp / PgDn 翻页', 8, FONT, GREY)
    return d


# ------------------------------------------------------- 图：数据流

def sch_dataflow():
    """符号库 -> 原理图 -> 封装 -> PCB 的数据流。"""
    d = Drawing(W, 168)
    steps = [
        ('符号库', '.kicad_sym', '引脚定义\n电气类型', ACCENT),
        ('原理图', '.kicad_sch', '位号 Reference\n数值 Value\n封装 Footprint', GREEN),
        ('封装库', '.pretty', '焊盘尺寸\n实际外形', AMBER),
        ('PCB', '.kicad_pcb', '焊盘 + 飞线\n网络连接', RED),
    ]
    bw, gx = 104, 34
    x = 8
    y = 62
    for i, (name, ext, items, col) in enumerate(steps):
        _box(d, x, y, bw, 74, colors.white, col, 1.2, r=4)
        d.add(Rect(x, y + 58, bw, 16, fillColor=col, strokeColor=col,
                   rx=4, ry=4))
        _txt(d, x + bw / 2, y + 63, name, 9, BOLD, colors.white, 'middle')
        _txt(d, x + bw / 2, y + 46, ext, 7, FONT, GREY, 'middle')
        for j, ln in enumerate(items.split('\n')):
            _txt(d, x + 8, y + 32 - j * 11, ln, 7.5, FONT, DARK)
        if i < len(steps) - 1:
            _arrow(d, x + bw + 4, y + 37, x + bw + gx - 4, y + 37, ACCENT, 1.2, 4.5)
        x += bw + gx

    _txt(d, 118, 146, '分配封装', 7.5, BOLD, ACCENT)
    _txt(d, 256, 146, '引用', 7.5, BOLD, ACCENT)
    _txt(d, 388, 146, '从原理图更新 PCB', 7.5, BOLD, ACCENT)

    _txt(d, 8, 40, '关键：原理图里的「封装」字段只是一个名字字符串，它必须能在封装库里找到对应项。',
         8, FONT, DARK)
    _txt(d, 8, 27, '符号的引脚数与封装的焊盘数必须一一对应，否则更新 PCB 时报错。',
         8, FONT, DARK)
    _txt(d, 8, 12, '常见错误：符号画 0402、实物买 0603；连接器封装引脚顺序镜像。',
         8, BOLD, RED)
    return d


# ------------------------------------------------------- 图：ERC 引脚类型

def sch_erc():
    """ERC 引脚类型冲突矩阵（常见组合）。"""
    d = Drawing(W, 224)
    types = ['输出\nOutput', '输入\nInput', '双向\nBidir', '无源\nPassive',
             '电源输入\nPwr In', '电源输出\nPwr Out']
    # 0 = 正常, 1 = 警告, 2 = 错误
    m = [
        [2, 0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 2],
    ]
    cs, x0, y0 = 46, 96, 214 - 34
    for j, t in enumerate(types):
        for k, ln in enumerate(t.split('\n')):
            _txt(d, x0 + j * cs + cs / 2, y0 + 6 - k * 9, ln,
                 6.8, BOLD if k == 0 else FONT, DARK if k == 0 else GREY, 'middle')
    y = y0 - 12
    for i, t in enumerate(types):
        y -= cs * 0.62
        for k, ln in enumerate(t.split('\n')):
            _txt(d, x0 - 6, y + 14 - k * 9, ln, 6.8,
                 BOLD if k == 0 else FONT, DARK if k == 0 else GREY, 'end')
        for j in range(len(types)):
            v = m[i][j]
            fill = {0: colors.HexColor('#e8f5ec'), 1: colors.HexColor('#fdf6e6'),
                    2: colors.HexColor('#fdeaea')}[v]
            edge = {0: GREEN, 1: AMBER, 2: RED}[v]
            d.add(Rect(x0 + j * cs, y, cs - 3, cs * 0.62 - 3,
                       fillColor=fill, strokeColor=edge, strokeWidth=0.7))
            _txt(d, x0 + j * cs + (cs - 3) / 2, y + 8,
                 {0: '✓', 1: '!', 2: '✕'}[v], 9, BOLD, edge, 'middle')

    ly = 30
    for i, (c, t) in enumerate(((GREEN, '✓ 正常'), (AMBER, '! 警告'), (RED, '✕ 错误'))):
        _txt(d, 8 + i * 76, ly, t, 8, BOLD, c)
    _txt(d, 8, 16, '两个输出引脚直接相连是硬错误（会短路）；电源输出对电源输出同理。',
         8, FONT, DARK)
    _txt(d, 8, 4, '电源网络必须有至少一个「电源输出」或 PWR_FLAG，否则报「电源未驱动」。',
         8, BOLD, RED)
    return d


# ---------------------------------------------------------------- 图：OCXO 压控端

def ocxo_vctrl():
    """OCXO 压控端（VCTRL）的电位器分压 + RC 低通接法。"""
    # 画布沿用 680 px 宽的草图坐标（原点左上），统一换算到 reportlab 坐标
    s = W / 680.0
    bot = 366.0
    d = Drawing(W, (bot - 110.0) * s)
    wire_c = colors.HexColor('#444444')

    def px(v):
        return v * s

    def py(v):
        return (bot - v) * s

    def t(x, y, txt, size=7.5, font=FONT, fill=DARK, anchor='start'):
        _txt(d, px(x), py(y), txt, size, font, fill, anchor)

    def wire(pts):
        d.add(PolyLine([c for p in pts for c in (px(p[0]), py(p[1]))],
                       strokeColor=wire_c, strokeWidth=0.8))

    def rect(x, y, w, h, fill, stroke):
        d.add(Rect(px(x), py(y + h), w * s, h * s, fillColor=fill,
                   strokeColor=stroke, strokeWidth=0.7, rx=3, ry=3))

    def gnd(x, y):
        for hw, dy in ((14, 0), (8, 5), (3, 10)):
            d.add(Line(px(x - hw), py(y + dy), px(x + hw), py(y + dy),
                       strokeColor=wire_c, strokeWidth=0.8))

    rect(60, 120, 150, 150, colors.HexColor('#f0f2f4'), GREY)
    t(135, 152, 'U6', 9, BOLD, DARK, 'middle')
    t(135, 172, 'OCXO-10M', 7.5, FONT, DARK, 'middle')
    t(200, 204, 'VREF', 7.5, FONT, DARK, 'end')
    t(200, 249, 'VCTRL', 7.5, FONT, DARK, 'end')
    t(222, 194, '4', 7.5, FONT, GREY)
    t(222, 239, '3', 7.5, FONT, GREY)

    wire([(210, 200), (517, 200), (517, 235)])
    wire([(210, 245), (330, 245)])
    wire([(390, 245), (440, 245), (440, 280), (494, 280)])
    d.add(Polygon([px(500), py(280), px(493), py(276.5), px(493), py(283.5)],
                  fillColor=wire_c, strokeColor=wire_c))
    wire([(300, 245), (300, 288)])
    wire([(300, 297), (300, 325)])
    wire([(517, 325), (517, 345)])
    d.add(Circle(px(300), py(245), 2 * s, fillColor=wire_c, strokeColor=wire_c))

    rect(330, 235, 60, 20, colors.white, DARK)
    t(360, 228, 'R33  1k', 7.5, FONT, DARK, 'middle')

    d.add(Line(px(282), py(288), px(318), py(288), strokeColor=DARK, strokeWidth=1.2))
    d.add(Line(px(282), py(297), px(318), py(297), strokeColor=DARK, strokeWidth=1.2))
    t(326, 296, 'C51  100nF')

    rect(500, 235, 34, 90, colors.HexColor('#dce8f3'), ACCENT)
    t(548, 272, 'R32', 9)
    t(548, 291, '10k，25 圈')
    t(494, 226, '3', 7.5, FONT, GREY, 'end')
    t(494, 343, '1', 7.5, FONT, GREY, 'end')
    t(480, 272, '2', 7.5, FONT, GREY, 'middle')

    gnd(300, 325)
    gnd(517, 345)

    rect(60, 310, 205, 46, colors.white, GREY)
    t(72, 330, '顺时针旋转调节螺丝')
    t(72, 347, '→ VCTRL 升高 → 频率升高')

    return d


# ------------------------------------------------- 图：OCXO 供电电压切换电路

def ocxo_vsel():
    """用两颗 0Ω 电阻在 +5V 与 +3.3V 之间二选一给 OCXO 供电。"""
    d = Drawing(W, 220)
    wire_c = colors.HexColor('#444444')

    def wire(pts):
        d.add(PolyLine([c for p in pts for c in p],
                       strokeColor=wire_c, strokeWidth=0.8))

    def gnd(x, y):
        for hw, dy in ((10, 0), (6, 3.5), (2.2, 7)):
            d.add(Line(x - hw, y - dy, x + hw, y - dy,
                       strokeColor=wire_c, strokeWidth=0.8))

    def supply(x, y):
        d.add(Polygon([x, y + 7, x - 3.5, y + 1, x + 3.5, y + 1],
                      fillColor=colors.white, strokeColor=wire_c, strokeWidth=0.8))
        d.add(Line(x, y, x, y + 1, strokeColor=wire_c, strokeWidth=0.8))

    # 上支路：+5V 经 R34
    _txt(d, 46, 190, '+5V', 8, BOLD, DARK, 'end')
    supply(52, 193)
    wire([(52, 193), (100, 193)])
    _box(d, 100, 185, 50, 16, colors.white, DARK, 0.7, r=2)
    _txt(d, 125, 205, 'R34  0Ω', 7.5, FONT, DARK, 'middle')
    _txt(d, 125, 173, '装配', 7.5, BOLD, GREEN, 'middle')
    wire([(150, 193), (205, 193), (205, 150)])

    # 下支路：+3.3V 经 R35（不装）
    _txt(d, 46, 104, '+3.3V', 8, BOLD, DARK, 'end')
    supply(52, 107)
    wire([(52, 107), (100, 107)])
    d.add(Rect(100, 99, 50, 16, fillColor=colors.HexColor('#f4f4f2'),
               strokeColor=GREY, strokeWidth=0.7, rx=2, ry=2,
               strokeDashArray=[2, 2]))
    _txt(d, 125, 119, 'R35  0Ω', 7.5, FONT, GREY, 'middle')
    _txt(d, 125, 87, '不装 (DNP)', 7.5, BOLD, RED, 'middle')
    wire([(150, 107), (205, 107), (205, 150)])

    # 汇合后的 VDD_OCXO 网络
    wire([(205, 150), (330, 150)])
    d.add(Circle(205, 150, 1.8, fillColor=wire_c, strokeColor=wire_c))
    _txt(d, 213, 155, 'VDD_OCXO', 7.5, BOLD, ACCENT)

    # 去耦电容组
    d.add(Circle(255, 150, 1.8, fillColor=wire_c, strokeColor=wire_c))
    wire([(255, 150), (255, 129)])
    d.add(Line(243, 129, 267, 129, strokeColor=DARK, strokeWidth=1.2))
    d.add(Line(243, 123, 267, 123, strokeColor=DARK, strokeWidth=1.2))
    wire([(255, 123), (255, 106)])
    gnd(255, 106)
    _txt(d, 255, 88, 'C48 / C49 / C50', 7.5, FONT, DARK, 'middle')

    # 测试点
    d.add(Circle(295, 150, 1.8, fillColor=wire_c, strokeColor=wire_c))
    wire([(295, 150), (295, 168)])
    d.add(Circle(295, 170, 2.5, fillColor=colors.white,
                 strokeColor=ACCENT, strokeWidth=0.8))
    _txt(d, 302, 167, 'TP1', 7.5, FONT, ACCENT)

    # OCXO
    _box(d, 330, 135, 110, 40, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, 385, 162, 'U6  OCXO', 8.5, BOLD, DARK, 'middle')
    _txt(d, 338, 147, 'VCC', 7.5, FONT, DARK)
    _txt(d, 326, 155, '5', 7.5, FONT, GREY, 'end')

    # 警示
    d.add(Rect(46, 20, 290, 44, fillColor=colors.HexColor('#fdeaea'),
               strokeColor=RED, strokeWidth=0.8, rx=3, ry=3))
    _txt(d, 56, 47, '严禁 R34 与 R35 同时装配', 8, BOLD, RED)
    _txt(d, 56, 31, '5V 将倒灌至 3.3V 轨，损坏 U4 / U5 及全部 3.3V 器件', 7.5, FONT, DARK)
    return d


# ------------------------------------------------- 图：供电路径与电流预算

def ocxo_ptree():
    """两种供电方案在电源树上的位置与各自代价。"""
    d = Drawing(W, 340)

    def node(x, y, w, h, title, sub, fill, edge, tcol=DARK):
        _box(d, x, y, w, h, fill, edge, 0.7, r=3)
        _txt(d, x + w / 2, y + h - 14, title, 8, BOLD, tcol, 'middle')
        _txt(d, x + w / 2, y + 8, sub, 7.5, FONT, GREY, 'middle')

    node(170, 286, 140, 38, 'USB-C  J11', 'VBUS 5V，≤ 500 mA',
         colors.HexColor('#fdf6e6'), AMBER)
    _arrow(d, 240, 286, 240, 270, GREY, 0.8)
    d.add(Line(105, 270, 375, 270, strokeColor=GREY, strokeWidth=0.8))
    _arrow(d, 105, 270, 105, 252, GREY, 0.8)
    _arrow(d, 375, 270, 375, 252, GREY, 0.8)

    node(45, 212, 120, 38, 'R34  0Ω', '方案 A',
         colors.HexColor('#eaf3de'), GREEN)
    _arrow(d, 105, 212, 105, 196, GREY, 0.8)
    node(45, 156, 120, 38, 'OCXO VCC', '= 5.0 V',
         colors.HexColor('#eaf3de'), GREEN)

    node(315, 212, 120, 38, 'TPS78633 ×2', 'U4 / U5',
         colors.HexColor('#f0f2f4'), GREY)
    _arrow(d, 375, 212, 375, 196, GREY, 0.8)
    node(315, 156, 120, 38, '+3.3V 轨', '另供 U1 / U2 / U3',
         colors.HexColor('#f0f2f4'), GREY)
    _arrow(d, 375, 156, 375, 140, GREY, 0.8)
    node(315, 100, 120, 38, 'R35  0Ω', '方案 B',
         colors.HexColor('#e6f1fb'), ACCENT)
    _arrow(d, 375, 100, 375, 84, GREY, 0.8)
    node(315, 28, 120, 38, 'OCXO VCC', '= 3.3 V',
         colors.HexColor('#e6f1fb'), ACCENT)

    _box(d, 178, 60, 124, 130, colors.white, colors.HexColor('#d5dee7'), 0.6, r=3)
    _txt(d, 188, 176, '两条路径的代价', 8, BOLD, DARK)
    for i, (s, c) in enumerate((
            ('方案 A（5V）', ACCENT), ('无 LDO 损耗，', DARK),
            ('但 VBUS 噪声直入', DARK), ('', DARK),
            ('方案 B（3.3V）', ACCENT), ('LDO 已滤噪，', DARK),
            ('但需耗散 1.7 V × I', DARK))):
        if s:
            _txt(d, 188, 158 - i * 15, s, 7.5, BOLD if c is ACCENT else FONT, c)

    _box(d, 45, 66, 120, 54, colors.HexColor('#fdf6e6'), AMBER, 0.7, r=3)
    _txt(d, 55, 104, '5V 路径建议', 7.5, BOLD, DARK)
    _txt(d, 55, 89, '加 π 型滤波：', 7.5, FONT, DARK)
    _txt(d, 55, 75, 'FB + 10 µF', 7.5, FONT, DARK)
    return d


# ------------------------------------------------- 图：LVDS 输出的交流端接回路

def lvds_out_ac():
    """AC 耦合的 LVDS 输出：两只 49.9Ω 在交流上串联成 100Ω 差分负载。"""
    d = Drawing(W, 215)
    wire_c = colors.HexColor('#444444')

    def wire(pts):
        d.add(PolyLine([c for p in pts for c in p],
                       strokeColor=wire_c, strokeWidth=0.8))

    def gnd(x, y):
        for hw, dy in ((9, 0), (5.5, 3.2), (2, 6.4)):
            d.add(Line(x - hw, y - dy, x + hw, y - dy,
                       strokeColor=wire_c, strokeWidth=0.8))

    def cap(x, y):
        d.add(Line(x, y - 8, x, y + 8, strokeColor=DARK, strokeWidth=1.2))
        d.add(Line(x + 6, y - 8, x + 6, y + 8, strokeColor=DARK, strokeWidth=1.2))

    _box(d, 40, 100, 80, 100, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, 80, 160, 'U1', 8.5, BOLD, DARK, 'middle')
    _txt(d, 80, 145, 'LVDS 驱动', 7.5, FONT, DARK, 'middle')
    _txt(d, 80, 128, '3.5 mA 电流源', 7, FONT, GREY, 'middle')

    # P 路
    wire([(120, 185), (163, 185)])
    cap(163, 185)
    wire([(169, 185), (330, 185)])
    _txt(d, 124, 190, 'OUT_P', 7, FONT, ACCENT)
    _txt(d, 166, 200, 'C3  100nF', 7, FONT, DARK, 'middle')

    # N 路
    wire([(120, 115), (163, 115)])
    cap(163, 115)
    wire([(169, 115), (330, 115)])
    _txt(d, 124, 120, 'OUT_N', 7, FONT, ACCENT)
    _txt(d, 166, 100, 'C4  100nF', 7, FONT, DARK, 'middle')

    # 端接：交流上 R7 与 R8 串联，中点接地
    _box(d, 273, 155, 14, 26, colors.white, DARK, 0.7, r=2)
    _box(d, 273, 127, 14, 26, colors.white, DARK, 0.7, r=2)
    wire([(280, 185), (280, 181)])
    wire([(280, 155), (280, 153)])
    wire([(280, 127), (280, 115)])
    d.add(Circle(280, 185, 1.8, fillColor=wire_c, strokeColor=wire_c))
    d.add(Circle(280, 115, 1.8, fillColor=wire_c, strokeColor=wire_c))
    d.add(Circle(280, 154, 1.8, fillColor=wire_c, strokeColor=wire_c))
    wire([(280, 154), (240, 154), (240, 146)])
    gnd(240, 146)
    _txt(d, 292, 166, 'R7  49.9Ω', 7, FONT, DARK)
    _txt(d, 292, 138, 'R8  49.9Ω', 7, FONT, DARK)

    # SMA
    for y, ref in ((185, 'J4'), (115, 'J5')):
        d.add(Circle(336, y, 5, fillColor=colors.white,
                     strokeColor=wire_c, strokeWidth=0.8))
        d.add(Circle(336, y, 1.6, fillColor=wire_c, strokeColor=wire_c))
        _txt(d, 346, y - 3, ref, 7, FONT, DARK)

    _box(d, 40, 28, 330, 50, colors.HexColor('#f8fafb'),
         colors.HexColor('#d5dee7'), 0.6, r=3)
    _txt(d, 50, 60, '交流回路：OUT_P → C3 → R7 → 地 → R8 → C4 → OUT_N', 7.5, FONT, DARK)
    _txt(d, 50, 43, '差分负载 = 49.9 + 49.9 = 99.8 Ω，正是 LVDS 需要的 100 Ω',
         7.5, BOLD, ACCENT)
    return d


# ------------------------------------------------- 图：三种负载下的差分阻抗

def lvds_out_load():
    """SMA 接上 50Ω 仪器后，板上端接被并联，差分负载随之塌缩。"""
    d = Drawing(W, 200)
    wire_c = colors.HexColor('#444444')

    def cell(x0, title, ext_p, ext_n, rdiff, swing, verdict, vcol):
        _box(d, x0, 45, 140, 140, colors.white,
             colors.HexColor('#d5dee7'), 0.6, r=3)
        _txt(d, x0 + 70, 170, title, 7.5, BOLD, DARK, 'middle')
        cx = x0 + 70
        d.add(Line(x0 + 20, 148, x0 + 120, 148, strokeColor=wire_c, strokeWidth=0.8))
        d.add(Line(x0 + 20, 108, x0 + 120, 108, strokeColor=wire_c, strokeWidth=0.8))
        _txt(d, x0 + 17, 145, 'P', 6.5, BOLD, ACCENT, 'end')
        _txt(d, x0 + 17, 105, 'N', 6.5, BOLD, ACCENT, 'end')

        # 板上端接
        _box(d, cx - 7, 130, 14, 14, colors.white, DARK, 0.6, r=1.5)
        _box(d, cx - 7, 112, 14, 14, colors.white, DARK, 0.6, r=1.5)
        d.add(Line(cx, 148, cx, 144, strokeColor=wire_c, strokeWidth=0.8))
        d.add(Line(cx, 130, cx, 126, strokeColor=wire_c, strokeWidth=0.8))
        d.add(Line(cx, 112, cx, 108, strokeColor=wire_c, strokeWidth=0.8))
        d.add(Circle(cx, 128, 1.5, fillColor=wire_c, strokeColor=wire_c))
        d.add(Line(cx, 128, cx - 22, 128, strokeColor=wire_c, strokeWidth=0.8))
        for hw, dy in ((7, 0), (4.2, 2.6), (1.6, 5.2)):
            d.add(Line(cx - 22 - hw, 128 - dy, cx - 22 + hw, 128 - dy,
                       strokeColor=wire_c, strokeWidth=0.8))
        _txt(d, cx + 10, 135, '49.9', 6.5, FONT, DARK)
        _txt(d, cx + 10, 117, '49.9', 6.5, FONT, DARK)

        # 外部 50Ω 负载（虚线 = 仪器输入）
        for on, y in ((ext_p, 148), (ext_n, 108)):
            if not on:
                continue
            ex = x0 + 108
            d.add(Rect(ex - 7, y - 22, 14, 14, fillColor=colors.white,
                       strokeColor=RED, strokeWidth=0.6,
                       strokeDashArray=[1.5, 1.5]))
            d.add(Line(ex, y, ex, y - 8, strokeColor=RED, strokeWidth=0.6,
                       strokeDashArray=[1.5, 1.5]))
            d.add(Line(ex, y - 22, ex, y - 26, strokeColor=RED, strokeWidth=0.6,
                       strokeDashArray=[1.5, 1.5]))
            for hw, dy in ((6, 0), (3.6, 2.4), (1.4, 4.8)):
                d.add(Line(ex - hw, y - 26 - dy, ex + hw, y - 26 - dy,
                           strokeColor=RED, strokeWidth=0.6))
            _txt(d, ex - 10, y - 18, '50', 6.5, FONT, RED, 'end')

        _txt(d, cx, 88, rdiff, 7.5, BOLD, ACCENT, 'middle')
        _txt(d, cx, 73, swing, 7, FONT, DARK, 'middle')
        _txt(d, cx, 57, verdict, 7, BOLD, vcol, 'middle')

    cell(15, '两端均空载', False, False,
         'R_diff = 99.8 Ω', 'VOD = 389 mV', '合规', GREEN)
    cell(170, '仅 P 端接仪器', True, False,
         'R_diff = 74.9 Ω', 'VOD = 292 mV', '幅度降、两侧不对称', AMBER)
    cell(325, '两端均接仪器', True, True,
         'R_diff = 49.9 Ω', 'VOD = 195 mV', '低于手册下限 250 mV', RED)

    _txt(d, 15, 28, '按 LMK5B12204 手册 AC-LVDS 的 VOD 典型值 390 mV @100 Ω 反推驱动电流 3.9 mA；'
                    '虚线为仪器输入端的 50 Ω', 7, FONT, GREY)
    return d


# ------------------------------------------------- 图：OCXO 输出的高阻取样

def xo_tap():
    """主路径直通、校准口经串联电阻旁路取样。"""
    d = Drawing(W, 230)
    wire_c = colors.HexColor('#444444')

    def wire(pts, col=None, dash=None):
        kw = dict(strokeColor=col or wire_c, strokeWidth=0.8)
        if dash:
            kw['strokeDashArray'] = dash
        d.add(PolyLine([c for p in pts for c in p], **kw))

    def gnd(x, y):
        for hw, dy in ((9, 0), (5.5, 3.2), (2, 6.4)):
            d.add(Line(x - hw, y - dy, x + hw, y - dy,
                       strokeColor=wire_c, strokeWidth=0.8))

    _box(d, 35, 155, 75, 50, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, 72, 191, 'U6  OCXO', 8.5, BOLD, DARK, 'middle')
    _txt(d, 72, 176, '10 MHz', 7, FONT, GREY, 'middle')
    _txt(d, 106, 163, 'RF', 7, FONT, DARK, 'end')

    # 主路径：直通
    d.add(PolyLine([110, 180, 400, 180], strokeColor=GREEN, strokeWidth=1.8))
    _txt(d, 250, 187, 'XO_P　50 Ω 走线，全程无有源器件', 7.5, BOLD, GREEN, 'middle')
    _txt(d, 120, 168, '+7 dBm（示例）', 7, FONT, GREY)
    d.add(Circle(175, 180, 2, fillColor=wire_c, strokeColor=wire_c))

    _box(d, 400, 155, 75, 50, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, 437, 191, 'U1', 8.5, BOLD, DARK, 'middle')
    _txt(d, 437, 176, 'LMK5B12204', 7, FONT, GREY, 'middle')
    _txt(d, 404, 163, 'XO_N', 7, FONT, DARK)
    wire([(400, 160), (380, 160), (380, 150)])
    gnd(380, 150)

    # 取样支路
    wire([(175, 180), (175, 140)])
    _box(d, 168, 112, 14, 28, colors.white, DARK, 0.7, r=2)
    _txt(d, 189, 130, 'R34  1 kΩ', 7, BOLD, DARK)
    _txt(d, 189, 119, '（现为 0 Ω，改值即可）', 6.5, FONT, GREY)
    wire([(175, 112), (175, 95), (215, 95)])
    d.add(Line(215, 87, 215, 103, strokeColor=DARK, strokeWidth=1.2))
    d.add(Line(221, 87, 221, 103, strokeColor=DARK, strokeWidth=1.2))
    _txt(d, 218, 108, 'C52  100nF', 7, FONT, DARK, 'middle')
    wire([(221, 95), (280, 95)])
    d.add(Circle(286, 95, 5, fillColor=colors.white,
                 strokeColor=wire_c, strokeWidth=0.8))
    d.add(Circle(286, 95, 1.6, fillColor=wire_c, strokeColor=wire_c))
    _txt(d, 280, 78, 'J12  校准口', 7, BOLD, DARK, 'middle')
    _txt(d, 280, 68, '约 −19 dBm', 7, FONT, ACCENT, 'middle')

    wire([(292, 95), (330, 95)], RED, [2, 2])
    d.add(Rect(330, 80, 72, 30, fillColor=colors.white, strokeColor=RED,
               strokeWidth=0.7, rx=3, ry=3, strokeDashArray=[2, 2]))
    _txt(d, 366, 97, '频率计', 7.5, BOLD, RED, 'middle')
    _txt(d, 366, 86, '50 Ω，仅校准时接', 6.5, FONT, GREY, 'middle')

    _box(d, 35, 18, 440, 40, colors.HexColor('#eaf3de'), GREEN, 0.7, r=3)
    _txt(d, 45, 44, '主路径不经过任何有源器件，OCXO 的相位噪声零劣化', 7.5, BOLD, DARK)
    _txt(d, 45, 28, '1 kΩ 串联使支路对主路径的负载影响仅 −0.4 dB；不接频率计时支路开路，影响为零',
         7, FONT, DARK)
    return d


# ------------------------------------------------- 图：三种分路方案对比

def xo_split_cmp():
    """高阻取样、电阻功分、有源缓冲三种做法的代价对比。"""
    d = Drawing(W, 290)
    wire_c = colors.HexColor('#444444')

    def blk(x, y, w, h, txt, fill, edge, size=7):
        _box(d, x, y, w, h, fill, edge, 0.7, r=2)
        _txt(d, x + w / 2, y + h / 2 - 2.5, txt, size, BOLD, DARK, 'middle')

    def row(base, title, tcol, notes, mode):
        _box(d, 20, base, 448, 88, colors.white,
             colors.HexColor('#d5dee7'), 0.6, r=3)
        _txt(d, 32, base + 76, title, 7.5, BOLD, tcol)
        y = base + 60
        blk(32, y - 10, 44, 20, 'OCXO', colors.HexColor('#f0f2f4'), GREY)

        if mode == 'tap':
            d.add(PolyLine([76, y, 150, y], strokeColor=GREEN, strokeWidth=1.6))
            d.add(Circle(100, y, 1.8, fillColor=wire_c, strokeColor=wire_c))
            d.add(Line(100, y, 100, base + 22, strokeColor=wire_c, strokeWidth=0.8))
            _txt(d, 105, base + 38, '1 kΩ', 6.5, FONT, DARK)
        elif mode == 'split':
            d.add(Line(76, y, 100, y, strokeColor=wire_c, strokeWidth=0.8))
            d.add(Circle(100, y, 1.8, fillColor=wire_c, strokeColor=wire_c))
            d.add(Line(100, y, 150, y, strokeColor=wire_c, strokeWidth=0.8))
            d.add(Line(100, y, 100, base + 22, strokeColor=wire_c, strokeWidth=0.8))
            _txt(d, 80, y + 5, '16.9', 6.5, FONT, DARK)
            _txt(d, 120, y + 5, '16.9', 6.5, FONT, DARK)
            _txt(d, 105, base + 38, '16.9', 6.5, FONT, DARK)
        else:
            d.add(Line(76, y, 88, y, strokeColor=wire_c, strokeWidth=0.8))
            blk(88, y - 10, 34, 20, 'BUF', colors.HexColor('#fdf6e6'), AMBER, 6.5)
            d.add(Line(122, y, 150, y, strokeColor=wire_c, strokeWidth=0.8))
            d.add(Circle(136, y, 1.8, fillColor=wire_c, strokeColor=wire_c))
            d.add(Line(136, y, 136, base + 22, strokeColor=wire_c, strokeWidth=0.8))

        blk(150, y - 10, 52, 20, 'LMK', colors.HexColor('#e6f1fb'), ACCENT)
        fx = 100 if mode != 'buf' else 136
        blk(fx - 26, base + 2, 52, 20, '频率计', colors.white, GREY)

        for i, (s, c) in enumerate(notes):
            _txt(d, 230, base + 66 - i * 15, s, 7, BOLD if c else FONT, c or DARK)

    row(196, '方案 A：高阻取样（推荐）', GREEN, [
        ('主路径相噪劣化：无', GREEN),
        ('主路径插损：−0.4 dB', None),
        ('校准口电平：约 −19 dBm（OCXO +7 dBm 时）', None),
        ('新增：1 只电容 + 1 个 SMA，R34 已在板上', None)], 'tap')
    row(100, '方案 B：6 dB 电阻功分', ACCENT, [
        ('主路径相噪劣化：无', GREEN),
        ('主路径插损：−6 dB', AMBER),
        ('两口对称、三端口均匹配 50 Ω', None),
        ('新增：3 只电阻 + 1 个 SMA', None)], 'split')
    row(4, '方案 C：有源缓冲（LMK1C1102 等）', AMBER, [
        ('主路径相噪劣化：取决于缓冲器 1/f 噪声', RED),
        ('主路径插损：无，且可提供增益', None),
        ('端口隔离好（通常 >40 dB）', None),
        ('新增：芯片 + 供电去耦，且需核对附加相噪', None)], 'buf')
    return d


# ------------------------------------------------- 图：OCXO 5V 升降压供电电路

def ocxo_buckboost():
    """VBUS 经 buck-boost 稳压到 5.0 V，再经 π 型滤波送 OCXO。"""
    d = Drawing(W, 275)
    wire_c = colors.HexColor('#444444')

    def wire(pts, col=None, w=0.8):
        d.add(PolyLine([c for p in pts for c in p],
                       strokeColor=col or wire_c, strokeWidth=w))

    def gnd(x, y):
        for hw, dy in ((8, 0), (5, 2.8), (1.8, 5.6)):
            d.add(Line(x - hw, y - dy, x + hw, y - dy,
                       strokeColor=wire_c, strokeWidth=0.8))

    def cap(x, ytop):
        d.add(Line(x - 10, ytop, x + 10, ytop, strokeColor=DARK, strokeWidth=1.2))
        d.add(Line(x - 10, ytop - 6, x + 10, ytop - 6, strokeColor=DARK, strokeWidth=1.2))

    def node(x, y):
        d.add(Circle(x, y, 1.8, fillColor=wire_c, strokeColor=wire_c))

    # ---- 输入侧 ----
    d.add(Polygon([38, 215, 34, 209, 42, 209],
                  fillColor=colors.white, strokeColor=wire_c, strokeWidth=0.8))
    wire([(38, 208), (38, 209)])
    _txt(d, 38, 222, 'VBUS', 7.5, BOLD, DARK, 'middle')
    _txt(d, 38, 231, '4.25 ~ 5.25 V', 6, FONT, GREY, 'middle')
    wire([(38, 208), (175, 208)])

    node(65, 208)
    wire([(65, 208), (65, 188)])
    cap(65, 188)
    wire([(65, 182), (65, 166)])
    gnd(65, 166)
    _txt(d, 50, 185, 'C53  10µF', 6.5, FONT, DARK, 'end')
    _txt(d, 50, 175, 'C54  100nF', 6.5, FONT, DARK, 'end')

    # ---- VINA 的 RC 滤波（控制级独立供电）----
    node(105, 208)
    wire([(105, 208), (105, 193)])
    _box(d, 105, 186, 25, 14, colors.white, DARK, 0.7, r=2)
    wire([(130, 193), (175, 193)])
    _txt(d, 117, 180, 'R38  10 Ω', 6.5, FONT, DARK, 'middle')
    node(150, 193)
    wire([(150, 193), (150, 181)])
    cap(150, 181)
    wire([(150, 175), (150, 167)])
    gnd(150, 167)
    _txt(d, 138, 170, 'C58  1µF', 6.5, FONT, DARK, 'end')

    # ---- 主芯片 ----
    _box(d, 175, 128, 115, 90, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, 232, 192, 'U7', 8, BOLD, DARK, 'middle')
    _txt(d, 232, 178, 'TPS63020', 7, FONT, DARK, 'middle')
    _txt(d, 180, 205, 'VIN', 6.5, FONT, DARK)
    _txt(d, 180, 190, 'VINA', 6.5, BOLD, ACCENT)
    _txt(d, 180, 162, 'EN　　接 VIN', 6.5, FONT, DARK)
    _txt(d, 180, 144, 'PS/SYNC　接 VIN', 6.5, FONT, DARK)
    _txt(d, 285, 205, 'VOUT', 6.5, FONT, DARK, 'end')
    _txt(d, 285, 172, 'FB', 6.5, FONT, DARK, 'end')
    _txt(d, 285, 144, 'PG', 6.5, BOLD, ACCENT, 'end')
    _txt(d, 196, 211, 'L1', 6.5, FONT, DARK)
    _txt(d, 261, 211, 'L2', 6.5, FONT, DARK)
    _txt(d, 199, 133, 'GND', 6.5, FONT, DARK)
    _txt(d, 253, 133, 'PGND', 6.5, FONT, DARK)
    wire([(175, 165), (165, 165)])
    wire([(175, 147), (165, 147)])
    wire([(205, 128), (205, 116)])
    gnd(205, 116)
    wire([(260, 128), (260, 116)])
    gnd(260, 116)

    # ---- 电感 ----
    wire([(200, 218), (200, 245), (212, 245)])
    wire([(254, 245), (265, 245), (265, 218)])
    _box(d, 212, 238, 42, 14, colors.white, DARK, 0.7, r=2)
    _txt(d, 233, 258, 'L1   2.2 µH', 7, BOLD, DARK, 'middle')

    # ---- PG（开漏，可选上拉）----
    wire([(290, 147), (302, 147)])
    d.add(Circle(304, 147, 2.2, fillColor=colors.white,
                 strokeColor=ACCENT, strokeWidth=0.8))

    # ---- 输出与反馈 ----
    wire([(290, 208), (466, 208)])

    node(330, 208)
    wire([(330, 208), (330, 196)])
    _box(d, 323, 170, 14, 26, colors.white, DARK, 0.7, r=2)
    node(330, 168)
    wire([(330, 168), (312, 168), (312, 175), (290, 175)])
    wire([(330, 168), (330, 162)])
    _box(d, 323, 136, 14, 26, colors.white, DARK, 0.7, r=2)
    wire([(330, 136), (330, 124)])
    gnd(330, 124)
    _txt(d, 342, 182, 'R36  909k', 6.5, FONT, DARK)
    _txt(d, 342, 148, 'R37  100k', 6.5, FONT, DARK)

    node(368, 208)
    wire([(368, 208), (368, 188)])
    cap(368, 188)
    wire([(368, 182), (368, 166)])
    gnd(368, 166)
    _txt(d, 382, 185, 'C55  22µF', 6.5, FONT, DARK)

    _box(d, 395, 201, 36, 14, colors.HexColor('#fdf6e6'), AMBER, 0.7, r=2)
    _txt(d, 413, 222, 'FB8', 6.5, BOLD, DARK, 'middle')
    _txt(d, 413, 231, '600 Ω @100 MHz', 6, FONT, GREY, 'middle')

    node(442, 208)
    wire([(442, 208), (442, 188)])
    cap(442, 188)
    wire([(442, 182), (442, 166)])
    gnd(442, 166)
    _txt(d, 452, 194, 'C57', 6.5, FONT, DARK)
    _txt(d, 452, 185, '10µF', 6.5, FONT, DARK)

    d.add(Polygon([472, 208, 465, 204.5, 465, 211.5],
                  fillColor=GREEN, strokeColor=GREEN))
    _txt(d, 450, 220, '至 OCXO', 7, BOLD, GREEN, 'middle')

    _box(d, 28, 20, 440, 62, colors.HexColor('#f8fafb'),
         colors.HexColor('#d5dee7'), 0.6, r=3)
    _txt(d, 38, 68, 'VINA 是控制级独立供电，必须经 R38 + C58 与功率级 VIN 隔离，'
                    '否则开关噪声会窜进控制环路', 6.5, BOLD, DARK)
    _txt(d, 38, 52, 'PS/SYNC 接高强制 PWM：省电模式下开关频率随负载漂移，'
                    '低频噪声会调制进相位噪声', 6.5, FONT, DARK)
    _txt(d, 38, 36, 'VOUT = 0.5 V × (1 + R36/R37)，手册要求 R37 在 100 kΩ~1 MΩ；'
                    'PG 为开漏，可上拉作电源就绪指示', 6.5, FONT, DARK)
    return d



# ------------------------------------------------- 图：开关电源布局要点

def ocxo_bb_layout():
    """buck-boost 的 PCB 布局：环路最小、与 OCXO 隔离。"""
    d = Drawing(W, 235)
    wire_c = colors.HexColor('#444444')

    _box(d, 25, 55, 430, 150, colors.HexColor('#fbfbf9'),
         colors.HexColor('#c9c9c4'), 0.7, r=3)

    # DC-DC 区
    _box(d, 45, 95, 150, 95, colors.HexColor('#fdf6e6'), AMBER, 0.7, r=3)
    _txt(d, 120, 196, 'DC-DC 区', 7, BOLD, AMBER, 'middle')
    _box(d, 95, 120, 48, 32, colors.white, DARK, 0.7, r=2)
    _txt(d, 119, 133, 'U7', 7.5, BOLD, DARK, 'middle')
    _box(d, 95, 160, 48, 18, colors.white, DARK, 0.7, r=2)
    _txt(d, 119, 166, 'L1', 7, BOLD, DARK, 'middle')
    _box(d, 62, 120, 20, 32, colors.white, DARK, 0.7, r=2)
    _txt(d, 72, 133, 'Cin', 6.5, FONT, DARK, 'middle')
    _box(d, 156, 120, 20, 32, colors.white, DARK, 0.7, r=2)
    _txt(d, 166, 133, 'Cout', 6.5, FONT, DARK, 'middle')
    d.add(Rect(56, 112, 126, 74, fillColor=None, strokeColor=RED,
               strokeWidth=1.0, rx=3, ry=3, strokeDashArray=[3, 2]))
    _txt(d, 119, 103, '高 di/dt 环路：面积压到最小', 6.5, BOLD, RED, 'middle')

    # 隔离带
    d.add(Line(250, 62, 250, 198, strokeColor=ACCENT, strokeWidth=1.0,
               strokeDashArray=[4, 3]))
    _txt(d, 250, 205, '完整地平面隔离', 6.5, BOLD, ACCENT, 'middle')
    _txt(d, 250, 70, '此处不走任何信号', 6, FONT, GREY, 'middle')

    # OCXO 区
    _box(d, 290, 95, 145, 95, colors.HexColor('#eaf3de'), GREEN, 0.7, r=3)
    _txt(d, 362, 196, 'OCXO 区', 7, BOLD, GREEN, 'middle')
    _box(d, 325, 118, 95, 55, colors.white, DARK, 0.7, r=2)
    _txt(d, 372, 148, 'U6', 8, BOLD, DARK, 'middle')
    _txt(d, 372, 134, 'OCXO', 7, FONT, DARK, 'middle')
    _box(d, 303, 128, 14, 32, colors.white, ACCENT, 0.7, r=2)
    _txt(d, 310, 166, 'C57', 6.5, BOLD, ACCENT, 'middle')
    _txt(d, 310, 118, '紧贴引脚', 6, FONT, ACCENT, 'middle')

    # 5V 走线
    d.add(PolyLine([195, 140, 290, 140], strokeColor=GREEN, strokeWidth=1.6))
    d.add(Polygon([296, 140, 289, 136.5, 289, 143.5],
                  fillColor=GREEN, strokeColor=GREEN))
    _txt(d, 242, 146, '5V，宽 ≥ 0.5 mm', 6.5, BOLD, GREEN, 'middle')

    _txt(d, 25, 40, '开关电源布局的第一原则：Cin—U7—L1—Cout 这个环路的包围面积决定了辐射与纹波，'
                    '优先于一切美观考虑', 6.5, BOLD, DARK)
    _txt(d, 25, 25, 'DC-DC 与 OCXO 之间保持完整地平面，中间不走时钟或模拟信号；'
                    'FB 分压网络远离电感，避免开关磁场耦合进反馈', 6.5, FONT, DARK)
    return d


# ------------------------------------------------- 图：CLOCK 板整板布局规划

def clk_layout():
    """100×100 mm 板框内的分区、连接器排布与输出走线方向。"""
    d = Drawing(W, 350)
    BX, BY, BW = 108, 42, 255     # 板框：255 pt 代表 100 mm

    _box(d, BX, BY, BW, BW, colors.HexColor('#fbfbf9'),
         colors.HexColor('#8a8a85'), 1.0, r=2)
    _txt(d, BX + BW / 2, BY + BW + 30, '板框 100 × 100 mm（免费打样上限）',
         7.5, BOLD, DARK, 'middle')

    d.add(Line(BX, BY - 14, BX + BW, BY - 14, strokeColor=GREY, strokeWidth=0.6))
    for x in (BX, BX + BW):
        d.add(Line(x, BY - 18, x, BY - 10, strokeColor=GREY, strokeWidth=0.6))
    _txt(d, BX + BW / 2, BY - 26, '100 mm', 7, FONT, GREY, 'middle')

    def sma_h(x, y):
        d.add(Rect(x - 8, y - 6, 16, 12, fillColor=colors.HexColor('#fdf6e6'),
                   strokeColor=AMBER, strokeWidth=0.7))

    def sma_v(x, y):
        d.add(Rect(x - 6, y - 8, 12, 16, fillColor=colors.HexColor('#fdf6e6'),
                   strokeColor=AMBER, strokeWidth=0.7))

    CX = BX + BW / 2
    xs = [CX - 49.5, CX - 16.5, CX + 16.5, CX + 49.5]

    # 上下两边：8 路时钟输出，正对 U1
    for x in xs:
        sma_h(x, BY + BW)
        sma_h(x, BY)
        d.add(Line(x, BY + BW - 8, x, BY + 232, strokeColor=GREEN, strokeWidth=1.4))
        d.add(Line(x, BY + 8, x, BY + 118, strokeColor=GREEN, strokeWidth=1.4))
    _txt(d, CX, BY + BW + 14, 'OUT0 / OUT1   4 × SMA', 6.5, BOLD, AMBER, 'middle')
    _txt(d, CX, BY - 34, 'OUT2 / OUT3   4 × SMA', 6.5, BOLD, AMBER, 'middle')

    # 左边参考输入、右边校准口与 USB
    for y, lb in ((BY + 205, 'J1'), (BY + 178, 'J6')):
        sma_v(BX, y)
        _txt(d, BX - 10, y - 2, lb, 6.5, FONT, DARK, 'end')
    _txt(d, BX - 10, BY + 226, '参考输入', 6.5, BOLD, DARK, 'end')
    sma_v(BX + BW, BY + 200)
    _txt(d, BX + BW + 10, BY + 198, 'J12 校准口', 6.5, FONT, DARK)
    d.add(Rect(BX + BW - 6, BY + 68, 12, 24, fillColor=colors.HexColor('#e6f1fb'),
               strokeColor=ACCENT, strokeWidth=0.7))
    _txt(d, BX + BW + 10, BY + 77, 'USB-C', 6.5, BOLD, ACCENT)

    # 中央：U1
    _box(d, BX + 72, BY + 118, 110, 114, colors.HexColor('#eef3f8'), ACCENT, 0.8, r=3)
    _txt(d, CX, BY + 220, 'U1  时钟发生器', 7, BOLD, ACCENT, 'middle')
    _box(d, CX - 20, BY + 160, 40, 40, colors.white, DARK, 0.8, r=2)
    _txt(d, CX, BY + 176, 'U1', 8, BOLD, DARK, 'middle')
    _txt(d, CX, BY + 144, '七路电源域去耦环绕', 6, FONT, GREY, 'middle')
    _txt(d, CX, BY + 130, '每域 10µF + 100nF 贴引脚', 6, FONT, GREY, 'middle')

    # 左上：参考缓冲
    _box(d, BX + 8, BY + 158, 58, 74, colors.HexColor('#f2f0f7'),
         colors.HexColor('#8878a8'), 0.7, r=3)
    _txt(d, BX + 37, BY + 220, 'U2 / U3', 6.5, BOLD, colors.HexColor('#6b5b95'), 'middle')
    _txt(d, BX + 37, BY + 206, '缓冲', 6, FONT, GREY, 'middle')
    _txt(d, BX + 37, BY + 176, 'J14', 6, FONT, GREY, 'middle')
    _txt(d, BX + 37, BY + 164, '主控接口', 6, FONT, GREY, 'middle')

    # 右上：OCXO
    _box(d, BX + 189, BY + 158, 58, 74, colors.HexColor('#eaf3de'), GREEN, 0.7, r=3)
    _txt(d, BX + 218, BY + 220, 'OCXO 区', 6.5, BOLD, GREEN, 'middle')
    _box(d, BX + 199, BY + 180, 38, 30, colors.white, DARK, 0.8, r=2)
    _txt(d, BX + 218, BY + 191, 'U6', 7.5, BOLD, DARK, 'middle')
    _txt(d, BX + 218, BY + 168, 'H1 / TP1 紧邻', 6, FONT, GREY, 'middle')

    # 左下：DC-DC（远离 OCXO）
    _box(d, BX + 8, BY + 20, 58, 84, colors.HexColor('#fdf0e6'), RED, 0.7, r=3)
    _txt(d, BX + 37, BY + 92, 'DC-DC  U7', 6.5, BOLD, RED, 'middle')
    _txt(d, BX + 37, BY + 76, 'L1 环路', 6, FONT, DARK, 'middle')
    _txt(d, BX + 37, BY + 64, '面积最小', 6, FONT, DARK, 'middle')
    _txt(d, BX + 37, BY + 44, '与 OCXO', 6, BOLD, RED, 'middle')
    _txt(d, BX + 37, BY + 32, '对角最远', 6, BOLD, RED, 'middle')

    # 右下：LDO
    _box(d, BX + 189, BY + 20, 58, 84, colors.HexColor('#f0f2f4'), GREY, 0.7, r=3)
    _txt(d, BX + 218, BY + 92, 'U4 / U5', 6.5, BOLD, DARK, 'middle')
    _txt(d, BX + 218, BY + 78, 'LDO', 6, FONT, GREY, 'middle')
    _txt(d, BX + 218, BY + 56, '散热铜箔', 6, BOLD, DARK, 'middle')
    _txt(d, BX + 218, BY + 44, '≥ 200 mm²', 6, FONT, DARK, 'middle')

    _txt(d, BX + BW + 10, BY + 240, '差分对垂直出线', 6, BOLD, GREEN)
    _txt(d, BX + BW + 10, BY + 231, '不绕行、不交叉', 6, FONT, GREEN)

    _box(d, 28, 8, 430, 26, colors.HexColor('#f8fafb'),
         colors.HexColor('#d5dee7'), 0.6, r=3)
    _txt(d, 38, 24, 'U1 的 OUT0/1 与 OUT2/3 位于 QFN 相对两侧，故输出 SMA 排在上下两边，'
                    'U1 居中、上下留出纯净出线通道', 6.5, BOLD, DARK)
    _txt(d, 38, 13, 'DC-DC 与 OCXO 置于对角，物理距离最大化；参考输入与 USB 分居左右，'
                    '不侵入输出走线区', 6.5, FONT, DARK)
    return d



# ------------------------------------------------------- 图：网络类与布线规则

def pcb_netclass():
    """网络类划分与线宽 / 间距 / 过孔规则的对应。"""
    d = Drawing(W, 220)
    heads = [(14, '网络类'), (96, '成员网络'), (250, '线宽'), (314, '间距'), (378, '过孔')]
    for x, t in heads:
        _txt(d, x, 220 - 14, t, 8, BOLD, ACCENT)
    d.add(Line(6, 220 - 20, 474, 220 - 20, strokeColor=ACCENT, strokeWidth=0.8))

    rows = [
        (RED, 'CLK_DIFF', 'OUT0～OUT3 共 8 对差分', '0.2 mm', '对内 0.2', '禁用',
         '100 Ω 差分；全程走 L1，对与对之间 ≥ 0.6 mm（3W）'),
        (RED, 'RF_50', 'XO_P、PRIREF', '0.36 mm', '≥ 0.72', '禁用',
         '50 Ω 单端微带；计算时 H 取 0.2104 mm，不是板厚 1.6 mm'),
        (AMBER, 'PWR_5V', 'VBUS、+5V_OCXO', '≥ 0.5，建议 1.0', '0.3 mm', '0.8 / 0.4',
         '冷启动 1.43 A；1.0 mm 外层 1 oz 在 ΔT=20 ℃ 下可过 3.2 A'),
        (AMBER, 'PWR_3V3', '+3.3V 与七路磁珠分支', '0.5 mm', '0.3 mm', '0.8 / 0.4',
         '负载 0.65 A；主干靠 L3 铜皮，只有分支才用走线'),
        (ACCENT, 'Default', 'I2C、GPIO、STATUS', '0.2 mm', '0.2 mm', '0.6 / 0.3',
         '低速信号，统一收到 L4'),
    ]
    y = 220 - 26
    for col, name, member, tw, gap, via, note in rows:
        y -= 34
        _box(d, 6, y, 468, 32, colors.white, colors.HexColor('#d5dee7'), 0.6, r=3)
        d.add(Rect(6, y, 3.5, 32, fillColor=col, strokeColor=col))
        _txt(d, 14, y + 20, name, 8, BOLD, col)
        _txt(d, 96, y + 20, member, 7.5, FONT, DARK)
        _txt(d, 250, y + 20, tw, 7.5, BOLD, DARK)
        _txt(d, 314, y + 20, gap, 7.5, FONT, DARK)
        _txt(d, 378, y + 20, via, 7.5, FONT, DARK)
        _txt(d, 96, y + 7, note, 6.5, FONT, GREY)

    _txt(d, 6, 14, '当前工程只有 Default 一个网络类——布线前必须先补齐前四类，'
                   '否则线宽全靠手动改，改一次就是全板返工。', 8, BOLD, RED)
    _txt(d, 6, 3, '过孔一栏的「禁用」指阻抗线不换层：换层会打断参考平面，'
                  '必须换时须在旁边补地过孔。', 7.5, FONT, GREY)
    return d


# ------------------------------------------------------- 图：制造输出与核对

def pcb_output():
    """制造输出文件与投板前的核对闭环。"""
    d = Drawing(W, 256)

    _box(d, 6, 60, 156, 176, colors.HexColor('#f8fafb'), ACCENT, 0.9, r=4)
    _txt(d, 84, 220, 'KiCad 导出', 9, BOLD, ACCENT, 'middle')
    items = [('Gerber ×9 层', 'F/In1/In2/B.Cu、阻焊、丝印、Edge.Cuts'),
             ('钻孔文件', 'PTH + NPTH，Excellon 格式'),
             ('贴片坐标', 'Pos，CSV，元件中心 + 旋转角'),
             ('BOM', '位号 + 型号 + 封装 + 数量')]
    y = 206
    for name, sub in items:
        y -= 38
        _box(d, 16, y, 136, 32, colors.white, colors.HexColor('#94a7b8'), 0.7, r=3)
        _txt(d, 24, y + 19, name, 7.8, BOLD, DARK)
        _txt(d, 24, y + 7, sub, 6.1, FONT, GREY)

    _arrow(d, 166, 148, 186, 148, ACCENT, 1.1)

    _box(d, 190, 118, 108, 60, colors.HexColor('#eef3f8'), ACCENT, 0.9, r=4)
    _txt(d, 244, 160, 'ZIP 打包', 9, BOLD, ACCENT, 'middle')
    _txt(d, 244, 144, '归入 hardware/gerber/', 6.5, FONT, GREY, 'middle')
    _txt(d, 244, 130, '按 v1.0 版本号命名', 6.5, FONT, GREY, 'middle')

    _arrow(d, 302, 148, 322, 148, ACCENT, 1.1)

    _box(d, 326, 60, 150, 176, colors.HexColor('#f7fbf8'), GREEN, 0.9, r=4)
    _txt(d, 401, 220, '投板前核对', 9, BOLD, GREEN, 'middle')
    checks = [('板框', '90 × 90 mm，Edge.Cuts 闭合'),
              ('层序', 'F.Cu / In1 / In2 / B.Cu'),
              ('叠层', 'JLC04161H-7628，1.6 mm'),
              ('阻抗', '备注写明 50 Ω / 100 Ω 及所在层'),
              ('丝印', '极性与 1 脚标记未被焊盘盖住')]
    y = 206
    for name, sub in checks:
        y -= 30
        d.add(Rect(334, y + 10, 8, 8, fillColor=colors.white,
                   strokeColor=GREEN, strokeWidth=0.8))
        _txt(d, 338, y + 12, '✓', 7, BOLD, GREEN, 'middle')
        _txt(d, 348, y + 17, name, 7.5, BOLD, DARK)
        _txt(d, 348, y + 6, sub, 6.1, FONT, GREY)

    _txt(d, 6, 30, '嘉立创免费打样只认常规工艺：阻抗按 ±20% 管控，'
                   '需要 ±10% 精密阻抗要单独下单并额外付费。', 7.5, FONT, DARK)
    _txt(d, 6, 17, '四层板必须在下单页面手动指定叠层型号，默认叠层的介质厚度与'
                   '阻抗计算依据不一致。', 7.5, BOLD, RED)
    _txt(d, 6, 4, 'Gerber 一旦发出就不可撤回——核对清单五项逐条打勾，'
                  '比返工一版便宜得多。', 7.5, FONT, GREY)
    return d


FIGURES = {
    'flow': flow,
    'stackup': stackup,
    'microstrip': microstrip,
    'priority': priority,
    'refplane': refplane,
    'layout': layout,
    'sch_flow': sch_flow,
    'sch_connect': sch_connect,
    'sch_hierarchy': sch_hierarchy,
    'sch_dataflow': sch_dataflow,
    'sch_erc': sch_erc,
    'ocxo_vctrl': ocxo_vctrl,
    'ocxo_vsel': ocxo_vsel,
    'ocxo_ptree': ocxo_ptree,
    'lvds_out_ac': lvds_out_ac,
    'lvds_out_load': lvds_out_load,
    'xo_tap': xo_tap,
    'xo_split_cmp': xo_split_cmp,
    'ocxo_buckboost': ocxo_buckboost,
    'ocxo_bb_layout': ocxo_bb_layout,
    'clk_layout': clk_layout,
    'pcb_netclass': pcb_netclass,
    'pcb_output': pcb_output,
}


def make(name, caption=''):
    """返回可插入 story 的 flowable 列表。"""
    if name not in FIGURES:
        raise SystemExit('[ERROR] 未定义的插图: %s（可用: %s）'
                         % (name, ', '.join(sorted(FIGURES))))
    out = [Spacer(1, 4), FIGURES[name]()]
    if caption:
        out.append(Paragraph(caption, CAP))
    else:
        out.append(Spacer(1, 8))
    return out
