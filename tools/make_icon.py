"""生成 2048 风格的应用程序图标 app.ico（多尺寸，含 16~256）。"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "app.ico")
SIZE = 512
BG = (237, 194, 46)       # 2048 标志性金色
FG = (249, 246, 242)      # 米白文字
BORDER = (211, 169, 31)


def load_font(size, bold=True):
    """优先用 Windows 常见黑体/雅黑粗体，找不到则用默认字体。"""
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc",      # 微软雅黑 Bold
        "C:/Windows/Fonts/msyh.ttc",        # 微软雅黑
        "C:/Windows/Fonts/arialbd.ttf",     # Arial Bold
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/simhei.ttf",      # 黑体
    ]
    if not bold:
        candidates = candidates[1:] + candidates[:1]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def main():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 圆角方块（带描边，经典 2048 棋子质感）
    radius = 92
    margin = 10
    draw.rounded_rectangle(
        [margin, margin, SIZE - margin, SIZE - margin],
        radius=radius,
        fill=BG,
        outline=BORDER,
        width=8,
    )
    # 顶部高光，增加立体感
    highlight = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.rounded_rectangle(
        [margin + 14, margin + 12, SIZE - margin - 14, SIZE * 0.38],
        radius=radius // 2,
        fill=(255, 255, 255, 46),
    )
    img = Image.alpha_composite(img, highlight)
    draw = ImageDraw.Draw(img)

    # 数字 "2048"
    text = "2048"
    font = load_font(150, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((SIZE - tw) / 2 - bbox[0], (SIZE - th) / 2 - bbox[1]),
        text,
        font=font,
        fill=FG,
    )

    # 输出多尺寸 ico
    img.save(OUT, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                                       (64, 64), (128, 128), (256, 256)])
    print("icon ->", OUT)


if __name__ == "__main__":
    main()
