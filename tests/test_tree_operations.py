import pytest
from parser.parser import parse
from parser.tree_operations import find_node, replace_node, edit_node
from parser.ast_nodes import Cell, Function, Number


def construct_test_ast():
    # Construct an AST using parser.py for a sample formula
    # Example formula: SUM(A1, 5)
    ast = parse("SUM(A1, 5)")
    return ast


def test_find_node():
    ast = construct_test_ast()
    # Assuming the ID of "A1" Cell node is known (e.g., extracted after parsing)
    a1_id_history = ast.arguments[0].id_history

    # Find the node with this ID history
    found_node = find_node(ast, a1_id_history)
    assert isinstance(found_node, Cell)
    assert found_node.col == "A"
    assert found_node.row == 1


def test_edit_node():
    ast = construct_test_ast()
    a1_id_history = ast.arguments[0].id_history
    user_id = "test_user"

    # Edit the "A1" node to "B1"
    edited_node = edit_node(ast, a1_id_history, "B1", user_id)
    assert edited_node is not None

    # assert edited_node.col == 'B'
    # assert edited_node.row == 1

    assert edited_node.node_content == "B1"
    assert edited_node.user_id == user_id


def test_replace_node():
    ast = construct_test_ast()
    a1_id_history = ast.arguments[0].id_history

    # Create a new node to replace "A1"
    new_node = Cell("C", 3, "test_user")
    replace_result = replace_node(ast, a1_id_history, new_node)

    # Check if the replacement was successful
    assert replace_result

    # Find the replaced node in the AST using the new node's id_history
    replaced_node = find_node(ast, new_node.id_history)

    # Assertions to verify the replacement
    assert isinstance(replaced_node, Cell)
    assert replaced_node.col == "C"
    assert replaced_node.row == 3
    assert replaced_node.user_id == "test_user"
