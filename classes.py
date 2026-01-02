# ------------------------------------TOPAZ classes---------------------------------------------------------------------
# Здесь представлены классы и методы для представления сущностей БД ТОПАЗа ПОБАЙТОВО:
from datetime import datetime
from typing import Optional

from constants import DATE_FORMAT, EXPOSURE_DAYS
from services import parse_real48


class tp:
    """
    TOTAL - 26 bytes

    Python-представление структуры "tip: tp" ТОПАЗ (Var_sufl.pas)
    sort: string[10] - 11 bytes
    nomer: string[10] - 11 bytes
    indeks: string[3] - 4 bytes
    """

    def __init__(self, chunk: bytes):
        # не декодируем на этой стороне, только считываем
        self.sort = chunk[0:11]
        self.nomer = chunk[11:22]
        self.indeks = chunk[22:26]

    def __repr__(self):
        return f"{self.sort} + {self.nomer} + {self.indeks}"


class his_sp:
    """
    TOTAL - 28 bytes

    nom_kam: byte - 1 byte
    nom_gr: byte - 1 byte
    nom_ych: byte - 1 byte
    tvs: string[20] - 21 byte
    most: word - 2 bytes (little-endian)
    tel: word - 2 bytes (little-endian)
    """

    def __init__(self, chunk):
        pass


class sp:
    """
    TOTAL - 592 bytes

    Python-представление структуры "cp: sp" ТОПАЗ (Var_sufl.pas)
    Длины полей в байтах
    nomer: string[10] - 11 bytes
    ty: string[30] - 31 bytes
    cher: string[30] - 31 bytes
    otr_cam: byte - 1 byte
    teff: real48 - 6 bytes
    max_timeAZ: word - 2 bytes (little-endian)
    max_timerr: word - 2 bytes (little-endian)
    h_cp: array[1..15] of his_sp - 420 bytes
    datain: string[10] - 11 bytes
    dataout: string[10] - 11 bytes
    dataotpr: string[10] - 11 bytes
    Teff_az: LongWord - 4 bytes (little-endian)
    Teff_rr: LongWord - 4 bytes (little-endian)
    ostatok_AZ: real48 - 6 bytes
    ostatok_RR: real48 - 6 bytes
    contCP: string[34] - 35 bytes
    """

    def __init__(self, chunk):
        self.nomer = chunk[0:11]
        self.ty = chunk[11:42]
        self.cher = chunk[42:73]
        self.otr_cam = chunk[73:74]
        self.teff = chunk[74:80]
        self.max_timeAZ = chunk[80:82]
        self.max_timerr = chunk[82:84]
        self.h_cp = chunk[84:504]
        self.datain = chunk[504:515]
        self.dataout = chunk[515:526]
        self.dataotpr = chunk[526:537]
        self.Teff_az = chunk[537:541]
        self.Teff_rr = chunk[541:545]
        self.ostatok_AZ = chunk[545:551]
        self.ostatok_RR = chunk[551:557]
        self.contCP = chunk[557:592]

    def __repr__(self):
        return (f"nomer: {self.nomer} "
                f"\n ty: {self.ty} "
                f"\n cher: {self.cher}")

    def encode(self):
        """
        Возвращает байтовую форму полей класса
        :return:
        """
        return b"".join(self.__dict__.values())


class k_mass:
    """
    TOTAL - 12 bytes

    ost: real48 - 6 bytes
    aktiv: real48 - 6 bytes
    """

    def __init__(self, chunk):
        ost_aktiv_chunk_size = 6

        self.ost = chunk[0:ost_aktiv_chunk_size]
        self.aktiv = chunk[ost_aktiv_chunk_size:]

    def __repr__(self):
        return f"ost: {self.ost}, aktiv: {self.aktiv}"


class aktiv_OE:
    """
    TOTAL - 168 bytes

    k_OE_akt: array[1..14] of k_mass - 168 bytes
    """

    def __init__(self, chunk):
        k_mass_size = 12
        k_mass_count = 14

        starts = [i * k_mass_size for i in range(k_mass_count)]
        ends = [s + k_mass_size for s in starts]
        self.aktiv_OE = [k_mass(chunk[s:e]) for s, e in zip(starts, ends)]

    def __repr__(self):
        return self.aktiv_OE


class kamNew:
    """
    TOTAL - 50 bytes

    n_kamp: byte - 1 byte
    bgn_kam: string[10] - 11 bytes  # запись в начале кампании
    end_kam: string[10] - 11 bytes
    cp: string[10] - 11 bytes
    shl_end: real48 - 6 bytes
    teff: real48 - 6 bytes
    rn: byte - 1 byte
    n360: byte - 1 byte
    most: byte - 1 byte
    tel: byte - 1 byte
    """

    def __init__(self, chunk):
        self.n_kamp = chunk[0:1]
        self.bgn_kam = chunk[1:12]
        self.end_kam = chunk[12: 23]
        self.cp = chunk[23: 34]
        self.shl_end = chunk[34: 40]
        self.teff = chunk[40: 46]
        self.rn = chunk[46:47]
        self.n360 = chunk[47:48]
        self.most = chunk[48:49]
        self.tel = chunk[49:50]


class hagNew:
    """
    TOTAL - 13 bytes

    most: byte - 1 byte
    tel: byte - 1 byte
    when: string[10] - 11 bytes
    """

    def __init__(self):
        pass


class hNew:
    """
    TOTAL - 419 bytes

    kamp: array[0..5] of kamNew - 250 bytes
    peremec: array[0..13] of hagNew - 169 bytes
    """

    def __init__(self, chunk):
        kamp_size = 250
        kamNew_size = 50
        kamNew_count = 5

        self.peremec = chunk[kamp_size:]  # пока не реализуем, т.к. не понадобилось
        kamp_chunk = chunk[0:kamp_size]

        starts = [i * kamNew_size for i in range(kamNew_count)]
        ends = [s + kamNew_size for s in starts]
        self.kamp = [kamNew(kamp_chunk[s:e]) for s, e in zip(starts, ends)]


class K:
    """
    TOTAL - 1686 bytes (1749 bytes)

    tip: tp - 26 bytes  # идентификатор ТВС
    cp: sp - 592 bytes   # СП СУЗ
    k_OE_akt - aktiv_OE - 168 bytes
    mesto: string[4] - 5 bytes  # место нахождения ТВС: реактор / БВ
    way: word - 2 bytes номер ячейки, куда переходит ТВС в процессе перегрузки
    ty: string[30] - 31 bytes       # ТУ ТВС
    cher: string[30] - 31 bytes     # чертеж ТВС
    datap: string[10] - 11 bytes    # дата производства ТВС
    datapr: string[10] - 11 bytes   # дата поступления на АЭС
    datin: string[10] - 11 bytes    # дата загрузки в реактор
    datout: string[10] - 11 bytes   # дата выгрузки в БВ
    dataotp: string[10] - 11 bytes  # дата отправки
    shlak: real48 - 6 bytes     # шлаки ТВС
    most: byte - 1 byte     # мост
    tel: byte - 1 byte      # телега
    n360: byte - 1 byte     # номер ячейки реактора (симметрия 360)
    rn: byte - 1 byte       # номер ячейки реактора (симметрия 60)
    otrkam: byte - 1 byte   # отработала кампаний ТВС
    potrkam: byte - 1 byte  # последняя отработанная кампания
    uo2:  real48  - 6 bytes # масса UO2 [г]
    u85:  real48 - 6 bytes  # масса U235 + U8 [г]
    u5c: real48 - 6 bytes  # масса U235 в свежей ТВС [г]
    u5: real48 - 6 bytes  # масса U235 в ТВС сейчас [г]
    u6: real48 - 6 bytes  # масса U236 [г]
    u8: real48 - 6 bytes  # масса U238 [г]
    p8: real48 - 6 bytes  # масса Pu238 [г]
    p9: real48 - 6 bytes  # масса Pu239 [г]
    p0: real48 - 6 bytes  # масса Pu240 [г]
    p1: real48 - 6 bytes  # масса Pu241 [г]
    p2: real48 - 6 bytes  # масса Pu242 [г]
    gdo: real48 - 6 bytes  # масса GdO [г] на самом деле - масса ТВС [кг]
    ost_ev: real48 - 6 bytes  # остаточное энерговыделение
    metka: str[10] - 11 bytes   # метка для служебных целей ???
    history: hNew - 419 bytes   # история ТВС
    postavcik: string[22] - 23 bytes
    poluchatel: string[19] - 20 bytes
    data_vh_k: string[19] - 20 bytes
    nom_tuk: string[19] - 20 bytes
    nakladnay: string[71] - 72 bytes
    kod_sob: byte - 1 byte
    mesto_tyk: byte - 1 byte
    naklanday_out: string[49] - 50 bytes
    aktiv: real48 - 6 bytes
    dat_ras_akt: string[10] - 11 bytes
    contekst: string[31] - 32 bytes
    tail: незадокумментированный остаток:
        задокумментированный размер экземпляра K - 1686 b, фактический размер - 1749 b.
    """

    def __init__(self, chunk):
        self.tip = tp(chunk[0:27])
        self.cp = sp(chunk[26:618])
        self.k_OE_akt = aktiv_OE(chunk[618:786])
        self.mesto = chunk[786:791]
        self.way = chunk[791:793]
        self.ty = chunk[793:824]
        self.cher = chunk[824:855]
        self.datap = chunk[855:866]
        self.datapr = chunk[866:877]
        self.datin = chunk[877:888]
        self.datout = chunk[888:899]
        self.dataotp = chunk[899:910]
        self.shlak = chunk[910:916]
        self.most = chunk[916:917]
        self.tel = chunk[917:918]
        self.n360 = chunk[918:919]
        self.rn = chunk[919:920]
        self.otrkam = chunk[920:921]
        self.potrkam = chunk[921:922]
        self.uo2 = chunk[922:928]
        self.u85 = chunk[928:934]
        self.u5c = chunk[934:940]
        self.u5 = chunk[940:946]
        self.u6 = chunk[946:952]
        self.u8 = chunk[952:958]
        self.p8 = chunk[958:964]
        self.p9 = chunk[964:970]
        self.p0 = chunk[970:976]
        self.p1 = chunk[976:982]
        self.p2 = chunk[982:988]
        self.gdo = chunk[988:994]
        self.ost_ev = chunk[994:1000]
        self.metka = chunk[1000:1011]
        self.history = hNew(chunk[1011:1430])
        self.postavcik = chunk[1430:1453]
        self.poluchatel = chunk[1453:1473]
        self.data_vh_k = chunk[1473:1493]
        self.nom_tuk = chunk[1493:1513]
        self.nakladnay = chunk[1513:1585]
        self.kod_sob = chunk[1585:1586]
        self.mesto_tyk = chunk[1586:1587]
        self.naklanday_out = chunk[1587:1637]
        self.aktiv = chunk[1637:1643]
        self.dat_ras_akt = chunk[1643:1654]
        self.contekst = chunk[1654:1686]
        self.tail = chunk[1686:]

    def __repr__(self):
        return f"ТВС: {self.tip}; ПС: {self.cp.nomer}; coord: {self.most}-{self.tel}; out: {self.datout}"


# ------------------------------------end of section TOPAZ classes------------------------------------------------------

class Campaign:
    """
    Содержит описание топливной кампании из истории перемещений ТВС
    """

    def __init__(self, kam_new: kamNew, codepage: str):
        """
        number: порядковый номер кампании ???
        begin: начало кампании
        end: конец кампании
        ar: номер ПС СУЗ (если был установлен)
        burn_end: выгорание в конце кампании
        t_eff: отработанное эффективное время
        rn: расчетный номер ячейки
        n360: номер в симмтрии 360
        most: мост
        tel: телега
        """
        len_bgn_kam = int(kam_new.bgn_kam[0])
        len_end_kam = int(kam_new.end_kam[0])
        len_cp = int(kam_new.end_kam[0])

        self.number = kam_new.n_kamp[0]
        begin = kam_new.bgn_kam[1:len_bgn_kam + 1].decode(codepage)
        try:
            self.begin = datetime.strptime(begin, DATE_FORMAT)
        except ValueError:
            pass
        end = kam_new.end_kam[1:len_end_kam + 1].decode(codepage)

        try:
            self.end = datetime.strptime(end, DATE_FORMAT)
        except:
            pass

        self.ar = None if len_cp == 0 else kam_new.cp[1: len_cp + 1].decode(codepage)
        self.burn_end = parse_real48(kam_new.shl_end)
        self.t_eff = parse_real48(kam_new.teff)
        self.rn = kam_new.rn[0]
        self.n360 = kam_new.n360[0]
        self.most = kam_new.most[0]
        self.tel = kam_new.tel[0]


class TVS:
    """
    rn: расчетный номер (симетрия 60)
    n360: номер в АЗ
    complete_camp: отработано кампаний
    last_camp: последняя отработанная кампания
    uo2: масса UO2 [граммы]
    u85: масса U5 + U8
    u5c: масса U5 в ТВС когда она была СТВС
    u5: масса U235 в ТВС [грамм]
    u6: масса U236 в ТВС [грамм]
    u8: масса U238 в ТВС [грамм]
    p8: масса Pu238 в ТВС [грамм]
    p9: масса Pu239 в ТВС [грамм]
    p0: масса Pu240 в ТВС [грамм]
    p1: масса Pu241 в ТВС [грамм]
    p2: масса Pu242 в ТВС [грамм]
    mass: масса ТВС [кг]
    heat: тепловыделение ТВС
    """

    def __init__(self, k: K, codepage: str, date: Optional[datetime] = None):
        # задаем границы жестко
        len_sort = int(k.tip.sort[0])
        len_nomer = int(k.tip.nomer[0])
        len_indeks = int(k.tip.indeks[0])

        sort = k.tip.sort[1:len_sort + 1].decode(codepage)
        nomer = k.tip.nomer[1:len_nomer + 1].decode(codepage)
        indeks = k.tip.indeks[1:len_indeks + 1].decode(codepage)

        self.number = sort + nomer + indeks

        len_ar = int(k.cp.nomer[0])
        ar = k.cp.nomer[1:len_ar + 1].decode(codepage)
        self.ar = None if ar == "" else ar

        self.most = k.most[0]
        self.tel = k.tel[0]
        self.coord = f"{k.most[0]}-{k.tel[0]}"

        self.year_out = k.datout[-4:].decode(codepage)

        len_cher = int(k.cher[0])
        self.cher = k.cher[1:len_cher + 1].decode(codepage)
        self.production_date = k.datap[1:].decode(codepage)
        self.date_in = k.datin[1:].decode(codepage)
        self.date_out = k.datout[1:].decode(codepage)
        self.burn = parse_real48(k.shlak)
        self.property = 'АО "Концерн Росэнергоатом"' if k.kod_sob == b" " else "Федеральная"

        self.rn = k.rn[0]  # расчетный номер (симетрия 60)
        self.n360 = k.n360[0]  # номер в АЗ
        self.complete_camp = k.otrkam[0]  # отработано кампаний
        self.last_camp = k.potrkam[0]  # последняя отработанная кампания
        self.uo2 = parse_real48(k.uo2)  # масса UO2 [граммы]
        self.u85 = parse_real48(k.u85)  # масса U5 + U8
        self.u5c = parse_real48(k.u5c)  # масса U5 в ТВС когда она была СТВС
        self.u5 = parse_real48(k.u5)  # масса U235 в ТВС [грамм]
        self.u6 = parse_real48(k.u6)  # масса U236 в ТВС [грамм]
        self.u8 = parse_real48(k.u8)  # масса U238 в ТВС [грамм]
        self.pu8 = parse_real48(k.p8)  # масса Pu238 в ТВС [грамм]
        self.pu9 = parse_real48(k.p9)  # масса Pu239 в ТВС [грамм]
        self.pu0 = parse_real48(k.p0)  # масса Pu240 в ТВС [грамм]
        self.pu1 = parse_real48(k.p1)  # масса Pu241 в ТВС [грамм]
        self.pu2 = parse_real48(k.p2)  # масса Pu242 в ТВС [грамм]
        self.summ_isotopes = self.u5 + self.u8 + self.pu8 + self.pu9 + self.pu0 + self.pu1 + self.pu2
        self.mass = parse_real48(k.gdo)  # масса ТВС [кг]
        self.heat = 0.0  # тепловыделение ТВС, задается только для ТВС, подлежащих отправке

        self.date_heat = k.dat_ras_akt

        self.heat_data = [parse_real48(elm.ost) for elm in k.k_OE_akt.aktiv_OE]
        self.activity_data = [parse_real48(elm.aktiv) for elm in k.k_OE_akt.aktiv_OE]

        self.history = [Campaign(elm, codepage) for elm in k.history.kamp if elm.bgn_kam != bytes(11)]

        if date:
            self.raw_heat = self.calculate_heat(date)

        pass

    def __repr__(self):
        return f"{self.number}  {self.ar}  {self.coord}  {self.heat}"

    def calculate_heat(self, date: datetime) -> float:
        """
        Вычисляет значение остаточного энерговыделения ТВС путем линейной интерполяции
        """
        try:
            last_campaign_end = self.history[-1].end
        except Exception:
            print(f"Невозможно вычислить остаточное энерговыделение ТВС {self.number}: ")
            print(f"(Проблемы с доступом к полям TVS.history)")
            return 0

        exposure = (date - last_campaign_end).days

        if exposure < EXPOSURE_DAYS[0]:
            print(f"Невозможно вычислить остаточное энерговыделение ТВС {self.number}: ")
            print(f"(Введена дата, предшествующая выгрузке ТВС из АЗ)")
            return 0
        elif exposure > EXPOSURE_DAYS[-1]:
            print(f"Невозможно вычислить остаточное энерговыделение ТВС {self.number}: ")
            print(f"(Введена дата, соответствующая выдержки ТВС более 30 лет)")
            return 0

        for i in range(0, len(EXPOSURE_DAYS) + 1):
            x2 = EXPOSURE_DAYS[i]
            if x2 >= exposure:
                y2 = self.heat_data[i]
                x1 = EXPOSURE_DAYS[i - 1]
                y1 = self.heat_data[i - 1]
                break

        return y1 + (exposure - x1) * (y2 - y1) / (x2 - x1)

    def get_passport(self, cell_number: int) -> dict:
        """
        Собирает данные для составления паспорта упаковки
        :return:
        """
        return {
            f"number{cell_number}": self.number,
            f"cher{cell_number}": self.cher,
            f"ar{cell_number}": self.ar if self.ar else "-",
            f"uo2_{cell_number}": str(round(self.uo2 / 1000, 3)).replace(".", ","),
            f"tvs_mass_{cell_number}": str(round(self.mass, 1)).replace(".", ","),
            f"u_init_{cell_number}": str(round(self.u85, 1)).replace(".", ","),
            f"u5_init_{cell_number}": str(round(self.u5c, 1)).replace(".", ","),
            f"prod_{cell_number}": self.production_date,
            f"date_in_{cell_number}": self.date_in,
            f"date_out_{cell_number}": self.date_out,
            f"burn_{cell_number}": str(round(self.burn, 2)).replace(".", ","),
            f"mU{cell_number}": str(round(self.u5 + self.u8, 1)).replace(".", ","),
            f"u5_{cell_number}": str(round(self.u5, 1)).replace(".", ","),
            f"u8_{cell_number}": str(round(self.u8, 1)).replace(".", ","),
            f"mPu{cell_number}": str(round(self.pu8 + self.pu9 + self.pu0 + self.pu1 + self.pu2, 1)).replace(".", ","),
            f"pu8_{cell_number}": str(round(self.pu8, 1)).replace(".", ","),
            f"pu9_{cell_number}": str(round(self.pu9, 1)).replace(".", ","),
            f"pu0_{cell_number}": str(round(self.pu0, 1)).replace(".", ","),
            f"pu1_{cell_number}": str(round(self.pu1, 1)).replace(".", ","),
            f"pu2_{cell_number}": str(round(self.pu2, 1)).replace(".", ","),
            f"heat_{cell_number}": str(round(self.heat, 2)).replace(".", ","),
            f"prop{cell_number}": self.property
        }

    def get_section(self) -> Optional[str]:
        """
        Возвращает название секции БВ, где находится ТВС
        :return: Optional[str]
        """
        if 43 <= self.most <= 58:
            return "b03"
        elif 60 <= self.most <= 75:
            return "b01"
        elif 76 <= self.most <= 90:
            return "b02"
        else:
            return None


class Cell:
    def __init__(self, number, tvs=None):
        self.number = number
        self.tvs = tvs

    def __repr__(self):
        return f"{self.number}: {self.tvs}"

    def is_empty(self):
        return True if self.tvs is None else False

    def removed_from_section_calculation(self, removed_from_b03, removed_from_b01, removed_from_b02):
        """
        Считает сколько ТВС вывезено из отсека
        :param removed_from_b03:
        :param removed_from_b01:
        :param removed_from_b02:
        :return:
        """
        if not self.is_empty():
            section = self.tvs.get_section()
            match section:
                case "b03":
                    removed_from_b03 += 1
                case "b01":
                    removed_from_b01 += 1
                case "b02":
                    removed_from_b02 += 1
                case None:
                    print(f"Попытка вывезти ТВС не из БВ (координаты: {self.tvs.coord})")
        return removed_from_b03, removed_from_b01, removed_from_b02

    def get_empty_passport(self) -> dict:
        """
        Собирает данные для составления паспорта упаковки
        :return:
        """
        return {
            f"number{self.number}": "-",
            f"cher{self.number}": "-",
            f"ar{self.number}": "-",
            f"uo2_{self.number}": "-",
            f"tvs_mass_{self.number}": "-",
            f"u_init_{self.number}": "-",
            f"u5_init_{self.number}": "-",
            f"prod_{self.number}": "-",
            f"date_in_{self.number}": "-",
            f"date_out_{self.number}": "-",
            f"burn_{self.number}": "-",
            f"mU{self.number}": "-",
            f"u5_{self.number}": "-",
            f"u8_{self.number}": "-",
            f"mPu{self.number}": "-",
            f"pu8_{self.number}": "-",
            f"pu9_{self.number}": "-",
            f"pu0_{self.number}": "-",
            f"pu1_{self.number}": "-",
            f"pu2_{self.number}": "-",
            f"heat_{self.number}": "-",
            f"prop{self.number}": "-",
        }


class Container:
    def __init__(self, number, **kwargs):
        self.number = number
        self.cells_num = kwargs["cells_num"] if kwargs.get("cells_num") else 12
        self.heat = 0.0
        self.tvs_lst = []
        self.cells = [Cell(i) for i in range(1, 13)]

    def __repr__(self):
        return f"Контейнер № {self.number}; кол-во ТВС: {self.get_tvs_count()}; тепловыделение: {round(self.heat, 4)}."

    def cell_gen_upload(self):
        """
        Генератор ячеек на загрузку
        :return:
        """
        queue = [7, 10, 12, 9, 8, 11, 1, 4, 5, 2, 3, 6]
        for i in queue:
            yield self.cells[i - 1]

    def cell_gen_upload_tvv(self):
        """
        Оставляет незагруженными ячейки 1 и 5 как ближайшие к соседним поездам
        :return:
        """
        queue = [7, 10, 12, 9, 8, 11, 2, 4, 3, 6, 1, 5]
        for i in queue:
            yield self.cells[i - 1]

    def add_mp_data(self, oper_gen, mp_file):
        """
        Добавляет в файл МП данные о перестановках для формирования чехла
        :param oper_gen: генератор номера операции
        :param mp_file: файл для записи данных для МП
        :return: None
        """
        with open(mp_file, "a") as file:
            for cell in self.cells:
                if not cell.is_empty():
                    ar_code = "606" if cell.tvs.ar else "600"
                    coord_split = cell.tvs.coord.split("-")
                    most = coord_split[0]
                    tel = coord_split[1]
                    file.write(
                        f"{next(oper_gen)}	12	{ar_code}	{cell.tvs.number}	{most}	{tel}	100{self.number}		{cell.number}		N	00:00	00:00	00:00	00:00	0	0	0	0	0\n"
                    )

    def get_tvs_count(self):
        """
        Возвращает количество ТВС в контейнере
        :return: int
        """
        if len(self.tvs_lst) > 0:
            return len(self.tvs_lst)
        else:
            return sum([0 if cell.is_empty() else 1 for cell in self.cells])

    def calculate_heat(self):
        """
        Рассчитывает тепловыделение контейнера
        :return:
        """
        self.heat = sum(tvs.heat for tvs in self.tvs_lst)

    def sort_tvs_lst(self):
        """
        Сортирует ТВС в списке self.tvs_lst по возрастанию энерговыделения
        :return:
        """
        self.tvs_lst = sorted(self.tvs_lst, key=lambda tvs: tvs.heat, reverse=False)

    def fill_cells(self):
        """
        Заполняет ячейки объектами ТВС
        :return:
        """
        self.sort_tvs_lst()
        cell_iter = iter(self.cell_gen_upload())
        while True:
            try:
                cell = next(cell_iter)
            except StopIteration:
                return
            try:
                cell.tvs = self.tvs_lst.pop()
            except IndexError:
                return

    def get_cartogram(self):
        """
        Составляет словарь, используемый для заполнения картограмм ТК-13
        :return: dict[str, str] в формате, описанном в odt_handler.py / add_tk_13()
        """
        cartogram = {}

        def add_cell(cartogram, cell):
            """
            Добавляет ячейку в словарь картограммы
            :param cartogram: словарь для передачи в обработчик картограммы
            :param cell: ячейка контейенра
            :return: словарь картограммы
            """
            if not cell.is_empty():
                cartogram[f"TVS{cell.number}"] = cell.tvs.number
                cartogram[f"AR{cell.number}"] = cell.tvs.ar if cell.tvs.ar else "-"
            else:
                cartogram[f"TVS{cell.number}"] = "-"
                cartogram[f"AR{cell.number}"] = "-"
            return cartogram

        for cell in self.cells:
            cartogram = add_cell(cartogram, cell)

        cartogram["n"] = self.number

        return cartogram

    def get_permutations(self, oper_gen):
        """
        Составляет список списков, используемый для заполнения таблицы перестановок в виде:
        [список состоящий из строк таблицы [список значений ячеек строки таблицы]]
        :param: oper_gen: генератор номера операции
        :return:
        """
        permutations = []

        def add_cell(permutations: list, cell):
            """
            Добавляет ячейку в словарь картограммы
            :param permutations: список из значений строк таблицы
            :param cell: ячейка контейенра
            :return: список значений для вставки в строку таблицы
            """
            ar = cell.tvs.ar if cell.tvs.ar else "-"
            permutations.append(
                [f"{next(oper_gen)}", f"{cell.tvs.number}", f"{ar}", f"{cell.tvs.coord}", " ", " ", f"{cell.number}"])
            return permutations

        for cell in self.cells:
            if not cell.is_empty():
                permutations = add_cell(permutations, cell)

        return permutations

    def get_passport_data(self) -> dict[str, str]:
        """
        Заполняет словарь для формирования паспорта упаковки
        :return:
        """
        data = {}
        for cell in self.cells:
            if cell.tvs is not None:
                data.update(cell.tvs.get_passport(cell.number))
            else:
                data.update(cell.get_empty_passport())
        data["heat_overall"] = str(round(self.heat, 2)).replace(".", ",")
        data["container_number"] = self.number
        return data
