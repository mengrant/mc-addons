import os
from PIL import Image, ImageFilter

SRC = r"outputs/_raw-generations"
DST = r"outputs/conveyor-mod-images"
os.makedirs(DST, exist_ok=True)

JOBS = [
    ("Square_game_icon_of_exactly_on_2026-11-08T08-27-08.png", "1_component-icon_1000x1000.png", (1000, 1000)),
    ("Wide_16_9_promotional_banner_i_2026-11-08T08-23-17.png", "2_iteration-icon_992x558.png", (992, 558)),
    ("Product_shot_of_a_voxel_game_c_2026-11-08T08-23-47.png", "3_device_900x580.png", (900, 580)),
    ("Wide_16_9_isometric_voxel_dior_2026-11-08T08-22-56.png", "4_carousel-1_992x558.png", (992, 558)),
    ("Wide_16_9_voxel_game_scene__is_2026-11-08T08-25-10.png", "5_carousel-2_992x558.png", (992, 558)),
    ("Wide_16_9_voxel_game_scene_fro_2026-11-08T08-24-30.png", "6_carousel-3_992x558.png", (992, 558)),
]

def strip_watermark(im):
    from PIL import ImageOps
    W, H = im.size
    bw, bh = int(W * 0.17), int(H * 0.11)
    x1, y1 = W - bw, H - bh
    # 把紧邻左侧的区域水平镜像过来，边界像素连续，不会出现矩形色块
    src = im.crop((max(0, x1 - bw), y1, x1, y1 + bh))
    patch = ImageOps.mirror(src)
    if patch.size != (bw, bh):
        patch = patch.resize((bw, bh), Image.LANCZOS)
    patch = patch.filter(ImageFilter.GaussianBlur(1.2))
    mask = Image.new("L", (bw, bh), 255)
    feather = 12
    px = mask.load()
    for y in range(bh):
        for x in range(bw):
            dx = min(x, bw - 1 - x)
            if dy_top := y < feather:
                px[x, y] = int(255 * min(x, y) / feather) if y < feather else px[x, y]
            else:
                px[x, y] = 255
    # 仅上边做羽化，左右下贴边
    px2 = mask.load()
    for y in range(feather):
        for x in range(bw):
            v = int(255 * y / feather)
            if v < px2[x, y]:
                px2[x, y] = v
    im.paste(patch, (x1, y1), mask)
    return im

for src, dst_name, size in JOBS:
    p = os.path.join(SRC, src)
    im = Image.open(p).convert("RGB")
    # 居中裁剪到目标比例
    tw, th = size
    sr, tr = im.width / im.height, tw / th
    if sr > tr:
        nw = int(round(im.height * tr))
        im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
    else:
        nh = int(round(im.width / tr))
        im = im.crop((0, (im.height - nh) // 2, im.width, (im.height - nh) // 2 + nh))
    im = strip_watermark(im)
    im = im.resize(size, Image.LANCZOS)
    out = os.path.join(DST, dst_name)
    im.save(out, optimize=True)
    print("%-34s %dx%d  %6.1f KB" % (dst_name, im.width, im.height, os.path.getsize(out) / 1024))
