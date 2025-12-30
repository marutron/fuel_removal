class CustomFileNotFound(FileNotFoundError):
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return f"\nНе найден файл: {self.file_path}.\nВосстановите его и перезапустите скрипт."
