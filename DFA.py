from collections.abc import Callable
from dataclasses import dataclass

EPSILON = ''

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # current_state is set to inital state
        current_state = self.q0
        # current_string is set to initial word
        current_string = word
        # while the string is not empty
        while(current_string != EPSILON):
            # current_state becomes the new state based on the dictionary
            current_state = self.d.get((current_state, current_string[0]))
            # if it reached a sinked state it will return False
            if current_state == frozenset():
                return False
            
            current_string = current_string[1:]

        # if there are no more characters to go through
        # we check what kind of state we reached
        return current_state in self.F
        

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass

