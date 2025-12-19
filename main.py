import time
import math
import os
from copy import copy
from multiprocessing import Process
from typing import Literal

from cartogram_handler import fill_bv_section
from cartogram_shapers import get_map
from classes import TVS, K
from equalizer import equalizer_main
from services import input_block_number, clear_folder_files, get_backup_tvs_count, get_tvs_to_remove, get_backup_tvs
from table_handler import add_table
from topaz_file_handler import read_topaz, decode_tvs_pool

cur_dir = os.getcwd()
input_dir = os.path.join(cur_dir, "input")
output_dir = os.path.join(cur_dir, "output")
initial_state_file = os.path.join(input_dir, "initial_state")
final_state_file = os.path.join(output_dir, "final_state")
tvs_to_remove_file = os.path.join(input_dir, "tvs_to_remove.txt")
result_file = os.path.join(output_dir, "result.txt")
mp_file = os.path.join(output_dir, "mp_file.mp")


def operation_gen():
    i = 1
    while True:
        yield i
        i += 1


def result_file_handler(result_file, containers_pool, backup):
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

        for container in containers_pool:
            # получаем данные для заполнения картограмм ТК-13
            tk_data = container.get_cartogram()
            # получаем данные для заполнения таблиц перестановок ТК-13
            permutations = container.get_permutations(oper_gen)
            # делаем запись в файл для МП
            container.add_mp_data(oper_gen_mp, mp_file)

            # заполняем таблицы перестановок и картограммы для ТК-13 в режиме многопроцессности
            prc = Process(target=add_table, args=(permutations, tk_data, container.number))
            prc.start()
            prc_pool.append(prc)

            # заполняем .txt файл
            file.write(
                f"{container}\n"
            )
            for cell in container.outer_layer + container.inner_layer:
                file.write(f"{cell}\n")
            file.write("\n")

        # дописываем резервные ТВС в конец файла
        file.write("Резервные ТВС:\n")
        for tvs in backup:
            file.write(f"{tvs}\n")

    # дожидаемся создания всех файлов
    for prc in prc_pool:
        prc.join()


def get_tvs_pool_for_final_state(input_pool: list[K], bv_hash: dict):
    """
    Формируем пул ТВС после вывоза ОТВС
    :param input_pool: list[K] - пул ТВС, сформированный из Топаз-файла
    :param bv_hash: словарь с ТВС
    :return: list[K]
    """
    final_pool = []
    for k in input_pool:
        tvs_number = f"{k.tip.sort} + {k.tip.nomer} + {k.tip.indeks}"
        if bv_hash.get(tvs_number) is None:
            # побайтово меняем на нули информацию о выгруженных ТВС
            # final_pool.append(k.replace_by_zero())
            final_pool.append(k.encode())
        else:
            final_pool.append(k.encode())
    return final_pool


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


if __name__ == "__main__":
    clear_folder_files(output_dir)
    topaz_tvs_pool = read_topaz(initial_state_file)
    bv_hash_initial = decode_tvs_pool(topaz_tvs_pool)
    for_remove, tvs_count, bv_hash_initial = get_tvs_to_remove(tvs_to_remove_file, bv_hash_initial)
    count = get_backup_tvs_count(tvs_count)
    block_number = input_block_number()
    # копируем словарь т.к. будем удалять из него вывезенные ТВС
    bv_hash_final = copy(bv_hash_initial)

    # замеряем время началы работы программы
    start = time.perf_counter()

    base_remove, backup = get_backup_tvs(count, for_remove, bv_hash_final)
    containers = []
    iterator = 1

    for restriction, remove_lst in base_remove.items():
        containers_count = math.ceil(len(remove_lst) / restriction)
        tvs_pool = []
        for number in remove_lst:
            try:
                tvs_pool.append(bv_hash_final.pop(number))
            except KeyError as err:
                print(f"Запрашиваемая на вывоз ТВС '{number}' не найдена в БВ. Проверьте данные.")

        new_containers, iterator = equalizer_main(containers_count, tvs_pool, iterator)
        for container in new_containers:
            container.fill_cells()
        containers.extend(new_containers)
    # заполняем файлы с результатами
    result_file_handler(result_file, containers, backup)

    # заполняем картограммы отсеков БВ
    bv_sections_handler(bv_hash_initial, block_number, "initial")
    bv_sections_handler(bv_hash_final, block_number, "final")

    # записываем данные в файл ТОПАЗ
    final_pool = get_tvs_pool_for_final_state(topaz_tvs_pool, bv_hash_final)
    with open(final_state_file, "wb") as file:
        file.writelines(final_pool)

    # вычисляем время выполнения программы
    end = time.perf_counter()
    elapsed = end - start
    print(f"Время выполнения: {elapsed:.5f} c.")
