"""
Cell_builder.py

Authors: 
Claudia Espinoza,  claumespinoza@gmail.com 
Jose Guzman,  sjm.guzman@gmail.com 

Last change: Wed Oct 12 16:11:56 CEST 2016

File that contains detailed morphologies of principal cells (PC)
and basquet cells (BC) in the prefrontal cortex 

To use it:

>>> from Cell_builder import PC
>>> myPC = PC()

"""
import numpy as np
from neuron import h 

class BCbuilder(object):
    """
    A test basquet-cell to perform lighter simulations
    """
    def __init__(self, idx = None):
        """
        creates a single compartment with a surface area of 100 um^2 
        and Wang and Buzsaki Na and K conductances (Wang and Buzsaki, 1996) 
        and a synapse
        Arguments:

        idx         -- (int) index of the neuron to be created
        """
        if idx is None:
            self.myid = 'BasquetCell'
        else:
            self.myid = 'BC_' + '{:04d}'.format(idx)

        self.soma = h.Section(name = self.myid, cell = self)
        self.soma.nseg = 1

        self.soma.diam = self.soma.L = 5.64 # in um
        self.soma.insert('hh_w') # Wang and Buzsaki Na & K channels

        # create current injection in the soma
        self.IClamp = h.IClamp(0.5, sec = self.soma)
        self.IClamp.amp = 0.0
        self.IClamp.dur = 0.0
        self.IClamp.delay = 0.0
        
        # create an inhibitory synapse in soma
        self.isyn = h.ExpSyn(self.soma(0.5), sec=self.soma)
        self.isyn.tau = 10.0 # in ms
        self.isyn.e = -75.0      # in mV

        # create an excitatory synapse in soma
        self.esyn = h.ExpSyn(self.soma(0.5), sec=self.soma)
        self.esyn.tau = 10.0 # in ms
        self.esyn.e = 0.0      # in mV

        # a list of connections to other cells
        self._netcon = list()

        # hoc Vectors to record time and voltage
        self._voltage = h.Vector()
        self._voltage.record( self.soma(0.5)._ref_v )

        # Netcon to monitor membrane potential at the soma (i.e. AP)
        self._nc = h.NetCon( self.soma(0.5)._ref_v, None, sec= self.soma)
        self._nc.threshold = 0.0

        self._spk_times = h.Vector()
        self._nc.record( self._spk_times ) # spike times
        
    def connect2target(self, target, weight=None):
        """
        connects the firing of basquet cell to a target via a NetCon
        and appends the NetCon to the netcon list

        Arguments:
        target      -- a point process (e.g h.ExpSyn) in the target cell

        """
        source = self.soma(0.5)._ref_v # voltage at soma
        netcon = h.NetCon(source, target, sec = self.soma)
        netcon.threshold = 0.0 # overshooting APs
        netcon.delay     = 1.0 # synaptic delay

        if weight is None:
            # 1.235e-8 will prevent AP in granule cells, see minimal.py
            netcon.weight[0] = 1.235e-7 
        else:
            netcon.weight[0] = weight

        self._netcon.append(netcon)

        return(netcon)

    # getters
    name      = property(lambda self: self.soma.name()[-len(self.myid):] )
    voltage   = property( lambda self: np.array( self._voltage))
    time      = property( lambda self: np.array( self._time  ))
    spk_times = property( lambda self: np.array( self._spk_times))

class PCbuilder(object):
    def __init__(self, idx = None):
        """
        creates a single compartment with a surface area of 50 um 
        and fast spikes using pulse-based HH model. See Destexhe, 1996.
        Arguments:

        idx         -- (int) index of the neuron to be created

        """
        if idx is None:
            self.myid = 'GranuleCell'
        else:
            self.myid = 'GC_' + '{:04d}'.format(idx)

        self.soma = h.Section(name = self.myid, cell = self)
        self.soma.nseg = 1

        self.soma.diam = self.soma.L = 2.0 # in um
        self.soma.insert('pas')
        self.soma.g_pas = 1e-4
        self.soma.e_pas = -70.0 # in mV
        self.soma.insert('hhPC') # Hodking and Huxley Na & K channels
        self.soma.ek = -80.0 # in mV
        self.soma.gnabar_hhPC = 0.1
        self.soma.gkbar_hhPC  = 0.03

        self.soma.Vtr_hhPC = -50.0  # AP threshold in mV
        self.soma.Dur_hhPC = 1.6    # spike duration
        self.soma.Ref_hhPC = 1.5    # refractory period

        self.soma.alphaM_hhPC = 22
        self.soma.betaM_hhPC = 13
        self.soma.alphaH_hhPC = 0.5
        self.soma.betaH_hhPC = 4
        self.soma.alphaN_hhPC = 2.2
        self.soma.betaN_hhPC = 0.76

        # create current injection in the soma
        self.IClamp = h.IClamp(0.5, sec = self.soma)
        self.IClamp.amp = 0.0
        self.IClamp.dur = 0.0
        self.IClamp.delay = 0.0

        # Inhibitory synapse in soma
        self.isyn = h.ExpSyn(self.soma(0.5), sec=self.soma)
        self.isyn.tau = 10.0 # in ms
        self.isyn.e = -95.0  # in mV

        # Excitatory synapse in soma
        self.esyn = h.ExpSyn(self.soma(0.5), sec=self.soma)
        self.esyn.tau = 10.0 # in ms
        self.esyn.e   = 0.0  # in mV

        # a list of connections to other cells
        self._netcon = list()

        # hoc Vectors to record time and voltage
        self._voltage = h.Vector()
        self._voltage.record( self.soma(0.5)._ref_v )

        # Netcon to monitor membrane potential at the soma (i.e. AP)
        self._nc = h.NetCon( self.soma(0.5)._ref_v, None, sec= self.soma)
        self._nc.threshold = 0.0

        self._spk_times = h.Vector()
        self._nc.record( self._spk_times ) # spike times

    def connect2target(self, target, weight = None):
        """
        connects the firing of granule cell to a target via a NetCon
        and appends the NetCon to the netcon list

        Arguments:
        target      -- a point process (e.g h.ExpSyn) in the target cell

        """
        source = self.soma(0.5)._ref_v # voltage at soma
        netcon = h.NetCon(source, target, sec = self.soma)
        netcon.threshold = 0.0 # overshooting APs
        netcon.delay     = 1.0 # synaptic delay

        if weight is None:
            # 1.7535e-5 will evoke an AP in granule cells, see minimal.py
            netcon.weight[0] = 1.7535e-6
        else:
            netcon.weight[0] = weight

        self._netcon.append(netcon)

        return(netcon)

    # getters
    name = property(lambda self: self.soma.name()[-len(self.myid):] )
    voltage   = property( lambda self: np.array( self._voltage))
    time      = property( lambda self: np.array( self._time  ))
    spk_times = property( lambda self: np.array( self._spk_times))
   
if __name__ == '__main__':
    # Cell Builder test
    GC = GCbuilder()
    pass
