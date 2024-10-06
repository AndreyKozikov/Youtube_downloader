import yt_dlp
import os


# Класс для обработки логов и передачи их в текстовое поле GUI
class MyLogger:
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def debug(self, msg):
        # Перехват отладочных сообщений
        if not msg.startswith('[download]'):
            self.log_callback(msg)

    def info(self, msg):
        # Перехват информационных сообщений
        self.log_callback(msg)

    def warning(self, msg):
        # Перехват предупреждений
        self.log_callback(msg)

    def error(self, msg):
        # Перехват ошибок
        self.log_callback(msg)


# Функция для скачивания видео с коллбэком прогресса и логгированием
def download_video(url, download_path, format_id, progress_callback, log_callback):
    # Получаем путь к корневой папке, где лежит скрипт
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к ffmpeg.exe в корневой папке
    ffmpeg_path = os.path.join(root_dir, 'ffmpeg.exe')

    ydl_opts = {
        'format': format_id,  # Используем выбранный формат
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,  # Указываем путь к FFmpeg
        'n_threads': 8,
        'progress_hooks': [progress_callback],  # Добавляем коллбэк для отслеживания прогресса
        'logger': MyLogger(log_callback),  # Добавляем кастомный логгер
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "Видео успешно скачано!"
    except Exception as e:
        return f"Произошла ошибка: {e}"


# Функция для получения доступных форматов видео
def get_available_formats(url):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])

        # Фильтруем форматы, оставляя только видео
        video_formats = [
            {
                'format_id': fmt['format_id'],
                'height': fmt.get('height', 'N/A'),
                'ext': fmt['ext'],
                'vcodec': fmt.get('vcodec', 'N/A'),
                'acodec': fmt.get('acodec', 'N/A'),
                'filesize': fmt.get('filesize', 'N/A'),
                'url': fmt.get('url', '')
            }
            for fmt in formats if 'vcodec' in fmt
        ]

    return video_formats
