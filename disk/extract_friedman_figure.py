"""Recover point sets from the figures on Friedman's archived circle page.

The 2026-08-23 prior-art work reconstructed Cantrell's configurations from these
figures, but committed only prose: no images, no code, no coordinates. All three
legs of the 2026-08-24 review flagged that as the one load-bearing claim nobody
could replay. This script is that missing artifact.

What the figures look like: a thin black circle outline, small filled black dots
for the points, and the minimum-area triangles filled in colour. Dots and the
outline are the same black, and the coloured triangles connect them, so naive
connected components merge everything into one blob. A single erosion removes
the one-pixel outline and the triangle edges while the filled dots survive.

Resolution is the hard limit: the circle is ~106 px in radius, so a dot centre
is good to ~0.5%, and a triangle area derived from three of them to a few
percent. That is enough to identify WHICH configuration a figure shows -- the
interior-radius signature is the discriminant -- and not enough to pin its
value. For the value, refine the extracted points under hard containment.

Usage:  python3 extract_friedman_figure.py friedman_figures/hc14b.gif ...
"""

from __future__ import annotations

import math
import sys
from collections import deque
from itertools import combinations

import numpy as np
from PIL import Image


def components(mask):
    height, width = mask.shape
    seen = np.zeros_like(mask, bool)
    found = []
    for i in range(height):
        for j in range(width):
            if mask[i, j] and not seen[i, j]:
                queue = deque([(i, j)])
                seen[i, j] = True
                blob = []
                while queue:
                    y, x = queue.popleft()
                    blob.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                                   (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            queue.append((ny, nx))
                found.append(blob)
    return found


def erode(mask):
    out = mask.copy()
    out[1:, :] &= mask[:-1, :]
    out[:-1, :] &= mask[1:, :]
    out[:, 1:] &= mask[:, :-1]
    out[:, :-1] &= mask[:, 1:]
    return out


def extract(path):
    """Return (points in the unit disk, circle radius in pixels)."""

    pixels = np.array(Image.open(path).convert("RGB")).astype(int)
    black = pixels.max(axis=2) < 90            # dots AND the outline
    ys, xs = np.nonzero(black)
    centre_y, centre_x = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    radius = ((ys.max() - ys.min()) + (xs.max() - xs.min())) / 4
    points = []
    for blob in components(erode(black)):      # the outline does not survive erosion
        if len(blob) < 2:
            continue
        y = float(np.mean([p[0] for p in blob]))
        x = float(np.mean([p[1] for p in blob]))
        points.append(((x - centre_x) / radius, -(y - centre_y) / radius))
    return points, radius


def minimum_area(points):
    return min(abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
               for a, b, c in combinations(points, 3))


def main(paths):
    for path in paths:
        points, radius = extract(path)
        radii = sorted(math.hypot(*p) for p in points)
        interior = [round(r, 3) for r in radii if r < 0.93]
        line = f"{path}: radius={radius:.1f}px  dots={len(points)}"
        if len(points) >= 3:
            line += f"  raw_min_area~{minimum_area(points):.4f}"
        print(line)
        print(f"    interior radii (the configuration's signature): {interior}")
        print(f"    on/near circle: {len(radii) - len(interior)}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["friedman_figures/hc14b.gif"])
