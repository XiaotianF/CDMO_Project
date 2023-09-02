import os
from pulp import *
import time


# Function to read data from txt files as we used in SMT
def read_input(file_path):
    with open(file_path, 'r') as f:
        width = int(f.readline().strip())
        n_circuits = int(f.readline().strip())
        data = [line.strip().split() for line in f.readlines()]
        w_size = [int(line[0]) for line in data]
        l_size = [int(line[1]) for line in data]
    return width, n_circuits, w_size, l_size


# Write the solution to a txt file
def write_solution(solution, file_path):
    with open(file_path, 'w') as f:
        f.write('\n'.join(map(str, solution)))

def create_solver(width, n_circuits, w_size, l_size, time_limit_seconds):
    # Create a PuLP problem
    model = pulp.LpProblem("Circuit_Placement", LpMinimize)

    # Create variables
    y_len = sum(l_size)
    x_pos = [pulp.LpVariable(f'x_pos{i}', lowBound=0, upBound=width, cat ='Integer') for i in range(n_circuits)]
    y_pos = [pulp.LpVariable(f'y_pos{i}', lowBound=0, upBound=y_len, cat='Integer') for i in range(n_circuits)]

    # Or value
    overlap = pulp.LpVariable.dicts("overlap", (range(n_circuits), range(n_circuits), range(2)), cat="Binary")

    # Objective function
    length = pulp.LpVariable("length", lowBound=0, upBound=y_len, cat='Integer')
    model += length, "length"

# Constraints
    # Main constraint for no-overlap
    for i in range(n_circuits):
        for j in range(n_circuits):
            if i < j:
                model += (x_pos[i] + w_size[i] <= x_pos[j] + overlap[i][j][0]*y_len)
                model += x_pos[j] + w_size[j] <= x_pos[i] + overlap[j][i][0]*y_len
                model += y_pos[i] + l_size[i] <= y_pos[j] + overlap[i][j][1]*y_len
                model += y_pos[j] + l_size[j] <= y_pos[i] + overlap[j][i][1]*y_len
                model += overlap[i][j][0] + overlap[i][j][1] + overlap[j][i][0] + overlap[j][i][1] <= 3

                #  model += (
                #         (x_pos[i] + w_size[i] <= x_pos[j]) or
                #         (x_pos[j] + w_size[j] <= x_pos[i]) or
                #         (y_pos[i] + l_size[i] <= y_pos[j]) or
                #         (y_pos[j] + l_size[j] <= y_pos[i])
                #         )
    for i in range(n_circuits):
        model += (x_pos[i] + w_size[i] <= width) # width constraint
        model += (y_pos[i] + l_size[i] <= length) # length constraint
        model += (0 <= x_pos[i])
        model += (0 <= y_pos[i])

    # symmetry breaking
    biggest_area = w_size[0] + l_size[0]
    index = 0

    for i in range(n_circuits):
        area = w_size[i] * l_size[i]
        if area > biggest_area:
            biggest_area = area
            index = i
    model += x_pos[index] == 0
    model += y_pos[index] == 0


    return model, length, x_pos, y_pos

def main():
    # record the time
    start_time = time.time()

    # set the time constraint
    time_limit_seconds = 300

    directory = r'./instances'
    selected_files = ["ins-4.txt"]  # Choose the files you want to input, like "ins-1.txt" "ins-2.txt together
    output_folder = "./out"

    for file_name in selected_files:
        input_file_path = os.path.join(directory, file_name)
        output_folder_path = os.path.join(output_folder, "out-" + file_name)
        if os.path.exists(input_file_path):
            width, n_circuits, w_size, l_size = read_input(input_file_path)

            model, length, x_pos, y_pos = create_solver(width, n_circuits, w_size,l_size, time_limit_seconds)

            # Solve the problem
            solver = pulp.PULP_CBC_CMD(mip=True, msg=False, timeLimit=time_limit_seconds)
            model.solve(solver)

            # Get the solution data
            solution = [width, int(value(length)), n_circuits]
            # get the time cost
            end_time = time.time()
            elapsed_time = end_time - start_time

            # print("The status of model:", LpStatus[model.status])
            # print("value of x_pos:", value(x_pos[0]))
            # print("value of y_pos:", value(y_pos[0]))
            # print("Value of length", value(model.objective))

            for i in range(n_circuits):
                solution.append(f"{w_size[i]} {l_size[i]} {int(value(x_pos[i]))} {int(value(y_pos[i]))}")

            if LpStatus[model.status] == 'Optimal' or LpStatus[model.status] == 'Not Solved':
                print(solution)
                print("Optimal Solution Found, with the time:",elapsed_time)
                solution.append(elapsed_time)
                # Write the solution to a file
                write_solution(solution, output_folder_path)
            else:
                print(solution)
                print("No solution found")

if __name__ == "__main__":
    main()