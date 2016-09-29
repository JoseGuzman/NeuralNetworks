"""
init.py

To execute in Ipython
%run init.py

In Python from the shell
$ nrngui init.py -python

>>> import init

"""

import numpy as np
from neuron import h, gui
from Cell_builder import BCbuilder, GCbuilder

h.load_file('stdrun.hoc') # need for h.tstop
h.tstop = 200

#=========================================================================
# 1. create a network of 100 inhibitory neurons and 1000 principal neurons
#=========================================================================
icells = 100
BC = [BCbuilder( idx = i) for i in range(icells)] 

ecells = 100
GC = [GCbuilder( idx = i) for i in range(ecells)] 

#=========================================================================
# 2. Apply tonic excitatory drive to inhibitory cells 
#=========================================================================
np.random.seed(10)

def inject_random_current(nrnSection):
    """
    Injects a current of random amplitude and duration to
    the section given in nrnSection
    """
    I_mu = 0.001      # in nanoAmp, corresponding to 1 uA/cm^2
    I_sigma = 0.00003 # corresponds to 3% heterogeneity

    stim = h.IClamp(0.5, sec = nrnSection )
    stim.amp   = np.random.normal( loc = I_mu, scale = I_sigma*I_sigma)
    stim.delay = np.abs( np.random.normal( loc = 5, scale = 4 ) )
    stim.dur   = h.tstop - stim.delay

    return (stim)

stim_icells = [inject_random_current(nrnSection = cell.soma) for cell in BC] 
stim_ecells = [inject_random_current(nrnSection = cell.soma) for cell in GC] 

#=========================================================================
# 3. Custom connections between all cells  
#=========================================================================
def recurrent_inh(cell_list):
    """
    Connects inhibitory neuron via recurrent inhibitory synapses 
    """
    mynetcon = list()
    for i in range( len(cell_list) ) :
        for j in np.delete( range(len(cell_list)), i): # avoid auptapse
            nc = cell_list[i].connect2target( target = cell_list[j].isyn )
            mynetcon.append( nc )

    #return (mynetcon)



#=========================================================================
# 4. Visualize
#=========================================================================

h.run()
h.load_file('gui/gSingleGraph.hoc')
#mygraph = h.VoltageGraph()
h.load_file('gui/gRasterPlot.hoc')

#=========================================================================
# 5. My custom run 
#=========================================================================
def myrun():
    h.run()
    h.update_rasterplot()

if '__name__' == '__main__':
    pass
