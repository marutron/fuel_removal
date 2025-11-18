class TVS:
    def __init__(self, number: str, heat: float, bv_coord: str, ps: str, u5, u8, pu8, pu9, pu0, pu1, pu2):
        self.number: str = number
        self.heat = heat
        self.bv_coord = bv_coord
        self.ps = ps
        self.u5 = u5
        self.u8 = u8
        self.pu8 = pu8
        self.pu9 = pu9
        self.pu0 = pu0
        self.pu1 = pu1
        self.pu2 = pu2
        self.sum_isotopes = u5 + u8 + pu8 + pu9 + pu0 + pu1 + pu2

    def __repr__(self):
        return f"{self.number}  {round(self.heat, 4)} {self.bv_coord} {self.ps}"


class Cell:
    def __init__(self, number, tvs=None):
        self.number = number
        self.tvs = tvs

    def __repr__(self):
        return f"{self.number}: {self.tvs}"

    def is_empty(self):
        return True if self.tvs is None else False


class Container:
    def __init__(self, number, **kwargs):
        self.number = number
        self.cells_num = kwargs["cells_num"] if kwargs.get("cells_num") else 12
        self.heat = 0.0
        self.tvs_lst = []
        self.outer_layer = [Cell(i) for i in range(1, 7)]
        self.inner_layer = [Cell(i) for i in range(7, 13)]

    def __repr__(self):
        return f"Контейнер № {self.number}; кол-во ТВС: {self.get_tvs_count()}; тепловыделение: {round(self.heat, 4)}."

    def get_tvs_count(self):
        """
        Возвращает количество ТВС в контейнере
        :return: int
        """
        if len(self.tvs_lst) > 0:
            return len(self.tvs_lst)
        else:
            outer_count = sum([0 if i.is_empty() else 1 for i in self.outer_layer])
            inner_count = sum([0 if j.is_empty() else 1 for j in self.inner_layer])
            return inner_count + outer_count

    def calculate_heat(self):
        self.heat = sum(tvs.heat for tvs in self.tvs_lst)

    def fill_cells(self):
        for cell in self.inner_layer:
            max_heat = 0
            hot_tvs_idx = 100500
            for tvs in self.tvs_lst:
                if tvs.heat > max_heat:
                    max_heat = tvs.heat
                    hot_tvs_idx = self.tvs_lst.index(tvs)
            try:
                cell.tvs = self.tvs_lst.pop(hot_tvs_idx)
            except IndexError:
                pass

        for cell in self.outer_layer:
            try:
                cell.tvs = self.tvs_lst.pop()
            except IndexError:
                pass

    def get_cartogram(self):
        """
        Составляет словарь, используемый для заполнения картограмм ТК-13
        :return: dict[str, str] в формате, описанном в odt_handler.py / add_tk_13()
        """
        cartogram = {}

        def add_cell(cartogram, cell, empty_mode=False):
            """
            Добавляет ячейку в словарь картограммы
            :param cartogram: словарь для передачи в обработчик картограммы
            :param cell: ячейка контейенра
            :param empty_mode: параметр заполнения
            :return: словарь картограммы
            """
            cartogram[f"TVS{cell.number}"] = cell.tvs.number if not empty_mode else "-"
            cartogram[f"AR{cell.number}"] = " "  # todo заменить на номер ПС СУЗ
            return cartogram

        for cell in self.outer_layer:
            if not cell.is_empty():
                cartogram = add_cell(cartogram, cell, False)
            else:
                cartogram = add_cell(cartogram, cell, True)

        for cell in self.inner_layer:
            if not cell.is_empty():
                cartogram = add_cell(cartogram, cell, False)
            else:
                cartogram = add_cell(cartogram, cell, True)

        cartogram["n"] = self.number

        return cartogram
