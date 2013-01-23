#########################################################################
#
#   transforms.py - This file is part of the Spectral Python (SPy)
#   package.
#
#   Copyright (C) 2001-2013 Thomas Boggs
#
#   Spectral Python is free software; you can redistribute it and/
#   or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   Spectral Python is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#     
#   You should have received a copy of the GNU General Public License
#   along with this software; if not, write to
#
#               Free Software Foundation, Inc.
#               59 Temple Place, Suite 330
#               Boston, MA 02111-1307
#               USA
#
#########################################################################
#
# Send comments to:
# Thomas Boggs, tboggs@users.sourceforge.net
#

'''
Base classes for various types of transforms
'''

import numpy as np

class LinearTransform:
    '''A callable linear transform object.
    
    In addition to the __call__ method, which applies the transform to given,
    data, a LinearTransform object also has the following members:
    
	`dim_in` (int):
	
	    The expected length of input vectors.
	
	`dim_out` (int):
	
	    The length of output vectors (after linear transformation).
	
	`dtype` (numpy dtype):
	
	    The numpy dtype for the output ndarray data.
    '''
    def __init__(self, A, **kwargs):
        '''Arguments:
        
            `A` (:class:`~numpy.ndarrray`):
            
                An (J,K) array to be applied to length-K targets.
                    
        Keyword Argments:
        
            `pre` (scalar or length-K sequence):
            
                An additive offset to be applied prior to linear transformation.
                
            `post` (scalar or length-J sequence):
        
                An additive offset to be applied after linear transformation.
		
	    `dtype` (numpy dtype):
	    
		Explicit type for transformed data.
        '''
        
        self._pre = kwargs.get('pre', None)
        self._post = kwargs.get('post', None)
        if len(A.shape) == 1:
            self._A = A.reshape(((1,) + A.shape))
        else:
            self._A = A
	(self.dim_out, self.dim_in) = self._A.shape
	self.dtype = kwargs.get('dtype', self._A.dtype)

    def __call__(self, X):
        '''Applies the linear transformation to the given data.
        
        Arguments:
        
            `X` (:class:`~numpy.ndarray`):
            
                `X` is either an (M,N,K) array containing M*N length-K vectors
                to be transformed or it is an (R,K) array of length-K vectors
                to be transformed.
                
        Returns an (M,N,J) or (R,J) array, depending on shape of `X`, where J
        is the length of the first dimension of the array `A` passed to
        __init__.
        '''
        shape = X.shape
        if len(shape) == 3:
            X = X.reshape((-1, shape[-1]))
            if self._pre != None:
                X = X + self._pre
            Y = np.dot(self._A, X.T).T
            if self._post != None:
                Y += self._post
            return Y.reshape((shape[:2] + (-1,))).squeeze().astype(self.dtype)
        else:
            if self._pre != None:
                X = X + self._pre
            Y = np.dot(self._A, X.T).T
            if self._post != None:
                Y += self._post
            return Y.astype(self.dtype)
    
    def chain(self, transform):
	'''Chains together two linear transforms.
	If the transform `f1` is given by
	
	.. math::
	
	    F_1(X) = A_1(X + b_1) + c_1
	
	and `f2` by
	
	.. math::
	
	    F_2(X) = A_2(X + b_2) + c_2
	
	then `f1.chain(f2)` returns a new LinearTransform, `f3`, whose output
	is given by
	
	.. math::
	
	    F_3(X) = F_2(F_1(X))
	'''
	
	if isinstance(transform, np.ndarray):
	    transform = LinearTransform(transform)
	if self.dim_in != transform.dim_out:
	    raise Exception('Input/Output dimensions of chained transforms'
			    'do not match.')

	# Internally, the new transform is computed as:
	# Y = f2._A.dot(f1._A).(X + f1._pre) + f2._A.(f1._post + f2._pre) + f2._post
	# However, any of the _pre/_post members could be `None` so that needs
	# to be checked.

	if transform._pre != None:
	    pre = np.array(transform._pre)
	else:
	    pre = None
	post = None
	if transform._post != None:
	    post = np.array(transform._post)
	    if self._pre != None:
		post += self._pre
	elif self._pre != None:
	    post = np.array(self._pre)
	if post != None:
	    post = self._A.dot(post)
	if self._post:
	    post += self._post
	if post != None:
	    post = np.array(post)
	A = self._A.dot(transform._A)
	return LinearTransform(A, pre=pre, post=post)

	
