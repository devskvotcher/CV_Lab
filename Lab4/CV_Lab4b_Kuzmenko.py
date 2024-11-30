import cv2
import numpy as np
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Глобальная переменная для изображения
image = None

# Функция для поиска дорожных знаков
def detect_traffic_signs():
    global image

    if image is None:
        print("Пожалуйста, загрузите изображение!")
        return

    # Преобразуем изображение в HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Определяем диапазоны цветов для красного и синего
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([130, 255, 255])

    # Создаем маски для красного (включая два диапазона) и синего цветов
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Обработка маски для красных треугольных знаков
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    output_image = image.copy()

    for cnt in contours_red:
        # Аппроксимация контуров
        epsilon = 0.04 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) == 3 and 1000 < cv2.contourArea(cnt) < 50000:
            x, y, w, h = cv2.boundingRect(approx)
            cv2.drawContours(output_image, [approx], -1, (0, 255, 0), 3)
            cv2.putText(output_image, "Triangular Sign", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Обработка маски для синих прямоугольных знаков
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_blue:
        epsilon = 0.04 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) == 4 and 1000 < cv2.contourArea(cnt) < 50000:
            x, y, w, h = cv2.boundingRect(approx)
            cv2.drawContours(output_image, [approx], -1, (255, 0, 0), 3)
            cv2.putText(output_image, "Pedestrian Crossing", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Отображение результата
    cv2.imshow("Detected Traffic Signs", output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Функция для обработки перетаскивания изображения
def drop_image(event):
    global image
    file_path = event.data.strip().strip("{").strip("}")
    image = cv2.imread(file_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return

    # Автоматическое распознавание после загрузки
    detect_traffic_signs()

# Создание GUI с помощью TkinterDnD
root = TkinterDnD.Tk()
root.title("Поиск дорожных знаков")
root.geometry("300x300")

# Инструкция
label_instruction = tk.Label(
    root,
    text="Перетащите изображение с дорожным знаком",
    font=("Arial", 14),
    wraplength=250,
    justify="center",
)
label_instruction.pack(pady=20)

# Добавление функциональности для перетаскивания
root.drop_target_register(DND_FILES)
root.dnd_bind("<<Drop>>", drop_image)

# Запуск основного цикла
root.mainloop()

# Уничтожение окон OpenCV
cv2.destroyAllWindows()
