#from qiskit import *

class Quantum():
    #backend = provider.get_backend("ionq.simulator")
    def __init__(self, parent, child, attribute):
        self.parent = parent
        self.child = child
        self.attribute = attribute

        # prepare the quantum circuit
        # this is only for entanglement (I think?)
        #qreg = QuantumRegister(1)
        #creg = ClassicalRegister(1)
        #self.circ = QuantumCircuit(qreg, creg)
        #circ.h(qreg[0])
        #circ.measure(qreg, creg)


    def measure(self): # I think this needs to get multithreaded to avoid conflict with GUI
        return True
        #result = self.backend.run(self.circ, shots=1).result()
        #counts = result.get_counts(circ)
        #return counts.keys()[0] == "1"

    def observe(self):
        pass
        if self.measure():
            print("")
            tmp = getattr(self.parent, self.attribute)
            setattr(self.parent, self.attribute, getattr(self.child, self.attribute))
            setattr(self.child, self.attribute, tmp)
        

    def edit_circuit(): # allow player to manipulate circuit themselves if there's time
        pass