"""Render the animated word-pair overlay as raw RGBA frames on stdout.

Usage: python3 overlay.py [--still t1,t2,...] > raw
The strip is BAND_H px tall and is composited at y=BAND_Y by ffmpeg.
"""
import sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS, DURATION = 30, 24.2
W, BAND_Y, BAND_H = 1080, 960, 280
SS = 2                                  # supersampling factor
PILL_W, PILL_H, GAP, RADIUS = 452, 126, 30, 40
CY = 1095 - BAND_Y                      # pill centre inside the strip
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"

NEUTRAL_FILL = (250, 249, 246)
NEUTRAL_TEXT = (28, 28, 30)
GREEN_FILL = (52, 178, 112)
GREEN_TEXT = (255, 255, 255)

# (left, right, chosen index, appear, select = speech onset, disappear)
PAIRS = [
    ("Brother", "Stomachache", 1, 0.10, 1.81, 3.20),
    ("Stomachache", "Typical", 1, 3.35, 4.95, 6.15),
    ("Typical", "Successfully", 1, 6.25, 7.69, 10.90),
    ("Successfully", "Business", 1, 11.05, 12.63, 14.40),
    ("Business", "Queue", 1, 14.55, 15.79, 17.05),
    ("Queue", "Bicycle", 0, 17.20, 18.73, 20.10),
    ("Queue", "Cucumber", 0, 20.25, 21.76, 99.0),
]

IN_DUR, OUT_DUR, SEL_DUR, STAGGER = 0.38, 0.28, 0.30, 0.07


def clamp(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def font_size():
    # one size for every pill so the whole video stays consistent
    words = {w for p in PAIRS for w in p[:2]}
    size = 62
    while size > 30:
        f = ImageFont.truetype(FONT, size * SS)
        if max(f.getlength(w) for w in words) <= (PILL_W - 70) * SS:
            return size
        size -= 1
    return size


FONT_OBJ = ImageFont.truetype(FONT, font_size() * SS)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_pill(canvas, word, cx, cy, alpha, green, scale, shine):
    """Draw one pill (supersampled) onto canvas centred at (cx, cy)."""
    if alpha <= 0.003:
        return
    w, h = PILL_W * scale * SS, PILL_H * scale * SS
    pad = 60 * SS
    tile = Image.new("RGBA", (int(w + 2 * pad), int(h + 2 * pad)), (0, 0, 0, 0))
    box = (pad, pad, pad + w, pad + h)
    r = RADIUS * scale * SS

    # soft shadow, turning into a gentle green glow once selected
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    shadow_col = mix((0, 0, 0), (40, 170, 100), green)
    shadow_a = round(95 + 40 * green)
    sd.rounded_rectangle((box[0], box[1] + 8 * SS, box[2], box[3] + 8 * SS), r, fill=shadow_col + (shadow_a,))
    sh = sh.filter(ImageFilter.GaussianBlur(16 * SS))
    tile.alpha_composite(sh)

    body = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle(box, r, fill=mix(NEUTRAL_FILL, GREEN_FILL, green) + (246,))
    # hairline inner border for a crisp edge
    bd.rounded_rectangle(box, r, outline=(255, 255, 255, round(70 + 40 * green)), width=2 * SS)

    if shine > 0:
        # short diagonal light sweep across the chosen pill
        sw = Image.new("L", tile.size, 0)
        swd = ImageDraw.Draw(sw)
        x = box[0] - 0.4 * w + shine * 1.8 * w
        band = 0.22 * w
        swd.polygon([(x, box[1]), (x + band, box[1]), (x + band - 0.35 * h, box[3]), (x - 0.35 * h, box[3])],
                    fill=round(80 * math.sin(math.pi * shine)))
        sw = sw.filter(ImageFilter.GaussianBlur(10 * SS))
        mask = Image.new("L", tile.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(box, r, fill=255)
        from PIL import ImageChops
        sw = ImageChops.multiply(sw, mask)
        white = Image.new("RGBA", tile.size, (255, 255, 255, 0))
        white.putalpha(sw)
        body.alpha_composite(white)

    f = FONT_OBJ if abs(scale - 1) < 1e-3 else ImageFont.truetype(FONT, max(1, round(FONT_OBJ.size * scale)))
    bd = ImageDraw.Draw(body)
    bd.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), word, font=f, anchor="mm",
            fill=mix(NEUTRAL_TEXT, GREEN_TEXT, green) + (255,))
    tile.alpha_composite(body)

    if alpha < 1:
        a = tile.getchannel("A").point(lambda v: round(v * alpha))
        tile.putalpha(a)
    canvas.alpha_composite(tile, (round(cx * SS - tile.width / 2), round(cy * SS - tile.height / 2)))


def render(t):
    canvas = Image.new("RGBA", (W * SS, BAND_H * SS), (0, 0, 0, 0))
    total = 2 * PILL_W + GAP
    centers = [(W - total) / 2 + PILL_W / 2, (W + total) / 2 - PILL_W / 2]
    for left, right, chosen, t_in, t_sel, t_out in PAIRS:
        if not (t_in <= t <= t_out + OUT_DUR):
            continue
        for i, word in enumerate((left, right)):
            k_in = ease_out((t - t_in - i * STAGGER) / IN_DUR)
            k_out = ease_in_out((t - t_out) / OUT_DUR)
            alpha = k_in * (1 - k_out)
            dy = (1 - k_in) * 26 + k_out * 18
            green, scale, shine = 0.0, 1.0, 0.0
            if i == chosen and t >= t_sel:
                s = (t - t_sel) / SEL_DUR
                green = ease_in_out(s)
                # pop 1.00 -> 1.06 -> settle at 1.035
                p = clamp((t - t_sel) / 0.45)
                scale = 1 + 0.035 * ease_out(p) + 0.025 * math.sin(math.pi * p)
                shine = clamp((t - t_sel - 0.12) / 0.55) if t - t_sel < 0.67 else 0.0
            scale *= 0.96 + 0.04 * k_in
            draw_pill(canvas, word, centers[i], CY + dy, alpha, green, scale, shine)
    return canvas.resize((W, BAND_H), Image.LANCZOS)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        for ts in sys.argv[2].split(","):
            render(float(ts)).save(f"still_{ts}.png")
    else:
        out = sys.stdout.buffer
        for n in range(round(DURATION * FPS)):
            out.write(render(n / FPS).tobytes())
