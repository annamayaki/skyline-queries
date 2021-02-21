from typing import Union
from sorting import iter_mergesort


class RangeNode:
    key: float
    point: list
    left_child: Union['RangeNode', None]
    right_child: Union['RangeNode', None]
    predecessor: Union['RangeNode', None]
    successor: Union['RangeNode', None]
    subtree_root: Union['RangeNode', None]

    def __init__(self, point, dimension):
        self.point = point
        self.key = point[dimension]
        self.left_child = None
        self.right_child = None
        self.predecessor = None
        self.successor = None
        self.subtree_root = None


def link_leaves(root: Union['RangeNode', None], points: list, dimension: int):
    previous = access(root, points[0][dimension])
    for i in range(1, len(points)):
        current = access(root, points[i][dimension])
        previous.successor = current
        current.predecessor = previous
        previous = current


def build_bbst(points: list, dimension: int, n_dimensions: int) -> Union['RangeNode', None]:
    """ Iteratively builds a Range tree from a (sorted) list of points.

    This function implements a standard iterative BBST
    (Balanced Binary Search Tree) construction from a
    list of sorted points. The tree may be nested inside
    of a tree node, in accordance with the definition of
    a multidimensional Range tree. The nesting level is
    controlled by the dimension-related arguments passed.

    """

    n_elements = len(points)
    # If no points are given, child nodes should be nonexistent (=> None)
    if n_elements == 0:
        return None
    # Else, extend left and right branches recursively
    else:
        # The list is sorted, so the middle value is also the median of the
        # values in the list (for the given dimension). To build the BBST of
        # the list, give the root node the median as key and recursively produce
        # the descendants from the rest of the values in the given list.
        mid_idx = int(n_elements / 2)
        root = RangeNode(points[mid_idx], dimension)
        root.left_child = build_bbst(points[:mid_idx], dimension, n_dimensions)
        root.right_child = build_bbst(points[mid_idx + 1:], dimension, n_dimensions)
        link_leaves(root, points, dimension)
        # Extend the tree into the next dimension, if needed
        if dimension + 1 < n_dimensions:
            points = iter_mergesort(points, dimension + 1)
            root.subtree_root = build_bbst(points, dimension + 1, n_dimensions)
        # Only the root of the BBST is needed (for identification purposes)
        return root


def access(root: Union["RangeNode", None], x: float) -> Union["RangeNode", None]:
    """ Standard BST search(x), also used to find a parent for a new node when inserting """

    if root is None:
        print("Tree is empty")
        return None
    else:
        parent = root
        found = False
        next_is_leaf = False
        while (not found) and (not next_is_leaf):
            if parent.key > x:
                if parent.left_child is not None:
                    parent = parent.left_child
                else:
                    next_is_leaf = True
            elif parent.key < x:
                if parent.right_child is not None:
                    parent = parent.right_child
                else:
                    next_is_leaf = True
            else:
                found = True
        return parent


def node_search(root: RangeNode, x: list, n_dimensions: int) -> bool:
    """ Searches Range tree for a node with the exact coordinates given """

    i = 0
    flag = True
    temp = root
    while (i < n_dimensions) and flag:
        temp = access(temp, x[i])
        if temp.key == x[i]:
            temp = temp.subtree_root
            i += 1
        else:
            flag = False
    return flag


def lca(current: Union["RangeNode", None], a: RangeNode, b: RangeNode) -> Union["RangeNode", None]:
    """ Iteratively searches for the lowest common ancestor of two given nodes (split node).

    This function traverses any one-dimensional BST, and
    thus can be used for any one dimension of a Range tree.

    """

    if current is None:
        return None
    elif current.key > a.key and current.key > b.key:
        return lca(current.left_child, a, b)
    elif current.key < a.key and current.key < b.key:
        return lca(current.right_child, a, b)
    else:
        return current


def inorder_traversal(root: Union["RangeNode", None], discovered: list):
    """ Standard inorder traversal of a BST. """

    if root is not None:
        inorder_traversal(root.left_child, discovered)
        discovered.append(root)
        inorder_traversal(root.right_child, discovered)


def range_search_1d(root: RangeNode, range_min: list, range_max: list, dimension: int) -> list:
    """ Basic function of a one-dimensional Range tree. """

    # Search for the nodes closest to the range bounds
    if range_min[dimension] > range_max[dimension]:
        temp = range_min
        range_min = range_max
        range_max = temp
    a = access(root, range_min[dimension])
    b = access(root, range_max[dimension])
    while a.predecessor is not None and a.predecessor.point[dimension] >= range_min[dimension]:
        a = a.predecessor
    while b.successor is not None and b.successor.point[dimension] <= range_max[dimension]:
        b = b.successor

    # Traverse the leaves of the tree between a and b and keep the ones in range
    current = a
    results = []
    while current is not None and current != b:
        if current.point[dimension] >= range_min[dimension]:
            results.append(current)
        current = current.successor
    if b.point[dimension] >= range_min[dimension]:
        results.append(b)
    return results


def range_search_kd(root: RangeNode, range_min: list, range_max: list, n_dimensions: int) -> list:
    """ Extension of the one-dimensional range search in multiple dimensions. """

    # Correct ranges
    for i in range(n_dimensions):
        if range_min[i] > range_max[i]:
            t = range_min[i]
            range_min[i] = range_max[i]
            range_max[i] = t

    # Search in tree of every dimension, starting at 1
    nodes = range_search_1d(root, range_min.copy(), range_max.copy(), 0)
    i = 1
    while i < n_dimensions:
        temp = []
        for current in nodes:
            for element in range_search_1d(current.subtree_root, range_min.copy(), range_max.copy(), i):
                if element not in temp:
                    temp.append(element)
        if not temp:
            # Unsuccessful, return []
            return temp
        else:
            # Successful so far, continue in next dimension
            nodes = temp.copy()
            i += 1

    # Successful, return points in nodes
    results = []
    for x in nodes:
        # Some edge cases require extra filtering
        in_range = True
        for dimension in range(n_dimensions):
            in_range &= x.point[dimension] >= range_min[dimension]
            in_range &= x.point[dimension] <= range_max[dimension]
        if in_range and x.point not in results:
            results.append(x.point)
    return results


def find_min_node(root: RangeNode) -> RangeNode:
    """ Returns the leftmost node of the tree, which stores the min value. """

    while root.left_child is not None:
        root = root.left_child
    return root


def find_max_node(root: RangeNode) -> RangeNode:
    """ Returns the rightmost node of the tree, which stores the max value. """

    while root.right_child is not None:
        root = root.right_child
    return root


def skyline_query_rt(root: RangeNode, n_dimensions: int) -> list:
    """ Computes the skyline of the points stored in the given Range tree. """

    # First bounding box: left bound is x_min.
    # Right bound is: x_max[0] in the first dimension,
    # and for every other dimension the coordinate is
    # the min value of that dimension.
    x_min = find_min_node(root)
    x_max = find_max_node(root)
    left_bound = x_min.point.copy()
    right_bound = [x_max.point[0]]
    dimension_root = root.subtree_root
    for i in range(1, n_dimensions):
        min_dim_node = find_min_node(dimension_root)
        right_bound.append(min_dim_node.point[i])
        dimension_root = dimension_root.subtree_root

    # Build set of skyline points
    # x_min is always the first point in the skyline
    skyline = [x_min.point.copy()]
    stop_flag = False
    while not stop_flag:
        target_box = range_search_kd(root, list(left_bound), list(right_bound), n_dimensions)
        n_points = len(target_box)
        if n_points == 0:
            return skyline
        elif n_points == 1:
            skyline.append(target_box[0].copy())
            return skyline
        # Sort the points in the bounding box.
        # Then, the first point in the range (after the left bound)
        # is the next point of the skyline set.
        target_box = iter_mergesort(list(target_box))
        skyline.append(target_box[1].copy())
        # Check if we have reached the end of the x axis
        if left_bound[0] < target_box[1][0]:
            left_bound = target_box[1].copy()
        else:
            stop_flag = True
    return skyline
