from PIL import Image
import os

# Папка с исходными изображениями (должна находиться в той же директории, что и скрипт)
input_folder = 'input'
# Папка для сохранения изменённых изображений (будет создана автоматически)
output_folder = 'output'
max_side = 1400  # Желаемая длина максимальной стороны

# Создаем выходную папку, если её нет
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Проходим по всем файлам в папке input
for file in os.listdir(input_folder):
    # Обрабатываем только изображения с указанными расширениями
    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
        image_path = os.path.join(input_folder, file)
        with Image.open(image_path) as img:
            width, height = img.size
            max_current = max(width, height)
            
            # Вычисляем коэффициент масштабирования для достижения max_side
            scale = max_side / max_current
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Выполняем ресайзинг с использованием фильтра LANCZOS
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Если изображение в режиме RGBA или P и сохраняется в JPEG, конвертируем в RGB
            if file.lower().endswith(('.jpg', '.jpeg')) and resized_img.mode in ('RGBA', 'P'):
                resized_img = resized_img.convert('RGB')
            
            # Сохраняем изменённое изображение в выходную папку с тем же именем файла
            output_path = os.path.join(output_folder, file)
            resized_img.save(output_path)
            
print("Ресайзинг завершён. Изображения сохранены в папке:", output_folder)
