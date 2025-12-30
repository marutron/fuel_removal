import time
import math
import os
from copy import copy

from equalizer import equalizer_main
from services import input_block_number, clear_folder_files, get_backup_tvs_count, get_tvs_to_remove, get_backup_tvs, \
    get_final_state, result_file_handler, bv_sections_handler
from topaz_file_handler import read_topaz, decode_tvs_pool, write_topaz_state_file

cur_dir = os.getcwd()
input_dir = os.path.join(cur_dir, "input")
output_dir = os.path.join(cur_dir, "output")
initial_state_file = os.path.join(input_dir, "initial_state")
final_state_file = os.path.join(output_dir, "final_state")
tvs_to_remove_file = os.path.join(input_dir, "tvs_to_remove.txt")
result_file = os.path.join(output_dir, "result.txt")
mp_file = os.path.join(output_dir, "mp_file.mp")

if __name__ == "__main__":
    CHUNK_SIZE = 1749
    clear_folder_files(output_dir)
    chunk_pool, k_pool = read_topaz(initial_state_file, CHUNK_SIZE)
    # chunk_pool_mapper: dict[str, int] задает соответствие номера ТВС индексу в списке chunk_pool
    bv_hash_initial, chunk_pool_mapper = decode_tvs_pool(k_pool)
    for_remove, tvs_count, bv_hash_initial = get_tvs_to_remove(tvs_to_remove_file, bv_hash_initial)
    # count = get_backup_tvs_count(tvs_count)
    # block_number = input_block_number()
    count = 1
    block_number = 2
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
    result_file_handler(result_file, containers, backup, mp_file)

    # заполняем картограммы отсеков БВ - начальную и конечную
    bv_sections_handler(bv_hash_initial, block_number, "initial")
    bv_sections_handler(bv_hash_final, block_number, "final")

    # записываем данные в файл ТОПАЗ
    final_pool = get_final_state(chunk_pool, chunk_pool_mapper, bv_hash_final, CHUNK_SIZE)
    write_topaz_state_file(final_state_file, final_pool)

    # вычисляем время выполнения программы
    end = time.perf_counter()
    elapsed = end - start
    print(f"Время выполнения: {elapsed:.5f} c.")
