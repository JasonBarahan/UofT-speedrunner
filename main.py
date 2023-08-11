"""
UofT Speedrunner

Module Description
==================
This module is the main module you need to run our program! Just click Run on your Python Interpreter and watch the
magic unfold as you become a speedy, efficient, and smart U of T Speedrunner!

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
import user_interaction as ui


if __name__ == '__main__':
    import doctest

    doctest.testmod()

    ui.io_main_menu()
