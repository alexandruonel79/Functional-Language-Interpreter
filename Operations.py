from .Parser import Lista, Atom, Lambda


# calculates the sum, going through all the lists
# recursively
def plus_function(lista: Lista | Atom) -> Atom | int:
    total = 0
    if not isinstance(lista, Lista):
        return lista
    for atom in lista.atoms_list:
        if isinstance(atom, Lista):
            total += plus_function(atom)
        elif atom.atom_type == "Number":
            total += int(atom.atom_value)
    return total


# concatenates the lists
def concat_function(lista: Lista) -> Lista:
    new_list = Lista(None)

    for atom in lista.atoms_list:
        if isinstance(atom, Lista):
            for inner_atom in atom.atoms_list:
                new_list.atoms_list.append(inner_atom)
        else:
            new_list.atoms_list.append(atom)

    return new_list


# iterative function, can be written recursively too
def lambda_function(op_one: Lambda, argument: Lambda | Atom | Lista) -> Lambda | Lista:
    lambda_id = op_one.id
    can_modify = True

    process_lambda = op_one.lambda_content
    # storing all the initial lambda
    all_lambda = []

    if isinstance(process_lambda, Atom) and process_lambda.atom_type == "Lambda":
        process_lambda = process_lambda.atom_value

    if isinstance(process_lambda, Lambda):
        all_lambda.append(process_lambda)

    while isinstance(process_lambda, Lambda) or (
        isinstance(process_lambda, Atom) and process_lambda.atom_type == "Lambda"
    ):
        if isinstance(process_lambda, Atom) and process_lambda.atom_type == "Lambda":
            process_lambda = process_lambda.atom_value
        # checks if already exists an inner lambda with the same identifier
        if process_lambda.id == lambda_id:
            can_modify = False

        process_lambda = process_lambda.lambda_content
        all_lambda.append(process_lambda)
    # if is in our visibility domain
    if can_modify:
        if isinstance(process_lambda, Atom) and process_lambda.atom_type == "List":
            process_lambda = process_lambda.atom_value

        if isinstance(process_lambda, Lista):
            replace_id_in_list(process_lambda, lambda_id, argument)
            all_lambda.append(process_lambda)
        else:
            # it must be an ID
            if process_lambda.atom_value == lambda_id:
                all_lambda.append(argument)

    if len(all_lambda) == 0:
        return process_lambda
    # after computing the lambda, reconstruct it, alternative for recursivity
    final_lambda = reconstruct_lambda(all_lambda.pop(0), all_lambda)
    return final_lambda


# The below functions are some helper functions for the operations


# replaces recursively, in all the lists, lambda_id with the replace_value
def replace_id_in_list(
    lista: Lista, lambda_id: str, replace_value: Lambda | Atom | Lista
):
    for index, atom in enumerate(lista.atoms_list):
        if isinstance(atom, Atom) and atom.atom_type == "List":
            atom = atom.atom_value

        if isinstance(atom, Lista):
            replace_id_in_list(atom, lambda_id, replace_value)

        elif isinstance(atom, Atom) and atom.atom_type == "Id" and lambda_id == atom.atom_value:
            lista.atoms_list[index] = replace_value



# given a list that contains a lambda object with all its content
# split inside the list, remake the original object
def reconstruct_lambda(lambda_elem: Lambda, lista: []):
    # base case for recursivity
    if not lista:
        return lambda_elem
    else:
        if isinstance(lambda_elem, Atom) and lambda_elem.atom_type == "Lambda":
            lambda_elem = lambda_elem.atom_value

        if isinstance(lambda_elem, Lambda):
            lambda_elem.lambda_content = reconstruct_lambda(lista.pop(0), lista)
        else:
            lambda_elem = lista.pop(0)
            # reconstruct the lambda_content
            if isinstance(lambda_elem, str):
                atom_node = Atom(None)
                # it can be both a number or an id
                if lambda_elem.isdigit():
                    atom_node.atom_type = "Number"
                else:
                    atom_node.atom_type = "Id"
                atom_node.atom_value = lambda_elem
                lambda_elem = atom_node
            elif isinstance(lambda_elem, int):
                atom_node = Atom(None)
                atom_node.atom_type = "Number"
                atom_node.atom_value = lambda_elem
                lambda_elem = atom_node

    return lambda_elem
