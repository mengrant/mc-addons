# -*- coding: utf-8 -*-
"""生成不死图腾堆叠模组的包图标（16x16 像素风放大到 256x256）。"""
from PIL import Image

GOLD = (232, 194, 74, 255)
GOLD_D = (169, 130, 43, 255)
GOLD_L = (250, 226, 150, 255)
GEM = (47, 191, 113, 255)
GEM_D = (26, 122, 71, 255)
BG = (24, 38, 46, 255)
BG2 = (33, 51, 61, 255)

W = 16
img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
px = img.load()

# 背景：圆角深色块 + 四角留空
for y in range(W):
    for x in range(W):
        corner = (x < 1 or x > W - 2) and (y < 1 or y > W - 2)
        if corner:
            continue
        px[x, y] = BG2 if 1 <= y <= 2 else BG

# 图腾柱身
for y in range(2, 14):
    for x in range(5, 11):
        px[x, y] = GOLD
# 头部略宽
for y in range(2, 8):
    px[4, y] = GOLD
    px[11, y] = GOLD
# 头顶两只角
for y in range(0, 3):
    px[4, y] = GOLD_D
    px[11, y] = GOLD_D
px[3, 1] = GOLD_D
px[12, 1] = GOLD_D
# 高光
for y in range(3, 13):
    px[5, y] = GOLD_L
# 眼睛（祖母绿宝石）
for y in (4, 5):
    px[6, y] = GEM
    px[9, y] = GEM
px[6, 4] = GEM_D
px[9, 4] = GEM_D
# 嘴 / 下巴纹路
for x in range(7, 9):
    px[x, 7] = GOLD_D
px[7, 10] = GOLD_D
px[8, 10] = GOLD_D
px[7, 11] = GOLD_D
px[8, 11] = GOLD_D
# 底部阴影
for x in range(5, 11):
    px[x, 13] = GOLD_D

out = img.resize((256, 256), Image.NEAREST)
for p in (r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\62dd8997bc9345d7afe2b8d2d0ea6af0\behavior_pack_mqyTKZzx\pack_icon.png",
          r"E:\MCStudioDownload\work\vv4u@163.com\Cpp\AddOn\62dd8997bc9345d7afe2b8d2d0ea6af0\resource_pack_QfZt549j\pack_icon.png",
          r"C:\Users\Jemmy\WorkBuddy\2026-10-17-13-14-00\.mcpwork\totem_pack_icon.png"):
    out.save(p)
    print("saved", p)
