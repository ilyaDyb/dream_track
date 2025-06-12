LEVELS = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 1000,
    6: 2000,
    7: 4000,
    8: 6000,
    9: 10000,
    10: 15000,
}

def get_level_by_xp(xp: int) -> int:
    levels_sorted = sorted(LEVELS.items(), key=lambda x: x[1])
    cur_level = 1
    for level, required_xp in levels_sorted:
        if xp >= required_xp:
            cur_level = level
        else:
            break
    return cur_level