def merge(left: list, right: list, dim: int = 0) -> list:
    """ Merges two lists into one sorted lists.

    Given two lists of multidimensional points and a dimension,
    this function merges them into one list sorted by
    the coordinates of the specified dimension.

    """

    merged = []
    i = 0
    j = 0
    left_len = len(left)
    right_len = len(right)
    # Iterate over both arrays until one end is reached
    while i < left_len and j < right_len:
        # Sort items by the elements of the given dimension
        if left[i][dim] < right[j][dim]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    # Iterate over the points left in the longer array
    # (which at this point are already sorted)
    if i == left_len:
        while j < right_len:
            merged.append(right[j])
            j += 1
    else:
        while i < left_len:
            merged.append(left[i])
            i += 1
    # Merging is complete, return list
    return merged


def iter_mergesort(points: list, dim: int = 0) -> list:
    """ Iteratively splits a list into smaller lists in order to sort it.

    Given two lists, this function splits them into multiple
    sub-lists of growing size. This is an iterative version
    of the Mergesort split phase. The lists are then sorted
    by the merge function defined above, according to the
    coordinates of a specified dimension.

    """

    # Start with lists containing one element only, sort them
    # and continue the process with lists of double size, until
    # all of the points are sorted
    n = len(points)
    step = 1
    while step < n:
        i = 0
        while i < n:
            # Calculate indices of step-length sub-lists
            l_first = i
            l_last = l_first + step
            r_first = l_last
            r_last = l_first + (2 * step)
            if r_first > n:
                break
            elif r_last > n:
                r_last = n
            # Merge points to produce a sorted (sub-)list
            temp = merge(points[l_first:l_last], points[r_first:r_last], dim)
            # Update given list
            for j in range(r_last - l_first):
                points[i + j] = temp[j]

            i += 2 * step
        step *= 2
    # Return fully sorted list
    return points
