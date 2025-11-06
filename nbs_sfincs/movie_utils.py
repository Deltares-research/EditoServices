import os
from os.path import join
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import PillowWriter

def make_movie_from_pngs(folder, fps=4, show_first_frame=False):
    print(f"🎞️ Creating GIF from PNGs in: {folder}")

    png_files = sorted([
        f.path for f in os.scandir(folder)
        if f.is_file() and f.name.lower().endswith(".png")
    ])
    if not png_files:
        print("⚠️ No PNG files found. Skipping movie creation.")
        return

    # Load frames (close PIL handles to avoid leaks)
    frames = []
    for p in png_files:
        im = Image.open(p)
        frames.append(np.asarray(im))
        im.close()

    fig, ax = plt.subplots(figsize=(8, 4), dpi=200)  # smaller dpi keeps GIF size down
    ax.set_axis_off()
    img = ax.imshow(frames[0])

    def update(i):
        img.set_data(frames[i])
        return (img,)

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames),
        interval=1000.0 / fps, blit=False
    )

    out_path = join(folder, "output_movie.gif")
    ani.save(out_path, writer=PillowWriter(fps=fps), dpi=200)
    plt.close(fig)

    print(f"✅ GIF saved to: {out_path}")

    if show_first_frame:
        print("🖼️ Showing first frame...")
        plt.figure(figsize=(8, 4), dpi=200)
        plt.imshow(frames[0])
        plt.axis('off')
        plt.tight_layout()
        plt.show()
