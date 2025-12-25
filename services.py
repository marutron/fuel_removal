import os
from copy import copy

from classes import TVS


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


def get_final_state(chunk_pool: list[bytes], mapper: dict[str, int], bv_hash_final: dict[str, TVS]) -> list[bytes]:
    """
    Формируем пул ТВС после вывоза ОТВС
    :param chunk_pool: list[bytes] - пул байтовых chunk-ов, считанный из ТОПАЗ-файла
    :param mapper:
    :param bv_hash_final:
    :return: list[bytes]
    """
    final_pool = copy(chunk_pool)
    for tvs_number, idx in mapper.items():
        if bv_hash_final.get(tvs_number) is None:
            final_pool[idx] = bytes(1749)
    return final_pool
