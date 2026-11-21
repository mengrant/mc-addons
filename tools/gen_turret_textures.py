# -*- coding: utf-8 -*-
"""绘制炮台方块贴图（16x16 像素风）：顶面炮塔转台、侧面钢甲、底面。"""
import os
import random
from PIL import Image, ImageDraw

RP = r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\0cf98d1c1ee64894b9a94f12e40560fb\resource_pack_dafe51bb"
OUT = os.path.join(RP, "textures", "blocks")
os.makedirs(OUT, exist_ok=True)

# 调色板
DARK = (36, 41, 48)
BASE = (37, 42, 50)
STEEL = (96, 105, 121)
STEEL_HI = (124, 134, 152)
STEEL_LO = (62, 69, 80)
BOLT = (138, 148, 166)
HOLE = (18, 22, 27)
HAZ_Y = (224, 179, 58)
HAZ_K = (32, 36, 42)
RED = (226, 74, 59)
GREEN = (74, 200, 120)

random.seed(20261114)


def noise(draw, x0, y0, x1, y1, base, amp=6):
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = random.randint(-amp, amp)
            draw.point((x, y), tuple(max(0, min(255, c + d)) for c in base))


def circle_fill(draw, cx, cy, r, color):
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                draw.point((x, y), color)


def ring(draw, cx, cy, r_out, r_in, color):
    for y in range(16):
        for x in range(16):
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if r_in * r_in < d2 <= r_out * r_out:
                draw.point((x, y), color)


# ---------------- 顶面：炮塔转台 ----------------
top = Image.new("RGB", (16, 16), BASE)
d = ImageDraw.Draw(top)
noise(d, 0, 0, 16, 16, BASE, 7)

# 外圈底座
circle_fill(d, 7.5, 7.5, 7.4, STEEL_LO)
circle_fill(d, 7.5, 7.5, 6.6, STEEL)
# 外圈高光（左上）
for (x, y) in [(3, 3), (4, 2), (5, 2), (2, 4), (2, 5), (3, 4)]:
    d.point((x, y), STEEL_HI)
# 外圈暗部（右下）
for (x, y) in [(12, 12), (11, 13), (12, 11), (13, 11), (11, 12)]:
    d.point((x, y), STEEL_LO)

# 内转台
circle_fill(d, 7.5, 7.5, 4.9, (48, 54, 63))
circle_fill(d, 7.5, 7.5, 4.2, (56, 63, 73))

# 炮管口（中央 3x3）与口沿高光
for y in range(6, 9):
    for x in range(6, 9):
        d.point((x, y), HOLE)
d.point((6, 6), (108, 118, 136))
d.point((7, 6), (108, 118, 136))

# 两侧弹匣
for x in (2, 3, 12, 13):
    for y in range(6, 10):
        d.point((x, y), (38, 43, 51))
d.point((2, 6), (86, 94, 108))
d.point((12, 6), (86, 94, 108))

# 转台螺栓
for (x, y) in [(4, 4), (11, 4), (4, 11), (11, 11)]:
    d.point((x, y), BOLT)

# 状态灯
d.point((11, 12), GREEN)
d.point((12, 12), (40, 120, 74))

# 外圈刻线（每 90°）
for (x, y) in [(7, 0), (8, 0), (7, 15), (8, 15), (0, 7), (0, 8), (15, 7), (15, 8)]:
    d.point((x, y), (96, 106, 122))

top.save(os.path.join(OUT, "turret_top.png"))

# ---------------- 侧面：钢甲 + 警示条 ----------------
side = Image.new("RGB", (16, 16), (69, 76, 87))
d = ImageDraw.Draw(side)
noise(d, 0, 0, 16, 14, (69, 76, 87), 6)

# 顶沿高光
for x in range(16):
    d.point((x, 0), (92, 101, 116))
# 横向接缝
for x in range(16):
    d.point((x, 5), (54, 60, 70))
    d.point((x, 10), (54, 60, 70))
# 铆钉
for (x, y) in [(2, 2), (13, 2), (2, 7), (13, 7), (2, 12), (13, 12)]:
    d.point((x, y), BOLT)
    d.point((x, y + 1), (52, 58, 68))
# 竖楞
for x in (7, 8):
    for y in range(1, 14):
        d.point((x, y), (60, 67, 78))

# 底部警示条（黄黑斜纹）
for y in range(14, 16):
    for x in range(16):
        d.point((x, y), HAZ_Y if ((x + y) // 2) % 2 == 0 else HAZ_K)

side.save(os.path.join(OUT, "turret_side.png"))

# ---------------- 底面 ----------------
bottom = Image.new("RGB", (16, 16), (38, 43, 50))
d = ImageDraw.Draw(bottom)
noise(d, 0, 0, 16, 16, (38, 43, 50), 5)
for x in range(16):
    d.point((x, 8), (30, 34, 40))
    d.point((x, 0), (48, 54, 62))
for (x, y) in [(3, 3), (12, 3), (3, 12), (12, 12)]:
    d.point((x, y), (78, 86, 100))
bottom.save(os.path.join(OUT, "turret_bottom.png"))

# ---------------- 预览 ----------------
S = 12
prev = Image.new("RGB", (3 * 16 * S + 2 * 16, 16 * S), (22, 22, 24))
for i, name in enumerate(("turret_top", "turret_side", "turret_bottom")):
    im = Image.open(os.path.join(OUT, name + ".png")).resize((16 * S, 16 * S), Image.NEAREST)
    prev.paste(im, (i * (16 * S + 16), 0))
prev.save(r"C:\Users\Jemmy\WorkBuddy\2026-10-17-13-14-00\.mcpwork\turret_tex_preview.png")
print("saved", OUT)
