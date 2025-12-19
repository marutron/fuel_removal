import time
import math
import os
from copy import copy
from multiprocessing import Process
from typing import Literal

from cartogram_handler import get_places, fill_bv_section, get_b02_places, get_b01_places, get_b03_places, \
    get_b03_gp_places, get_b01_gp_places
from classes import TVS, K
from equalizer import equalizer_main
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


def clear_folder_files(folder_path):
    """Удаляет все файлы в папке."""
    try:
        # Получаем список всех элементов в папке
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            os.remove(item_path)
    except Exception as e:
        print(f"Ошибка: {e}")


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


def get_b2_additional():
    """
    Возвращает дополнительную картограмму отсеков энергоблока 2
    :return: dict[str, str]
    """
    return {
        # b03
        # телега 122
        "TVS45-122": "ГП № 1",
        "GP46-122": "ГП № 2",
        "GP47-122": "ГП № 3",
        "GP48-122": "ГП № 4",
        "TVS49-122": "ГП № 5",
        "GP50-122": "ГП № 6",
        "GP51-122": "ГП № 7",
        "GP52-122": "ГП № 8",
        "GP53-122": "ГП № 9",
        "TVS54-122": "ГП № 10",
        # телега 124
        "GP47-124": "ГП № 11",
        "GP48-124": "ГП № 12",
        "TVS49-124": "ГП № 13",
        "TVS50-124": "Ячейка для",
        "AR50-124": "ГП № 14",
        "TVS51-124": "Ячейка для",
        "AR51-124": "ГП № 15",
        "TVS52-124": "Ячейка для",
        "AR52-124": "ГП № 16",
        "TVS53-124": "ГП № 17",
        "TVS54-124": "ГП № 18",
        # телега 126
        "TVS47-126": "Ячейка для",
        "AR47-126": "ГП № 19",
        "TVS48-126": "Ячейка для",
        "AR48-126": "ГП № 20",
        "TVS53-126": "Ячейка для",
        "AR53-126": "ГП № 21",

        # b01
        # телега 122
        "TVS63-122": "ГП № 22*",
        "TVS64-122": "Ячейка для",
        "AR64-122": "ГП № 23",
        "TVS65-122": "Ячейка для",
        "AR65-122": "ГП № 24",
        "TVS66-122": "Ячейка для",
        "AR66-122": "ГП № 25",
        "TVS67-122": "Ячейка для",
        "AR67-122": "ГП № 26",
        "TVS68-122": "Ячейка для",
        "AR68-122": "ГП № 27",
        "TVS69-122": "ГП № 28",
        "TVS70-122": "ГП № 29",
        "TVS71-122": "ГП № 30",
        "TVS72-122": "ГП № 31",
        # телега 124
        "TVS63-124": "ГП № 32*",
        "TVS64-124": "Ячейка для",
        "AR64-124": "ГП № 33",
        "TVS65-124": "Ячейка для",
        "AR65-124": "ГП № 34",
        "TVS66-124": "Ячейка для",
        "AR66-124": "ГП № 35",
        "TVS67-124": "Ячейка для",
        "AR67-124": "ГП № 36",
        "TVS68-124": "Ячейка для",
        "AR68-124": "ГП № 37",
        "TVS69-124": "ГП № 38",
        "TVS70-124": "ГП № 39",
        "TVS71-124": "ГП № 40",
        "TVS72-124": "ГП № 41",
        # телега 126
        "TVS63-126": "Ячейка для",
        "AR63-126": "ГП № 42",
        "TVS64-126": "Ячейка для",
        "AR64-126": "ГП № 43",
        "TVS65-126": "Ячейка для",
        "AR65-126": "ГП № 44",
        "TVS66-126": "Ячейка для",
        "AR66-126": "ГП № 45",
        "TVS67-126": "Ячейка для",
        "AR67-126": "ГП № 46",
        "TVS68-126": "Ячейка для",
        "AR68-126": "ГП № 47",
        "TVS69-126": "Ячейка для",
        "AR69-126": "ГП № 48",
        "TVS70-126": "Ячейка для",
        "AR70-126": "ГП № 49",
        "TVS71-126": "ПС СУЗ 03105",
        "AR71-126": "ГП № 50",

        # необслуживаемые
        "TVS61-91": "Необсл.",
        "AR61-91": "ячейка",
        "TVS76-98": "Ячейка для",
        "AR76-98": "ЧКл",
        "TVS76-102": "Ячейка для",
        "AR76-102": "ЧКл",
        "TVS85-91": "Необсл.",
        "AR85-91": "ячейка",
        "TVS87-91": "Необсл.",
        "AR87-91": "ячейка",
    }


def get_b3_additional():
    """
    Возвращает дополнительную картограмму отсеков энергоблока 3
    :return: dict[str, str]
    """
    return {
        # b03
        # телега 122
        "TVS45-122": "Ячейка под",
        "AR45-122": "ГП № 1",
        "TVS46-122": "Ячейка под",
        "AR46-122": "ГП № 2",
        "TVS47-122": "Ячейка под",
        "AR47-122": "ГП № 3",
        "TVS48-122": "Ячейка под",
        "AR48-122": "ГП № 4",
        "TVS49-122": "Ячейка под",
        "AR49-122": "ГП № 5",
        "TVS50-122": "Ячейка под",
        "AR50-122": "ГП № 6",
        "TVS51-122": "Ячейка под",
        "AR51-122": "ГП № 7",
        "TVS52-122": "Ячейка под",
        "AR52-122": "ГП № 8",
        "TVS53-122": "Ячейка под",
        "AR53-122": "ГП № 9",
        "TVS54-122": "Ячейка под",
        "AR54-122": "ГП № 10",
        # телега 124
        "TVS47-124": "Ячейка под",
        "AR47-124": "ГП № 11",
        "TVS48-124": "Ячейка под",
        "AR48-124": "ГП № 12",
        "TVS49-124": "Ячейка под",
        "AR49-124": "ГП № 13",
        "TVS50-124": "Ячейка под",
        "AR50-124": "ГП № 14",
        "TVS51-124": "Ячейка под",
        "AR51-124": "ГП № 15",
        "TVS52-124": "Ячейка под",
        "AR52-124": "ГП № 16",
        "TVS53-124": "Ячейка под",
        "AR53-124": "ГП № 17",
        "TVS54-124": "Ячейка под",
        "AR54-124": "ГП № 18",
        # телега 126
        "TVS47-126": "Ячейка для",
        "AR47-126": "ГП № 19",
        "TVS48-126": "Ячейка для",
        "AR48-126": "ГП № 20",
        "TVS53-126": "Ячейка для",
        "AR53-126": "ГП № 21",

        # b01
        # телега 122
        "TVS63-122": "ГП № 22",
        "TVS64-122": "ГП № 23",
        "TVS65-122": "ГП № 24",
        "TVS66-122": "ГП № 25",
        "GP67-122": "ГП № 26",
        "AR68-122": "ГП № 27",
        "TVS69-122": "ГП № 28",
        "GP70-122": "ГП № 29",
        "GP71-122": "ГП № 30*",
        "GP72-122": "ГП № 31*",
        # телега 124
        "TVS63-124": "ГП № 32",
        "TVS64-124": "ГП № 33",
        "TVS65-124": "ГП № 34",
        "TVS66-124": "ГП № 35",
        "TVS67-124": "ГП № 36",
        "TVS68-124": "ГП № 37*",
        "GP69-124": "ГП № 38",
        "TVS70-124": "ГП № 39*",
        "GP71-124": "ГП № 40*",
        "GP72-124": "ГП № 41*",
        # телега 126
        "TVS63-126": "ГП № 42",
        "TVS64-126": "ГП № 43",
        "TVS65-126": "ГП № 44",
        "TVS66-126": "ГП № 45",
        "TVS67-126": "ГП № 46",
        "TVS68-126": "ГП № 47",
        "GP69-126": "ГП № 48",
        "TVS70-126": "ГП № 49",
        "TVS71-126": "ПС СУЗ 01182",
        "AR71-126": "ГП № 50",

        # необслуживаемые
        "TVS61-91": "Необсл.",
        "AR61-91": "ячейка",
    }


def get_additional_hash(block_number: int) -> dict[str, str]:
    """
    Возвращает дополнительные значения для координат отсеков бассейна выдержки
    :param block_number: номер блока
    :return:
    """
    match block_number:
        case 1:
            pass
        case 2:
            return get_b2_additional()
        case 3:
            return get_b3_additional()
        case 4:
            pass


def get_map(bv_hash: dict[str, TVS], block_number: int, mode: Literal["b03", "b01", "b02"]):
    """
    Получает словарь для заполнения отсека БВ вида: dict[(TVS_coord, TVS_number), (AR_coord, AR_number)]
    :param bv_hash: словарь ТВС, находящихся в отсеке
    :param mode: номер отсека ["b03", "b01", "b02"]
    :return: словарь, содержащий все ячейки отсека - заполненный значениями или пробелами (для пустых ячеек)
    """
    match mode:
        case "b03":
            places = get_places(get_b03_places)
            places = get_places(get_b03_gp_places, places, "gp")
        case "b01":
            places = get_places(get_b01_places)
            places = get_places(get_b01_gp_places, places, "gp")
        case "b02":
            places = get_places(get_b02_places)

    additional_hash = get_additional_hash(block_number)

    for tvs in bv_hash.values():
        # тут не могу использовать небезопасныы координаты, т.к. bv_hash содержит много паразитных данных
        if places.get(f"TVS{tvs.coord}") is not None:
            places[f"TVS{tvs.coord}"] = tvs.number
            places[f"AR{tvs.coord}"] = f"{tvs.year_out}г." if tvs.ar is None else f"{tvs.ar} {tvs.year_out}г."

    # специально использую небезопасные координаты, чтобы отлавливать ошибки здесь, а не на картограмме
    for coord, data in additional_hash.items():
        places[coord] = data

    return places


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


def input_block_number() -> int:
    while True:
        block_number = input("Введите номер блока: ")
        try:
            block_number = int(block_number)
        except:
            print("Нужно ввести цифру 1, 2, 3 или 4")
        else:
            if block_number == 1 or block_number == 2 or block_number == 3 or block_number == 4:
                return block_number


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
