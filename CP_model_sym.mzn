% This model contains symmetry breaking, but no rotation included

include "diffn.mzn";

/*    Data  input   */
int: width;
int: n_circuits;

set of int: N = 1..n_circuits;

%C_size[i,1] represents the width of each circuit, C_size[i,2] represents the length of each circuit.
array[N, 1..2] of int: C_size;

% give a range of the length of y coordinate
int: y_len = sum([C_size[i,2] | i in N]);
% horizontal coordinate of each circuit
array[N] of var 0..width: x_pos;
%vertical coordinate of each circuit
array[N] of var 0..y_len: y_pos;

var int: length = max([y_pos[i] + C_size[i, 2] | i in N]);

%function for symmetry breaking
function int: index() = arg_max([C_size[i,1] * C_size[i,2] | i in N]); % get the index of the biggest circuit


/*   constraints    */
% global constraint 
constraint diffn(x_pos, y_pos, [C_size[i,1] | i in N], [C_size[i,2] | i in N]);

% Make sure the curcit is inside of the silicon plate
constraint forall(i in N)(x_pos[i] + C_size[i,1] <= width);

% symmetry breaking constraint, put the biggest rock at the left-bottom corner
constraint (x_pos[index()] = 0 /\ y_pos[index()] = 0);

% solve
solve
minimize length;
%:: int_search(corner_coords, first_fall, indomain_min);

output ["\(width)"++" "++"\(length)"++"\n"]++
       ["\(n_circuits)"++"\n"]++
       ["\(C_size[i,1])" ++" "++ "\(C_size[i,2])" ++" "++ "\(x_pos[i])" ++" "++"\(y_pos[i])"++"\n" | i in N]++["\n"]
      