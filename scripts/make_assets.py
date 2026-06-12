#!/usr/bin/env python3
"""간다GO 브랜드 에셋 생성 — 파비콘·아이콘·OG 이미지.

한글 폰트가 없는 빌드 환경을 고려해 로고 텍스트는 라틴 표기(GANDA GO)를 쓴다.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

NAVY = (10, 17, 32, 255)        # #0a1120
NAVY_SOFT = (16, 26, 48, 255)
GOLD = (200, 162, 94, 255)      # #c8a25e
CREAM = (233, 215, 171, 255)    # #e9d7ab
GREY = (170, 180, 198, 255)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def monogram(size: int) -> Image.Image:
    """골드 이중 링 안에 G 모노그램."""
    s = size * 4  # 슈퍼샘플링 후 축소
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s // 2
    d.ellipse([0, 0, s - 1, s - 1], fill=NAVY)
    w = max(s // 28, 4)
    d.ellipse([w, w, s - 1 - w, s - 1 - w], outline=GOLD, width=w)
    r2 = int(s * 0.085)
    d.ellipse([r2, r2, s - 1 - r2, s - 1 - r2],
              outline=(200, 162, 94, 90), width=max(w // 4, 2))
    font = ImageFont.truetype(SERIF_BOLD, int(s * 0.52))
    bbox = d.textbbox((0, 0), "G", font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((c - tw / 2 - bbox[0], c - th / 2 - bbox[1]), "G",
           font=font, fill=CREAM)
    return img.resize((size, size), Image.LANCZOS)


def og_image():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # 은은한 방사형 배경
    for i, r in enumerate(range(520, 120, -100)):
        col = (16 + i * 2, 26 + i * 2, 48 + i * 3, 255)
        d.ellipse([W // 2 - r, 60 - r // 2, W // 2 + r, 60 + r // 2], fill=col)
    d.rectangle([0, 0, W, 14], fill=GOLD)
    d.rectangle([0, H - 14, W, H], fill=GOLD)

    mark = monogram(190)
    img.alpha_composite(mark, (W // 2 - 95, 78))

    f_brand = ImageFont.truetype(SERIF_BOLD, 96)
    f_sub = ImageFont.truetype(SANS, 30)
    f_tel = ImageFont.truetype(SANS, 34)

    def center(text, font, y, fill, tracking=0):
        if tracking:
            text = (" " * 1).join(text)  # 자간 효과
        bbox = d.textbbox((0, 0), text, font=font)
        d.text(((W - (bbox[2] - bbox[0])) / 2 - bbox[0], y), text,
               font=font, fill=fill)

    center("GANDA GO", f_brand, 310, CREAM)
    center("SEONGNAM PREMIUM VISITING CARE", f_sub, 448, GOLD, tracking=1)
    d.line([W // 2 - 170, 520, W // 2 + 170, 520], fill=(70, 80, 100), width=2)
    center("0508 - 202 - 4719", f_tel, 540, GREY)

    img.convert("RGB").save(os.path.join(ASSETS, "og-image.png"))


def icons():
    for size, name in [(512, "icon-512.png"), (192, "icon-192.png"),
                       (180, "apple-touch-icon.png"),
                       (32, "favicon-32.png"), (16, "favicon-16.png")]:
        monogram(size).save(os.path.join(ASSETS, name))
    base = monogram(48)
    base.save(os.path.join(ROOT, "favicon.ico"),
              sizes=[(16, 16), (32, 32), (48, 48)])


def favicon_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <circle cx="256" cy="256" r="246" fill="#0a1120"/>
  <circle cx="256" cy="256" r="237" fill="none" stroke="#c8a25e" stroke-width="18"/>
  <circle cx="256" cy="256" r="208" fill="none" stroke="#c8a25e" stroke-opacity="0.35" stroke-width="4"/>
  <text x="256" y="348" font-family="'DejaVu Serif', Georgia, 'Times New Roman', serif"
        font-size="270" font-weight="bold" fill="#e9d7ab" text-anchor="middle">G</text>
</svg>
"""
    with open(os.path.join(ASSETS, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    favicon_svg()
    icons()
    og_image()
    print("assets generated:", sorted(os.listdir(ASSETS)))
