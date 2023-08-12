%This model does not containing with rotation function since the coordinate of each circuit is fixed

include "diffn.mzn";
include "cumulative.mzn";


%Data
int: width;    %  the width of silicon the board
int: n_circuits;    % number of circuits to place

set of int: N = 1..n_circuits;

array[N] of int: w_size; % the width of each circuit
array[N] of int: l_size; % the length of each circuit


% give a range of the length of y coordinate
int: y_len = sum([l_size[i] | i in N]);
% horizontal coordinate of each circuit
array[N] of var 0..width: x_pos;
%vertical coordinate of each circuit
array[N] of var 0..y_len: y_pos;

% 
var int: length = max([y_pos[i] + l_size[i] | i in N]);


%------------------ Constraints --------------------

% global constraint 
constraint diffn(x_pos, y_pos, [w_size[i] | i in N], [l_size[i] | i in N]);
constraint cumulative([x_pos[i] | i in N], [w_size[i] | i in N], [l_size[i] | i in N], width);
%constraint cumulative([x_pos[i], y_pos[i], w_size[i] , l_size[i] | i in N]);

% Make sure the curcit is inside of the silicon plate
constraint forall(i in N)(
%   x_pos[i] >= 0 /\ 
%   y_pos[i] >= 0 /\ 
   x_pos[i] + w_size[i] <= width
);

% The values must stay in the range between 1 and the legnth of the relative silicon plate found
%constraint forall(i in N)(corner_coords[i, 2] + dims[i, 2] <= length);
%constraint length <= max_length;

% The length of the silicon plate should stay between the min_length and max_length
%constraint length <= sum([C_size[i,2] | i in N]);
%constraint length >= max([C_size[i,2] | i in N]);

% * Search  *
%ann : restart_strategy = restart_linear(200);

solve
%:: restart_strategy
%:: int_search(x_pos, input_order, indomain_min)
%:: int_search(y_pos, input_order, indomain_min);
%:: int_search(x_pos, dom_w_deg, indomain_min)
%:: int_search(x_pos, dom_w_deg, indomain_min)
minimize length;      
                        
/*********************
*  output *
**********************/
        
output [show(width)++" "++show(length)++"\n"]++
       [show(n_circuits)++"\n"]++
       [show(w_size[i]) ++" "++ show(l_size[i])++" "++ show(x_pos[i])++" "++show(y_pos[i])++"\n" | i in N]
