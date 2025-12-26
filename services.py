import os
from copy import copy
from multiprocessing import Process
from typing import Literal

from cartogram_shapers import get_map
from classes import TVS
from table_handler import add_table
from text_replacers import fill_passport, fill_bv_section


def input_block_number() -> int:
    """
    Управляет получением номера блока от пользователя
    :return:
    """
    while True:
        block_number = input("Введите номер блока: ")
        try:
            block_number = int(block_number)
        except:
            print("Нужно ввести цифру 1, 2, 3 или 4")
        else:
            if block_number == 1 or block_number == 2 or block_number == 3 or block_number == 4:
                return block_number


def get_backup_tvs_count(tvs_count):
    """
    Обработчик ввода количества резервных ТВС
    :param tvs_count: количество ТВС для выгрузки из БВ
    :return:
    """
    while True:
        count = -10
        try:
            inp = input("Укажите количество резервных ТВС ")
            count = int(inp)
        except ValueError:
            print(f"Невозможно распарсить '{inp}' как число. Повторите ввод.")
        if count < 0 or count >= tvs_count:
            print(f"Введите значение в диапазоне [0, {tvs_count - 1}]")
        else:
            return count


def get_tvs_to_remove(filename: str, bv_hash: dict[str, TVS]):
    """
    Парсит файл с ТВС, помеченными для вывоза с АЭС
    :param filename: имя фала, с которого выполняем считывание
    :param bv_hash: dict[номер ТВС, ТВС] словарь, содержащий ТВС
    :return:
    """
    tvs_counter = 0
    with open(filename) as remove_file:
        lines = remove_file.readlines()
        restrictions = {}
        last_restriction = 12
        for line in lines:
            line_lst = line.split()
            tvs_number = line_lst[0].strip()
            try:
                tvs_heat = float(line_lst[1].strip())
            except IndexError:
                tvs_heat = 0.0
            if len(line) < 10:
                try:
                    # не употребляю `tvs_number` чтобы подчеркнуть что в этом случае имеем дело не с ТВС,
                    # а с ограничением
                    last_restriction = int(line_lst[0].strip())
                except ValueError:
                    print(f"Ограничение задано неверно. Невозможно представить строку '{line}' как число")
                restrictions.setdefault(last_restriction, [])
            else:
                tvs_counter += 1
                try:
                    restrictions[last_restriction].append(tvs_number)
                except KeyError:
                    # задействуется в случае если в файле сразу начинаются ТВС, без задания количества ТВС в контейнере
                    # в таком случае укладываем по 12 ТВС
                    restrictions.setdefault(12, [])
                    # специально не указывал 12 тут чтобы отлавливать ошибки неправильного парсинга и пр.
                    restrictions[last_restriction].append(tvs_number)
                bv_hash[tvs_number].heat = tvs_heat
        return restrictions, tvs_counter, bv_hash


def clear_folder_files(folder_path):
    """Удаляет все файлы в папке и её вложенных подпапках, сохраняя структуру каталогов."""
    try:
        # Обходим все директории и поддиректории
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении файла {file_path}: {e}")
    except Exception as e:
        print(f"Ошибка при обходе директории {folder_path}: {e}")


# Выбирает из ТВС, готовящихся к вывозу с АЭС те, сумма ЯМ в которых наименьшая
#   count - количество ТВС, которые надо направить в резерв
def get_backup_tvs(count, for_remove, bv_hash):
    # собираем из словаря с номерами ТВС список экземпляров TVS
    all_tvs_for_remove = []
    for tvs_lst in for_remove.values():
        for tvs_number in tvs_lst:
            try:
                tvs = bv_hash[tvs_number]
            except KeyError as err:
                print(f"Не получается найти ТВС {tvs_number} в БВ!")
                raise err
            all_tvs_for_remove.append(tvs)
    # сортируем полученный список по убыванию масс ЯМ
    sorted_tvs = sorted(all_tvs_for_remove, key=lambda tvs: tvs.summ_isotopes, reverse=True)

    # собираем в множество номера 'count' ТВС с минимальной суммой масс ЯМ
    backup_numbers = set()
    backup = []
    while count > 0:
        tvs = sorted_tvs.pop()
        backup_numbers.add(tvs.number)
        backup.append(tvs)
        count -= 1

    result_for_remove = {}
    # собираем новый словарь номеров ТВС для вывоза, не включая в него ТВС, попавшие в backup
    for key, tvs_lst in for_remove.items():
        tvs_lst_new = []
        for tvs_number in tvs_lst:
            if tvs_number not in backup_numbers:
                tvs_lst_new.append(tvs_number)
        result_for_remove[key] = tvs_lst_new

    return result_for_remove, backup


def get_final_state(
        chunk_pool: list[bytes],
        mapper: dict[str, int],
        bv_hash_final: dict[str, TVS],
        chunk_size: int
) -> list[bytes]:
    """
    Формируем пул ТВС после вывоза ОТВС
    :param chunk_pool: list[bytes] - пул байтовых chunk-ов, считанный из ТОПАЗ-файла
    :param mapper: указывает индекс в списке байтовых данных для номера ТВС
    :param bv_hash_final: конечное состояние словаря ТВС БВ (после вывоза)
    :param chunk_size: размер chunk-а файла ТОПАЗ
    :return: list[bytes]
    """
    final_pool = copy(chunk_pool)
    for tvs_number, idx in mapper.items():
        if bv_hash_final.get(tvs_number) is None:
            final_pool[idx] = bytes(chunk_size)
    return final_pool


def operation_gen():
    i = 1
    while True:
        yield i
        i += 1


def result_file_handler(result_file, containers_pool, backup, mp_file):
    """
    Создает файлы с результатом операций
    :param result_file: файл результата .txt (устаревшее)
    :param containers_pool: пул сущностей контейнеров
    :param backup: пул резервных ТВС
    :return: None
    """
    with open(result_file, "w") as file:
        # список для добавления порожденных процессов
        prc_pool = []

        # делаем "touch" для инициализации пустого файла
        with open(mp_file, "w"):
            pass

        # инициализируем генератор номера операции (для проставки номера в первом столбце таблицы операций)
        oper_gen = operation_gen()
        # инициализируем генератор номера операции (для файла МП)
        oper_gen_mp = operation_gen()

        # счетчики вывезенных ТВС из отсеков
        removed_from_b03 = 0
        removed_from_b01 = 0
        removed_from_b02 = 0

        for container in containers_pool:
            # получаем данные для заполнения картограмм ТК-13
            tk_data = container.get_cartogram()
            # получаем данные для заполнения таблиц перестановок ТК-13
            permutations = container.get_permutations(oper_gen)
            # делаем запись в файл для МП
            container.add_mp_data(oper_gen_mp, mp_file)
            # заполняем паспорта упаковки ТУК
            passport_data = container.get_passport_data()
            fill_passport(passport_data)

            # заполняем таблицы перестановок и картограммы для ТК-13 в режиме многопроцессности
            prc = Process(target=add_table, args=(permutations, tk_data, container.number))
            prc.start()
            prc_pool.append(prc)

            # заполняем .txt файл
            file.write(
                f"{container}\n"
            )
            for cell in container.outer_layer + container.inner_layer:
                removed_from_b03, removed_from_b01, removed_from_b02 = cell.removed_from_section_calculation(
                    removed_from_b03, removed_from_b01, removed_from_b02
                )

                file.write(f"{cell}\n")
            file.write("\n")

        # дописываем резервные ТВС в конец файла
        file.write("Резервные ТВС:\n")
        for tvs in backup:
            file.write(f"{tvs}\n")

        file.write("\nВывезено ТВС по отсекам:\n")
        file.write(f"b01: {removed_from_b01};\n")
        file.write(f"b02: {removed_from_b02};\n")
        file.write(f"b03: {removed_from_b03}.")

    # дожидаемся создания всех файлов
    for prc in prc_pool:
        prc.join()


def bv_sections_handler(bv_hash: dict[str, TVS], block_number: int, mode: Literal["initial", "final"]):
    """
    Заполняет картограммы отсеков БВ в отдельных процессах
    :param bv_hash:
    :param mode: Literal["initial", "final"]
    :return:
    """
    # список для добавления порожденных процессов
    prc_pool = []

    section_names = ["b03", "b01", "b02"]
    sections_maps = [get_map(bv_hash, block_number, section_name) for section_name in section_names]

    section_name_gen = iter(section_names)

    for map in sections_maps:
        prc = Process(target=fill_bv_section, args=(map, next(section_name_gen), mode))
        prc.start()
        prc_pool.append(prc)

    # дожидаемся создания всех файлов
    for prc in prc_pool:
        prc.join()
