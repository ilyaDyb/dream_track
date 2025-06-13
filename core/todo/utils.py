xp_by_lvl = {
    1: 10,
    2: 15,
    3: 25
}

coins_by_lvl = {
    1: 5,
    2: 10,
    3: 20
}

def get_xp_by_lvl(lvl: int) -> int:
    return xp_by_lvl.get(lvl, 0)

def get_coins_by_lvl(lvl: int) -> int:
    return coins_by_lvl.get(lvl, 0)