from typing import Union
from sorting import iter_mergesort


class KDNode:
    point: list
    axis: int
    key: float
    left_child: Union['KDNode', None]
    right_child: Union['KDNode', None]

    def __init__(self, point, axis):
        self.point = point
        self.axis = axis
        self.key = point[axis]
        self.left_child = None
        self.right_child = None


def build_kd_tree(points: list, n_dimensions: int, depth: int = 0) -> Union['KDNode', None]:
    """ Builds a k-d tree using the median splitting strategy.

    Note: Assumes given list is already sorted.
    """

    n_elements = len(points)
    # If no points are given, child nodes should be nonexistent (=> None)
    if n_elements == 0:
        return None
    # Else, extend left and right branches recursively
    else:
        # Cycle through axes with every level drop
        axis = depth % n_dimensions
        points = iter_mergesort(points, axis)
        # The list is sorted, so the middle value is also the median of the
        # values in the list (for the given dimension). To build the tree from
        # the list, give the root node the median as key and recursively produce
        # the descendants from the rest of the values in the given list.
        mid_idx = int(n_elements / 2)
        root = KDNode(points[mid_idx], axis)
        root.left_child = build_kd_tree(points[:mid_idx], n_dimensions, depth + 1)
        root.right_child = build_kd_tree(points[mid_idx + 1:], n_dimensions, depth + 1)
        return root


def access(root: Union['KDNode', None], x: list, n_dimensions: int) -> Union["KDNode", None]:
    """ Standard search(x) in k-d Tree, also used to find a parent for a new node when inserting. """

    if root is None:
        print("Tree is empty")
        return None
    else:
        axis = 0
        next_is_leaf = False
        found = False
        parent = root
        # Walk down the tree cycling through axes
        while (not found) and (not next_is_leaf):
            if parent.key > x[axis]:
                if parent.left_child is not None:
                    parent = parent.left_child
                    axis = axis + 1 if axis + 1 < n_dimensions else 0
                else:
                    next_is_leaf = True
            elif parent.key < x[axis]:
                if parent.right_child is not None:
                    parent = parent.right_child
                    axis = axis + 1 if axis + 1 < n_dimensions else 0
                else:
                    next_is_leaf = True
            else:
                found = True
        return parent


def insert(root: Union['KDNode', None], x: list, n_dimensions: int) -> KDNode:
    """ Inserts new node with given coordinates to k-d tree specified by root. """

    parent = access(root, x, n_dimensions)
    if parent is None:
        # The tree is empty, create root node and return it
        root = KDNode(x, 0)
        return root
        # Note: It is expected that this function is not used
        # to build a tree from scratch, however we added the
        # code that returns the (new) tree root as a fail-safe
    else:
        # Insert x node as a child of parent, side is determined by axis value
        x_axis = parent.axis + 1 if parent.axis + 1 < n_dimensions else 0
        x_node = KDNode(x, x_axis)
        if x_node.key < parent.key:
            parent.left_child = x_node
        elif x_node.key > parent.key:
            parent.right_child = x_node
        # Else x already in tree, no duplicates allowed
        return root


def node_search(root: Union['KDNode', None], x: list, n_dimensions: int) -> bool:
    """ Searches k-d tree for a node with the exact coordinates given. """

    candidate = access(root, x, n_dimensions)
    if candidate.point == x:
        return True
    else:
        return False


def node_in_range(node: KDNode, range_min: list, range_max: list, n_dimensions: int) -> bool:
    """ Checks if a given node represents a point in [range_min, range_max]. """

    in_range = True
    for axis in range(n_dimensions):
        in_range &= node.point[axis] >= range_min[axis]
        in_range &= node.point[axis] <= range_max[axis]
    return in_range


def range_search(root: KDNode, range_min: list, range_max: list, n_dimensions: int, curr_axis: int = 0) -> list:
    """ Returns nodes that store points in [range_min, range_max] (multidimensional search). """

    if root is None:
        return []

    # Correct ranges
    for i in range(n_dimensions):
        if range_min[i] > range_max[i]:
            t = range_min[i]
            range_min[i] = range_max[i]
            range_max[i] = t

    # Examine root and descend accordingly
    new_axis = curr_axis + 1 if curr_axis + 1 < n_dimensions else 0
    if root.point[curr_axis] < range_min[curr_axis]:
        # Need to increase value, prune left subtree
        return range_search(root.right_child, range_min, range_max, n_dimensions, new_axis)
    elif root.point[curr_axis] > range_max[curr_axis]:
        # Need to decrease value, prune right subtree
        return range_search(root.left_child, range_min, range_max, n_dimensions, new_axis)
    elif node_in_range(root, range_min, range_max, n_dimensions):
        # Node is in range for all dimensions, report it and descend
        left_branch = range_search(root.left_child, range_min, range_max, n_dimensions, new_axis)
        right_branch = range_search(root.right_child, range_min, range_max, n_dimensions, new_axis)
        return left_branch + [root.point.copy()] + right_branch
    else:
        # Node is not in range, for all dimensions, just descend
        left_branch = range_search(root.left_child, range_min, range_max, n_dimensions, new_axis)
        right_branch = range_search(root.right_child, range_min, range_max, n_dimensions, new_axis)
        return left_branch + right_branch


def compare_for_min(a: KDNode, b: KDNode, axis) -> KDNode:
    """ Returns the one of the two nodes that stores the min value for the specified axis.

    NOTE: We assume that both nodes passed to this function are NOT None!

    """

    if a.point[axis] < b.point[axis]:
        return a
    else:
        return b


def find_min_node(root: KDNode, axis: int, n_dimensions: int):
    """ Returns the node which stores the min value for the specified axis. """

    if root is None:
        return root
    else:
        # If root axis is the desired one, search along left branch to find min
        if root.axis == axis:
            # Check if root is the lowest child of its branch, in which case
            # root contains the min value. Else, continue deeper into left branch
            if root.left_child is not None:
                return find_min_node(root.left_child, axis, n_dimensions)
            else:
                return root
        # Else both branches may contain the min value, continue searching
        else:
            left_candidate = find_min_node(root.left_child, axis, n_dimensions)
            right_candidate = find_min_node(root.right_child, axis, n_dimensions)
            # Let the comparisons begin...
            if left_candidate is None:
                if right_candidate is None:
                    # L, R are None
                    return root
                else:
                    # L is None, R is not None, compare R with root
                    return compare_for_min(root, right_candidate, axis)
            elif right_candidate is None:
                # L is not None, R is None, compare L with root
                return compare_for_min(root, left_candidate, axis)
            else:
                # L is not None, R is not None, compare all three
                branch_min = compare_for_min(left_candidate, right_candidate, axis)
                return compare_for_min(root, branch_min, axis)


def compare_for_max(a: KDNode, b: KDNode, axis) -> KDNode:
    """ Returns the one of the two nodes that stores the max value for the specified axis.

    NOTE: We assume that both nodes passed to this function are NOT None!

    """

    if a.point[axis] > b.point[axis]:
        return a
    else:
        return b


def find_max_node(root: KDNode, axis: int, n_dimensions: int):
    """ Returns the node which stores the max value for the specified axis."""

    if root is None:
        return root
    else:
        # If root axis is the desired one, search along right branch to find max
        if root.axis == axis:
            # Check if root is the lowest child of its branch, in which case
            # root contains the max value. Else, continue deeper into right branch
            if root.right_child is not None:
                return find_max_node(root.right_child, axis, n_dimensions)
            else:
                return root
        # Else both branches may contain the max value, continue searching
        else:
            left_candidate = find_max_node(root.left_child, axis, n_dimensions)
            right_candidate = find_max_node(root.right_child, axis, n_dimensions)
            # Let the comparisons begin...
            if left_candidate is None:
                if right_candidate is None:
                    # L, R are None
                    return root
                else:
                    # L is None, R is not None, compare R with root
                    return compare_for_max(root, right_candidate, axis)
            elif right_candidate is None:
                # L is not None, R is None, compare L with root
                return compare_for_max(root, left_candidate, axis)
            else:
                # L is not None, R is not None, compare all three
                branch_min = compare_for_max(left_candidate, right_candidate, axis)
                return compare_for_max(root, branch_min, axis)


def skyline_query_kdt(root: KDNode, n_dimensions: int) -> list:
    """ Computes the skyline of the points stored in the given k-d tree. """

    # First bounding box: left bound is x_min.
    # Right bound is: x_max[0] in the first dimension,
    # and for every other dimension the coordinate is
    # the min value of that dimension.
    x_min = find_min_node(root, 0, n_dimensions)
    x_max = find_max_node(root, 0, n_dimensions)
    left_bound = x_min.point.copy()
    right_bound = [x_max.point[0]]
    for i in range(1, n_dimensions):
        min_dim_node = find_min_node(root, i, n_dimensions)
        right_bound.append(min_dim_node.point[i])

    # Build set of skyline points
    # x_min is always the first point in the skyline
    skyline = [x_min.point.copy()]
    stop_flag = False
    while not stop_flag:
        target_box = range_search(root, list(left_bound), list(right_bound), n_dimensions)
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
        if left_bound[0] != target_box[1][0]:
            left_bound = target_box[1].copy()
        else:
            stop_flag = True
    return skyline
