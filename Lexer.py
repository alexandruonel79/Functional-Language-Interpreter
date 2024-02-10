from .Regex import parse_regex
from .NFA import NFA

EPSILON = ""
initial_state = -1


class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # stores every token and it's final nfa states
        self.dictionary_token_final_states = {}
        # initialize the new nfa variables
        symbols = set()
        dictionary = {(initial_state, EPSILON): set()}
        states = set()
        states.update({initial_state})
        final_states = set()
        # get the union nfa's attributes
        for index, (_, regex) in enumerate(spec):
            # transform all regex's to nfa's
            nfa = parse_regex(regex).thompson()
            # update with values from all the nfa's
            symbols.update(nfa.S)
            dictionary.update(nfa.d)
            final_states.update(nfa.F)
            states.update(nfa.K)
            # add epsilon transition from initial state to nfa's initial state
            dictionary[(initial_state, EPSILON)].add(nfa.q0)
            # store the final states for each token-nfa
            self.dictionary_token_final_states[spec[index][0]] = nfa.F
        # create the 'union-like' nfa
        union_nfa = NFA(symbols, states, initial_state, dictionary, final_states)
        # create the dfa
        self.dfa = union_nfa.subset_construction()

    # error helper function -> char not in the dfa's symbols
    def handle_incorrect_word(self, word: str) -> []:
        # position variables
        error_index = 0
        error_line_counter = 0

        for char in word:
            error_index += 1
            if char == "\n":
                error_line_counter += 1
                error_index = 0
            if char not in self.dfa.S:
                return [
                    (
                        "",
                        f"No viable alternative at character {error_index - 1}, line {error_line_counter}",
                    )
                ]
        return ["Unexpected error"]

    # checks if word respects the specification
    def check_if_word_is_correct(self, word: str) -> bool:
        # if all chars are present in the dfa's symbols
        # then the word is correct
        return all(char in self.dfa.S for char in word)

    # determines the last char position and creates the error output
    def handle_no_viable_alternative(self, word: str) -> []:
        # position variables
        line_number = 0
        character_position = 0

        for char in word:
            if char == "\n":
                character_position = 0
                line_number += 1
            else:
                character_position += 1

        return [
            (
                "",
                f"No viable alternative at character {character_position}, line {line_number}",
            )
        ]

    # creates the output error for no token at EOF
    def handle_no_match_at_EOF(self, word: str) -> []:
        total_word_lines = word.count("\n")
        return [
            ("", f"No viable alternative at character EOF, line {total_word_lines}")
        ]

    # checks if current state contains a 'nfa-final' state
    def contains_nfa_final_state(self, current_state: frozenset[int] | None) -> bool:
        return any(
            any((s in states for s in current_state))
            for (_, states) in self.dictionary_token_final_states.items()
        )

    # gets the first token found from the current state
    def get_token_from_final_state(
        self, current_state: frozenset[int] | None
    ) -> str | None:
        for token, states in self.dictionary_token_final_states.items():
            if any(s in states for s in current_state):
                return token
        return None

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # check if a char from word is not in specification
        # if so -> output the error
        if not self.check_if_word_is_correct(word):
            return self.handle_incorrect_word(word)
        # output tokens list
        found_tokens = []
        # initialise the current state
        current_state = self.dfa.q0
        current_string = word
        last_accepted_string_pos = -1
        last_accepted_token = None
        current_string_pos = 0
        # for error
        word_position = 0
        while current_string_pos < len(current_string):
            # get the next transition of the dfa
            current_state = self.dfa.d.get(
                (current_state, current_string[current_string_pos])
            )
            passed_a_final_state = False
            # search through the dictionary to check if current transition
            # contains any nfa-final state
            if self.contains_nfa_final_state(current_state):
                current_string_pos += 1
                passed_a_final_state = True
                last_accepted_string_pos = current_string_pos
                last_accepted_token = self.get_token_from_final_state(current_state)
            # special case when the last char matches
            if current_string_pos == len(current_string) and passed_a_final_state:
                found_tokens.append(
                    (last_accepted_token, current_string[:last_accepted_string_pos])
                )
            # error -> arrived in sink state and we did not pass a final state
            # this means that there is no viable alternative
            if current_state == frozenset() and not last_accepted_token:
                return self.handle_no_viable_alternative(word[: word_position + 1])
            # if we arrived in a sink state and we can match a token, it
            # means it won't match in the future, so add the token
            # to the token list
            if current_state == frozenset() and last_accepted_token:
                # reinitialise the current state with the dfa initial
                current_state = self.dfa.q0
                passed_a_final_state = False
                # add the token to the found tokens
                found_tokens.append(
                    (last_accepted_token, current_string[:last_accepted_string_pos])
                )
                # reinitialise it
                last_accepted_token = None
                # update it by eliminating the matched part of the word
                current_string = current_string[last_accepted_string_pos:]
                # current_string's counter is reinitialised
                current_string_pos = 0
                # update the word_position
                word_position += last_accepted_string_pos
                continue
            # visited a non final state and it isn't sink state
            # then consume a char from word
            if not passed_a_final_state and current_state != frozenset():
                current_string_pos += 1
        # before leaving the while we should have passed one or more
        # final states, if we didn't pass a final state before leaving
        # it means we cannot match the remained word
        if not passed_a_final_state:
            return self.handle_no_match_at_EOF(word)
        # return all the found tokens
        return found_tokens
