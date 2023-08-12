% This model contains symmetry breaking, but no rotation included

include "diffn.mzn";
include "cumulative.mzn";

/*    Data  input   */
int: width;
int: n_circuits;

set of int: N = 1..n_circuits;

array[N] of int: w_size; % the width of each circuit
array[N] of int: l_size; % the length of each circuit

% give a range of the length of y coordinate
int: y_len = sum([l_size[i] | i in N]);
% horizontal coordinate of each circuit
array[N] of var 0..width: x_pos;
%vertical coordinate of each circuit
array[N] of var 0..y_len: y_pos;

var int: length = max([y_pos[i] + l_size[i] | i in N]);

%function for symmetry breaking
function int: index() = arg_max([w_size[i] * l_size[i] | i in N]); % get the index of the biggest circuit


/*   constraints    */
% global constraint 
constraint diffn(x_pos, y_pos, [w_size[i] | i in N], [l_size[i] | i in N]);
constraint cumulative([x_pos[i] | i in N], [w_size[i] | i in N], [l_size[i] | i in N], width);

% Make sure the curcit is inside of the silicon plate
constraint forall(i in N)(x_pos[i] + w_size[i] <= width);

% symmetry breaking constraint, put the biggest rock at the left-bottom corner
constraint (x_pos[index()] = 0 /\ y_pos[index()] = 0);

% solve
solve
minimize length;
%:: int_search(corner_coords, first_fall, indomain_min);

output ["\(width)"++" "++"\(length)"++"\n"]++
       ["\(n_circuits)"++"\n"]++
       ["\(w_size[i])" ++" "++ "\(l_size[i])" ++" "++ "\(x_pos[i])" ++" "++"\(y_pos[i])"++"\n" | i in N]++["\n"]
      