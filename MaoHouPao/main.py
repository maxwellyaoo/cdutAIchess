# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import os
import time
import re
from itertools import count
from collections import namedtuple
from datetime import datetime
import pygame

# 生成棋谱内容到文件MaoHouPao.txt中，并将棋谱内容转换为PGN格式
def convert_and_save_Date(input_str: str, output_file: str) -> None:
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("[Date:{}]\n".format(input_str))

def convert_and_save_Player(input_str: str, output_file: str) -> None:
    with open(output_file, 'a', encoding='utf-8') as file:
        if input_str == "1":
            file.write("[Red:{}]\n".format("Player"))
            file.write("[Black:{}]\n".format("MaHouPao"))
        else :
            file.write("[Red:{}]\n".format("MaHouPao"))
            file.write("[Black:{}]\n".format("Player"))

def convert_and_save_Undo(output_file: str) -> None:
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write("[Re]")

def convert_and_save_0(input_str: str, output_file: str) -> None:
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write("\n"+input_str)


def convert_and_save_1(input_str: str, output_file: str) -> None:
    # 将字符串中的小写字母转换为大写
    upper_str = input_str.upper()
    # 前2个字符后加“-”，再连接后2个字符
    converted_str = upper_str[0:2] + '-' + upper_str[2:4]
    # 将转换后的字符串写入文件
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write("    User:{}".format(converted_str))


def convert_and_save_2(input_str: str, output_file: str) -> None:
    # 将字符串中的小写字母转换为大写
    upper_str = input_str.upper()
    # 前2个字符后加“-”，再连接后2个字符
    converted_str = upper_str[0:2] + '-' + upper_str[2:4]
    # 将转换后的字符串写入文件
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write("    AI:{}".format(converted_str))

# piece字典定义了中国象棋中每种棋子的基本分值。这些分值是评估棋局时的基础，用于计算棋子的相对价值和棋局的得分。例如'P': 44表示兵的基本分值为44。
'''
● 'P': 兵（卒），分值为 44。
● 'N': 马（骑士），分值为 108。
● 'B': 象（相），分值为 23。
● 'R': 车（战车），分值为 233。
● 'A': 仕（顾问），分值为 23。
● 'C': 炮，分值为 101。
● 'K': 将（帅），分值为 2500。
'''
piece = {'P': 44, 
         'N': 108, 
         'B': 23, 
         'R': 233, 
         'A': 23, 
         'C': 101, 
         'K': 2500
         }


# 设置棋盘的位置常量
# A0和A9、I0和I9表示棋盘的边界位置
# A0 = 195（左下角）；I0 = 203（右下角）；A9 = 51（左上角）；I9 = 59（右上角）
A0, I0, A9, I9 = 12 * 16 + 3, 12 * 16 + 11, 3 * 16 + 3, 3 * 16 + 11

# 棋盘布局定义了中国象棋游戏开始时的初始设置，包括各种棋子的初始位置以及棋盘上的空白区域。
initial_map = (
    '               \n'  # 0 -  9
    '               \n'  # 10 - 19
    '               \n'  # 20 - 29
    '   rnbakabnr   \n'  # 30 - 39
    '   .........   \n'  # 40 - 49
    '   .c.....c.   \n'  # 50 - 59
    '   p.p.p.p.p   \n'  # 60 - 69
    '   .........   \n'  # 70 - 79
    '   .........   \n'  # 80 - 89
    '   P.P.P.P.P   \n'  # 90 - 99
    '   .C.....C.   \n'  # 100 - 109
    '   .........   \n'  # 110 - 119
    '   RNBAKABNR   \n'  # 120 - 129
    '               \n'  # 130 - 139
    '               \n'  # 140 - 149
    '               \n'  # 150 - 159
)

# directions 字典定义了中国象棋中每种棋子的合法移动方向。
N, E, S, W = -16, 1, 16, -1

directions = {
    'P': (N, W, E),
    'N': (N + N + E, E + N + E, E + S + E, S + S + E, S + S + W, W + S + W, W + N + W, N + N + W),
    'B': (2 * N + 2 * E, 2 * S + 2 * E, 2 * S + 2 * W, 2 * N + 2 * W),
    'R': (N, E, S, W),
    'C': (N, E, S, W),
    'A': (N + E, S + E, S + W, N + W),
    'K': (N, E, S, W)
}

# MATE_LOWER 和 MATE_UPPER 分别定义了评估棋局时的胜负评分阈值。
# MATE_LOWER 计算了在棋局中失去所有棋子（除了国王）的评分，即国王的价值减去两个车、两个马、两个象、两个士和五个兵的价值。
MATE_LOWER = piece['K'] - (
            2 * piece['R'] + 2 * piece['N'] + 2 * piece['B'] + 2 * piece['A'] + 2 * piece['C'] + 5 * piece['P'])
# MATE_UPPER 计算了在棋局中获得所有棋子的评分，即国王的价值加上两个车、两个马、两个象、两个士和五个兵的价值。
MATE_UPPER = piece['K'] + (
            2 * piece['R'] + 2 * piece['N'] + 2 * piece['B'] + 2 * piece['A'] + 2 * piece['C'] + 5 * piece['P'])

# TABLE_SIZE 定义了转置表（transposition table）的最大大小，单位是元素数量。转置表用于存储棋局评分和最佳移动，以加速搜索算法。
TABLE_SIZE = 1e7
# QS_LIMIT 是启发式搜索中的一个阈值，用于决定是否在某个深度下停止搜索，以节省时间。
QS_LIMIT = 219
# EVAL_ROUGHNESS 是评估函数中的一个参数，用于控制评分的粗糙度，影响搜索的精度。
EVAL_ROUGHNESS = 13
# DRAW_TEST是一个布尔值，用于控制是否进行和棋检测。如果为 True，则在搜索过程中检测三次重复局面，这可能导致和棋。
DRAW_TEST = True
# THINK_TIME 定义了AI思考的时间限制，单位是秒。这个值用于控制搜索的深度和广度，以确保AI在有限的时间内做出决策。
def level(nan):
    if nan == 1:
        return 4
    elif nan == 2:
        return 8
    elif nan == 3:
        return 12
    elif nan == 4:
        return 18
    elif nan == 5:
        return 24
#THINK_TIME = level()

# 位置状态表是一组用于评估棋子在棋盘上不同位置的价值的分数表。
# 每个棋子类型（如兵、马、炮等）都有其对应的位置评估，它是一个二维数组，数组中的每个元素代表该棋子在特定棋盘位置上的额外分值。
ping_gu = {
    "P": (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 9, 9, 9, 11, 13, 11, 9, 9, 9, 0, 0, 0, 0,
        0, 0, 0, 19, 24, 34, 42, 44, 42, 34, 24, 19, 0, 0, 0, 0,
        0, 0, 0, 19, 24, 32, 37, 37, 37, 32, 24, 19, 0, 0, 0, 0,
        0, 0, 0, 19, 23, 27, 29, 30, 29, 27, 23, 19, 0, 0, 0, 0,
        0, 0, 0, 14, 18, 20, 27, 29, 27, 20, 18, 14, 0, 0, 0, 0,
        0, 0, 0, 7, 0, 13, 0, 16, 0, 13, 0, 7, 0, 0, 0, 0,
        0, 0, 0, 7, 0, 7, 0, 15, 0, 7, 0, 7, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 11, 15, 11, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ),
    "B": (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 40, 0, 0, 0, 40, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 38, 0, 0, 40, 43, 40, 0, 0, 38, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 43, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 40, 40, 0, 40, 40, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ),
    "N": (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 90, 90, 90, 96, 90, 96, 90, 90, 90, 0, 0, 0, 0,
        0, 0, 0, 90, 96, 103, 97, 94, 97, 103, 96, 90, 0, 0, 0, 0,
        0, 0, 0, 92, 98, 99, 103, 99, 103, 99, 98, 92, 0, 0, 0, 0,
        0, 0, 0, 93, 108, 100, 107, 100, 107, 100, 108, 93, 0, 0, 0, 0,
        0, 0, 0, 90, 100, 99, 103, 104, 103, 99, 100, 90, 0, 0, 0, 0,
        0, 0, 0, 90, 98, 101, 102, 103, 102, 101, 98, 90, 0, 0, 0, 0,
        0, 0, 0, 92, 94, 98, 95, 98, 95, 98, 94, 92, 0, 0, 0, 0,
        0, 0, 0, 93, 92, 94, 95, 92, 95, 94, 92, 93, 0, 0, 0, 0,
        0, 0, 0, 85, 90, 92, 93, 78, 93, 92, 90, 85, 0, 0, 0, 0,
        0, 0, 0, 88, 85, 90, 88, 90, 88, 90, 85, 88, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ),
    "R": (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 206, 208, 207, 213, 214, 213, 207, 208, 206, 0, 0, 0, 0,
        0, 0, 0, 206, 212, 209, 216, 233, 216, 209, 212, 206, 0, 0, 0, 0,
        0, 0, 0, 206, 208, 207, 214, 216, 214, 207, 208, 206, 0, 0, 0, 0,
        0, 0, 0, 206, 213, 213, 216, 216, 216, 213, 213, 206, 0, 0, 0, 0,
        0, 0, 0, 208, 211, 211, 214, 215, 214, 211, 211, 208, 0, 0, 0, 0,
        0, 0, 0, 208, 212, 212, 214, 215, 214, 212, 212, 208, 0, 0, 0, 0,
        0, 0, 0, 204, 209, 204, 212, 214, 212, 204, 209, 204, 0, 0, 0, 0,
        0, 0, 0, 198, 208, 204, 212, 212, 212, 204, 208, 198, 0, 0, 0, 0,
        0, 0, 0, 200, 208, 206, 212, 200, 212, 206, 208, 200, 0, 0, 0, 0,
        0, 0, 0, 194, 206, 204, 212, 200, 212, 204, 206, 194, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ),
    "C": (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 100, 100, 96, 91, 90, 91, 96, 100, 100, 0, 0, 0, 0,
        0, 0, 0, 98, 98, 96, 92, 89, 92, 96, 98, 98, 0, 0, 0, 0,
        0, 0, 0, 97, 97, 96, 91, 92, 91, 96, 97, 97, 0, 0, 0, 0,
        0, 0, 0, 96, 99, 99, 98, 100, 98, 99, 99, 96, 0, 0, 0, 0,
        0, 0, 0, 96, 96, 96, 96, 100, 96, 96, 96, 96, 0, 0, 0, 0,
        0, 0, 0, 95, 96, 99, 96, 100, 96, 99, 96, 95, 0, 0, 0, 0,
        0, 0, 0, 96, 96, 96, 96, 96, 96, 96, 96, 96, 0, 0, 0, 0,
        0, 0, 0, 97, 96, 100, 99, 101, 99, 100, 96, 97, 0, 0, 0, 0,
        0, 0, 0, 96, 97, 98, 98, 98, 98, 98, 97, 96, 0, 0, 0, 0,
        0, 0, 0, 96, 96, 97, 99, 99, 99, 97, 96, 96, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    )
}

# # 仕（士）和象（相）使用相同的评估
ping_gu["A"] = ping_gu["B"]

# # 将（帅）和兵（卒）使用相同的评估作为基础
ping_gu["K"] = ping_gu["P"]

# 将的评估在兵的评估基础上加上其基本分值，如果原分值大于0
ping_gu["K"] = [i + piece["K"] if i > 0 else 0 for i in ping_gu["K"]]

# Position_0类

class Position_0(namedtuple('Position_0', 'board score')):
    """
    Position_0 类继承自 namedtuple，它是一个不可变的元组，包含 board 和 score 两个字段。
    这个类表示国际象棋游戏的一个状态：
    board 是一个包含 256 个字符的字符串，表示棋盘布局；
    score 是对当前棋盘局面的评估得分。
    """

    # gen_moves 方法生成当前位置下所有可能的合法移动。它遍历棋盘上每个棋子，并根据棋子类型生成移动。
    def gen_moves(self):

        for i, p in enumerate(self.board):

            # 国王特殊移动
            # 处理国王的移动，特别是“将”和“帅”的移动，它们在棋盘上的特定位置可以左右移动，但不能越过中心线。
            if p == 'K':
                # 这行开始一个循环，从当前帅的位置向上（即向北）扫描，步长为16，直到A9这个变量（左上角）所代表的位置。
                for scanpos in range(i - 16, A9, -16):
                    # 如果在扫描过程中发现对方帅（用小写的'k'表示），则生成一个元组(i, scanpos)，表示当前帅可以将军对方帅的位置。
                    if self.board[scanpos] == 'k':
                        # yield (i, scanpos) 这行是生成器的一部分，它生成并返回当前帅可以攻击到的对方帅的位置。
                        yield (i, scanpos)
                    # 如果在扫描过程中遇到任何非空位置（即不是'.'），则停止扫描。这意味着在当前帅和对方帅之间有其他棋子阻挡，无法将军。
                    elif self.board[scanpos] != '.':
                        break

            # 车（C）的移动
            # 车（C）可以直线移动，包括水平和垂直方向。代码中的 directions[p] 表示车的可能移动方向。

            # 检查当前遍历到的棋子p是否为大写字母。如果不是大写（即小写字母表示的棋子），则使用continue跳过当前循环的剩余部分，开始下一次循环迭代。
            # 这是因为在生成走法时，只需要考虑大写字母表示的己方棋子。
            if not p.isupper(): continue
            if p == 'C':
                # directions[p]提供了“车”可以移动的方向，它包括上下左右四个方向。
                for d in directions[p]:
                    cfoot = 0
                    # count(i+d, d)生成一个起始为i+d（即第一次移动后的坐标），步长为d的无限序列，代表“车”可以沿直线移动任意格，但不能跳过其他棋子。
                    for j in count(i + d, d):
                        # q是当前坐标j上的棋子。如果q是一个空格（即坐标为空），则退出当前内层循环。
                        q = self.board[j]
                        if q.isspace(): break
                        # 如果cfoot（捕获棋子计数器）为0，并且当前坐标j上的棋子是'.'（空位），则生成一个走法(i, j)。这是“车”在没有捕获任何棋子的情况下移动。
                        if cfoot == 0 and q == '.':
                            yield (i, j)
                        # 如果cfoot为0，且当前坐标j上有棋子（不是'.'），则将cfoot设置为1，表示“车”已经捕获了一个棋子。
                        elif cfoot == 0 and q != '.':
                            cfoot += 1
                        # 如果cfoot为1，并且当前坐标j上的棋子是小写字母（即敌方棋子），则生成一个捕获该棋子的走法(i, j)，然后退出内层循环。这是“车”在捕获一个敌方棋子后的走法。
                        elif cfoot == 1 and q.islower():
                            yield (i, j); break
                        # 如果cfoot为1，并且当前坐标j上的棋子是大写字母（即己方棋子），则退出内层循环。这是为了防止“车”移动到己方棋子的位置。
                        elif cfoot == 1 and q.isupper():
                            break
                continue

            # 其他棋子的移动
            # 处理其他棋子（如马、象、兵、炮）的移动。它遍历每个方向 d，并在该方向上生成所有可能的移动。
            for d in directions[p]:
                for j in count(i + d, d):
                    q = self.board[j]
                    if q.isspace() or q.isupper(): break
                    if p == 'P' and d in (E, W) and i > 128:
                        break
                    elif p in ('A', 'K') and (j < 160 or j & 15 > 8 or j & 15 < 6):
                        break
                    elif p == 'B' and j < 128:
                        break
                    elif p == 'N':
                        n_diff_x = (j - i) & 15
                        if n_diff_x == 14 or n_diff_x == 2:
                            if self.board[i + (1 if n_diff_x == 2 else -1)] != '.': break
                        else:
                            if j > i and self.board[i + 16] != '.':
                                break
                            elif j < i and self.board[i - 16] != '.':
                                break
                    elif p == 'B' and self.board[i + d // 2] != '.':
                        break

                    # 当找到一个合法的移动时，使用 yield 关键字生成一个包含起始位置 i 和目标位置 j 的元组。
                    yield (i, j)
                    if p in 'PNBAK' or q.islower(): break

    # revolve 方法旋转棋盘，同时保持吃过路兵（enpassant）的规则。返回一个新的 Position_0 对象，棋盘翻转，分数取反。
    def revolve(self):
        return Position_0(
            self.board[-2::-1].swapcase() + " ", -self.score)

    # nullmove 方法类似于 revolve，但它清除了吃过路兵和王车易位（kingside/queenside castling）的状态。
    def nullmove(self):
        return self.revolve()

    # move 方法执行一个给定的移动。它更新棋盘状态，计算新的评分，并返回一个新的 Position_0 对象。
    def move(self, move):
        # 从移动 move 中提取起始位置 i 和目标位置 j，更新棋盘上的棋子位置，计算移动的评分，并返回旋转后的棋盘状态。
        i, j = move
        p, q = self.board[i], self.board[j]
        put = lambda board, i, p: board[:i] + p + board[i + 1:]
        board = self.board
        score = self.score + self.value(move)
        board = put(board, j, board[i])
        board = put(board, i, '.')
        return Position_0(board, score).revolve()

    # value 方法计算一个移动的评分。它根据棋子的价值和移动后的位置来评估移动的得分。
    def value(self, move):
        i, j = move
        p, q = self.board[i], self.board[j]

        # 根据棋子 p 从位置 i 移动到位置 j 的价值变化来计算评分。如果移动导致捕获了一个较低的棋子 q，则增加相应的评分。
        score = ping_gu[p][j] - ping_gu[p][i]
        if q.islower():
            score += ping_gu[q.upper()][255 - j - 1]
        return score



# Search类

# 使用了 namedtuple 来定义一个名为 Entry 的元组类型，包含两个属性：lower 和 upper。用于存储搜索过程中的边界值。
Entry = namedtuple('Entry', 'lower upper')


# 用于执行搜索操作
class Searcher_0:

    # 构造函数 __init__
    def __init__(self):
        self.tp_score = {}  # 一个字典，用于存储每个位置、深度和根状态的评分边界
        self.tp_move = {}  # 一个字典，用于存储每个位置的杀手移动（killer move）
        self.history = set()  # 一个集合，用于存储历史位置，用于检测重复局面
        self.nodes = 0  # 一个整数，用于统计搜索过程中访问的节点数

    '''
    bounds方法————搜索算法的核心，用于计算某个位置的评分边界
    pos: 当前位置。
    gamma: 当前搜索的边界值。
    depth: 当前搜索的深度。
    root: 是否是根节点。
    '''

    def bounds(self, pos, gamma, depth, root=True):
        """ returns r where
                s(pos) <= r < gamma    if gamma > s(pos)
                gamma <= r <= s(pos)   if gamma <= s(pos)"""

        # 每次调用bounds函数时，都会增加节点计数器self.nodes。
        self.nodes += 1

        # 确保搜索深度不小于0。
        depth = max(depth, 0)

        # 如果当前位置的评分小于或等于-MATE_LOWER（通常表示失败），则返回最坏情况的评分-MATE_UPPER。
        if pos.score <= -MATE_LOWER:
            return -MATE_UPPER

        # 如果开启了重复局面检测（DRAW_TEST），并且当前位置在历史中出现过，且不是根节点，则返回0，表示局面可能和棋。
        if DRAW_TEST:
            if not root and pos in self.history:
                return 0

        # 从self.tp_score字典中获取当前位置、深度和根状态的评分边界条目，如果不存在，则使用Entry(-MATE_UPPER, MATE_UPPER)作为初始值。
        entry = self.tp_score.get((pos, depth, root), Entry(-MATE_UPPER, MATE_UPPER))

        # 使用α-β剪枝技术，根据当前的评分边界和gamma值，尝试快速返回，减少搜索空间。
        if entry.lower >= gamma and (not root or self.tp_move.get(pos) is not None):
            return entry.lower
        if entry.upper < gamma:
            return entry.upper

        # 定义了一个名为moves的内部生成器函数，用于生成当前棋盘位置的所有可能移动。
        def moves():

            # 如果当前深度大于0，不是根节点，并且棋盘上有国王被将军（'RNC'表示国王被将军的情况），则生成一个空移动，并对其调用bounds函数。
            if depth > 0 and not root and any(c in pos.board for c in 'RNC'):
                yield None, -self.bounds(pos.nullmove(), 1 - gamma, depth - 3, root=False)

            # 如果当前深度为0，则生成当前位置的评分。
            if depth == 0:
                yield None, pos.score

            # 如果当前位置在self.tp_move字典中存在，则生成一个杀手移动，并对其调用bounds函数。
            killer = self.tp_move.get(pos)
            if killer and (depth > 0 or pos.value(killer) >= QS_LIMIT):
                yield killer, -self.bounds(pos.move(killer), 1 - gamma, depth - 1, root=False)

            # 生成当前位置的所有合法移动，对所有可能的移动按价值排序，并对其调用bounds函数。
            for move in sorted(pos.gen_moves(), key=pos.value, reverse=True):
                if depth > 0 or pos.value(move) >= QS_LIMIT:
                    yield move, -self.bounds(pos.move(move), 1 - gamma, depth - 1, root=False)

        # 初始化best变量为-MATE_UPPER，表示最坏情况的评分。
        best = -MATE_UPPER

        # 遍历所有可能的移动，更新best。如果找到的评分大于或等于gamma，则更新self.tp_move字典，并跳出循环。
        for move, score in moves():
            best = max(best, score)
            if best >= gamma:
                if len(self.tp_move) > TABLE_SIZE: self.tp_move.clear()
                self.tp_move[pos] = move
                break

        # 如果best小于gamma，且best小于0，且深度大于0，则检查当前位置的所有移动是否都会导致失败。如果是，则根据是否是平局或被将军，更新best。
        if best < gamma and best < 0 and depth > 0:
            is_dead = lambda pos: any(pos.value(m) >= MATE_LOWER for m in pos.gen_moves())
            if all(is_dead(pos.move(m)) for m in pos.gen_moves()):
                in_check = is_dead(pos.nullmove())
                best = -MATE_UPPER if in_check else 0

        # 如果self.tp_score字典的大小超过了预设的表大小TABLE_SIZE，则清空它。
        if len(self.tp_score) > TABLE_SIZE: self.tp_score.clear()

        # 根据best与gamma的关系，更新self.tp_score字典中的评分边界。
        if best >= gamma:
            self.tp_score[pos, depth, root] = Entry(best, entry.upper)
        if best < gamma:
            self.tp_score[pos, depth, root] = Entry(entry.lower, best)

        # 返回计算得到的评分best。
        return best

    # search函数实现了迭代加深的MTD-bi搜索算法。
    def search(self, pos, history=()):
        '''
        self: 类实例的引用。
        pos: 当前棋盘位置。
        history: 历史棋盘位置列表。
        '''

        # 重置节点计数器，如果开启了重复局面检测，则更新历史局面集合并清空评分字典。
        self.nodes = 0
        if DRAW_TEST:
            self.history = set(history)
            self.tp_score.clear()

        # 进行最大深度为1000层的迭代加深搜索。
        for depth in range(1, 1000):

            # 初始化评分边界为极值。
            lower, upper = -MATE_UPPER, MATE_UPPER

            # 在当前深度下，执行二分搜索，缩小评分边界。
            while lower < upper - EVAL_ROUGHNESS:
                gamma = (lower + upper + 1) // 2
                score = self.bounds(pos, gamma, depth)
                if score >= gamma:
                    lower = score
                if score < gamma:
                    upper = score

            # 在当前深度和最窄的评分边界下，调用bounds函数进行搜索。
            self.bounds(pos, lower, depth)

            # 生成器返回当前深度、最佳移动和评分下界。
            yield depth, self.tp_move.get(pos), self.tp_score.get((pos, depth, True),
                                                                  Entry(-MATE_UPPER, MATE_UPPER)).lower

# User interface

# 坐标转换函数:

# 函数将用户输入的棋步坐标（如 'h2e2'）转换为程序内部使用的整数索引。
# 棋盘坐标通常是字母和数字的组合，如 'a1' 到 'i9'。函数首先计算文件（列）的索引，通过将字母的 ASCII 码减去 'a' 的 ASCII 码来获取列索引，
# 然后计算等级（行）的索引，通过将数字转换为整数并用它来从 A0（棋盘的起始索引）中减去相应的偏移量。
def parsing(c):
    fil, rank = ord(c[0]) - ord('a'), int(c[1])
    return A0 + fil - 16 * rank


# 函数将程序内部使用的整数索引转换回用户可读的棋步坐标。
# 它首先计算列索引和行索引，然后通过将列索引加上 'a' 的 ASCII 码来获取对应的字母，
# 并将其与行索引（取负数并转换为字符串）组合成用户可读的格式。
def rendering(i):
    rank, fil = divmod(i - A0, 16)
    return chr(fil + ord('a')) + str(-rank)


def print_pos(pos, side=None):
    """
    打印棋盘状态的函数。

    参数:
    pos: Position_0 类的一个实例，表示当前的棋盘状态。
    side: 字符串，表示打印棋盘时的视角方。如果为 'black'，则打印黑方视角的棋盘。
    """
    print()  # 打印一个空行，为了美观

    # 定义棋子的Unicode表示和中文表示的映射
    uni_pieces = {
        'R': '车', 'N': '马', 'B': '相', 'A': '仕', 'K': '帅', 'P': '兵', 'C': '炮',  # 红方棋子
        'r': '俥', 'n': '傌', 'b': '象', 'a': '士', 'k': '将', 'p': '卒', 'c': '砲',  # 黑方棋子
        '.': '．'  # 空位
    }

    # 如果指定了 'black' 视角，旋转棋盘以适应黑方视角
    if side == 'black':
        pos = pos.revolve()

    # 遍历棋盘的每一行
    for i, row in enumerate(pos.board.split()):
        # 打印当前行的行号（从9到0），然后打印该行的棋子
        # 使用 uni_pieces 字典将棋子的Unicode表示转换为中文表示
        print(' ', 9 - i, ''.join(uni_pieces.get(p, p) for p in row))
    # 播放音频
    pygame.mixer.init()  # 初始化混音器
    pygame.mixer.music.load('MaoHouPao/move.mp3')  # 加载音频文件
    pygame.mixer.music.play()  # 播放音频
    # 打印棋盘的列标
    print('    ａｂｃｄｅｆｇｈｉ\n\n')



def main():
    global THINK_TIME  # 确保可以在函数内修改 THINK_TIME
    sum_time = 0
    move_time = 0

    # 获取当前日期和时间
    now = datetime.now()
    convert_and_save_Date(str(now), "MaHouPao.pgn")

    # 初始化棋盘历史记录，存储棋盘状态
    hist = [Position_0(initial_map, 0)]
    # 初始化搜索器，用于AI搜索最佳走法
    searcher = Searcher_0()

    # 询问用户选择难度
    difficulty = input("请选择难度等级（1: 菜鸟，2: 小白，3: 新手，4: 入门，5: 小难）：\n——")
    while difficulty not in ['1', '2', '3', '4', '5']:
        difficulty = input("输入无效。请选择难度等级（1: 菜鸟，2: 小白，3: 新手，4: 入门，5: 小难）：\n——")
    pygame.mixer.init()  # 初始化混音器
    pygame.mixer.music.load('MaoHouPao/bin.mp3')  # 加载音频文件
    pygame.mixer.music.play()  # 播放音频
    
    # 根据用户选择设置 THINK_TIME
    THINK_TIME = level(int(difficulty))

    # 请求用户选择先手（红方）还是后手（黑方）
    user_choice = input("你想玩先手（红方）还是后手（黑方）？先手输入“1”，后手输入“2”： \n——")
    print("\a")
    # 确保用户输入有效
    while user_choice not in ['1', '2']:
        user_choice = input("输入无效。请输入“1”作为先手（红方）或“2”作为后手（黑方）： \n——")

    # 根据用户选择确定用户操作红方还是黑方
    user_is_red = (user_choice == '1')

    convert_and_save_Player(str(user_choice), "MaHouPao.pgn")

    print_pos(hist[-1], "red")

    i = 0
    rounds_number = 1.0

    # 游戏主循环
    while True:

        # 根据用户选择红方或黑方，显示当前棋盘状态
        current_side = 'red' if user_is_red else 'black'
        # 打印棋局
        # print_pos(hist[-1], current_side)

        # 检查游戏是否结束，如果评分低于MATE_LOWER则用户输了
        if hist[-1].score <= -MATE_LOWER:
            print("——————————————马后炮赢了.——————————————")
            break
        # 检查游戏是否结束，如果评分高于MATE_UPPER则用户赢了
        if hist[-1].score >= MATE_UPPER:
            print("——————————————马后炮输了.——————————————")
            break

        if i % 2 == 0:
            if (rounds_number/0.5) % 2 == 0:
                print("\n******************************！第--{}--轮！******************************\n".format(rounds_number))
                convert_and_save_0("{}.  ".format(rounds_number), "MaHouPao.pgn")

        flag = 1
        # 用户回合
        if user_is_red:
            move = None

            # 循环直到用户输入有效的走法
            while move is None or move not in hist[-1].gen_moves():
                # 请求用户输入动作
                action = input("请选择输入 '1'->'move' 来走棋，'2'-> 'undo' 悔棋，或 '3'->'quit' 退出游戏： \n——")
                pygame.mixer.init()  # 初始化混音器
                pygame.mixer.music.load('MaoHouPao/bin.mp3')  # 加载音频文件
                pygame.mixer.music.play()  # 播放音频
                if action == '3':
                    print("——————————————结束游戏.——————————————")
                    return

                # 悔棋操作
                elif action == '2' and len(hist) > 1:
                    flag = 0
                    hist.pop()  # 撤销用户的走棋
                    if len(hist) > 1:
                        hist.pop()  # 撤销AI的走棋
                        sum_time -= move_time
                    searcher = Searcher_0()  # 重置搜索器状态
                    rounds_number -= 1
                    convert_and_save_Undo("MaHouPao.pgn")
                    print("\n******************************！恢复棋局！******************************\n".format(rounds_number))
                    histt = hist[-1]
                    print_pos(histt, current_side)
                    break

                # 用户走棋
                elif action == '1':
                    print("请输入类似的移动指令，比如：h2e2")
                    user_input = input('你的移动: \n——')

                    match = re.match('([a-i][0-9])([a-i][0-9])', user_input)
                    if match:
                        move = parsing(match.group(1)), parsing(match.group(2))

            # 如果用户输入了有效的走法，执行走法并更新棋盘历史
            if move:
                hist.append(hist[-1].move(move))
                rounds_number += 0.5
                i += 1
                convert_and_save_1(user_input, "MaHouPao.pgn")
                histt = hist[-1].revolve()
                print_pos(histt, current_side)
                # 打印棋局
                # print_pos(hist[-1], current_side)

        # AI回合
        else:
            move_time = 0
            # 记录AI思考开始时间
            start_time = time.time()

            # 执行AI搜索并获取最佳走法
            for _depth, move, score in searcher.search(hist[-1], hist):
                move_time = time.time() - start_time
                if move_time > THINK_TIME:
                    break

            # 累加到累计思考时间
            sum_time += move_time

            # 如果AI将用户将死
            if score == MATE_UPPER:
                #pygame.mixer.init()  # 初始化混音器
                #pygame.mixer.music.load('jiangjun.m4a')  # 加载音频文件
                #pygame.mixer.music.play()  # 播放音频
                print("——————————————将军!——————————————")

            # 输出AI下棋棋谱
            convert_and_save_2(rendering(255 - move[0] - 1) + rendering(255 - move[1] - 1), "MaHouPao.pgn")

            # 打印AI思考深度和走法
            print("累计思考时间（秒）:{} ————本次思考时间（秒）:{} \n本次思考深度:{} ————本次AI的走法:{}".format(sum_time, move_time, _depth,
                                                                                    rendering(255 - move[0] - 1) + rendering(
                                                                                        255 - move[1] - 1)))
            # 执行AI走法并更新棋盘历史
            hist.append(hist[-1].move(move))
            rounds_number += 0.5
            i += 1
            histt = hist[-1].revolve()
            print_pos(histt, current_side)
            # 打印棋局
            # print_pos(hist[-1], current_side)

        # 切换回合
        if flag == 1:
            user_is_red = not user_is_red

if __name__ == '__main__':
    main()


