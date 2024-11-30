import cv2
import numpy as np
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import matplotlib.pyplot as plt


# Глобальные переменные
images = []  # Список изображений
result_image = None  # Итоговое изображение


# Функция для загрузки изображений
def drop_images(event):
    global images
    file_paths = event.data.strip().strip('{').strip('}').split(' ')
    for file_path in file_paths:
        image = cv2.imread(file_path)
        if image is not None:
            images.append(image)
    print(f"Загружено изображений: {len(images)}")
    tk.Label(root, text=f"Загружено изображений: {len(images)}", font=("Arial", 12)).pack()


# Функция для склейки изображений
def stitch_images():
    global images, result_image

    if len(images) < 2:
        print("Необходимо минимум два изображения!")
        return

    # Используем OpenCV Stitcher
    stitcher = cv2.Stitcher_create()
    status, result_image = stitcher.stitch(images)

    if status == cv2.Stitcher_OK:
        print("Изображения успешно склеены!")
        cv2.imshow("Result", result_image)
        cv2.imwrite("stitched_result.jpg", result_image)
        print("Результат сохранён как stitched_result.jpg")
    else:
        print("Ошибка при склеивании изображений:", status)


# Функция для отображения результата
def show_result():
    global result_image

    if result_image is None:
        print("Результат отсутствует!")
        return

    # Отображение изображения через Matplotlib
    result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
    plt.imshow(result_rgb)
    plt.title("Склеенное изображение")
    plt.axis('off')
    plt.show()


# Графический интерфейс
root = TkinterDnD.Tk()
root.title("Склейка изображений")
root.geometry("400x300")

# Инструкция для пользователя
label_instruction = tk.Label(root, text="Перетащите изображения для склейки", font=("Arial", 14), wraplength=300, justify="center")
label_instruction.pack(pady=20)

# Кнопка для запуска склейки
stitch_button = tk.Button(root, text="Склеить изображения", command=stitch_images, font=("Arial", 12))
stitch_button.pack(pady=10)

# Кнопка для отображения результата
result_button = tk.Button(root, text="Показать результат", command=show_result, font=("Arial", 12))
result_button.pack(pady=10)

# Добавление функциональности для перетаскивания
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_images)

# Запуск основного цикла Tkinter
root.mainloop()

# Уничтожение окон OpenCV
cv2.destroyAllWindows()
