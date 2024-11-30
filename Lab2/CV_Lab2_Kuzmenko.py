import cv2
import numpy as np
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Глобальные переменные
image = None
window_name = "Filters Comparison"
current_filter = "Gaussian"
gaussian_ksize = 15
median_ksize = 15
bilateral_d = 9
bilateral_sigma_color = 75
bilateral_sigma_space = 75
trackbars_initialized = False


# Применение фильтров
def apply_gaussian_blur(img, ksize=(15, 15)):
    return cv2.GaussianBlur(img, ksize, 0)


def apply_median_blur(img, ksize=15):
    return cv2.medianBlur(img, ksize)


def apply_bilateral_blur(img, d=15, sigma_color=75, sigma_space=75):
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


# Многоуровневая фильтрация
def apply_multilevel_filter(img, levels=3):
    filtered_img = img.copy()
    for level in range(levels):
        filtered_img = apply_gaussian_blur(filtered_img, ksize=(5 + 2 * level, 5 + 2 * level))
    return filtered_img


# Обновление фильтров
def update(val):
    global image, current_filter, gaussian_ksize, median_ksize, bilateral_d, bilateral_sigma_color, bilateral_sigma_space, trackbars_initialized

    if image is None or not trackbars_initialized:
        return

    filtered_image = image

    try:
        if current_filter == "Gaussian":
            gaussian_ksize = cv2.getTrackbarPos("Kernel Size", window_name) * 2 + 1
            filtered_image = apply_gaussian_blur(image, (gaussian_ksize, gaussian_ksize))

        elif current_filter == "Median":
            median_ksize = cv2.getTrackbarPos("Kernel Size", window_name) * 2 + 1
            filtered_image = apply_median_blur(image, median_ksize)

        elif current_filter == "Bilateral":
            bilateral_d = max(1, cv2.getTrackbarPos("Diameter", window_name))
            bilateral_sigma_color = cv2.getTrackbarPos("Sigma Color", window_name)
            bilateral_sigma_space = cv2.getTrackbarPos("Sigma Space", window_name)
            filtered_image = apply_bilateral_blur(image, bilateral_d, bilateral_sigma_color, bilateral_sigma_space)

        elif current_filter == "Comparison":
            filtered_image = compare_filters(image)

        elif current_filter == "Multilevel":
            levels = cv2.getTrackbarPos("Levels", window_name)
            filtered_image = apply_multilevel_filter(image, levels=levels)

    except cv2.error as e:
        print(f"OpenCV error: {e}")

    # Отображение фильтрованного изображения
    cv2.imshow(window_name, filtered_image)


# Сравнение фильтров
def compare_filters(img):
    gaussian_blur = apply_gaussian_blur(img, (15, 15))
    median_blur = apply_median_blur(img, 15)
    bilateral_blur = apply_bilateral_blur(img, 15, 75, 75)
    combined = np.hstack((gaussian_blur, median_blur, bilateral_blur))
    return combined


# Изменение текущего фильтра
def change_filter(new_filter):
    global current_filter, trackbars_initialized
    current_filter = new_filter
    trackbars_initialized = False
    setup_trackbar()


# Настройка трекбаров
def setup_trackbar():
    global trackbars_initialized

    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow(window_name)

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 600)

    if current_filter == "Gaussian":
        cv2.createTrackbar("Kernel Size", window_name, gaussian_ksize // 2, 50, update)

    elif current_filter == "Median":
        cv2.createTrackbar("Kernel Size", window_name, median_ksize // 2, 50, update)

    elif current_filter == "Bilateral":
        cv2.createTrackbar("Diameter", window_name, bilateral_d, 50, update)
        cv2.createTrackbar("Sigma Color", window_name, bilateral_sigma_color, 200, update)
        cv2.createTrackbar("Sigma Space", window_name, bilateral_sigma_space, 200, update)

    elif current_filter == "Multilevel":
        cv2.createTrackbar("Levels", window_name, 3, 10, update)

    trackbars_initialized = True
    update(0)


# Функция для обработки перетаскивания изображения
def drop_image(event):
    global image
    file_path = event.data.strip().strip('{').strip('}')
    image = cv2.imread(file_path)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return
    setup_trackbar()


root = TkinterDnD.Tk()
root.title("Перетащите изображение сюда")
root.geometry("300x600")
label_instruction = tk.Label(root, text="Перетащите изображение сюда", font=("Arial", 14), wraplength=250, justify="center")
label_instruction.pack(pady=20)
tk.Button(root, text="Gaussian Filter", command=lambda: change_filter("Gaussian"), font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Median Filter", command=lambda: change_filter("Median"), font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Bilateral Filter", command=lambda: change_filter("Bilateral"), font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Compare Filters", command=lambda: change_filter("Comparison"), font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="Multilevel Filter", command=lambda: change_filter("Multilevel"), font=("Arial", 12)).pack(pady=5)
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop_image)
root.mainloop()
cv2.destroyAllWindows()
