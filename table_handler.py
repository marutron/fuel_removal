import os
from copy import deepcopy

from odf.text import P
from odf.opendocument import load
from odf.table import *

from text_replacers import set_text


class ODFHandler:
    """
    Обертка-обработчик odt-файлов
    """

    def __init__(self, file):
        self.document = load(file)
        self.tables = self.document.getElementsByType(Table)

    def __repr__(self):
        return self.document.getAttribute('name')

    def get_table_by_name(self, table_name: str):
        """
        Получает таблицу из документа по переданному имени
        :param table_name:
        :return: Optional(Table)
        """
        for table in self.tables:
            if table.getAttribute('name') == table_name:
                return table
        print(f"Таблицы с именем {table_name}' не существует в документе.")
        return None

    def save(self, file_name):
        """
        Сохнаняет файл по именем file_name
        :param file_name: имя сохраняемого файла
        :return:
        """
        self.document.save(file_name)


class TableHandler:
    def __init__(self, document_table: Table):
        self.table = document_table

    def __repr__(self):
        return self.table.getAttribute('name')

    def get_row(self, row_number: int = None) -> TableRow or TableRows or None:
        """
        Возвращает экземпляр строки таблицы (если найдет)
        :param row_number: номер искомой строки
        :return: Optional(TableRow)
        """
        row = None
        if row_number is None:
            row = self.table.getElementsByType(TableRow)
        else:
            try:
                row = self.table.getElementsByType(TableRow)[row_number]
            except IndexError:
                print("Запрошенный номер строки превышает количество строк таблицы")
        return row

    def clone_row(self, row_number: int):
        """
        Клонирует строку со всеми вложенными узлами.
        :param row_number: номер строки, которую клонируем
        :return: None
        """
        cloned_row = self.get_row(row_number)
        new_row = deepcopy(cloned_row)
        self.table.addElement(new_row)

    def fill_row(self, row_number: int, data: list):
        """
        Заполняет строку данными из переданного списка data
        :param row_number: номер заполняемой строки
        :param data: list[str] данные для занесения в строку (поячеично)
        :return: None
        """
        data_iter = iter(data)
        row = self.get_row(row_number)
        for cell in row.childNodes:
            try:
                par = cell.getElementsByType(P)[0]
            except IndexError:
                print("Попытка выхода за границы ячейки таблицы при заполнении.")
                print("Ячейка оставлена пустой.")
                return

            try:
                text = next(data_iter)
            except StopIteration:
                return
            par.addText(P(text=text))


def add_table(table_data: list, tk_data: dict, n: int):
    """
    Заполняет таблицу ТК-13 и сохраняет её в папке result.
    В словаре предусмотреть пару ключ-значение: {n: номер чехла}
    :param table_data: данные для заполнения таблицы list[list['str']] писок формата [список [список из значений ячеек]]
    :param tk_data: данные для заполнения картограммы dict[str, str] старый текст - новый текст
    :param n: int порядковый номер ТК-13
    :param operation_gen: генератор номера операции
    :return: None
    """
    template = os.path.join(os.path.curdir, "template", "table+tk.odt")
    result = os.path.join(os.path.curdir, "output", f"Таблица контейнера № {n}.odt")

    doc = ODFHandler(template)

    # пробегаем по документу, меняем "__" на номер ТК-13 (n)
    for paragraph in doc.document.getElementsByType(P):
        set_text(paragraph, tk_data)

    # заполняем таблицу перестановок
    table = TableHandler(doc.get_table_by_name("Таблица1"))
    row_iter = 2
    for row_data in table_data:
        table.clone_row(row_iter)
        table.fill_row(row_iter, row_data)
        row_iter += 1

    doc.save(result)
