"""
В данном модуле представлены методы для парсинга файла БД ТОПАЗа.
"""
import os.path

from classes import TVS, K


def read_topaz(file):
    """
    Считывает файл ТОПАЗ, производя байтовый парсинг (декодирование и изменение не производятся здесь!)
    :return: list[K]
    """
    file_size = os.path.getsize(file)  # размер файла
    chunk_size = 1749  # размер описания одной ТВС
    pool = []
    with open(file, "rb") as inp:
        while file_size >= chunk_size:
            k = K(inp.read(chunk_size))
            pool.append(k)
            file_size -= chunk_size
        tail = inp.read()
        if tail != b"":
            print(f"Файл ТОПАЗ считан не полностью, осталось {len(tail)} нераспределенных байт.")
            print(f"Вывод нераспределенных байт считанного файла ТОПАЗ:\n{tail}")
        else:
            print("Файл ТОПАЗ считан полностью.")
        return pool


def write_topaz(pool: list):
    """
    Записывает файл ТОПАЗ из переданных ТВС в pool
    :param pool: список ТВС, переданных для записи в файл
    :return: file
    """
    # todo доделать метод
    pass


def decode_tvs_pool(raw_pool: list[K], codepage: str = "cp1251"):
    """
    Производит расшифровку пула ТВС в байтовых данных
    :param raw_pool: list[K] - пул ТВС в байтовом виде без расшифровки
    :param codepage: используемая кодировка
    :return: dict[str, TVS] (dict[номер ТВС, ТВС])
    """
    parsed_pool = {}

    for tvs in raw_pool:
        try:
            parsed_tvs = TVS(tvs, codepage)
        except Exception:
            print("Неудача парсинга ТВС.")
        else:
            parsed_pool.setdefault(parsed_tvs.number, parsed_tvs)
    return parsed_pool


if __name__ == "__main__":
    input_file = "ZAGR96TVS"
    codepage = "cp1251"

    raw_pool = read_topaz(input_file)
    tvs_dict = decode_tvs_pool(raw_pool, codepage)

    tvs = tvs_dict["53-122"]
    a = tvs.k.encode()
    b = tvs.k.replace_by_zero()

    pass
