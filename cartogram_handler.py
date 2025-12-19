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
