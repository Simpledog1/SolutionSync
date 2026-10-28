"""Draw the SolutionSync brand mark (the dashboard's sidebar logo) into assets/solsync.ico.

Standard library only: rasterises the same shapes as the SVG mark in dashboard.html
(teal rounded square, sea-foam wave, light upload arrow) and writes a PNG-based ICO.
    py scripts\\make_icon.py
"""
import math
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "solsync.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]
TEAL, FOAM, LIGHT = (0x16, 0x4A, 0x5B), (0x4F, 0xC1, 0xA8), (0xE2, 0xEF, 0xEA)

# Shapes in the SVG's 32x32 viewBox
WAVE = [(x / 4, 19.75 + 1.25 * math.cos(2 * math.pi * (x / 4 - 6) / 10)) for x in range(24, 105)]
ARROW = [((16, 6), (16, 15)), ((12.5, 9.5), (16, 6)), ((16, 6), (19.5, 9.5))]
STROKE = 2.2 / 2


def seg_dist(px, py, a, b):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def in_rounded_rect(x, y, x0=1, y0=1, x1=31, y1=31, r=7):
    cx, cy = min(max(x, x0 + r), x1 - r), min(max(y, y0 + r), y1 - r)
    return x0 <= x <= x1 and y0 <= y <= y1 and math.hypot(x - cx, y - cy) <= r


def color_at(x, y):
    """RGBA of the mark at viewBox point (x, y)."""
    if not in_rounded_rect(x, y):
        return (0, 0, 0, 0)
    if any(seg_dist(x, y, a, b) <= STROKE for a, b in ARROW):
        return (*LIGHT, 255)
    if 18 <= y <= 22 and any(seg_dist(x, y, WAVE[i], WAVE[i + 1]) <= STROKE for i in range(len(WAVE) - 1)):
        return (*FOAM, 255)
    return (*TEAL, 255)


def render(size, ss=3):
    """Supersampled ss x ss per pixel for smooth edges at small sizes."""
    rows = []
    for py in range(size):
        row = bytearray()
        for px in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = color_at((px + (sx + .5) / ss) * 32 / size, (py + (sy + .5) / ss) * 32 / size)
                    for i in range(3):
                        acc[i] += c[i] * c[3]
                    acc[3] += c[3]
            a = acc[3] / (ss * ss)
            row += bytes([round(acc[i] / acc[3]) if acc[3] else 0 for i in range(3)] + [round(a)])
        rows.append(bytes(row))
    return rows


def png(size, rows):
    raw = b"".join(b"\x00" + r for r in rows)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    images = [png(s, render(s, 4 if s <= 32 else 2)) for s in SIZES]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    for s, data in zip(SIZES, images):
        entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(header + entries + b"".join(images))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
