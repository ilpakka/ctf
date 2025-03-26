# Summoners Incantation
- Author: Ilja Ylikangas / ilpakka
- Event: [HTB Cyber Apocalypse CTF 2025: Tales from Eldoria](https://ctf.hackthebox.com/event/details/cyber-apocalypse-ctf-2025-tales-from-eldoria-2107)

## Details:

- **Category**: Coding
- **Description**: - 
- **Attachment**: None

### Overview
We need to find the maximum sum of non-adjacent numbers from a list of integers. The key is that no two selected tokens (numbers) should be adjacent in the list, which adds a constraint on how we can select the tokens.

## 1. Tokens
We maintain two variables while iterating through the list:
- `include`: The maximum sum if we include the current token
- `exclude`: The maximum sum if we exclude the current token

For each token:
- The new `include` value is `exclude + current token`
- The new `exclude` value is `max(include, exclude)`

```python
input_text = input()

def max_energy(tokens):
    if not tokens:
        return 0
    
    include = 0
    exclude = 0
    
    for token in tokens:
        new_include = exclude + token
        new_exclude = max(include, exclude)
        include, exclude = new_include, new_exclude

    return max(include, exclude)
```
After processing all tokens the final result `max(include, exclude)` represents the best possible outcome by either including or excluding the last token.

## 3. Results and Flag
**Input**:<br>
`[18, 5, 17, 12, 7, 3, 20, 1]`<br>
**Output**:<br>
`62`<br>
**FLAG:** `HTB{SUMM0N3RS_INC4NT4T10N_R3S0LV3D_3fbc9d0f59ad60b75dea241f867bc8ff}`