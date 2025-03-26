# Dragon Flight
- Author: Ilja Ylikangas / ilpakka
- Event: [HTB Cyber Apocalypse CTF 2025: Tales from Eldoria](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)

## Details:

- **Category**: Coding
- **Description**: - 
- **Attachment**: None

### Overview:
In the mystical realm of the Floating Isles, your role as the **Dragon Flight Master** is to guide ancient dragons across flight paths affected by variable wind conditions. Missions:

1. **Updating wind conditions** for specific flight segments.
2. **Querying the maximum favorable flight stretch** within a given range.

## 1. Input Parsing
We begin by reading the number of flight segments and operations. The wind effects for each segment are stored as an array, where:
- Positive values represent tailwind (favorable conditions).
- Negative values represent headwind (unfavorable conditions).
```python
def main():
    input1 = input()
    input2 = input()
    inputs = [input().strip() for _ in range(int(input1.split()[1]))]

    n, q = map(int, input1.split())
    arr = list(map(int, input2.split()))
```
## 2. Segment Tree

The Segment Tree nodes store:
- **Total Sum**: The sum of all elements in the node's range.
- **Prefix Sum**: Maximum sum of a prefix subarray in the range.
- **Suffix Sum**: Maximum sum of a suffix subarray in the range.
- **Max Subarray Sum**: Maximum contiguous subarray sum in the range.

1. Update `U i x`: Modify the wind effect at index `i`
2. Query `Q l r`: Find the maximum contiguous flight strech within `[l, r]`.
```python
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
```
## 3. Processing
Let's process the quories as follows:
```python
def main():
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
```

## 4. Results and Flag
**Flight Path:**<br>
`8 4 -3 -9 4 -6 -3 5 2 4 U 1 -6 Q 2 6 Q 5 7 U 7 -8`<br>
**Journey Distance:**<br>
`5 7`<br>
**FLAG:** `HTB{DR4G0N_FL1GHT_5TR33_e550455d924c7282261887c42bdfdaeb}`
