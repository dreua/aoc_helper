import aoc_helper
import copy
import math
import queue  # reminder to use get_nowait instead of get
import re

from collections import defaultdict, Counter
from functools import cache
from itertools import batched
from pprint import pprint

o_raw = None
raw = """X"""
raw = aoc_helper.fetch({day}, {year})


def parse_raw(raw):
    ...


data = parse_raw(raw)


def part_one(data):
    ...


aoc_helper.lazy_test(day={day}, year={year}, parse=parse_raw, solution=part_one)


def part_two(data):
    ...


aoc_helper.lazy_test(day={day}, year={year}, parse=parse_raw, solution=part_two)

if not o_raw:
    aoc_helper.lazy_submit(day={day}, year={year}, solution=part_one, data=data)
    aoc_helper.lazy_submit(day={day}, year={year}, solution=part_two, data=data)
else:
    pprint(part_one(data=data))
    pprint(part_two(data=data))
