"""Combine slide-01..12.png into a single Deal-Desk-Agent-deck.pdf."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
files = [os.path.join(HERE, f"slide-{i:02d}.png") for i in range(1, 13)]
imgs = [Image.open(f).convert("RGB") for f in files if os.path.exists(f)]
out = os.path.join(HERE, "Deal-Desk-Agent-deck.pdf")
imgs[0].save(out, save_all=True, append_images=imgs[1:], resolution=150.0)
print(f"{out}  ({len(imgs)} slides, {os.path.getsize(out)/1e6:.2f} MB)")
