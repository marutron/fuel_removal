"""
В данном модуле представлены классы и методы для парсинга файла БД ТОПАЗа ПОБАЙТОВО:

здесь не производится парсинг в python-ориентированные структуры, только лишь представлены классы и методы для парсинга
входного файла с использованием я.п. Python3.
"""
import os.path


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

    def encode(self):
        """Возвращает конкатенацию строк sort, nomer, indeks для получения байтового представления"""
        return self.sort + self.nomer + self.indeks


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
        pass


class aktiv_OE:
    """
    TOTAL - 168 bytes

    k_OE_akt: array[1..14] of k_mass - 168 bytes
    """

    def __init__(self, chunk):
        self.k_OE_akt = chunk

    def encode(self):
        """
        Возвращает байтовую форму полей класса
        :return:
        """
        return self.k_OE_akt


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

    def __init__(self):
        pass


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

    def __init__(self):
        pass


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
    gdo: real48 - 6 bytes  # масса GdO [г]
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
        self.k_OE_akt = aktiv_OE(chunk[617:785])
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
        self.history = chunk[1011:1430]
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

    def encode(self):
        """
        Возвращает байтовую форму полей класса
        :return:
        """
        data = []
        for item in self.__dict__.values():
            try:
                data.append(item.encode())
            except AttributeError:
                data.append(item)
        return b"".join(data)

    def replace_by_zero(self):
        """
        Заменяет все значения полей на байтовые нули
        :return: Возвращает байтовое значение
        """
        for key in self.__dict__.keys():
            value = self.__dict__[key]
            try:
                b_value = value.encode()
            except AttributeError:
                b_value = value
            new_value = bytes(len(b_value))
            self.__dict__[key] = new_value
        return self.encode()


def read_topaz(file):
    """
    Считывает файл ТОПАЗ, производя байтовый парсинг (декодирование и изменение не производятся здесь!)
    :return: list[K]
    """
    file_size = os.path.getsize(file)  # размер файла
    chunk_size = 1749  # размер описания одной ТВС
    pool = []
    with open(file, "rb") as inp:
        while file_size >= chunk_size:
            k = K(inp.read(chunk_size))
            pool.append(k)
            file_size -= chunk_size
        tail = inp.read()
        if tail != b"":
            print(f"Файл ТОПАЗ считан не полностью, осталось {len(tail)} нераспределенных байт.")
            print(f"Вывод нераспределенных байт считанного файла ТОПАЗ:\n{tail}")
        else:
            print("Файл ТОПАЗ считан полностью.")
        return pool


def write_topaz(pool: list[K]):
    """
    Записывает файл ТОПАЗ из переданных ТВС в pool
    :param pool: список ТВС, переданных для записи в файл
    :return: file
    """
    pass


if __name__ == "__main__":
    input_file = "ZAGR96TVS"
    res = read_topaz(input_file)
