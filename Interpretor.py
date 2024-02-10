from .Operations import *


# checks if a list contains a lambda function
def list_contains_lambda(lista: Lista | Atom) -> bool:
    if isinstance(lista, Atom) and lista.atom_type == "List":
        lista = lista.atom_value

    for atom in lista.atoms_list:
        if isinstance(atom, Lambda):
            return True
        if isinstance(atom, Atom) and atom.atom_type == "List":
            if list_contains_lambda(atom):
                return True
        if isinstance(atom, Lista):
            if list_contains_lambda(atom):
                return True

    return False


# checks if a lambda function contains another lambda inside a list
# that means the inner lambda will need to be calculated upfront
def lambda_is_constant(lambda_func: Lambda | Atom) -> bool:
    if isinstance(lambda_func, Atom) and (
            lambda_func.atom_type == "Lambda" or lambda_func.atom_type == "List"
    ):
        lambda_func = lambda_func.atom_value

    if isinstance(lambda_func, Lambda):
        return lambda_is_constant(lambda_func.lambda_content)

    if isinstance(lambda_func, Lista):
        if list_contains_lambda(lambda_func):
            return False

    return True


# checks if the stack contains only numbers and lists
# then it's constant
def stack_is_constant(stack: []) -> bool:
    if isinstance(stack, Lista):
        stack = stack.atoms_list

    for atom in stack:
        if isinstance(atom, Lista):
            stack_is_constant(atom)
        elif not (
                (isinstance(atom, str) and atom != '+' and atom != '++')
                or (isinstance(atom, Atom) and atom.atom_type == "Number")
        ):
            return False
    return True


# creates a list from a constant stack
def create_constant_sublist(sub_stack: []) -> Lista:
    sublist = Lista(None)
    # place all the elements in the correct order
    while sub_stack:
        node = sub_stack.pop(0)
        if isinstance(node, Lista):
            sublist.atoms_list.append(node)
        else:
            if not isinstance(node, Atom):
                atom = Atom(None)
                if node.isdigit():
                    atom.atom_type = "Number"
                else:
                    atom.atom_type = "Id"
                atom.atom_value = node
                sublist.atoms_list.append(atom)
            else:
                sublist.atoms_list.append(node)

    return sublist


# creates the stack by going through every list and
# adding its atoms
def create_stack(program: Lista) -> []:
    # check if a lambda was before to delay the eval of the list
    lambda_before = False
    stack = []
    for atom in program.atoms_list:
        if isinstance(atom, Atom):
            atom = atom.atom_value
        if isinstance(atom, Lista):
            sub_stack = create_stack(atom)
            # check if substack contains only numbers
            # and constant lists
            # or a lambda was before, then append the sublist
            if stack_is_constant(sub_stack) or lambda_before:
                # create a sublist with the numbers and lists
                # in the correct order
                sublist = create_constant_sublist(sub_stack)
                stack.append(sublist)
            else:
                # can calculate the list so append the result
                result = process_stack(sub_stack)
                stack.append(result)
        else:
            # basic atom
            stack.append(atom)
        # update it
        lambda_before = isinstance(atom, Lambda)

    return stack


# calculates the inner lambda and return the initial
# lambda function, with the updated lambda_content
def compute_inner_lambda(lambda_func: Lambda) -> Lambda:
    all_lambda = []

    if isinstance(lambda_func, Lambda):
        all_lambda.append(lambda_func)
    # traversing to the last inner lambda
    while isinstance(lambda_func, Lambda) or (
            isinstance(lambda_func, Atom) and lambda_func.atom_type == "Lambda"
    ):
        if isinstance(lambda_func, Atom) and lambda_func.atom_type == "Lambda":
            lambda_func = lambda_func.atom_value

        lambda_func = lambda_func.lambda_content
        all_lambda.append(lambda_func)

    if isinstance(lambda_func, Atom) and lambda_func.atom_type == "List":
        lambda_func = lambda_func.atom_value

    if isinstance(lambda_func, Lista):
        # when called this function, we know the list isn't constant
        # so it is calculated
        all_lambda.append(process_stack(create_stack(lambda_func)))
    # recompose the initial lambda with the updated content
    final_lambda = reconstruct_lambda(all_lambda.pop(0), all_lambda)
    return final_lambda


def process_stack(stack: []) -> Atom | Lista:
    must_swap = False
    reset_both = False
    # check if the stack is needed to be calculated
    if stack_is_constant(stack):
        return create_constant_sublist(stack)

    # op_one is the operator
    op_one = stack.pop(0)
    while stack:
        # op_two is the operand
        op_two = stack.pop(0)

        if must_swap:
            # when op_one becomes the operand and op_two the operator
            # they must be swapped
            op_one, op_two = op_two, op_one
        must_swap = False

        if reset_both:
            # both ops are newly extracted
            op_one = op_two
            op_two = stack.pop(0)
        reset_both = False

        if op_one == "+":
            # op two must be a list
            op_one = plus_function(op_two)
        elif op_one == "++":
            # op two must be a list
            op_one = concat_function(op_two)
            if op_one.is_constant():
                must_swap = True
        else:
            # it must be a lambda
            # checks if exists an inner lambda that must be solved
            if not lambda_is_constant(op_one):
                # the algorithm cannot continue until the inner lambda has the result
                # case when inside a lambda is a list that has a computable lambda
                op_one = compute_inner_lambda(op_one)
            # lambda case
            op_one = lambda_function(op_one, op_two)
            # it can arrive as an Atom that contains a list
            if isinstance(op_one, Atom) and op_one.atom_type == "List":
                op_one = op_one.atom_value
            # or directly a Lista
            if isinstance(op_one, Lista):
                # if it's a constant list must swap
                if op_one.is_constant():
                    must_swap = True
                else:
                    # get the inner elements
                    new_stack = create_stack(op_one)
                    # add the inner elements first in the stack
                    while new_stack:
                        stack.insert(0, new_stack.pop())
                    if stack_is_constant(stack):
                        return create_constant_sublist(stack)
                    # reset is needed to start with a new op_one and op_two
                    reset_both = True
            # if its a number, a swap is needed
            if isinstance(op_one, Atom) and op_one.atom_type == "Number":
                must_swap = True
    # if the result is a str or an int, recreate is as an atom obj
    if isinstance(op_one, (str, int)):
        atom_node = Atom(None)
        atom_node.atom_type = "Number"
        if isinstance(op_one, str):
            if op_one.isdigit():
                atom_node.atom_type = "Number"
            else:
                atom_node.atom_type = "Id"
        atom_node.atom_value = str(op_one)
        op_one = atom_node

    return op_one
