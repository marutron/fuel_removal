class CustomFileNotFound(FileNotFoundError):
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return f"\nНе найден файл: {self.file_path}.\nВосстановите его и перезапустите скрипт."


class AzExportException(Exception):

    def __init__(self, tvs_number: str, tvs_coord: str):
        self.tvs_coord = tvs_coord

    def __str__(self):
        return f"\nПопытка вывезти ТВС не из БВ (координаты: {self.tvs_coord})"
