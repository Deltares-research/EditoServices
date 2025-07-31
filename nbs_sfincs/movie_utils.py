import os
from os.path import join
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import animation

def make_movie_from_pngs(folder, fps=4):
    def update(frame):
        img.set_data(images[frame])
        return img

    png_files = sorted([f.path for f in os.scandir(folder) if f.is_file() and f.name.endswith(".png")])
    images = [Image.open(p) for p in png_files]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.set_axis_off()
    img = ax.imshow(images[0])
    
    ani = animation.FuncAnimation(fig, update, frames=len(images), interval=200, blit=False)
    ani.save(join(folder, 'output_movie.mp4'), writer='ffmpeg', fps=fps, dpi=300)

    plt.close(fig)  # ✅ Prevents unwanted figure display in notebook