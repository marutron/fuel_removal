import os

from odf import text
from odf.opendocument import load

from cartogram_handler import set_text


def fill_passport(data: dict[str, str]):
    """
    Заполняет таблицу паспорта ТК по данным в полученном словаре. Результат сохраняет в папку result.
    Номер ТУК передается в словаре data["container_number"]
    :param data: dict[str, str] старый текст - новый текст словарь таблицы
    :return: None
    """
    template = os.path.join(os.path.curdir, "template", "passport_tk.odt")
    result = os.path.join(os.path.curdir, "output", f"Паспорт ТУК № {data.get("container_number")}.odt")
    doc = load(template)
    paragraphs = doc.getElementsByType(text.P)
    for p in paragraphs:
        set_text(p, map)
    doc.save(result)
