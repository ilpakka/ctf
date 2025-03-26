class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [None] * (4 * self.n)
        self.build(0, 0, self.n - 1, arr)

    def build(self, node, start, end, arr):
        if start == end:
            self.tree[node] = (arr[start], arr[start], arr[start], arr[start])
        else:
            mid = (start + end) // 2
            left = 2 * node + 1
            right = 2 * node + 2
            self.build(left, start, mid, arr)
            self.build(right, mid + 1, end, arr)
            self.tree[node] = self.merge(self.tree[left], self.tree[right])

    def merge(self, left, right):
        total = left[0] + right[0]
        prefix = max(left[1], left[0] + right[1])
        suffix = max(right[2], right[0] + left[2])
        max_subarray = max(left[3], right[3], left[2] + right[1])
        return (total, prefix, suffix, max_subarray)

    def update(self, node, start, end, idx, value):
        if start == end:
            self.tree[node] = (value, value, value, value)
        else:
            mid = (start + end) // 2
            left = 2 * node + 1
            right = 2 * node + 2
            if start <= idx <= mid:
                self.update(left, start, mid, idx, value)
            else:
                self.update(right, mid + 1, end, idx, value)
            self.tree[node] = self.merge(self.tree[left], self.tree[right])

    def query(self, node, start, end, l, r):
        if r < start or end < l:
            return (0, float('-inf'), float('-inf'), float('-inf'))
        if l <= start and end <= r:
            return self.tree[node]
        mid = (start + end) // 2
        left = 2 * node + 1
        right = 2 * node + 2
        left_result = self.query(left, start, mid, l, r)
        right_result = self.query(right, mid + 1, end, l, r)
        return self.merge(left_result, right_result)

def main():
    input1 = input()
    input2 = input()
    inputs = [input().strip() for _ in range(int(input1.split()[1]))]

    n, q = map(int, input1.split())
    arr = list(map(int, input2.split()))
    
    seg_tree = SegmentTree(arr)
    
    for operation in inputs:
        parts = operation.split()
        if parts[0] == 'U':
            i, x = int(parts[1]) - 1, int(parts[2])
            seg_tree.update(0, 0, n - 1, i, x)
        elif parts[0] == 'Q':
            l, r = int(parts[1]) - 1, int(parts[2]) - 1
            _, _, _, max_subarray = seg_tree.query(0, 0, n - 1, l, r)
            print(max_subarray)

if __name__ == "__main__":
    main()
