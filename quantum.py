#from qiskit import *
import unit
import gui
import room
import fonts as f

class Quantum():
    #backend = provider.get_backend("ionq.simulator")
    def __init__(self, parent, child, attribute):
        self.parent: unit.Unit = parent
        self.child: unit.Unit = child
        self.attribute: str = attribute

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
        if self.measure():
            modal = gui.Dialog(f"SWITCHAROO!!! Switched stat {self.attribute}",
                              f.MAIN, layout=room.Layout(gravity=gui.Gravity.CENTER), dismiss_callback=True,
                              clear_screen=None)
            room.run_room(modal)
            print(f"SWITCHAROO!!! Switched stat {self.attribute}")
            tmp = getattr(self.parent, self.attribute)
            setattr(self.parent, self.attribute, getattr(self.child, self.attribute))
            setattr(self.child, self.attribute, tmp)
        

    def edit_circuit(): # allow player to manipulate circuit themselves if there's time
        pass