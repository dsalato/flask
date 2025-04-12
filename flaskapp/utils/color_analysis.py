import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io


def plot_color_distribution(img, title):
    plt.figure(figsize=(10, 4))

    for i, color in enumerate(['red', 'green', 'blue']):
        hist = np.array(img)[:, :, i].flatten()
        plt.hist(hist, bins=256, color=color, alpha=0.5, label=color.upper())

    plt.title(f'Color Distribution - {title}')
    plt.xlabel('Color Value')
    plt.ylabel('Pixel Count')
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf