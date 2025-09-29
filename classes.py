class TVS:
    def __init__(self, number: str, heat: float, bv_coord: str, ps: str):
        self.number: str = number
        self.heat = heat
        self.bv_coord = bv_coord
        self.ps = ps

    def __repr__(self):
        return f"{self.number}  {round(self.heat, 4)} {self.bv_coord} {self.ps}"


class Cell:
    def __init__(self, tvs, number):
        self.number = number
        self.tvs = tvs

    def __repr__(self):
        return f"{self.number}: {self.tvs}"


class Container:
    def __init__(self, number, **kwargs):
        self.number = number
        self.cells_num = kwargs["cells_num"] if kwargs.get("cells_num") else 12
        self.heat = 0.0
        self.tvs_lst = []
        self.outer_layer = [Cell(None, i) for i in range(1, 7)]
        self.inner_layer = [Cell(None, i) for i in range(7, 13)]

    def __repr__(self):
        return f"Контейнер № {self.number}; кол-во ТВС: {len(self.tvs_lst)}; средн. тепловыд.:{self.heat}."

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
            cell.tvs = self.tvs_lst.pop(hot_tvs_idx)

        for cell in self.outer_layer:
            try:
                cell.tvs = self.tvs_lst.pop()
            except IndexError:
                pass
