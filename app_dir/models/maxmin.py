#! /usr/bin/env python

##################################
# This program generates sets of new data following the LHS
# and the grid search method. 
##################################

from __future__ import print_function
import numpy as np
import itertools
import time
import pyDOE as doe

def compute_LHS(num_samples, var_LB, var_UB):
	'''
	var_LB/var_UB: vector that contains the min/max values of its parameter
	e.g. for initial example: 
	xmin = [Tmin = 100, Rac_ratio = 0.8, Micro_Pow = 150] and 
	xmax = [Tmax = 200, Rac_ratio = 1.8, MIcro_Pow = 250]
	'''
	# number of variables
	dim = len(var_LB)
	lhs_set = doe.lhs(dim, num_samples)
	# Convert output to parameter space
	for j in range(dim):
		lhs_set[:,j] = var_LB[j] + lhs_set[:,j]*(var_UB[j] - var_LB[j])
	# print(np.shape(lhs_set))

	return lhs_set

def compute_grid(nsamples_x, nsamples_y, var_LB, var_UB, NVARS):
    '''
    var_LB/var_UB: vector that contains the min/max values of its parameter
    e.g. for initial example: 
    xmin = [Tmin = 100, Rac_ratio = 0.8, Micro_Pow = 150] and 
    xmax = [Tmax = 200, Rac_ratio = 1.8, MIcro_Pow = 250]
    '''
	# number of variables
    c_1 = np.linspace(var_LB[0], var_UB[0], nsamples_x)
    c_2 = np.linspace(var_LB[1], var_UB[1], nsamples_y)
            
    # print (np.shape(M))
    M = np.array(np.meshgrid([c_1], [c_2])).T

    nsamples = nsamples_x * nsamples_y
    M = M.reshape(nsamples,NVARS)
    # print("M matrix in mamin, compute grid = /n", M )
    # print("M size: ", np.shape(M))
    return (M)





