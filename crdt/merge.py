from parser.ast_nodes import (Binary, Cell, CellRange, Function, Name, Number,
                              Unary)

from crdt.apply_changes import add_child, find_node, remove_child, replace_node


class NodeNotFoundError(Exception):
    pass


def merge_ast(original_ast, changes):
    def calculate_depth(original_history, updated_history):
        last_common_index = -1
        for i in range(min(len(original_history), len(updated_history))):
            if original_history[i] == updated_history[i]:
                last_common_index = i
            else:
                break

        # Calculate depth based on lengths after the last common ID
        if last_common_index != -1:
            return len(updated_history) - last_common_index - 1
        return -1  # No common history found

    for change in changes:
        # Handle modifications

        if change["type"] == "modification":
            modified_node = change["node"]
            original_node = find_node(original_ast, modified_node.id_history)

            # print("Modified node ID history: ", modified_node.id_history)
            # print("Original node ID history: ", original_node.id_history)

            if not original_node:
                raise NodeNotFoundError("Node not found in original AST")

            # Enhanced conflict resolution for CellRange nodes
            if isinstance(original_node, CellRange) and isinstance(
                modified_node, CellRange
            ):
                merged_range = merge_cell_ranges(original_node, modified_node)
                replace_node(original_node, merged_range, user_id="merged")
                continue

            depth = calculate_depth(original_node.id_history, modified_node.id_history)

            if depth > 0:
                replace_node(original_node, modified_node, user_id="merged")
            elif depth == 0:
                winner = conflict_resolution(
                    original_node, modified_node
                )  # Placeholder for conflict resolution logic

                if winner == modified_node:
                    replace_node(original_node, modified_node, user_id="merged")

        elif change["type"] == "addition_arg":
            node_to_add = find_node(original_ast, change["parent"].id_history)
            child_node = change["node"]
            user = change["node"].user_id
            if node_to_add is None:
                raise Exception("Parent node not found in original AST")
            add_child(node_to_add, child_node, user_id=user)

        elif change["type"] == "deletion_arg":
            node_to_remove = find_node(original_ast, change["parent"].id_history)
            child_node = change["node"]
            if node_to_remove is None:
                raise Exception("Parent node not found in original AST")
            remove_child(node_to_remove, child_node)

        else:
            raise Exception("Invalid change type")

    return original_ast


def merge_cell_ranges(node1, node2):
    start_row = min(node1.start.row, node2.start.row)
    end_row = max(node1.end.row, node2.end.row)
    start_col = min(
        node1.start.col, node2.start.col, key=lambda x: col_name_to_number(x)
    )
    end_col = max(node1.end.col, node2.end.col, key=lambda x: col_name_to_number(x))

    # Creating the merged range
    merged_range = CellRange(
        Cell(start_col, start_row, user_id="merged"),
        Cell(end_col, end_row, user_id="merged"),
        user_id="merged",
    )

    return merged_range


def col_name_to_number(col):
    number = 0
    for char in col:
        number = number * 26 + (ord(char.upper()) - ord("A") + 1)
    return number


def conflict_resolution(original_node, updated_node):
    # Placeholder function for conflict resolution
    # Implement conflict resolution logic here

    # compare timestamps

    if original_node.timestamp > updated_node.timestamp:
        # original_node commited later
        return updated_node
    elif original_node.timestamp < updated_node.timestamp:
        # updated_node is more recent
        return original_node
    else:
        pass
