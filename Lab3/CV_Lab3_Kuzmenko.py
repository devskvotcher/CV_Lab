import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Глобальные переменные
image = None
results = []


def mse(imageA, imageB):
    return np.mean((imageA - imageB) ** 2)


def update(val):
    global image

    if image is None:
        return

    quality = int(val)
    _, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    compressed_image = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)


    cv2.imshow("Compressed Image", compressed_image)


def build_graphs_and_save():
    global image, results

    if image is None:
        print("Пожалуйста, загрузите изображение!")
        return

    qualities = list(range(0, 105, 5))
    mse_values, psnr_values, ssim_values = [], [], []

    for quality in qualities:
        _, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        decoded = cv2.imdecode(encoded, cv2.IMREAD_GRAYSCALE)

        mse_value = mse(image, decoded)
        psnr_value = psnr(image, decoded, data_range=image.max() - image.min())
        ssim_value = ssim(image, decoded, data_range=image.max() - image.min())

        mse_values.append(mse_value)
        psnr_values.append(psnr_value)
        ssim_values.append(ssim_value)


    df = pd.DataFrame({
        "Quality": qualities,
        "MSE": mse_values,
        "PSNR": psnr_values,
        "SSIM": ssim_values
    })
    results.append(df)


    df.to_csv("image_metrics.csv", index=False)
    print("Результаты сохранены в файл image_metrics.csv")


    plt.figure(figsize=(12, 8))


    plt.subplot(3, 1, 1)
    plt.plot(qualities, mse_values, marker='o')
    plt.title("MSE при различном JPEG-сжатии")
    plt.xlabel("Качество JPEG")
    plt.ylabel("MSE")
    plt.grid(True)

    # PSNR
    plt.subplot(3, 1, 2)
    plt.plot(qualities, psnr_values, marker='o')
    plt.title("PSNR при различном JPEG-сжатии")
    plt.xlabel("Качество JPEG")
    plt.ylabel("PSNR (dB)")
    plt.grid(True)

    # SSIM
    plt.subplot(3, 1, 3)
    plt.plot(qualities, ssim_values, marker='o')
    plt.title("SSIM при различном JPEG-сжатии")
    plt.xlabel("Качество JPEG")
    plt.ylabel("SSIM")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def drop_image(event):
    global image
    file_path = event.data.strip().strip('{').strip('}')
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return

    cv2.imshow("Original Image", image)

root = TkinterDnD.Tk()
root.title("Перетащите изображение сюда")
root.geometry("300x400")
label_instruction = tk.Label(root, text="Перетащите изображение сюда", font=("Arial", 14), wraplength=250, justify="center")
label_instruction.pack(pady=20)
quality_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Качество JPEG", command=update)
quality_slider.pack(pady=10)
build_graphs_button = tk.Button(root, text="Построить графики и сохранить", command=build_graphs_and_save, font=("Arial", 12))
build_graphs_button.pack(pady=20)
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_image)
root.mainloop()
cv2.destroyAllWindows()
