import platform
import os


def clear_terminal():
    if platform.system() == "Windows":
        os.system("cls")
        return
    os.system("clear")
