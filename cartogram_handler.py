import os.path

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
    :param element: рассматриаваемый элемент
    :param new_text: dict[str, str]: старый текст - новый текст
    """
    # Собираем все текстовые узлы
    text_nodes = []
    collect_text_nodes(element, text_nodes)

    # Если текстовых узлов нет — выходим
    if not text_nodes:
        print("В элементе не найдено ни одного текстового узла. Замен не произведено.")
        return

    for node in text_nodes:
        if new_text.get(node.data):
            node.data = new_text[node.data]


def add_tk_13(replace_text: dict):
    """
    Получает на вход словарь с заменяемыми величинами и создает новую картограмму ТК-13
    :param replace_text: dict[str, str] старый текст - новый текст
    :return: None
    """
    template = os.path.join(os.path.curdir, "template", "tk-13.odt")
    result = os.path.join(os.path.curdir, "result", f"Картограмма ТК № {replace_text.get('n')}.odt")
    doc = load(template)
    textboxes = doc.getElementsByType(draw.TextBox)
    for textbox in textboxes:
        paragraphs = textbox.getElementsByType(text.P)
        for p in paragraphs:
            set_text(p, replace_text)
    doc.save(result)

def fill_bv(replace_text: dict):
    """
    Заполняет картограмму БВ по данным в полученном словаре. Результат сохраняет в папку result.
    :param replace_text: dict[str, str] старый текст - новый текст
    :return: None
    """
    template = os.path.join(os.path.curdir, "template", "map.odt")
    result = os.path.join(os.path.curdir, "result", "Картограмма БВ.odt")
    doc = load(template)

    textboxes = doc.getElementsByType(draw.TextBox)
    for textbox in textboxes:
        paragraphs = textbox.getElementsByType(text.P)
        for p in paragraphs:
            set_text(p, replace_text)
    doc.save(result)


if __name__ == "__main__":
    fill_bv({"TVS48-117": "N123456789", "AR48-117": "N123456 2023г."})
