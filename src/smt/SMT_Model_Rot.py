import os
from z3 import *
import time
import matplotlib.pyplot as plt
import random


def read_input(file_path):  # read the data from txt files
    with open(file_path, 'r') as f:
        width = int(f.readline().strip())
        n_circuits = int(f.readline().strip())
        data = [line.strip().split() for line in f.readlines()]  # used to save the data of the circuits
        w_size = [int(line[0]) for line in data]
        l_size = [int(line[1]) for line in data]
    return width, n_circuits, w_size, l_size


def creat_solver(width, n_circuits, w_size, l_size):  # Used for setting constraints
    solver = Optimize()
    x_pos = [Int(f'x_{i}') for i in range(n_circuits)]
    y_pos = [Int(f'y_{i}') for i in range(n_circuits)]

    R = [Int(f"R_{i}") for i in range(n_circuits)]
    for i in range(n_circuits):
        solver.add(Or(R[i] == 0, R[i] == 1))
    #R = [Or((R[i] == 0),R[i] == 1) for i in range(n_circuits)]

    # Main constraint for no-overlap
    for i in range(n_circuits):
        for j in range(n_circuits):
            if i != j:
                solver.add(
                    Or(
                        x_pos[i] + (1 - R[i]) * w_size[i] + R[i] * l_size[i] <= x_pos[j],
                        x_pos[j] + (1 - R[i]) * w_size[j] + R[i] * l_size[i] <= x_pos[i],
                        y_pos[i] + (1 - R[i]) * l_size[i] + R[i] * w_size[i] <= y_pos[j],
                        y_pos[j] + (1 - R[i]) * l_size[j] + R[i] * w_size[i] <= y_pos[i]
                    )
                )
    # Make sure every circuit is included inside of the silicon plate
    if R == 0:
        l = sum(l_size)
    else:
        l = sum(w_size)

    length = Int('length')
    for i in range(n_circuits):
        solver.add(And(0 <= x_pos[i], x_pos[i] <= width))
        solver.add(And(0 <= y_pos[i], y_pos[i] <= l))
        solver.add(x_pos[i] + (1 - R[i]) * w_size[i] + R[i] * l_size[i] <= width)
        #solver.add(y_pos[i] + (1 - R[i]) * l_size[i] + R[i] * w_size[i] <= length)
        solver.add(y_pos[i] + l_size[i] <= length)

    # symmetry breaking constraint
    biggest_area = w_size[0] * l_size[0]
    index = 0
    for i in range(1, n_circuits):
        area = w_size[i] * l_size[i]
        if area > biggest_area:
            biggest_area = area
            index = i
    solver.add(And((x_pos[index] == 0), (y_pos[index] == 0)))

    solver.set("Timeout", 300 * 1000)
    solver.minimize(length)

    # print(solver.help())
    return solver, length, x_pos, y_pos


def solve_and_output(length, x_pos, y_pos, n_circuits, solver):
    start_time = time.time()

    result = []
    res = solver.check()

    print(res)
    if res == sat:
        model = solver.model()
        end_time = time.time()
        print(model)
        elapsed_time = end_time - start_time
        for i in range(n_circuits):
            result.append((model[x_pos[i]].as_long(), model[y_pos[i]].as_long()))
        result.append(model[length].as_long())
        return result, elapsed_time
    else:
        end_time = time.time()
        elapsed_time = end_time - start_time
        model = solver.model()
        print(model)
        for i in range(n_circuits):
            result.append((model[x_pos[i]].as_long(), model[y_pos[i]].as_long()))
        result.append(model[length].as_long())

        return result, elapsed_time


def save_output(output_path, width, length, n_circuits, circuit_data, elapsed_time):
    '''

    To read and write the date into the file

    '''
    with open(output_path, "w+") as f:
        f.write((f"{width} {length}\n{n_circuits}\n"))
        for circuits in circuit_data:
            f.write(" ".join(map(str, circuits)) + "\n")
        f.write((f"runtime:{elapsed_time:.2f}seconds"))


if __name__ == "__main__":
    '''
    The main function used to read the data, and save the data into the out fold

    '''
    directory = r'./instances'
    #    directory = "./instances"  # Replace with the actual directory path
    selected_files = ["ins-1.txt"]  # Choose the files you want to input
    output_folder = "./out"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in selected_files:
        input_file_path = os.path.join(directory, file_name)
        output_file_name = "out-" + file_name
        output_folder_path = os.path.join(output_folder, "out-" + file_name)

        if os.path.exists(input_file_path):
            width, n_circuits, w_size, l_size = read_input(input_file_path)
            solver, length, x_pos, y_pos = creat_solver(width, n_circuits, w_size, l_size)
            result, elapsed_time = solve_and_output(length, x_pos, y_pos, n_circuits, solver)

            if result and result[0] != "Timeout":
                circuit_data = [(w_size[i], l_size[i], pos[0], pos[1]) for i, pos in enumerate(result[:-1])]
                output_path = os.path.join(output_folder, "out-" + file_name)
                save_output(output_path, width, result[-1], n_circuits, circuit_data, elapsed_time)
                print(f"File: {file_name} processed and saved as {output_folder_path}")
            elif result and result[0] == "Timeout":
                output_path = os.path.join(output_folder, "out-" + file_name)
                with open(output_folder, "w+") as f:
                    f.write("Timeout\n")
                print(f"File: {file_name} processed, but timeout occurred, save as {output_folder}")
