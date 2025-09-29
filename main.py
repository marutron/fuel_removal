import math
import os

from classes import TVS
from equalizer import equalizer_main

cur_dir = os.getcwd()
into_bv_file = os.path.join(cur_dir, "into_bv.txt")
tvs_to_remove_file = os.path.join(cur_dir, "tvs_to_remove.txt")
result_file = os.path.join(cur_dir, "result.txt")


# Парсит файл ТВС в БВ в словарь
def get_bv_tvs(filename):
    bv_hash = {}
    with open(filename) as bv_file:
        lines = bv_file.readlines()[1::]
        for line in lines:
            split_line = line.split()
            tvs_number = split_line[0] + split_line[1]
            heat = float(split_line[4])
            coordinates = f"{split_line[2]}-{split_line[3]}"
            ps = split_line[5].strip()
            tvs = TVS(tvs_number, heat, coordinates, ps)
            bv_hash[tvs.number] = tvs
    return bv_hash


# Парсит файл с ТВС, помеченными для вывоза с АЭС
def get_tvs_to_remove(filename):
    with open(filename) as remove_file:
        lines = remove_file.readlines()
        restrictions = {}
        last_restriction = 12
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                try:
                    last_restriction = int(line)
                except ValueError:
                    print(f"Ограничение задано неверно. Невозможно представить строку '{line}' как число")
                restrictions.setdefault(last_restriction, [])
            else:
                try:
                    restrictions[last_restriction].append(line.strip())
                except KeyError:
                    # задействуется в случае если в файле сразу начинаются ТВС, без задания количества ТВС в контейнере
                    # в таком случае укладываем по 12 ТВС
                    restrictions.setdefault(12, [])
                    # специально не указывал 12 тут чтобы отлавливать ошибки неправильного парсинга и пр.
                    restrictions[last_restriction].append(line.strip())
        return restrictions


# Создание файла с результатом операций
def result_file_handler(result_file, containers_pool):
    with open(result_file, "w") as file:
        for container in containers_pool:
            file.write(
                f"{container}\n"
            )
            for cell in container.outer_layer + container.inner_layer:
                file.write(f"{cell}\n")
            file.write("\n")


if __name__ == "__main__":
    bv_hash = get_bv_tvs(into_bv_file)
    for_remove = get_tvs_to_remove(tvs_to_remove_file)
    containers = []
    iterator = 1

    for restriction, remove_lst in for_remove.items():
        containers_count = math.ceil(len(remove_lst) / restriction)
        tvs_pool = []
        for number in remove_lst:
            try:
                tvs_pool.append(bv_hash.pop(number))
            except KeyError as err:
                print(f"Запрашиваемая на вывоз ТВС '{number}' не найдена в БВ. Проверьте данные.")

        print(tvs_pool)
        new_containers, iterator = equalizer_main(containers_count, tvs_pool, iterator)
        for container in new_containers:
            container.fill_cells()
        containers.extend(new_containers)
    result_file_handler(result_file, containers)
