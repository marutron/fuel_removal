import os.path
from typing import Literal

from odf.opendocument import load
from odf import text, draw


def collect_text_nodes(node, text_nodes):
    """
    Реккурсивно собирает текстовые узлы элемента node в список text_nodes
    :param node: предоставленный элемент (Element)
    :param text_nodes: список текстовых узлов (Text)
    :return: None
    """
    if node.nodeType == node.TEXT_NODE:
        text_nodes.append(node)
    elif node.nodeType == node.ELEMENT_NODE:
        for child in node.childNodes:
            collect_text_nodes(child, text_nodes)


def set_text(element, new_text: dict):
    """
    Рекурсивно заменяет весь текст в элементе, сохраняя структуру и стили.
    :param element: рассматриаваемый элемент (Element)
    :param new_text: dict[str, str]: старый текст - новый текст
    """
    # Собираем все текстовые узлы
    text_nodes = []
    collect_text_nodes(element, text_nodes)

    # Если текстовых узлов нет — выходим
    if not text_nodes:
        # print("В элементе не найдено ни одного текстового узла. Замен не произведено.")
        return

    for node in text_nodes:
        if new_text.get(node.data):
            node.data = new_text[node.data]


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
def get_b01_gp():
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


def get_places(places_func, *args):
    """
    Формирует список мест отсека
    """
    places_hash: dict[str, str] = {}

    # получаем места картограммы отсека БВ
    places_gen = places_func()
    for item, val in places_gen.items():
        for elm in val:
            if "gp" in args:
                # todo дополнить секцию ГП TVS, AR
                places_hash[f"{elm}-{item}"] = " "
            else:
                places_hash[f"TVS{item}-{elm}"] = " "
                places_hash[f"AR{item}-{elm}"] = " "
    return places_hash


def fill_bv_section(
        map: dict[str, str], section_name: Literal["b03", "b01", "b02"],
        mode: Literal["initial", "final"]
):
    """
    Заполняет картограмму БВ по данным в полученном словаре. Результат сохраняет в папку result.
    :param map: dict[str, str] старый текст - новый текст словарь картограммы
    :param section_name: название шаблоона Literal["b03", "b01", "b02"]
    :param mode: метка для обозначения заполнения начальной или конечной картограммы
    :return: None
    """
    template = os.path.join(os.path.curdir, "template", f"{section_name}.odt")
    result = os.path.join(os.path.curdir, "output", f"Начальная картограмма отсека {section_name} БВ.odt") \
        if mode == "initial" \
        else os.path.join(os.path.curdir, "output", f"Конечная картограмма отсека {section_name} БВ.odt")
    doc = load(template)
    textboxes = doc.getElementsByType(draw.TextBox)
    for textbox in textboxes:
        paragraphs = textbox.getElementsByType(text.P)
        for p in paragraphs:
            set_text(p, map)
    doc.save(result)


if __name__ == "__main__":
    fill_bv_section({"TVS48-117": "N123456789", "AR48-117": "N123456 2023г."}, "b03", "initial")
