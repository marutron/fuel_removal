from copy import deepcopy

from classes import Container, TVS


def get_aim_heat(mas, mode):
    if mode == "hot":
        aim_q = max((elm.heat for elm in mas))
    elif mode == "cold":
        aim_q = min(elm.heat for elm in mas)
    else:
        raise KeyError
    aim_index = [elm.heat for elm in mas].index(aim_q)
    if isinstance(mas[0], Container):
        return mas[aim_index]
    elif isinstance(mas[0], TVS):
        return mas.pop(aim_index)




def average_heat_calculation(mas):
    return sum([elm.heat for elm in mas]) / len(mas)


def disp_calculate(pool, avg_q):
    return sum([(_cont.heat - avg_q) ** 2 for _cont in pool])


def replace_tvs(cont_1: Container, cont_2: Container, tvs_1_num: int, tvs_2_num: int):
    tvs_1 = cont_1.tvs_lst[tvs_1_num]
    tvs_2 = cont_2.tvs_lst[tvs_2_num]

    cont_1.tvs_lst.remove(tvs_1)
    cont_2.tvs_lst.remove(tvs_2)

    cont_1.tvs_lst.insert(tvs_1_num, tvs_2)
    cont_2.tvs_lst.insert(tvs_2_num, tvs_1)


def equalizer_main(containers_count, tvs_pool, iterator):
    containers_pool = [Container(i) for i in range(iterator, iterator + containers_count)]
    iterator += containers_count

    while len(tvs_pool) > 0:
        cold_container = get_aim_heat(containers_pool, "cold")
        hot_tvs = get_aim_heat(tvs_pool, "hot")
        cold_container.tvs_lst.append(hot_tvs)
        cold_container.calculate_heat()

    avg_q = average_heat_calculation(containers_pool)
    base_disp = disp_calculate(containers_pool, avg_q)

    exp_containers_pool = deepcopy(containers_pool)
    for cont_1 in exp_containers_pool:
        for cont_2 in exp_containers_pool:
            if cont_1 != cont_2:
                for tvs_1_num in range(0, len(cont_1.tvs_lst)):
                    for tvs_2_num in range(0, len(cont_2.tvs_lst)):
                        replace_tvs(cont_1, cont_2, tvs_1_num, tvs_2_num)
                        cont_1.calculate_heat()
                        cont_2.calculate_heat()
                        exp_avg_q = average_heat_calculation(exp_containers_pool)
                        exp_disp = disp_calculate(exp_containers_pool, exp_avg_q)
                        if exp_disp < base_disp:
                            base_disp = exp_disp
                            containers_pool = exp_containers_pool
                        else:
                            replace_tvs(cont_1, cont_2, tvs_1_num, tvs_2_num)
                            cont_1.calculate_heat()
                            cont_2.calculate_heat()

    print("Выравнивание тепловыделения завершено")
    return containers_pool, iterator
