import aoc_helper
from pprint import pprint

o_raw = None
raw = """X"""
raw = aoc_helper.fetch({day}, {year})


def parse_raw(raw):
    ...


data = parse_raw(raw)


def part_one():
    ...


def part_two():
    ...

if not o_raw:
    aoc_helper.lazy_submit(day={day}, year={year}, solution=part_one)
    aoc_helper.lazy_submit(day={day}, year={year}, solution=part_two)
else:
    pprint(part_one())
    pprint(part_two())
