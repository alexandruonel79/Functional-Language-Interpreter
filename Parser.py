class Lista:
    # token_list -> the unconsumed tokens from the lexer
    # atoms_list -> a list with all the atoms that this list contains
    def __init__(self, token_list) -> None:
        self.token_list = token_list
        self.atoms_list = []

    # follows the grammar
    def parse(self):
        if get_token(self.token_list) == "Space":
            self.token_list.pop(0)

        if get_token(self.token_list) == "RightBracket":
            self.token_list.pop(0)
            return self
        else:
            atom = Atom(self.token_list).parse()
            self.atoms_list.append(atom)
            self.token_list = atom.token_list
            self.parse()
            return self

    # checks if contains just numbers
    # and sublists that contain only numbers
    def is_constant(self):
        # for when is empty list
        if not self.atoms_list:
            return True
        # all members must be constant
        for atom in self.atoms_list:
            if isinstance(atom, Atom) and atom.atom_type == "List":
                atom = atom.atom_value
            if isinstance(atom, Lista):
                if not atom.is_constant():
                    return False
            elif isinstance(atom, Lambda):
                return False
            elif isinstance(atom, Atom) and atom.atom_type != "Number":
                # it is allowed to contain only numbers to be a constant list
                return False
        return True

    # generates the printable output for the list
    def generate_output(self):
        # for when is empty list
        if not self.atoms_list:
            return "()"

        output = "("

        for atom in self.atoms_list:
            if isinstance(atom, (str, int)):
                output += " "
                output += atom
            elif isinstance(atom, Lista):
                if atom.atoms_list:
                    output += " "
                    output += atom.generate_output()
                else:
                    output += " ()"
            elif atom.atom_type == "List":
                if len(atom.atom_value.atoms_list) > 0:
                    output += " "
                    output += atom.atom_value.generate_output()
                else:
                    output += " ()"

            elif atom.atom_type == "Number":
                output += " "
                output += atom.atom_value
        output += " )"

        return output


class Atom:
    def __init__(self, token_list) -> None:
        self.token_list = token_list
        self.atom_type = None
        self.atom_value = None

    def parse(self):
        if get_token(self.token_list) == "Space":
            self.token_list.pop(0)

        if get_token(self.token_list) == "LeftBracket":
            self.token_list.pop(0)
            self.atom_type = "List"
            self.atom_value = Lista(self.token_list).parse()
            return self
        elif get_token(self.token_list) == "Number":
            self.atom_type = "Number"
            self.atom_value = get_regex(self.token_list)
            self.token_list.pop(0)
            return self
        elif get_token(self.token_list) == "Plus":
            self.atom_type = "Plus"
            self.atom_value = get_regex(self.token_list)
            self.token_list.pop(0)
            return self
        elif get_token(self.token_list) == "Concat":
            self.atom_type = "Concat"
            self.atom_value = get_regex(self.token_list)
            self.token_list.pop(0)
            return self
        elif get_token(self.token_list) == "Id":
            self.atom_type = "Id"
            self.atom_value = get_regex(self.token_list)
            self.token_list.pop(0)
            return self
        elif get_token(self.token_list) == "Lambda":
            self.atom_type = "Lambda"
            self.token_list.pop(0)
            self.atom_value = Lambda(self.token_list).parse()
            return self

    def generate_output(self) -> []:
        if self.atom_type == "Number" or self.atom_type == "Id":
            return self.atom_value
        elif self.atom_type == "List":
            return self.atom_value.generate_output()


class Lambda:
    def __init__(self, token_list) -> None:
        self.token_list = token_list
        self.id = None
        self.lambda_content = None

    def parse(self):
        if get_token(self.token_list) == "Space":
            self.token_list.pop(0)

        if get_token(self.token_list) == "Id":
            self.id = get_regex(self.token_list)
            self.token_list.pop(0)

        if get_token(self.token_list) == "Colon":
            self.token_list.pop(0)
            self.lambda_content = Atom(self.token_list).parse()
            return self


def get_token(token_list: [(str, str)]):
    token, _ = token_list[0]
    return token


def get_regex(token_list: [(str, str)]):
    _, regex = token_list[0]
    return regex
