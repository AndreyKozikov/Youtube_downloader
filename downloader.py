import yt_dlp
import os


# Класс для обработки логов и передачи их в текстовое поле GUI
class MyLogger:
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def debug(self, msg):
        #Перехват отладочных сообщений
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
def download_video(url, download_path, progress_callback, log_callback):
    # Получаем путь к корневой папке, где лежит скрипт
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к ffmpeg.exe в корневой папке
    ffmpeg_path = os.path.join(root_dir, 'ffmpeg.exe')

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'ffmpeg_location':  ffmpeg_path,  # Указываем путь к FFmpeg
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

# URL видео на YouTube
#video_url = "https://www.youtube.com/watch?v=5Bk4K2qxL3A"


