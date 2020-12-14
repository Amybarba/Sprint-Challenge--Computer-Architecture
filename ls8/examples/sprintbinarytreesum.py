class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class SumOfNodes:
    def __init__(self):
        self.root = None;

    def calculate_sum(self, temp):
        sum = sum_right = sum_left = 0

        if self.root is None:
            print("Tree is empty")
            return 0
        else:
            if temp.left is not None:
                sum_left = self.calculate_sum(temp.left)

            if temp.right is not None:
                sum_right = self.calculate_sum(temp.right)

            sum = temp.data + sum_left + sum_right
            return sum


bt = SumOfNodes()
bt.root = Node(5)
bt.root.left = Node(2)
bt.root.right = Node(9)
bt.root.left.left = Node(1)
bt.root.right.left = Node(8)
bt.root.right.right = Node(6)

print("Sum of all nodes of binary tree: " + str(bt.calculate_sum(bt.root)))