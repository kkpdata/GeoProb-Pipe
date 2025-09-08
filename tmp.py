from concurrent.futures import ThreadPoolExecutor
import time
from typing import List
import threading


class Calculation:

    def __init__(self, calc_id: int):
        self.id = calc_id

    def run(self):
        print(f"Now running calculation {self.id}")
        time.sleep(5)


def run_calculation(calculation: Calculation):
    try:
        calculation.run()
    except Exception as e:
        print(f"Could not run reliability calculation {calculation.id}: {e}")


calculations: List[Calculation] = [Calculation(calc_id=index) for index in range(500)]


def progress_reporter():
    counter = 0
    while counter <= 8:
        print(f"Progress = {counter}")
        counter += 1
        time.sleep(6)
    print(f"Finished progress reporter")


reporter_thread = threading.Thread(target=progress_reporter)
reporter_thread.start()


with ThreadPoolExecutor(max_workers=24) as executor:
    executor.map(run_calculation, calculations)
print(f"Finished all calculations")

