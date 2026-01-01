"""
В данном модуле представлены методы для парсинга файла БД ТОПАЗа.
"""
import os.path
from datetime import datetime
from typing import Optional

from classes import TVS, K
from error import CustomFileNotFound


def read_topaz(file_path, chunk_size):
    """
    Считывает файл ТОПАЗ, производя байтовый парсинг (декодирование и изменение не производятся здесь!)
    :return: list[K]
    """

    try:
        file_size = os.path.getsize(file_path)  # размер файла
    except FileNotFoundError:
        raise CustomFileNotFound(file_path)

    # инициализируем 2 пула ТВС
    chunk_pool = []  # сюда помещаем байтовые вырезки (chunks) из оригинального файла
    k_pool = []  # сюда помещаем сущности k, получившиеся после парсинга chunk-ов в объекты K питоном

    with open(file_path, "rb") as inp:
        while file_size >= chunk_size:
            chunk = inp.read(chunk_size)
            k = K(chunk)
            chunk_pool.append(chunk)
            k_pool.append(k)
            file_size -= chunk_size
        tail = inp.read()
        if tail != b"":
            print(f"Файл ТОПАЗ считан не полностью, осталось {len(tail)} нераспределенных байт.")
            print(f"Вывод нераспределенных байт считанного файла ТОПАЗ:\n{tail}")
        else:
            print("Файл ТОПАЗ считан полностью.")
        return chunk_pool, k_pool


def write_topaz_state_file(file_name: str, pool: list[bytes]):
    """
    Записывает файл ТОПАЗ из переданных ТВС в pool
    :param pool: список chunk-ов, переданных для записи в файл
    :param file_name: расположение файла, в который производится запись
    :return: None
    """
    with open(file_name, "wb") as file:
        file.writelines(pool)


def decode_tvs_pool(
        raw_pool: list[K],
        codepage: str = "cp1251",
        date: Optional[datetime] = None
) -> (dict[str, TVS], dict[str, int]):
    """
    Производит расшифровку пула ТВС в байтовых данных
    :param raw_pool: list[K] - пул ТВС в байтовом виде без расшифровки
    :param codepage: используемая кодировка
    :param date: дата, на которую производится расчет (для расчета остаточного тепловыделения ТВС) - опционально
    :return: dict[str, TVS] (dict[номер ТВС, ТВС])
    """
    parsed_pool = {}
    # словарь вида dict[TVS.number, индекс в сыром списке]
    # необходим для понимания какой номер ТВС на каком месте стоит в сыром списке ТВС
    mapper = {}

    for i in range(0, len(raw_pool)):
        try:
            k = raw_pool[i]
            tvs = TVS(k, codepage, date)
        except Exception as exc:
            print("Неудача парсинга ТВС.")
            print(exc)
        else:
            mapper.setdefault(tvs.number, i)
            parsed_pool.setdefault(tvs.number, tvs)
    return parsed_pool, mapper
