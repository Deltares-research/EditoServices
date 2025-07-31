import os
from os.path import join
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import display

def make_movie_from_pngs(folder, fps=4, show_first_frame=True):
    """
    Create a movie (MP4) from PNGs in a folder and optionally display the first frame.
    """
    print(f"🎞️ Creating movie from PNGs in: {folder}")

    png_files = sorted([
        f.path for f in os.scandir(folder)
        if f.is_file() and f.name.endswith(".png")
    ])
    if len(png_files) == 0:
        print("⚠️ No PNG files found. Skipping movie creation.")
        return

    images = [Image.open(p) for p in png_files]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.set_axis_off()
    img = ax.imshow(images[0])

    def update(frame):
        img.set_data(images[frame])
        return img

    ani = animation.FuncAnimation(fig, update, frames=len(images), interval=200 // fps, blit=False)
    out_path = join(folder, 'output_movie.mp4')
    ani.save(out_path, writer='ffmpeg', fps=fps, dpi=300)
    plt.close(fig)

    print(f"✅ Movie saved to: {out_path}")

    if show_first_frame:
        print("🖼️ Showing first frame...")
        plt.figure(figsize=(8, 4))
        plt.imshow(images[0])
        plt.axis('off')
        plt.title("First Frame of Animation")
        plt.tight_layout()
        plt.show()
