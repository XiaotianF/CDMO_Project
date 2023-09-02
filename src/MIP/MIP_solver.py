from ortools.linear_solver import pywraplp
import os
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


def main():
    # create the MIP solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    #Read the input data
    directory = r'./instances'
    # directory = "./instances"  # Replace with the actual directory path
    selected_files = ["ins-1.txt"]  # Choose the files you want to input, like "ins-1.txt" "ins-2.txt together
    output_folder = "./out"
    for file_name in selected_files:
        input_file_path = os.path.join(directory, file_name)
        output_folder_path = os.path.join(output_folder, "out-" + file_name)
        if os.path.exists(input_file_path):
            width, n_circuits, w_size, l_size = read_input(input_file_path)
            # print(width, n_circuits, w_size, l_size)
            #create variables
            N = list(range(1, n_circuits + 1))
            y_len = sum(l_size)
            x_pos = [solver.IntVar(0, width, f'x_pos{i+1}') for i in N]
            y_pos = [solver.IntVar(0, y_len, f'y_pos{i+1}') for i in N]
            length = solver.IntVar(0, sum(l_size), 'length')
            #solver.Add(length == solver.Max([y_pos[i-1] + l_size[i -1] for i in N]))
            #constraints
            for i in N:
                x_pos[i-1].SetBounds(0, width)
                y_pos[i-1].SetBounds(0, y_len)
                solver.Add(x_pos[i-1] + w_size[i-1] <= width) # the constraint for width
                solver.Add(y_pos[i-1] + l_size[i-1] <= y_len)
                for j in N:
                    if i != j:  #the main constraint for overlap
                        solver.Add((x_pos[i-1] + w_size[i-1] <= x_pos[j-1]) or
                                   (x_pos[j-1] + w_size[j-1] <= x_pos[i-1]) or
                                   (y_pos[i-1] + l_size[i-1] <= y_pos[j-1]) or
                                   (y_pos[j-1] + l_size[j-1] <= y_pos[i-1]))
            print(x_pos[i-1].SolutionValue())
    # create the objective function, minimize the length
    objective = solver.Objective()
    objective.SetCoefficient(length, 1)
    objective.SetMinimization()

    # set the time limit
    solver.SetTimeLimit(300*1000)
    # solver.set_time_limit(15)

    start_time = time.time()
    end_time = time.time()
    elapsed_time = end_time - start_time

    status = solver.Solve()

    # Get the solution_data
    solution = [width, length.SolutionValue(), n_circuits] +[f'{w_size[i-1]} {l_size[i-1]} {x_pos[i-1].solution_value()} {y_pos[i-1].solution_value()}' for i in N]
    solution.append(elapsed_time)
    print(solution)
    #print results
    if status == pywraplp.Solver.OPTIMAL:
        print('\n', solution)
        print('\n', elapsed_time)
        write_solution(solution, output_folder_path)
    # elif status == pywraplp.SolverReasultStatus.FRASIBLE:
    #     print('Time out, got a solution:')
    #     print('\n', solution)
    #     write_solution(solution, output_folder_path)
    else:
        print('No solution found')

if __name__ == "__main__":
    main()

