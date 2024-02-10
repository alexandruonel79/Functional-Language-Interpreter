from .NFA import NFA

operations = "*|?+"
EPSILON = ""


class Regex:
    contor_stari = -1

    def __init__(self, ordered_queue):
        # the operators and operations in the correct order
        self.ordered_queue = ordered_queue

    def thompson(self) -> NFA[int]:
        # holds all the nfas while building the final nfa
        nfa_stack = []
        # translate through all the queue
        # it's already in the correct order
        while self.ordered_queue:
            token = self.ordered_queue.pop(0)
            # squareBracket will be made as a single NFA
            if isinstance(token, (Character, SquareBracket)):
                nfa_stack.append(token.thompson(token))
            # if it's Concat or Union we need the last two nfas to
            # apply the thompson method
            elif isinstance(token, (Concat, Union)):
                first_nfa = nfa_stack.pop()
                second_nfa = nfa_stack.pop()
                nfa_stack.append(token.thompson(first_nfa, second_nfa))
            # for kleen star, + and ? operations we need only the last nfa
            elif isinstance(token, (Star, OnceOrMore, OnceOrNever)):
                first_nfa = nfa_stack.pop()
                nfa_stack.append(token.thompson(first_nfa))

        # stack[0] is the final nfa
        return nfa_stack[0]


class Character:
    def __init__(self, value):
        # ord returns the ascii code
        self.value = ord(value)

    def thompson(self, caracter) -> NFA[int]:
        # symbols contains the character and EPSILON
        symbols = {chr(caracter.get_value()), EPSILON}
        Regex.contor_stari += 1
        # initial state is the next available state
        initial_state = Regex.contor_stari
        Regex.contor_stari += 1
        # final state is the next state
        final_state = Regex.contor_stari
        # there are only two states needed for representing a
        # nfa for a character
        states = {initial_state, final_state}
        # contains a transition from the initial state to the
        # final state on the symbol character
        dictionary = {(initial_state, chr(caracter.get_value())): {final_state}}
        # return the newly created nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_value(self):
        return self.value


class Concat:
    # empty constructor
    def __init__(self):
        pass

    # requires two nfas to concat them into one nfa
    def thompson(self, second_nfa, first_nfa) -> NFA[int]:
        # symbols is the combination of the first and second nfa
        symbols = first_nfa.S
        symbols.update(second_nfa.S)
        # states is the combination of the first and second nfa
        states = first_nfa.K
        states.update(second_nfa.K)

        initial_state = first_nfa.q0
        # dictionary is the combination of the first and second nfa
        dictionary = first_nfa.d
        dictionary.update(second_nfa.d)
        # all the final states from the first nfa go into the
        # initial state of the second one
        for s_final in first_nfa.F:
            dictionary[(s_final, EPSILON)] = {second_nfa.q0}

        final_state = second_nfa.F
        # create the new nfa combining the two ones
        return NFA(symbols, states, initial_state, dictionary, final_state)

    def get_priority(self):
        return 2


class OnceOrMore:
    # empty constructor
    def __init__(self):
        pass

    def thompson(self, nfa) -> NFA[int]:
        # get the states, symbols
        symbols = nfa.S
        states = nfa.K
        Regex.contor_stari += 1
        # the new initial state
        initial_state = Regex.contor_stari
        Regex.contor_stari += 1
        # the new final state
        final_state = Regex.contor_stari
        # add the new states
        states.add(initial_state)
        states.add(final_state)

        dictionary = nfa.d
        dictionary[(initial_state, EPSILON)] = {nfa.q0}
        # all the final states from the nfa go into the newly
        #  ->final state on a epsilon transition
        # all the final states from the nfa go to the
        # ->initial state of the nfa
        for sf in nfa.F:
            if (sf, EPSILON) in dictionary:
                dictionary[(sf, EPSILON)].add(final_state)
                dictionary[(sf, EPSILON)].add(nfa.q0)
            else:
                dictionary[(sf, EPSILON)] = {final_state, nfa.q0}
        # return the newly created nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_priority(self):
        return 3


class OnceOrNever:
    # empty constructor
    def __init__(self):
        pass

    def thompson(self, nfa) -> NFA[int]:
        # get the states, symbols
        symbols = nfa.S
        states = nfa.K

        Regex.contor_stari += 1
        # the new initial state
        initial_state = Regex.contor_stari
        Regex.contor_stari += 1
        # the new final state
        final_state = Regex.contor_stari
        # add the new states
        states.add(initial_state)
        states.add(final_state)

        dictionary = nfa.d
        # add a transition from the newly created initial state
        # to the newly final state and the initial state of the nfa
        dictionary[(initial_state, EPSILON)] = {nfa.q0}
        dictionary[(initial_state, EPSILON)].add(final_state)
        # every final state from the nfa goes into the newly
        # created final state
        for sf in nfa.F:
            if (sf, EPSILON) in dictionary:
                dictionary[(sf, EPSILON)].add(final_state)
            else:
                dictionary[(sf, EPSILON)] = {final_state}
        # return the newly generated nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_priority(self):
        return 3


class Star:
    # empty constructor
    def __init__(self):
        pass

    def thompson(self, nfa) -> NFA[int]:
        # get the states, symbols
        symbols = nfa.S
        states = nfa.K
        Regex.contor_stari += 1
        # the new initial state
        initial_state = Regex.contor_stari
        Regex.contor_stari += 1
        # the new final state
        final_state = Regex.contor_stari
        # add the new states
        states.add(initial_state)
        states.add(final_state)

        dictionary = nfa.d
        # add a transition from the newly created initial state
        # to the newly final state and the initial state of the nfa
        dictionary[(initial_state, EPSILON)] = {nfa.q0}
        dictionary[(initial_state, EPSILON)].add(final_state)
        # all the final states from the nfa go into the newly
        # final state on a epsilon transition
        # every final state from the nfa goes into the newly
        # created final state
        for sf in nfa.F:
            if (sf, EPSILON) in dictionary:
                dictionary[(sf, EPSILON)].add(final_state)
                dictionary[(sf, EPSILON)].add(nfa.q0)
            else:
                dictionary[(sf, EPSILON)] = {final_state, nfa.q0}
        # return the newly generated nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_priority(self):
        return 3


class Union:
    # empty constructor
    def __init__(self):
        pass

    def thompson(self, second_nfa, first_nfa) -> NFA[int]:
        # get the symbols from both nfas
        symbols = first_nfa.S
        symbols.update(second_nfa.S)
        # get the states from both nfas
        states = first_nfa.K
        states.update(second_nfa.K)
        # initial state
        Regex.contor_stari += 1
        initial_state = Regex.contor_stari
        # final state
        Regex.contor_stari += 1
        final_state = Regex.contor_stari
        # add the newly created states
        states.add(initial_state)
        states.add(final_state)
        # get all the transitions
        dictionary = first_nfa.d
        dictionary.update(second_nfa.d)
        # transition from the newly created initial state
        # to the initial states of both nfas
        dictionary[(initial_state, EPSILON)] = {first_nfa.q0}
        dictionary[(initial_state, EPSILON)].add(second_nfa.q0)
        # for every final state of the first nfa it
        # has a transition into the newly final state
        for s_final in first_nfa.F:
            dictionary[(s_final, EPSILON)] = {final_state}
        # for every final state of the second nfa it
        # has a transition into the newly final state
        for s_final in second_nfa.F:
            dictionary[(s_final, EPSILON)] = {final_state}
        # return the newly creaated nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_priority(self):
        return 1


class SquareBracket:
    def __init__(self, value=None):
        self.value = value

    def thompson(self, bracket) -> NFA[int]:
        # add all the characters between start_state
        # and end_state
        symbols = set()
        start_state = ord(bracket.get_value()[0])
        end_state = ord(bracket.get_value()[2])

        while start_state <= end_state:
            symbols.add(chr(start_state))
            start_state += 1

        Regex.contor_stari += 1
        # newly created initial state
        initial_state = Regex.contor_stari
        Regex.contor_stari += 1
        # newly created final state
        final_state = Regex.contor_stari
        # states contains just the initial and final state
        states = {initial_state, final_state}
        # add a transition from initial state on
        # every symbol s to the final state
        dictionary = {}
        for s in symbols:
            dictionary[(initial_state, s)] = {final_state}
        # return the newly created nfa
        return NFA(symbols, states, initial_state, dictionary, {final_state})

    def get_value(self):
        return self.value

    def get_priority(self):
        return 4


class RightBracket:
    def __init__(self):
        pass


class LeftBracket:
    def __init__(self):
        pass

    def get_priority(self):
        return 1


def remove_spaces(regex: str) -> str:
    new_regex = ""
    # keep only the spaces that have escaping character before them
    # keep all the other characters
    for i, _ in enumerate(regex):
        if regex[i] == " " and i > 0 and regex[i - 1] == "\\":
            new_regex += regex[i]
        elif regex[i] == " " and i > 0 and regex[i - 1] != "\\":
            continue
        else:
            new_regex += regex[i]

    return new_regex


def add_Concat_if_possible(regex: str, i: int, objects_list: []) -> []:
    if len(regex) - 1 > i:
        if regex[i + 1] != ")" and (
            regex[i + 1] == "\\"
            or regex[i + 1] == "("
            or regex[i + 1] == "["
            or regex[i + 1] not in operations
        ):
            objects_list.append(Concat())
    return objects_list


def create_regex_token_list(regex: str) -> []:
    # objects_list stores all the new created objects depending on char's type
    objects_list = []
    regex = remove_spaces(regex)
    i = 0
    last_is_escaped = False
    # create the token objects
    while i < len(regex):
        if last_is_escaped:
            # next is definetly a char
            objects_list.append(Character(regex[i]))
            add_Concat_if_possible(regex, i, objects_list)
            # make it false
            last_is_escaped = False
        elif regex[i] == "\\":
            last_is_escaped = True
        elif regex[i] == "(":
            objects_list.append(LeftBracket())
        elif regex[i] == ")":
            objects_list.append(RightBracket())
            add_Concat_if_possible(regex, i, objects_list)
        elif regex[i] == "[":
            inside = ""
            inside += regex[i + 1]  # a
            inside += regex[i + 2]  # -
            inside += regex[i + 3]  # z
            i += 4  # jumps at ]
            objects_list.append(SquareBracket(inside))
            add_Concat_if_possible(regex, i, objects_list)
        elif regex[i] == "*":
            objects_list.append(Star())
            add_Concat_if_possible(regex, i, objects_list)
        elif regex[i] == "+":
            objects_list.append(OnceOrMore())
            add_Concat_if_possible(regex, i, objects_list)
        elif regex[i] == "?":
            objects_list.append(OnceOrNever())
            add_Concat_if_possible(regex, i, objects_list)
        elif regex[i] == "|":
            objects_list.append(Union())
        else:
            # it s definetely a char
            objects_list.append(Character(regex[i]))
            add_Concat_if_possible(regex, i, objects_list)

        i += 1

    return objects_list


def shunting_yard(objects_list: []) -> ([], []):
    # saves the tokens in the correct order
    ordered_queue = []
    # helper for the shunting yard
    # stores brackets and operations
    auxiliary_stack = []
    # translate through all the tokens from the list
    for token in objects_list:
        # put it in the queue
        if isinstance(token, (Character, SquareBracket)):
            ordered_queue.append(token)
        # if the token is an operator and while there is on top of the stack
        # an operator with bigger priority, append the operator from
        # stack into the output queue, then place the token in the op stack
        elif isinstance(token, (Star, OnceOrMore, OnceOrNever, Concat, Union)):
            while (
                auxiliary_stack
                and (auxiliary_stack[-1].get_priority() >= token.get_priority())
                and (
                    isinstance(
                        auxiliary_stack[-1],
                        (Star, OnceOrMore, OnceOrNever, Concat, Union),
                    )
                )
            ):
                ordered_queue.append(auxiliary_stack.pop())

            auxiliary_stack.append(token)
        # if the stack top is a left bracket and token is an operation
        # append it into the operator stack
        elif (
            auxiliary_stack
            and isinstance(auxiliary_stack[-1], LeftBracket)
            and (isinstance(token, (Star, OnceOrMore, OnceOrNever, Concat, Union)))
        ):
            auxiliary_stack.append(token)
        # if the token is a left bracket, append it into the operator stack
        elif isinstance(token, LeftBracket):
            auxiliary_stack.append(token)
        # if the token is a right bracket
        # pop the elements from the stack until meeting
        # left bracket operator and add them into the queue , then pop it
        elif isinstance(token, RightBracket):
            while auxiliary_stack and not isinstance(auxiliary_stack[-1], LeftBracket):
                ordered_queue.append(auxiliary_stack.pop())

            if auxiliary_stack:
                auxiliary_stack.pop()

    return (ordered_queue, auxiliary_stack)


def parse_regex(regex: str) -> Regex:
    # transforms the regex into a token list
    objects_list = create_regex_token_list(regex)
    # shunting yard orders the operations
    ordered_queue, auxiliary_stack = shunting_yard(objects_list)
    # add the remaining operations
    while auxiliary_stack:
        ordered_queue.append(auxiliary_stack.pop())

    return Regex(ordered_queue)
