"""生成项目横幅 banner.png（浅色背景 + 深色棋盘 + 金色 2048）。"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "banner.png")
W, H = 1200, 480
BG = (250, 248, 239)
CELL = (238, 228, 218)
TILE_BG = (237, 194, 46)
TILE_FG = (249, 246, 242)
GAP = 18
SIZE = 4

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)


def load_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    if not bold:
        candidates = candidates[1:] + candidates[:1]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


# 棋盘（右侧）
board_size = 360
x0, y0 = W - board_size - 90, (H - board_size) // 2
draw.rounded_rectangle([x0 - 10, y0 - 10, x0 + board_size + 10, y0 + board_size + 10],
                       radius=24, fill=(187, 173, 160))
cell = (board_size - GAP * (SIZE + 1)) // SIZE
grid = [
    [2, 4, 8, 16],
    [32, 64, 128, 256],
    [512, 1024, 2048, 4],
    [8, 16, 32, 64],
]
for r in range(SIZE):
    for c in range(SIZE):
        cx = x0 + GAP + c * (cell + GAP)
        cy = y0 + GAP + r * (cell + GAP)
        v = grid[r][c]
        # 按数值取近似经典配色
        if v <= 4:
            tbg, fg = (238, 228, 218), (119, 110, 101)
        elif v <= 64:
            tbg, fg = (245, 149, 99), (249, 246, 242)
        elif v <= 256:
            tbg, fg = (237, 204, 97), (249, 246, 242)
        else:
            tbg, fg = TILE_BG, TILE_FG
        draw.rounded_rectangle([cx, cy, cx + cell, cy + cell], radius=10, fill=tbg)
        fsize = cell * (0.42 if v < 1000 else 0.34)
        font = load_font(int(fsize), bold=True)
        text = str(v)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((cx + (cell - tw) / 2 - bbox[0], cy + (cell - th) / 2 - bbox[1]),
                  text, font=font, fill=fg)

# 标题（左侧）
font_title = load_font(96, bold=True)
draw.text((60, 120), "2048", font=font_title, fill=(119, 110, 101))
font_arena = load_font(64, bold=True)
draw.text((60, 240), "Arena-1", font=font_arena, fill=(237, 194, 46))
font_sub = load_font(30, bold=False)
draw.text((60, 340), "AI 自动玩 · 双排行榜 · 桌面版", font=font_sub, fill=(119, 110, 101))

img.save(OUT)
print("banner ->", OUT)


if __name__ == "__main__":
    main() if False else None
