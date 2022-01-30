from qiskit import *
import unit
import gui
import room
import fonts as f
from azure.quantum.qiskit import AzureQuantumProvider
from qiskit.tools.monitor import job_monitor
from qiskit.visualization import plot_histogram
from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
from typing import Optional, Tuple
from enum import Enum, auto

resource_id = "/subscriptions/b1d7f7f8-743f-458e-b3a0-3e09734d716d/resourceGroups/aq-hackathons/providers/Microsoft.Quantum/Workspaces/aq-hackathon-01"

provider = AzureQuantumProvider(
    resource_id=resource_id,
    location= "East US"
)


Coord = Tuple[int, int]

#certainly not the most elegant enum I've ever written...
class Attributes(Enum):
    health = auto()
    level = auto()
    strength = auto()
    skill = auto()
    speed = auto()
    luck = auto()
    defence = auto()
    resistance = auto()
    movement = auto() # might want to implement an edge case here, because how far should a unit be able to move if this stat is in superposition? one option would be to collapse before moving the unit
    constitution = auto()
    aid = auto()
    affinity = auto()
    condition = auto()
    wrank = auto()
    items = auto()
    position = auto()


# can only entangle weapons if max wrank of unit >= min rank of weapon (who cares though w)

class Quantum():
    #backend = provider.get_backend("ionq.simulator")
    def __init__(self, parent, child, attribute):
        self.parent: unit.Unit = parent
        self.child: unit.Unit = child
        self.attribute: Attributes = attribute
        self.result: Tuple[bool, int] = (False, None)  # this doesn't necessarily have to be an int, but might as well be

        # prepare the quantum circuit
        # this is only for entanglement (I think?)
        q = QuantumRegister(2, "q")  # quantum register with 2 qubits
        c = ClassicalRegister(2, "c")  # classical register with 2 bits
        self.qc = QuantumCircuit(q, c)  # quantum circuit with quantum and classical registers

        # prepare the quantum circuit
        # this is only for entanglement (I think?)
        self.qc.h(q[0])
        self.qc.cx(q[0], q[1])
        self.qc.barrier()
        self.qc.measure(q, c)
        # job = backend.run(qc, shots=100)
        # job_monitor(job)


    def measure(self):  # I think this needs to get multithreaded to avoid conflict with GUI
        # return True
        backend = provider.get_backend("ionq.simulator")
        job = backend.run(self.qc, shots=10)
        job_monitor(job)
        result = job.result()
        counts = result.get_counts(self.qc)
        #print(result)
        #print(counts)
        entangled_states = counts.keys()
        if ('00' in entangled_states and '11' in entangled_states):
            return True
        else:
            return False

    def observe(self) -> bool:
        if self.measure():
            # this may not work on your machine (python 10 feature), so ig you can change to if-elif as needed
            attr_list = []
            moving = False

            if self.attribute == Attributes.position:
                pass
            elif Attributes.health:
                attr_list = ["health", "health_max", "health_prev"]

            elif Attributes.level:
                attr_list = ["level", "level_prev", "experience", "exp_prev"]
            else:
                attr_list = [str(self.attribute.name)]

            for attr in attr_list:
                tmp = getattr(self.parent, attr)
                # just... don't switch attributes like image. Don't do it!
                setattr(self.parent, attr, getattr(self.child, self.attribute))
                setattr(self.child, attr, tmp)

            modal = gui.Dialog(f"SWITCHAROO!!! Switched stat {self.attribute.name}",
                               f.MAIN, layout=room.Layout(gravity=gui.Gravity.CENTER), dismiss_callback=True,
                               clear_screen=None)
            room.run_room(modal)
            print(f"SWITCHAROO!!! Switched stat {self.attribute}")

            return moving

    def edit_circuit():  # allow player to manipulate circuit themselves if there's time
        pass
