def addPaddingToList(
    lst: list[int],
    padding: int,
    maxAllowedIndex: int
) -> list[int]:
    """
    Padding every element in the list with a certain amount
    of increments/decrements to the right/left of every element.

    Parameters:

    - `lst` - original list of indexes;
    - `padding` - how many new indexes to add to the left and right
    of every original list index;
    - `maxAllowedIndex` - there is actually a yet another list, for which
    this list is a subset of indexes, and we need to care not to pad more
    indexes to the right of the last element here.
    """
    paddedList: list[int] = []
    for i in lst:
        # pad to the left
        paddingIndex = 0
        leftPad: list[int] = []
        while paddingIndex > -padding and i + paddingIndex > 0:
            paddingIndex -= 1
            x = i + paddingIndex
            if x not in lst and x not in paddedList:
                leftPad.insert(0, x)
            else:
                break
        paddedList += leftPad
        paddedList.append(i)
        # pad to the right
        paddingIndex = 0
        rightPad: list[int] = []
        while paddingIndex < padding and i + paddingIndex < maxAllowedIndex:
            paddingIndex += 1
            x = i + paddingIndex
            if x not in lst and x not in paddedList:
                rightPad.append(x)
            else:
                break
        paddedList += rightPad
    return paddedList


incomingList = [2, 4, 11, 19, 21, 30]
print(incomingList)

paddedList = addPaddingToList(
    incomingList,
    3,
    32
)
print(paddedList)
