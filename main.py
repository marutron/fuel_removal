import time
import math
import os
from multiprocessing import Process

from classes import TVS
from equalizer import equalizer_main
from table_handler import add_table

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
            heat = float(split_line[11])
            coordinates = f"{split_line[2]}-{split_line[3]}"
            ps = split_line[12].strip()
            u5 = float(split_line[4])
            u8 = float(split_line[5])
            pu8 = float(split_line[6])
            pu9 = float(split_line[7])
            pu0 = float(split_line[8])
            pu1 = float(split_line[9])
            pu2 = float(split_line[10])
            tvs = TVS(tvs_number, heat, coordinates, ps, u5, u8, pu8, pu9, pu0, pu1, pu2)
            bv_hash[tvs.number] = tvs
    return bv_hash


# Парсит файл с ТВС, помеченными для вывоза с АЭС
def get_tvs_to_remove(filename):
    tvs_counter = 0
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
                tvs_counter += 1
                try:
                    restrictions[last_restriction].append(line.strip())
                except KeyError:
                    # задействуется в случае если в файле сразу начинаются ТВС, без задания количества ТВС в контейнере
                    # в таком случае укладываем по 12 ТВС
                    restrictions.setdefault(12, [])
                    # специально не указывал 12 тут чтобы отлавливать ошибки неправильного парсинга и пр.
                    restrictions[last_restriction].append(line.strip())
        return restrictions, tvs_counter


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
    sorted_tvs = sorted(all_tvs_for_remove, key=lambda tvs: tvs.sum_isotopes, reverse=True)

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

        # инициализируем генератор номера операции (для проставки номера в первом столбце таблицы операций)
        oper_gen = operation_gen()

        for container in containers_pool:
            # получаем данные для заполнения картограмм ТК-13
            tk_data = container.get_cartogram()
            # получаем данные для заполнения таблиц перестановок ТК-13
            permutations = container.get_permutations(oper_gen)

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


if __name__ == "__main__":

    bv_hash = get_bv_tvs(into_bv_file)
    for_remove, tvs_count = get_tvs_to_remove(tvs_to_remove_file)
    count = get_backup_tvs_count(tvs_count)

    # замеряем время началы работы программы
    start = time.perf_counter()

    base_remove, backup = get_backup_tvs(count, for_remove, bv_hash)
    containers = []
    iterator = 1

    for restriction, remove_lst in base_remove.items():
        containers_count = math.ceil(len(remove_lst) / restriction)
        tvs_pool = []
        for number in remove_lst:
            try:
                tvs_pool.append(bv_hash.pop(number))
            except KeyError as err:
                print(f"Запрашиваемая на вывоз ТВС '{number}' не найдена в БВ. Проверьте данные.")

        new_containers, iterator = equalizer_main(containers_count, tvs_pool, iterator)
        for container in new_containers:
            container.fill_cells()
        containers.extend(new_containers)
    result_file_handler(result_file, containers, backup)

    # вычисляем время выполнения программы
    end = time.perf_counter()
    elapsed = end - start
    print(f"Время выполнения: {elapsed:.5f} c.")
