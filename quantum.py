#from qiskit import *
import unit
import gui
import room
import fonts as f

from typing import Optional, Tuple
from enum import Enum, auto

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
        self.result: Tuple[bool, int] = (False, None) # this doesn't necessarily have to be an int, but might as well be

        # prepare the quantum circuit
        # this is only for entanglement (I think?)
        #qreg = QuantumRegister(1)
        #creg = ClassicalRegister(1)
        #self.circ = QuantumCircuit(qreg, creg)
        #circ.h(qreg[0])
        #circ.measure(qreg, creg)

    # call this after qubits are superimposed to offload the expensive call to azure. Won't actually affect game state until observe() is called.
                       # v check this please. Game is supposed to hang, but add a scroll wheel or something to prevent failure of other key functions. Maybe you can even use async or something
    def measure(self): # I think this needs to get multithreaded to avoid conflict with GUI
        if not self.result[0]:
            # compute result
            answer = 1
            self.result = (True, answer)
        return self.result[1]
        #result = self.backend.run(self.circ, shots=1).result()
        #counts = result.get_counts(circ)
        #return counts.keys()[0] == "1"

    def observe(self) -> bool:
        if self.measure():
            # this may not work on your machine (python 10 feature), so ig you can change to if-elif as needed
            attr_list = []
            moving = False
            match self.attribute:
                case Attributes.position:
                    # coords are the weird ones. Try TileMap.move_unit() and sprite.reposition()
                    # I'm going to take care of this logic within map.py because it's simply easier. Who cares about project structure, amirite?
                    moving = True
                    pass
                case Attributes.health:
                    attr_list = ["health", "health_max", "health_prev"]
                case Attributes.level:
                    attr_list = ["level", "level_prev", "experience", "exp_prev"]
                case _:
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
        

    def edit_circuit(): # allow player to manipulate circuit themselves if there's time
        pass