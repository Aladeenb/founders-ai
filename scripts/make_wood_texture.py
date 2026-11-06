"""Generate the Fahem & Wasel bright wood texture (original, replaces the wood theme's photo): a seamless 512x512 tile, deterministic for a seed.
Every wave uses an integer number of cycles per tile, so the tile repeats with no seam."""
import numpy as np
from PIL import Image

def periodic_noise(rng, n, kx_max, ky_max, terms, falloff=1.2):
    y, x = np.mgrid[0:n, 0:n] / n
    out = np.zeros((n, n))
    for _ in range(terms):
        kx = rng.integers(0, kx_max + 1); ky = rng.integers(1, ky_max + 1)
        amp = 1.0 / (np.hypot(kx, ky) ** falloff)
        out += amp * np.cos(2 * np.pi * (kx * x + ky * y) + rng.uniform(0, 2 * np.pi))
    out -= out.min(); return out / out.max()

def make(seed=11, n=512, path="brand/assets/wood-bright.jpg"):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n] / n
    warp = periodic_noise(rng, n, 1, 2, 8) - 0.5             # slow bends that vary the gap between grain lines
    rings = 0.5 + 0.5 * np.sin(2 * np.pi * (9 * y + 0.9 * warp))  # 9 grain bands per tile
    fine = periodic_noise(rng, n, 1, 120, 160, falloff=0.9)  # fine fiber streaks, nearly horizontal
    v = 0.5 * rings ** 6 + 0.5 * fine                        # rings to the 6th: thin darker lines, wide light wood
    v = (v - v.min()) / (v.max() - v.min())
    light = np.array([253, 249, 241]); dark = np.array([233, 220, 199])   # pale birch range
    rgb = light[None, None, :] * (1 - v[..., None]) + dark[None, None, :] * v[..., None]
    Image.fromarray(rgb.round().astype("uint8")).save(path, quality=82, optimize=True)
    return path

if __name__ == "__main__":
    print(make())
