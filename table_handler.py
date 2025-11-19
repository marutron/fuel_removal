from copy import deepcopy

from odf.text import P
from odf.opendocument import load
from odf.table import *


class ODFHandler:
    def __init__(self, file):
        self.document = load(file)
        self.tables = self.document.getElementsByType(Table)

    def __repr__(self):
        return self.document.getAttribute('name')

    def get_table_by_name(self, table_name: str):
        for table in self.tables:
            if table.getAttribute('name') == table_name:
                return table

    def save(self, save_file_name):
        self.document.save(save_file_name)


class TableHandler:
    def __init__(self, document_table: Table):
        self.table = document_table

    def __repr__(self):
        return self.table.getAttribute('name')

    def get_row(self, row_number: int = None) -> TableRow or TableRows or None:
        result = None
        if row_number is None:
            result = self.table.getElementsByType(TableRow)
        else:
            try:
                result = self.table.getElementsByType(TableRow)[row_number]
            except:
                pass

        return result

    def get_cell_paragraph(self, row_number: int, column_number: int, paragragraph_number: int) -> None or P:
        result = None
        try:
            cell = self.get_cell(row_number, column_number)
            result = cell.getElementsByType(P)[paragragraph_number]
        except:
            pass
        return result

    def get_cell(self, row_number: int, column_number: int) -> TableCell or None:
        result = None
        try:
            table_row = self.get_row(row_number)
            result = table_row.getElementsByType(TableCell)[column_number]
        except:
            pass

        return result

    def clone_row(self, row_number: int):
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


if __name__ == "__main__":
    doc = ODFHandler("template/table.odt")
    table = TableHandler(doc.get_table_by_name("Таблица1"))

    table.clone_row(2)
    table.fill_row(2, ["a", "b", "c"])

    doc.save("result/output.odt")
    pass
