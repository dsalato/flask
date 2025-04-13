import numpy as np
import matplotlib.pyplot as plt
import io

# Функция визуализации распределения цветов в изображении
def plot_color_distribution(img, title):
    # Создание графика с тремя гистограммами (RGB)
    plt.figure(figsize=(10, 4))

    # Построение гистограмм для каждого цветового канала
    for i, color in enumerate(['red', 'green', 'blue']):
        hist = np.array(img)[:, :, i].flatten()
        plt.hist(hist, bins=256, color=color, alpha=0.5, label=color.upper())

    # Настройка отображения графика
    plt.title(f'Распределение цветов - {title}')
    plt.xlabel('Значение цвета')
    plt.ylabel('Значение в пикселях')
    plt.legend()

    # Сохранение графика в буфер и возврат
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf