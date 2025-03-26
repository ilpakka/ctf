# Dragon Fury
- Author: Ilja Ylikangas / ilpakka
- Event: [HTB Cyber Apocalypse CTF 2025: Tales from Eldoria](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)

## Details:

- **Category**: Coding
- **Description**: -
- **Attachment**: None

### Overview
The task is to find a valid combination of damage values from multiple rounds of attacks such that the sum of the selected values equals a given target damage. The input consists of a list of subarrays, each containing possible damage values for one round, and a target total damage.

## 1. Input Parsing
We use a recursive backtracking approach to explore all possible combinations of values from the subarrays. The key insight is that we need to select one number from each subarray and check if their sum matches the target. The algorithm ensures that there is exactly one valid combination.
- The input is given as a string that represents a list of subarrays. We use `ast.literal_eval()` to safely convert this input string into a list of lists (subarrays). We also read the target damage value.
```python
import ast

input_text = input()
target_damage = int(input())

damage_values = ast.literal_eval(input_text)
```

## 2. Recursive Search
A recursive function `helper()` explores all possible combinations by selecting one value from each subarray and checking if the sum matches the target damage.
- We start from the first subarray and try each possible value from it.
- For each selection, we recursively attempt to select values from the remaining subarrays.
- If we reach the last subarray and the sum matches the target damage, we return the current combination.
```python
def find_combination(damage_values, target_damage):
    def helper(index, current_combination, current_sum):
        if index == len(damage_values):
            if current_sum == target_damage:
                return current_combination
            else:
                return None
        
        for value in damage_values[index]:
            result = helper(index + 1, current_combination + [value], current_sum + value)
            if result:
                return result  
        return None
    return helper(0, [], 0)
```
The recursion ends when all subarrays have been considered. If the sum of the selected values equals the target, we return the valid combination.
```python
valid_combination = find_combination(damage_values, target_damage)

print(valid_combination)
```
## 3. Results and Flag
**Attack Options:**<br>
`[[7, 30, 8, 7], [20, 11, 15, 30], [25, 7, 10], [21, 11], [9, 29]] 76`<br>
**Battle Result:**<br>
`[8, 11, 7, 21, 29]`<br>
**FLAG:**<br> `HTB{DR4G0NS_FURY_SIM_C0MB0_a6456d2511876ba1479554986d7a98e8}`
