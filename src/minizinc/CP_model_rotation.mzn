% This model contains rotation function
include "diffn.mzn";

/*    Data input   */
int: width;
int: n_circuits;

set of int: N = 1..n_circuits;

array[N] of int: w_size; % the width of each circuit
array[N] of int: l_size; % the length of each circuit

% R=0 represents no rotation, R=1 means rotation happens
array[N] of var 0..1: R; 

% give a range of the length of y coordinate
int: y_len = sum([l_size[i] | i in N]);
% horizontal coordinate of each circuit
array[N] of var 0..width: x_pos;
% vertical coordinate of each circuit
array[N] of var 0..y_len: y_pos;

% 
var int: length = max([(1 - R[i]) * y_pos[i] + R[i] * x_pos[i] + (1 - R[i]) * l_size[i] + R[i] * w_size[i] | i in N]);

%function for symmetry breaking
function int: index() = arg_max([w_size[i] * l_size[i] | i in N]); % get the index of the biggest circuit


/*   constraints    */
% global constraint 
constraint diffn(x_pos, y_pos, [w_size[i] | i in N], [l_size[i] | i in N]);

% Make sure the curcit is inside of the silicon plate
constraint forall(i in N)((1 - R[i]) * x_pos[i] + R[i] * y_pos[i] + (1 - R[i]) * w_size[i] + R[i] * l_size[i] <= width);

% symmetry breaking constraint, put the biggest block at the left-bottom corner
constraint (x_pos[index()] = 0 /\ y_pos[index()] = 0);


% solve
solve
minimize length;


output ["\(width)"++" "++"\(length)"++"\n"]++
       ["\(n_circuits)"++"\n"]++
       ["\(w_size[i])" ++" "++ "\(l_size[i])" ++" "++ "\(x_pos[i])" ++" "++"\(y_pos[i])"++"\n" | i in N]++["\n"]