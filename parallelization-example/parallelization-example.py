import argparse
import time
import timeit
from datetime import datetime
# import psutil
# import os


def somethingToParallelize(seconds, numbr):
    print(f"Sleeping for {seconds} second(s)")
    time.sleep(seconds / 3)
    print("Done sleeping")
    return f"#{numbr}: slept for {seconds} seconds!"


def main() -> None:
    # must be here, inside main()
    import multiprocessing
    import concurrent.futures

    # print(os.cpu_count())
    # print(psutil.cpu_count(logical=True))
    # print(psutil.cpu_count(logical=False))

    availableCores: int = multiprocessing.cpu_count()
    # print(f"Total available cores: {availableCores}")

    parallelized: bool = True
    numberOfWorkers: int = availableCores
    withMap: bool = False

    copyrightMessage: str = " ".join((
        f"Copyright (C) 2022-{datetime.now().year}",
        "Declaration of VAR"
    ))
    argParser = argparse.ArgumentParser(
        prog="parallelization-example",
        description=" ".join((
            f"%(prog)s\n{copyrightMessage}\nAn",
            "example of parallelizing processing"
        )),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False
    )
    argParser.add_argument(
        "--workers",
        type=int,
        metavar="4",
        help="number of workers"
    )
    argParser.add_argument(
        "--not-parallelized",
        action='store_false',
        help="disable parallelization (default: %(default)s)"
    )
    argParser.add_argument(
        "--with-map",
        action='store_true',
        help="mapping parallelizable function arguments (default: %(default)s)"
    )
    cliArgs = argParser.parse_args()
    # print(cliArgs)

    withMap = cliArgs.with_map
    parallelized = cliArgs.not_parallelized
    if parallelized:
        if cliArgs.workers is not None:
            numberOfWorkers = cliArgs.workers
            # print(f"Number of workers: {numberOfWorkers}")
            if numberOfWorkers < 2:
                raise SystemExit(
                    " ".join((
                        "You cannot have less than 2 workers",
                        "in parallelized processing"
                    ))
                )
            if numberOfWorkers > availableCores:
                raise SystemExit(
                    " ".join((
                        "You cannot have the number of workers to be bigger",
                        "than the total number of available cores",
                        f"({availableCores})"
                    ))
                )
    else:
        if withMap:
            raise SystemExit(
                " ".join((
                    "You cannot have parallelization with map()",
                    "when parallelization itself has been disabled"
                ))
            )
        if cliArgs.workers is not None:
            raise SystemExit(
                " ".join((
                    "You cannot provide a number of workers",
                    "when parallelization itself has been disabled"
                ))
            )

    # ---

    startTime = timeit.default_timer()

    someIterable = range(20, 0, -1)

    if not parallelized:
        for i in someIterable:
            somethingToParallelize(i, i)
    else:  # https://analyticsindiamag.com/run-python-code-in-parallel-using-multiprocessing/
        # if your code IO-bound (disk read-write, network requests)
        # with concurrent.futures.ThreadPoolExecutor(
        #     max_workers=numberOfWorkers
        # ) as executor:
        # if your code CPU-bound
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=numberOfWorkers
        ) as executor:
            if not withMap:
                pool = [
                    executor.submit(somethingToParallelize, i, i)
                    for i in someIterable
                ]
                for itr in concurrent.futures.as_completed(pool):
                    print(f"Result: {itr.result()}")
            else:
                pool = executor.map(
                    somethingToParallelize,
                    someIterable, someIterable
                )
                for rez in pool:
                    print(f"Result: {rez}")

    endTime = timeit.default_timer()

    print(f"Timer: {round(endTime - startTime, 3)} seconds")


# this kind of guarding is required for parallelized processing
if __name__ == "__main__":
    main()
