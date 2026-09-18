# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import sys
from pathlib import Path

空 = "·"
红子 = set("俥傌相仕帅炮兵")
黑子 = set("車馬象士將砲卒")


def 阵营(子):
    if 子 in 红子:
        return "红"
    if 子 in 黑子:
        return "黑"
    return ""


def 读局面(文本):
    行 = 文本.splitlines()
    if 行 and 行[-1] == "":
        行 = 行[:-1]
    if len(行) != 11 or 行[0] not in ("红", "黑"):
        return None
    盘文 = 行[1:]
    允许 = 红子 | 黑子 | {空}
    帅数 = 将数 = 0
    盘 = []
    for 行文 in 盘文:
        if len(行文) != 9 or any(字 not in 允许 for 字 in 行文):
            return None
        帅数 += 行文.count("帅")
        将数 += 行文.count("將")
        盘.append(list(行文))
    if 帅数 != 1 or 将数 != 1:
        return None
    return 行[0], 盘


def 找(盘, 子):
    for 行号 in range(10):
        for 列号 in range(9):
            if 盘[行号][列号] == 子:
                return 行号, 列号
    return None


def 直线格(行1, 列1, 行2, 列2):
    if 行1 == 行2 and 列1 != 列2:
        步 = 1 if 列2 > 列1 else -1
        return [(行1, 列) for 列 in range(列1 + 步, 列2, 步)]
    if 列1 == 列2 and 行1 != 行2:
        步 = 1 if 行2 > 行1 else -1
        return [(行, 列1) for 行 in range(行1 + 步, 行2, 步)]
    return None


def 在宫里(边, 行号, 列号):
    if not 3 <= 列号 <= 5:
        return False
    if 边 == "红":
        return 7 <= 行号 <= 9
    return 0 <= 行号 <= 2


def 走法理由(盘, 行1, 列1, 行2, 列2):
    子 = 盘[行1][列1]
    边 = 阵营(子)
    行差 = 行2 - 行1
    列差 = 列2 - 列1
    终点有子 = 盘[行2][列2] != 空

    if 子 in ("俥", "車"):
        格 = 直线格(行1, 列1, 行2, 列2)
        if 格 is None:
            return "这个子不能这么走"
        if any(盘[行号][列号] != 空 for 行号, 列号 in 格):
            return "车被挡住"
        return None

    if 子 in ("傌", "馬"):
        if sorted((abs(行差), abs(列差))) != [1, 2]:
            return "这个子不能这么走"
        if abs(行差) == 2:
            腿行 = 行1 + (1 if 行差 > 0 else -1)
            腿列 = 列1
        else:
            腿行 = 行1
            腿列 = 列1 + (1 if 列差 > 0 else -1)
        if 盘[腿行][腿列] != 空:
            return "马腿被挡"
        return None

    if 子 in ("相", "象"):
        if abs(行差) != 2 or abs(列差) != 2:
            return "这个子不能这么走"
        if 子 == "相" and 行2 < 5:
            return "象不能过河"
        if 子 == "象" and 行2 > 4:
            return "象不能过河"
        if 盘[行1 + 行差 // 2][列1 + 列差 // 2] != 空:
            return "象眼被塞"
        return None

    if 子 in ("仕", "士"):
        if abs(行差) != 1 or abs(列差) != 1:
            return "这个子不能这么走"
        if not 在宫里(边, 行2, 列2):
            return "士不能出宫"
        return None

    if 子 in ("帅", "將"):
        if abs(行差) + abs(列差) != 1:
            return "这个子不能这么走"
        if not 在宫里(边, 行2, 列2):
            if 子 == "帅":
                return "帅不能出宫"
            return "将不能出宫"
        return None

    if 子 in ("炮", "砲"):
        格 = 直线格(行1, 列1, 行2, 列2)
        if 格 is None:
            return "这个子不能这么走"
        隔子 = sum(1 for 行号, 列号 in 格 if 盘[行号][列号] != 空)
        if 终点有子:
            if 隔子 != 1:
                return "炮要隔一个才能吃"
            return None
        if 隔子 != 0:
            return "炮平移不能有子"
        return None

    if 子 == "兵":
        过河 = 行1 <= 4
        向前 = 行差 == -1 and 列差 == 0
        横走 = 行差 == 0 and abs(列差) == 1
        if 向前 or (过河 and 横走):
            return None
        return "兵不能这么走"

    if 子 == "卒":
        过河 = 行1 >= 5
        向前 = 行差 == 1 and 列差 == 0
        横走 = 行差 == 0 and abs(列差) == 1
        if 向前 or (过河 and 横走):
            return None
        return "卒不能这么走"

    return "这个子不能这么走"


def 将帅照面(盘):
    红帅 = 找(盘, "帅")
    黑将 = 找(盘, "將")
    if 红帅 is None or 黑将 is None or 红帅[1] != 黑将[1]:
        return False
    格 = 直线格(红帅[0], 红帅[1], 黑将[0], 黑将[1])
    return all(盘[行号][列号] == 空 for 行号, 列号 in 格)


def 自己会被将(盘, 边):
    自家 = "帅" if 边 == "红" else "將"
    位置 = 找(盘, 自家)
    if 位置 is None:
        return False
    对方 = "黑" if 边 == "红" else "红"
    目标行, 目标列 = 位置
    for 行号 in range(10):
        for 列号 in range(9):
            if 阵营(盘[行号][列号]) != 对方:
                continue
            if 走法理由(盘, 行号, 列号, 目标行, 目标列) is None:
                return True
    return False


def 判定(边, 盘, 数字):
    if len(数字) != 4 or any(not isinstance(数, int) for 数 in 数字):
        return 1, "", "着法不对\n"
    行1, 列1, 行2, 列2 = 数字
    if not (0 <= 行1 <= 9 and 0 <= 行2 <= 9 and 0 <= 列1 <= 8 and 0 <= 列2 <= 8):
        return 1, "", "着法不对\n"
    if (行1, 列1) == (行2, 列2):
        return 1, "", "着法不对\n"
    子 = 盘[行1][列1]
    if 子 == 空:
        return 1, "", "起点是空的\n"
    if 阵营(子) != 边:
        return 1, "", "轮不到这边\n"
    终点 = 盘[行2][列2]
    if 终点 != 空 and 阵营(终点) == 边:
        return 1, "", "不能吃自己人\n"
    理由 = 走法理由(盘, 行1, 列1, 行2, 列2)
    if 理由:
        return 1, "", 理由 + "\n"
    吃掉主将 = 终点 in ("帅", "將")
    新盘 = [list(行) for 行 in 盘]
    新盘[行2][列2] = 子
    新盘[行1][列1] = 空
    if not 吃掉主将:
        if 将帅照面(新盘):
            return 1, "", "将帅照面\n"
        if 自己会被将(新盘, 边):
            return 1, "", "自己会被将\n"
    return 0, "可以\n", ""


def 入口():
    路径 = Path.cwd() / "局面"
    try:
        文本 = 路径.read_text(encoding="utf-8")
    except OSError:
        sys.stderr.write("找不到局面\n")
        sys.exit(1)
    读到 = 读局面(文本)
    if 读到 is None:
        sys.stderr.write("局面不对\n")
        sys.exit(1)
    边, 盘 = 读到
    if len(sys.argv) != 5 or any(re.fullmatch(r"[0-9]+", 文) is None for 文 in sys.argv[1:]):
        sys.stderr.write("着法不对\n")
        sys.exit(1)
    数字 = [int(文) for 文 in sys.argv[1:]]
    码, 出, 错 = 判定(边, 盘, 数字)
    if 出:
        sys.stdout.write(出)
    if 错:
        sys.stderr.write(错)
    sys.exit(码)


if __name__ == "__main__":
    入口()
