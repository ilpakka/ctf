# GPN CTF 2026 - specCTF

## Info
- **Flag:** `GPNCTF{ThiS_m341_IS_SpeCuL47iVElY_D3LICioUs!!!!}`

## Analysis

The challenge binary pretends to validate the flag through a Spectre/cache-timing side channel. In reality, the important logic is a normal 64-bit hash comparison:

```c
hashy(user_chunk) == ENC[i]
```

The input is processed in 8-byte chunks. The binary contains six 64-bit target values in a global array called `ENC`, meaning the correct flag is 6 × 8 = 48 bytes long.

The hash function is reversible because it only uses:

1. XOR with a shifted copy of itself,
2. multiplication by an odd 64-bit constant, and
3. XOR with a fixed constant.

By reversing the hash for each value in `ENC`, we recover the flag directly without brute force.

## Extracting the challenge

After extracting the archive, there is only one interesting file:

```bash
tar -xzf specctf.tar.gz
cd specctf
file specCTF
```

Output:

```text
specCTF: ELF 64-bit LSB pie executable, x86-64, dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=0b002e82c00ea825a7f1bc2e037109224e93d879, for GNU/Linux 3.2.0, not stripped
```

The important part is that the binary is **not stripped**. That gives us useful symbol names:

```bash
nm -C specCTF | grep -E 'main|hashy|ENC|specte|specEnvTime'
```

Relevant symbols:

```text
00000000000070c0 D ENC
0000000000001c07 T specte_byte(unsigned long, int)
0000000000001363 T specEnvTime(unsigned long, int)
0000000000001239 t hashy(unsigned long)
0000000000001d3a T main
```

The names already suggest the intended theme: `specte_byte`, `specEnvTime`, and other cache/timing-related helper functions.

## First look at `main`

Disassembling `main` shows the program repeatedly checks the provided argument. The relevant logic is:

```asm
call strlen
and eax, 0x7
test rax, rax
je valid_length
puts "NOPE"
exit
```

So the input length must be divisible by 8.

Later, the binary loops over the input in 8-byte chunks:

```asm
lea rax, [rip+0x52e8]        # ENC
mov rax, QWORD PTR [rdx+rax] # ENC[i]
mov r15, rax                 # expected hash

mov rax, QWORD PTR [input + i*8]
mov r14, rax                 # user-controlled 8-byte chunk

call specte_byte
```

The important detail is that before calling `specte_byte`, the program stores:

- `r15 = ENC[i]`
- `r14 = current 8-byte input chunk`

This is slightly unusual because the check is hidden through global register state instead of being passed cleanly as normal arguments.

The result of `specte_byte` is added into a counter. If every chunk appears correct, the program increments a confidence counter. If not, it decrements it. Once the confidence counter is greater than 2, it prints `CORRECT`.

This repeated voting is likely there because the side-channel timing classification can be noisy.

## The Spectre-style wrapper

The challenge uses a side-channel themed wrapper to hide a normal boolean comparison.

Inside `specEnvTime`, we find the real check:

```asm
mov rax, r14
mov rdi, rax
call hashy

mov rdx, r15
cmp rax, rdx
sete al
```

In C-like pseudocode, the important part is:

```c
if (hashy(r14) == r15) {
    access arr2[0x2800];
} else {
    access arr2[0xa200];
}
```

So the cache-timing machinery is only used to classify whether the branch used the "true" cache line or the "false" cache line.

For solving the challenge, we do not need to reproduce the side channel. We can ignore the timing wrapper and solve the real condition directly:

```c
hashy(input_chunk) == ENC[i]
```

## Dumping the table

The global symbol `ENC` is located in `.data` at virtual address `0x70c0`:

```bash
nm -C specCTF | grep ENC
```

```text
00000000000070c0 D ENC
```

Dumping the `.data` section shows the six 64-bit values:

```bash
objdump -s -j .data specCTF
```

Relevant bytes:

```text
70c0 e57571b9 b94d27d4 4a27ef71 774591bc
70d0 f23d8c3b c87cb972 a13bdc3a be1a2e7f
70e0 1f56f457 516a083e 1fe88de8 3d210af4
```

Because this is a little-endian x86-64 binary, these become the following 64-bit integers:

```python
ENC = [
    0xd4274db9b97175e5,
    0xbc91457771ef274a,
    0x72b97cc83b8c3df2,
    0x7f2e1abe3adc3ba1,
    0x3e086a5157f4561f,
    0xf40a213de88de81f,
]
```

There are six entries, so the expected input is six 8-byte chunks:

```text
6 * 8 = 48 bytes
```

## Reversing the hash function

The function `hashy` is short:

```asm
0000000000001239 <hashy(unsigned long)>:
    mov    rax, QWORD PTR [rbp-0x8]
    shr    rax, 0x21
    xor    QWORD PTR [rbp-0x8], rax

    mov    rax, QWORD PTR [rbp-0x8]
    movabs rdx, 0xf451af975d152cad
    imul   rax, rdx
    mov    QWORD PTR [rbp-0x8], rax

    mov    rax, QWORD PTR [rbp-0x8]
    shr    rax, 0x21
    xor    QWORD PTR [rbp-0x8], rax

    movabs rax, 0xc2ceaade1a351c23
    xor    QWORD PTR [rbp-0x8], rax

    mov    rax, QWORD PTR [rbp-0x8]
    shr    rax, 0x21
    xor    QWORD PTR [rbp-0x8], rax
```

Translated to Python/C-like pseudocode:

```python
MASK = (1 << 64) - 1

C = 0xf451af975d152cad
K = 0xc2ceaade1a351c23

def hashy(x):
    x ^= x >> 33
    x &= MASK
    x *= C
    x &= MASK
    x ^= x >> 33
    x &= MASK
    x ^= K
    x &= MASK
    x ^= x >> 33
    x &= MASK
    return x
```

At first glance this looks like a one-way hash, but it is actually reversible.

### Hash is reversible, but why?

The operation:

```python
x ^= x >> 33
```

is reversible on 64-bit integers. Since the shift is 33 bits, applying the same operation again recovers the original value:

```python
def unxor_shift_33(y):
    return y ^ (y >> 33)
```

The multiplication is also reversible modulo `2^64` because the multiplier is odd:

```python
C = 0xf451af975d152cad
```

Any odd number has a modular inverse modulo `2^64`, so we can compute:

```python
INV_C = pow(C, -1, 1 << 64)
```

Then multiplication by `C` can be undone by multiplication with `INV_C`.

The XOR with the fixed constant is trivially reversible because XOR is its own inverse:

```python
x ^= K
```

Therefore, to invert `hashy`, we simply undo the operations in reverse order.

## The solver

Final solve script:

```python
import struct

MASK = (1 << 64) - 1

C = 0xf451af975d152cad
K = 0xc2ceaade1a351c23
INV_C = pow(C, -1, 1 << 64)

ENC = [
    0xd4274db9b97175e5,
    0xbc91457771ef274a,
    0x72b97cc83b8c3df2,
    0x7f2e1abe3adc3ba1,
    0x3e086a5157f4561f,
    0xf40a213de88de81f,
]

def unxor_shift_33(y):
    return (y ^ (y >> 33)) & MASK

def invert_hash(y):
    # Undo final: x ^= x >> 33
    x = unxor_shift_33(y)

    # Undo: x ^= K
    x ^= K
    x &= MASK

    # Undo middle: x ^= x >> 33
    x = unxor_shift_33(x)

    # Undo: x *= C modulo 2^64
    x = (x * INV_C) & MASK

    # Undo first: x ^= x >> 33
    x = unxor_shift_33(x)

    return x

flag = b"".join(struct.pack("<Q", invert_hash(x)) for x in ENC)
print(flag.decode())
```

Running it:

```bash
python3 solve.py
```

Output:

```text
GPNCTF{ThiS_m341_IS_SpeCuL47iVElY_D3LICioUs!!!!}
```

## Chunk-by-chunk recovery

The recovered 8-byte chunks are:

```text
0: GPNCTF{T
1: hiS_m341
2: _IS_SpeC
3: uL47iVEl
4: Y_D3LICi
5: oUs!!!!}
```

Joining them gives:

```text
GPNCTF{ThiS_m341_IS_SpeCuL47iVElY_D3LICioUs!!!!}
```

## So, the final flag is

```text
GPNCTF{ThiS_m341_IS_SpeCuL47iVElY_D3LICioUs!!!!}
```
