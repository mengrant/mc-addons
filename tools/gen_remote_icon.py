# -*- coding: utf-8 -*-
"""生成炮塔遥控器的 16x16 物品图标。"""
import os
from PIL import Image

OUT = r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\0cf98d1c1ee64894b9a94f12e40560fb\resource_pack_dafe51bb\textures\items\turret_remote.png"
PREVIEW = r"C:\Users\Jemmy\WorkBuddy\2026-10-17-13-14-00\.mcpwork\remote_icon_preview.png"

EDGE = (22, 25, 31)
BODY = (62, 70, 82)
BODY_HI = (94, 104, 119)
BODY_LO = (39, 44, 53)
SCREEN = (54, 210, 178)
SCREEN_D = (28, 148, 126)
METAL = (150, 159, 174)
RED = (212, 62, 52)
RED_HI = (240, 108, 92)
YELLOW = (238, 194, 62)


def rect(d, x1, y1, x2, y2, c):
    d.rectangle([x1, y1, x2, y2], fill=c)


im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
d = __import__("PIL.ImageDraw", fromlist=["ImageDraw"]).Draw(im)

# 天线：右侧斜出
for (x, y) in [(11, 2), (11, 3), (10, 3), (10, 4)]:
    d.point((x, y), METAL)
d.point((12, 1), RED_HI)
d.point((11, 1), RED)

# 机身
rect(d, 3, 4, 12, 14, EDGE)
rect(d, 4, 5, 11, 13, BODY)
rect(d, 4, 5, 11, 5, BODY_HI)      # 顶面高光
rect(d, 4, 13, 11, 13, BODY_LO)    # 底部暗面
rect(d, 3, 5, 3, 13, BODY_LO)      # 左侧暗边
rect(d, 12, 5, 12, 13, BODY_HI)    # 右侧亮边

# 屏幕
rect(d, 5, 6, 10, 9, EDGE)
rect(d, 5, 6, 10, 8, SCREEN)
rect(d, 5, 8, 10, 8, SCREEN_D)
d.point((6, 7), (200, 255, 240))
d.point((7, 7), (200, 255, 240))

# 按键：一红一黄
rect(d, 5, 10, 6, 12, RED)
d.point((5, 10), RED_HI)
rect(d, 9, 10, 10, 12, YELLOW)
d.point((9, 10), (255, 236, 160))

# 机身内的握持纹（不外凸）
for y in (10, 12):
    d.point((4, y), BODY_LO)
    d.point((11, y), BODY_HI)
# 顶部散热槽
for x in (6, 7, 8, 9):
    d.point((x, 5), BODY_LO)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
im.save(OUT)
print("saved", OUT, im.size)

scale = 18
prev = Image.new("RGB", (16 * scale + 40, 16 * scale + 40), (26, 28, 32))
prev.paste(im.resize((16 * scale, 16 * scale), Image.NEAREST), (20, 20), im.resize((16 * scale, 16 * scale), Image.NEAREST))
prev.save(PREVIEW)
print("preview", PREVIEW)
