#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Sequence

from asgiref.sync import sync_to_async

from src.common.enums import BuildTreeType
from src.utils.serializers import RowData, select_list_serialize


async def get_tree_nodes(row: Sequence[RowData]) -> list[dict[str, Any]]:
    """Get all tree structure nodes"""
    tree_nodes = await select_list_serialize(row)
    tree_nodes.sort(key=lambda x: x['sort'])
    return tree_nodes


@sync_to_async
def traversal_to_tree(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Construct a tree structure using traversal algorithm

    :param nodes: List of nodes to build the tree from
    :return: Tree structure as a list of dictionaries
    """
    tree = []
    node_dict = {node['id']: node for node in nodes}

    for node in nodes:
        parent_id = node['parent_id']
        if parent_id is None:
            tree.append(node)
        else:
            parent_node = node_dict.get(parent_id)
            if parent_node is not None:
                if 'children' not in parent_node:
                    parent_node['children'] = []
                parent_node['children'].append(node)

    return tree


async def recursive_to_tree(nodes: list[dict[str, Any]], *, parent_id: int | None = None) -> list[dict[str, Any]]:
    """
    Construct a tree structure using recursive algorithm

    :param nodes: List of nodes to build the tree from
    :param parent_id: ID of the parent node
    :return: Tree structure as a list of dictionaries
    """
    tree = []
    for node in nodes:
        if node['parent_id'] == parent_id:
            child_node = await recursive_to_tree(nodes, parent_id=node['id'])
            if child_node:
                node['children'] = child_node
            tree.append(node)
    return tree


async def get_tree_data(
    row: Sequence[RowData], build_type: BuildTreeType = BuildTreeType.traversal, *, parent_id: int | None = None
) -> list[dict[str, Any]]:
    """
    Get tree structure data

    :param row: Sequence of row data
    :param build_type: Type of algorithm to use for building the tree
    :param parent_id: ID of the parent node
    :return: Tree structure as a list of dictionaries
    """
    nodes = await get_tree_nodes(row)
    match build_type:
        case BuildTreeType.traversal:
            tree = await traversal_to_tree(nodes)
        case BuildTreeType.recursive:
            tree = await recursive_to_tree(nodes, parent_id=parent_id)
        case _:
            raise ValueError(f'Invalid algorithm type: {build_type}')
    return tree
