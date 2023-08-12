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
%constraint cumulative([y_pos[i] | i in N], [l_size[i] | i in N],[w_size[i] | i in N], length);

% Make sure the curcit is inside of the silicon plate
constraint forall(i in N)(x_pos[i] + w_size[i] <= width);

%constraint forall(i in N)(y_pos[i] + l_size[i] <= length);

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
