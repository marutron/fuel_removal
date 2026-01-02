from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from classes import TVS


# Генераторные функции мест для картограмм БВ
def get_b03_places():
    return {
        43: (col for col in range(94, 120, 2)),
        44: (col for col in range(95, 121, 2)),
        45: (col for col in range(94, 120, 2)),
        46: (col for col in range(91, 121, 2)),
        47: (col for col in range(92, 120, 2)),
        48: (col for col in range(91, 121, 2)),
        49: (col for col in range(92, 120, 2)),
        50: (col for col in range(91, 121, 2)),
        51: (col for col in range(92, 120, 2)),
        52: (col for col in range(91, 121, 2)),
        53: (col for col in range(92, 120, 2)),
        54: (col for col in range(91, 121, 2)),
        55: (col for col in range(92, 120, 2)),
        56: (col for col in range(91, 121, 2)),
        57: (col for col in range(92, 120, 2)),
        58: (col for col in range(91, 121, 2))
    }


# реверсивное заполнение!
def get_b03_gp_places():
    return {
        122: (row for row in range(45, 55, 1)),
        124: (row for row in range(47, 55, 1)),
        126: (row for row in range(47, 54, 1))
    }


def get_b01_places():
    return {
        60: (col for col in range(92, 120, 2)),
        61: (col for col in range(91, 121, 2)),
        62: (col for col in range(92, 120, 2)),
        63: (col for col in range(91, 121, 2)),
        64: (col for col in range(92, 120, 2)),
        65: (col for col in range(91, 121, 2)),
        66: (col for col in range(92, 120, 2)),
        67: (col for col in range(91, 121, 2)),
        68: (col for col in range(92, 120, 2)),
        69: (col for col in range(91, 121, 2)),
        70: (col for col in range(92, 120, 2)),
        71: (col for col in range(91, 121, 2)),
        72: (col for col in range(92, 120, 2)),
        73: (col for col in range(95, 121, 2)),
        74: (col for col in range(96, 120, 2)),
        75: (col for col in range(97, 121, 2))
    }


# реверсивное заполнение!
def get_b01_gp_places():
    return {
        122: (row for row in range(63, 73, 1)),
        124: (row for row in range(63, 73, 1)),
        126: (row for row in range(63, 72, 1))
    }


def get_b02_places():
    return {
        76: (col for col in range(96, 108, 2)),
        77: (col for col in range(97, 107, 2)),
        78: (col for col in range(96, 108, 2)),
        79: (col for col in range(91, 107, 2)),
        80: (col for col in range(92, 108, 2)),
        81: (col for col in range(91, 107, 2)),
        82: (col for col in range(92, 108, 2)),
        83: (col for col in range(91, 107, 2)),
        84: (col for col in range(92, 108, 2)),
        85: (col for col in range(91, 107, 2)),
        86: (col for col in range(92, 108, 2)),
        87: (col for col in range(91, 107, 2)),
        88: (col for col in range(92, 108, 2)),
        89: (col for col in range(95, 107, 2)),
        90: (col for col in range(94, 108, 2))
    }


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
            # todo доработать
            pass
        case 2:
            return get_b2_additional()
        case 3:
            return get_b3_additional()
        case 4:
            # todo доработать
            pass


def get_map(bv_hash: dict[str, "TVS"], block_number: int, mode: Literal["b03", "b01", "b02"]):
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


def get_places(places_func, places_hash=None, *args):
    """
    Формирует список мест отсека
    """
    # получаем места картограммы отсека БВ
    if places_hash is None:
        places_hash = {}
    if places_hash is None:
        places_hash = {}
    places_gen = places_func()
    for item, val in places_gen.items():
        for elm in val:
            if "gp" in args:
                places_hash[f"TVS{elm}-{item}"] = " "
                places_hash[f"AR{elm}-{item}"] = " "
                places_hash[f"GP{elm}-{item}"] = " "
            else:
                places_hash[f"TVS{item}-{elm}"] = " "
                places_hash[f"AR{item}-{elm}"] = " "
    return places_hash
