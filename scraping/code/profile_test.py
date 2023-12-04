import asyncio
from functools import partial

from cProfile import Profile
from pstats import Stats
from memory_profiler import profile

from scrap import run_single, run_multy


@profile
def mem_test_single(student_number: str):
    res = asyncio.run(run_single(student_number))
    print(res)


@profile
def mem_test_multy(student_number: str):
    res = asyncio.run(run_multy(student_number))
    print(res)


def profile_func(func, **kwargs):
    profiler = Profile()
    profiler.runcall(partial(func, **kwargs))
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats()


if __name__ == "__main__":
    profile_func(mem_test_multy, student_number="20180811")
