# -*- coding: utf-8 -*-
"""生成 4 个方向的传送带贴图（顶面 8 帧动画 + 共用侧面/底面）。"""
import os
from PIL import Image

RP = r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\5c73955f25334332a81ffd8dec4e960a\resource_pack_rJIjDXWG\textures\blocks"
OUT = r"C:\Users\Jemmy\WorkBuddy\2026-10-17-13-14-00\.mcpwork"

W = H = 16
FRAMES = 8
STEP = 2          # 每帧位移像素
PERIOD = 16       # 图案在流向方向上的循环周期（能整除 16，保证无缝）

RAIL = (108, 113, 121)
RAIL_D = (66, 70, 78)
RAIL_L = (140, 146, 155)
BELT = (40, 42, 46)
BELT_D = (30, 32, 36)
TREAD = (58, 61, 67)
CHEV = (226, 170, 40)
CHEV_D = (152, 110, 24)


def make_top(flow):
    """flow: 'north' | 'south' | 'east' | 'west'  -> 8 帧竖排图"""
    vertical = flow in ("north", "south")   # 流向沿纹理 v 轴
    base = Image.new("RGB", (W, H), BELT)
    px = base.load()

    for y in range(H):
        for x in range(W):
            # 导轨：贴两条沿流向的边
            edge = x if vertical else y
            if edge in (0, 15):
                px[x, y] = RAIL_D
            elif edge in (1, 14):
                px[x, y] = RAIL_L if edge == 1 else RAIL
            else:
                # 带面：沿流向排布的横棱，周期 4
                along = y if vertical else x
                m = along % 4
                px[x, y] = TREAD if m == 0 else (BELT_D if m == 3 else BELT)

    # 黄色雪佛龙：指向流向前方，沿流向每 8px 一组
    def put(x, y, c):
        if 2 <= x <= 13 and 2 <= y <= 13:
            base.putpixel((x, y), c)

    for start in (2, 10):
        for i in range(4):
            a = start + i
            if flow == "north":      # 指向 -v：^
                put(7 - i, a, CHEV); put(8 + i, a, CHEV)
            elif flow == "south":    # 指向 +v：v
                put(7 - i, 15 - a, CHEV); put(8 + i, 15 - a, CHEV)
            elif flow == "east":     # 指向 +u：>
                put(15 - a, 7 - i, CHEV); put(15 - a, 8 + i, CHEV)
            else:                    # west：<
                put(a, 7 - i, CHEV); put(a, 8 + i, CHEV)

    # 生成 8 帧：图案沿流向逐步位移
    strip = Image.new("RGB", (W, H * FRAMES), BELT)
    for f in range(FRAMES):
        off = (f * STEP) % PERIOD
        fr = Image.new("RGB", (W, H))
        for y in range(H):
            for x in range(W):
                if flow == "north":
                    sx, sy = x, (y + off) % H
                elif flow == "south":
                    sx, sy = x, (y - off) % H
                elif flow == "east":
                    sx, sy = (x - off) % W, y
                else:
                    sx, sy = (x + off) % W, y
                fr.putpixel((x, y), base.getpixel((sx, sy)))
        strip.paste(fr, (0, f * H))
    return strip


def make_side():
    """侧面：上下金属框 + 中间橡胶带 + 斜纹"""
    im = Image.new("RGB", (W, H), RAIL)
    px = im.load()
    for y in range(H):
        for x in range(W):
            if y < 3 or y > 12:
                px[x, y] = RAIL if (y in (1, 14)) else RAIL_D
            else:
                px[x, y] = BELT
    for x in range(W):
        if (x % 4) == 0:
            for y in range(3, 3):
                pass
    # 斜向传动纹
    for x in range(W):
        for y in range(3, 13):
            if (x + y) % 4 == 0:
                px[x, y] = TREAD
    # 铆钉
    for x in (2, 13):
        for y in (1, 14):
            px[x, y] = RAIL_L
    return im


def make_bottom():
    im = Image.new("RGB", (W, H), (58, 58, 62))
    px = im.load()
    for y in range(H):
        for x in range(W):
            if x in (0, 15) or y in (0, 15):
                px[x, y] = (40, 40, 44)
            elif (x + y) % 8 == 0:
                px[x, y] = (48, 48, 52)
    for x in (3, 12):
        for y in (3, 12):
            px[x, y] = (86, 86, 92)
    return im


if __name__ == "__main__":
    for d in ("north", "south", "east", "west"):
        p = os.path.join(RP, "conveyor_belt_top_%s.png" % d)
        make_top(d).save(p)
        print("saved", p)
    make_side().save(os.path.join(RP, "conveyor_belt_side.png"))
    make_bottom().save(os.path.join(RP, "conveyor_belt_bottom.png"))
    print("side/bottom saved")

    # 预览：4 方向帧序列横向展开
    dirs = ("north", "south", "east", "west")
    cell = W * 5
    gap = 6
    prev = Image.new("RGB", (len(dirs) * (cell * 4 + 3 * gap + 20), H * 5 + 40), (24, 24, 26))
    for di, d in enumerate(dirs):
        strip = make_top(d)
        ox = di * (cell * 4 + 3 * gap + 20)
        for f in range(4):
            fr = strip.crop((0, f * H, W, (f + 1) * H)).resize((cell, H * 5), Image.NEAREST)
            prev.paste(fr, (ox + f * (cell + gap), 30))
    prev.save(os.path.join(OUT, "belt_4dir_preview.png"))
    print("preview saved")
