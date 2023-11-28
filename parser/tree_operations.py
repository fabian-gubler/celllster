import uuid

# Assuming that BaseNode and its derived classes are defined in ast_nodes.py
from parser.ast_nodes import BaseNode, Function, Binary, Unary


def find_node(root, target_history):
    # Check for the longest common prefix in the history
    common_length = min(len(root.id_history), len(target_history))
    if root.id_history[:common_length] == target_history[:common_length]:
        return root

    # Recursive search in composite nodes
    if isinstance(root, Function):
        for arg in root.arguments:
            result = find_node(arg, target_history)
            if result:
                return result

    if isinstance(root, Binary):
        left_result = find_node(root.left, target_history)
        if left_result:
            return left_result

        right_result = find_node(root.right, target_history)
        if right_result:
            return right_result

    if isinstance(root, Unary):
        return find_node(root.expr, target_history)

    return None


def find_parent_and_child(root, child_history, parent=None):
    if isinstance(root, BaseNode):
        if root.id_history == child_history:
            return (parent, root)

    if isinstance(root, Function):
        for arg in root.arguments:
            result = find_parent_and_child(arg, child_history, root)
            if result[1]:
                return result

    if isinstance(root, Binary):
        left_result = find_parent_and_child(root.left, child_history, root)
        if left_result[1]:
            return left_result
        right_result = find_parent_and_child(root.right, child_history, root)
        if right_result[1]:
            return right_result

    if isinstance(root, Unary):
        return find_parent_and_child(root.expr, child_history, root)

    return (None, None)


from copy import deepcopy


def edit_node(node, target_history, new_content, user_id):
    node_to_edit = find_node(node, target_history)
    if node_to_edit:
        new_node = deepcopy(node_to_edit)
        new_node.update_content(new_content, user_id)
        # new_node.id_history.append(str(uuid.uuid4()))  # Add new ID to history
        return new_node
    return None


def replace_node(root, target_history, new_node):
    parent, child_to_replace = find_parent_and_child(root, target_history)
    if parent and child_to_replace:
        if isinstance(parent, Function):
            parent.arguments = [
                new_node if child is child_to_replace else child
                for child in parent.arguments
            ]
        elif isinstance(parent, Binary):
            if parent.left is child_to_replace:
                parent.left = new_node
            elif parent.right is child_to_replace:
                parent.right = new_node
        elif isinstance(parent, Unary):
            if parent.expr is child_to_replace:
                parent.expr = new_node
        new_node.id_history = child_to_replace.id_history + [str(uuid.uuid4())]
        return True
    return False