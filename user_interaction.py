"""
UofT Speedrunner

Module Description
==================
Simplified text-based interaction with program using Python input/output.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the students
mentioned below and all CSC111 course staff at the University of Toronto.
Any other parties not mentioned may not use or possess copies of
this code, whether modified or otherwise.

This file is Copyright (c) 2023
Jason Barahan, Vibhas Raizada, Benjamin Sandoval, Eleonora Scognamiglio.
"""
import load_all_data
import map_generation as mg


def run_path_generation(start: str, end: str, stopover: list[str] = None) -> None:
    """
    Generate a path using the SpeedRunner.

    Preconditions:
    - start is a valid building code
    - end is a valid building code
    - all elements in stopover are valid building codes
    """
    if stopover is None or len(stopover) == 0:
        mg.visualize_djikstra(start, end)

    else:
        mg.visualize_djikstra_with_stopovers(start, end, stopover)
        # mg.visualize_dfs(start, end, stopover)


# IO functions
def io_main_menu() -> None:
    """
    input output interface
    """
    string = 0
    print('Welcome to UofT Speedrunner!')
    print('We get you to where you want to go!')
    print('')
    print('[A] Show me buildings at the University of Toronto')
    print('[B] Show me all the intersections at the University of Toronto')
    print('[C] Get me somewhere')
    while string not in {'A', 'B', 'C'}:
        string = input()

        # user chooses option A
        if string == 'A':
            io_show_buildings()

        # user chooses option B
        elif string == 'B':
            mg.generate_all_intersection_points_with_edges()

        # user chooses option C
        elif string == 'C':
            io_get_path()

        # non recognizable input
        else:
            print("Invalid entry.")
            string = 0


def io_get_path() -> None:
    """
    CLI IO handling for getting a desired shortest path.
    """
    # get building data
    a = load_all_data.load_data('data/building_data.csv', 'data/intersections_data.csv')
    building_codes = list(a.buildings)
    code, code2, code3 = 'a', 'a', 'a'
    stopover = []

    # initial menu
    print('For reference, here are the building codes:')

    # print out all building codes
    for key in a.buildings:
        print(key + ': ' + a.buildings[key].name)

    print('Lost? Use [ctrl] + [f]')

    # 1: input start building
    print('\n')
    print('Input your start building code')
    while code not in building_codes:
        code = input('')

        # destination in building codes
        if code in building_codes:
            pass

        # non recognizable input
        else:
            print('Invalid entry.')

    # 2: input end building
    print('\n')
    print('Print your destination')
    while code2 not in building_codes:
        code2 = input('')

        # destination in building codes
        if code2 in building_codes:
            pass

        # non recognizable input
        else:
            print('Invalid entry.')

    # 3: input stopovers
    print('\n')
    print('Input any places you would like to stop over at.')
    print('You can also put an amenity down:')
    print(str(load_all_data.AMENITIES))
    print('Enter one of the above amenities as shown to view building options. No quotation marks please')
    print('Press enter if you have none to add')
    while code3 not in building_codes and code3 != '':
        code3 = input('')

        # no more stopovers
        if code3 == '':
            # print final info / generate path
            print('Directions from ' + code + ' to ' + code2 + ' via ' + str(stopover))
            print('Now processing...')
            run_path_generation(code, code2, stopover)

        # stopover is an amenity
        elif code3 in load_all_data.AMENITIES:
            print('Here is a list of buildings with ' + code3 + '. Pick one')
            for key in a.buildings:
                if code3 in a.buildings[key].amenities:
                    print(key + ': ' + a.buildings[key].name)
            print('Lost? Use [ctrl] + [f]')

        # stopover added
        elif code3 in building_codes:
            stopover.append(code3)
            code3 = 'a'
            print('Type another stopover or press enter if you have none to add (this can be an amenity'
                  ' or a building code)')

        # non recognizable input
        else:
            print('Invalid entry.')


def io_show_buildings() -> None:
    """
    CLI IO handling for showing all buildings, or showing buildings with a certain amenity.
    """
    io = 'a'
    print('Are you looking for a building with a certain amenity in mind?')
    print('We have:' + str(list(load_all_data.AMENITIES)))
    print('Type one of the above options, or press enter to show all buildings:')
    print('No quotation marks please')
    while (io != '') and (io not in load_all_data.AMENITIES):
        io = input()
        if io == '':
            mg.generate_all_building_points()
        elif io in load_all_data.AMENITIES:
            mg.generate_all_building_points(io)
        else:
            print('Invalid entry. Try again')


if __name__ == '__main__':
    # for reference, these are the amenities:
    # 'study', 'dining', 'coffee', 'microwave', 'gym', 'library', 'atm',
    # 'math learning centre', 'writing centre', 'transportation'

    import doctest

    doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9992', 'E9997', 'E9998', 'E9999', 'W0401', 'R1702', 'R0912']
    })

    io_main_menu()
