from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ""


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    # auxiliary recursive function
    def epsilon_closure_aux_function(
        self, states: set[STATE], current_states: STATE
    ) -> set[STATE]:
        # base case for stopping the recursivity
        if current_states == []:
            return states
        # go through all the states from 'current_states'
        # all of them are reacheable with epsilon transition
        # if they are not already in the set, add them
        for state in current_states:
            if state not in states:
                states.add(state)
                new_list = list(self.d.get((state, EPSILON), []))
                # epsilon close the current one
                self.epsilon_closure_aux_function(states, new_list)

        return states

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        epsilon_enclosures = set()
        # add the initial
        epsilon_enclosures.add(state)
        # takes the list of epsilon transition states
        # if none then current_states becomes '[]'
        current_states = list(self.d.get((state, EPSILON), []))
        return self.epsilon_closure_aux_function(epsilon_enclosures, current_states)

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # initial state is the epsilon closure of the initial state
        initial_states = self.epsilon_closure(self.q0)
        # the dictionary for the new_dfa
        new_dictionary = dict()
        # the list where the algorithm translates through all the states
        # works like a queue
        translating_states = []
        # append the initial states as a starting point
        translating_states.append(list(initial_states))
        # all the states for the new_dfa
        k_states = set()
        # add the initial epsilon closure
        k_states.add(frozenset(initial_states))
        # also add the sink state, frozenset()
        k_states.add(frozenset())
        # final states for the new_dfa
        final_states = set()
        # if any initial state is final
        # add the intial states to the final states
        if any(s in self.F for s in initial_states):
            final_states.add(frozenset(list(initial_states)))

        # for the sink state, every symbol goes into it
        new_dictionary = {(frozenset(), symbol): frozenset() for symbol in self.S}

        # while there are more states to translate through
        while translating_states:
            current_states = translating_states[0]
            # search through all the symbols
            for symbol in self.S:
                # found states contains all the accesible states
                # "the states in the new bubble created"
                found_states = set()

                for current_state in current_states:
                    # if the current_state has a transition
                    new_state = list(self.d.get((current_state, symbol), []))
                    # add all its states, with their epsilon closure
                    for s in new_state:
                        # they can already exist in found_states, so i used update instead of add
                        found_states.update(self.epsilon_closure(s))

                # add found_states to the final states if contains any final state
                if any(
                    s in self.F and found_states not in final_states
                    for s in found_states
                ):
                    final_states.add(frozenset(list(found_states)))

                if found_states:
                    # we have a transition to a group of states
                    new_dictionary[frozenset(current_states), symbol] = frozenset(
                        found_states
                    )
                    # if it's new, add it to the dfa states and translating_states
                    if found_states not in k_states:
                        k_states.add(frozenset(list(found_states)))
                        translating_states.append(list(found_states))
                else:
                    # no found_states so we go into the sink state
                    new_dictionary[frozenset(current_states), symbol] = frozenset()

            # go to the next group of states
            translating_states.pop(0)

        return DFA(
            self.S, k_states, frozenset(initial_states), new_dictionary, final_states
        )

    def remap_states[
        OTHER_STATE
    ](self, f: "Callable[[STATE], OTHER_STATE]") -> "NFA[OTHER_STATE]":
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        pass
