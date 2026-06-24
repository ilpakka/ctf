# GPN CTF 2026 -  my-favorite-ingredient

## Flag

```text
GPNCTF{jusT_onE_onstrUc71oNs_1s_4ll_yOU_N3eD_MAYB3123979AFKfnDh}
```

## Summary

Linux ELF binary, a 64-character flag checker. The checker looks complicated because it uses AVX/AVX512-style vectorized code and a large matrix operation but the core logic goes:

1. Require exactly 64 input characters
2. Apply a byte transform to the input
3. Run a matrix-vector multiplication routine
4. Compare the 64-byte result against the bitwise inverse of a 64-byte target stored in `.rodata`

The trick is that two byte transforms cancel each other out so the matrix routine effectively receives the original input bytes.

---

## Beginning

Extracting the archive and checking

```text
my-favorite-ingredient: ELF 64-bit LSB pie executable, x86-64, dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=10a1203f0e16b31de5978eade28ea29108f9615b, for GNU/Linux 3.2.0, not stripped
5b4f94ebfc2596a1543c937dd17970bf0cdf5f496aefc9b1b328dbeca0439930  my-favorite-ingredient
```

Running it without arguments shows the expected usage:

```bash
./my-favorite-ingredient
```

```text
Usage: ./my-favorite-ingredient <flag>
```

Wrong input test shows:

```text
Flag must be 64 characters long.
```

So we know that the checker expects exactly **64 characters**.

---

## Symbols

The binary is not stripped -> cool, so reverse engineering is a tad easier.

```bash
nm -C my-favorite-ingredient
```

Some interesting stuff pops out:

```text
0000000000001170 T verify_flag
00000000000015b0 t matvec_mul_vectorized
0000000000006c00 T main
0000000000006cf0 t matvec_mul_bitslice
00000000000321b0 r row_order
```

The important functions are:

| Function | Purpose |
| :------------ | :----------- |
| `main` | Checks argument count and length, copies constants from `.rodata`, calls `verify_flag` |
| `verify_flag` | Performs the input pre-transform, calls the matrix-vector routine, compares output to target |
| `matvec_mul_vectorized` | Large vectorized matrix-vector multiplication routine |

---

## The Main

The relevant part of `main` does three important things:

```asm
0000000000006c00 <main>:
    6c18: call   strlen@plt
    6c1d: cmp    rax,0x40
    6c21: jne    wrong_length

    ; copy user input to stack
    6c27: vmovups zmm0,ZMMWORD PTR [rbx]
    6c2d: vmovups ZMMWORD PTR [rsp+0x40],zmm0

    ; copy 4096-byte matrix from .rodata
    6c35: lea    rsi,[rip+0x2a534]        # 0x31170
    6c44: mov    edx,0x1000
    6c4f: call   memcpy@plt

    ; copy 64-byte target from .rodata
    6c54: vmovups zmm0,ZMMWORD PTR [rip+0x2b512] # 0x32170
    6c5e: vmovups ZMMWORD PTR [rsp],zmm0

    ; verify_flag(input, 64, matrix, target)
    6c78: call   verify_flag
```

From this we can pretty much make out the layout:

| Address | Size | What is it |
|:------------ |:----- |:--------------|
| `0x31170` | `0x1000` bytes | lookup data |
| `0x32170` | `0x40` bytes | Target bytes |

The exact call goes:

```c
verify_flag(input, 64, matrix, target);
```

---

## `verify_flag` analysis

At the start of `verify_flag` the length is checked again:

```asm
1172: cmp esi,0x40
1175: jne fail
```

Then the input bytes are transformed with vector instructions. Visible in `.rodata`:

```text
0x31020: c5 00 c5 00 c5 00 ...
0x31040: ff 00 ff 00 ff 00 ...
0x31060: 65 65 65 65 65 65 ...
```

This corresponds to the byte operation:

```c
y = (0xc5 * x + 0x65) & 0xff;
```

Or decimal:

```c
y = (197 * x + 101) mod 256;
```

After transforming all 64 bytes `verify_flag` calls:

```asm
1204: call matvec_mul_vectorized
```

Immediately after the matrix-vector routine returns, the output buffer is compared byte by byte against the bitwise inverse of the stored target:

```asm
1209: mov    cl,BYTE PTR [rbx]
120b: not    cl
120f: cmp    BYTE PTR [rsp],cl
```

This pattern repeats for all 64 bytes.

So we know that the final condition is:

```c
output[i] == (~target[i] & 0xff)   for i = 0..63
```

---

## The important cancellation

Inside `matvec_mul_vectorized`, the first operation performed on each input byte is another affine byte transform:

```asm
15c3: movzx  eax,BYTE PTR [rsi]
15c6: lea    ecx,[rax+rax*2]
15c9: lea    eax,[rax+rcx*4]
15cc: add    al,0xdf
```

The two `lea` instructions compute:

```text
ecx = 3*x
eax = x + 4*ecx = x + 12*x = 13*x
```

So this second transform is:

```c
z = (13 * y + 0xdf) & 0xff;
```

Substituting the earlier transform from `verify_flag`:

```text
y = 197*x + 0x65 mod 256
z = 13*y + 0xdf mod 256
```

Now simplify:

```text
13 * 197 = 2561 ≡ 1 mod 256
13 * 0x65 + 0xdf = 13 * 101 + 223 = 1536 ≡ 0 mod 256
```

So:

```text
z = x mod 256
```

This means the scary-looking pair of transforms cancels out. The matrix routine ultimately operates on the original input bytes.

---

## Checker reduction

After reversing the control flow, the checker can be modeled as:

```c
bool verify(char input[64]) {
    uint8_t matrix[4096] = rodata[0x31170:0x32170];
    uint8_t target[64]   = rodata[0x32170:0x321b0];

    uint8_t output[64];
    matvec_mul_vectorized(input, matrix, output);

    for (int i = 0; i < 64; i++) {
        if (output[i] != ((~target[i]) & 0xff)) {
            return false;
        }
    }

    return true;
}
```

So the target output vector is:

```python
wanted = bytes((~b) & 0xff for b in target)
```

The remaining task is solving for the 64-byte input that makes the matrix-vector routine produce `wanted`.

---

## Matrix Relation Dynamically

The function name `matvec_mul_vectorized` is accurate: the check is a matrix-vector style operation.
The implementation is very heavily optimized and unrolled, so reading it instruction by instruction is noisy.

A practical way to solve it is to treat `matvec_mul_vectorized` as an oracle:

1. Run the binary under a debugger.
2. Break immediately after the call to `matvec_mul_vectorized`.
3. Dump the 64-byte output buffer from the stack.
4. Repeat with controlled inputs.
5. Reconstruct the affine system.
6. Solve for the input that gives the wanted output.

The breakpoint location is `verify_flag + 0x99`, because:

```text
verify_flag = 0x1170
call matvec_mul_vectorized is at 0x1204
next instruction is at 0x1209
0x1209 - 0x1170 = 0x99
```

At that point, the matrix output is stored at `$rsp`.

on GDB:

```gdb
set pagination off
set args AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
start
break *verify_flag+0x99
continue
dump memory out.bin $rsp $rsp+0x40
quit
```

`out.bin` then contains the 64-byte output for that chosen input.

---

## Constructing the solver script

I used a byte-level affine solve:

```text
F(input) = output
```

Pick a base input:

```text
base = "A" * 64
```

Dump:

```text
F(base)
```

Then for each position `i`, change only that byte from `A` to `B` and dump:

```text
F(base with byte i changed by +1)
```

The difference gives one coefficient column of the byte-level system:

```text
column_i = F(base + e_i) - F(base) mod 256
```

Then solve:

```text
C * delta = wanted - F(base) mod 256
```

Finally:

```text
flag = base + delta mod 256
```

Behold the 64-byte flag.

---

## Solver

The following script shows the method. It uses GDB as the output oracle and solves the recovered modular system.

```python
#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import tempfile

BIN = Path("./my-favorite-ingredient").resolve()
FLAG_LEN = 64
VERIFY_AFTER_MATVEC = "*verify_flag+0x99"


def run_and_dump_output(candidate: bytes) -> bytes:
    """Run the binary in GDB and dump the 64-byte matvec output."""
    assert len(candidate) == FLAG_LEN

    # The probing inputs used here are printable and contain no spaces,
    # so passing them through `set args` is fine.
    arg = candidate.decode("latin-1")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out_file = td / "out.bin"
        gdb_file = td / "script.gdb"

        gdb_file.write_text(f"""
set pagination off
set confirm off
file {BIN}
set args {arg}
start
break {VERIFY_AFTER_MATVEC}
continue
dump memory {out_file} $rsp $rsp+0x40
quit
""")

        subprocess.run(
            ["gdb", "-q", "-batch", "-x", str(gdb_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        return out_file.read_bytes()


def inv_mod_256(x: int) -> int:
    """Inverse modulo 256. Only odd numbers are invertible modulo 256."""
    x &= 0xff
    if x % 2 == 0:
        raise ValueError(f"non-invertible pivot modulo 256: {x:#x}")
    return pow(x, -1, 256)


def solve_mod_256(A, b):
    """Gaussian elimination modulo 256 for a 64x64 system."""
    n = len(b)
    M = [row[:] + [b[i] & 0xff] for i, row in enumerate(A)]

    row = 0
    pivots = []

    for col in range(n):
        pivot = None
        for r in range(row, n):
            if M[r][col] & 1:
                pivot = r
                break

        if pivot is None:
            continue

        M[row], M[pivot] = M[pivot], M[row]

        inv = inv_mod_256(M[row][col])
        for c in range(col, n + 1):
            M[row][c] = (M[row][c] * inv) & 0xff

        for r in range(n):
            if r == row:
                continue
            factor = M[r][col]
            if factor:
                for c in range(col, n + 1):
                    M[r][c] = (M[r][c] - factor * M[row][c]) & 0xff

        pivots.append(col)
        row += 1

        if row == n:
            break

    if row != n:
        raise RuntimeError("system was not full rank")

    x = [0] * n
    for r, col in enumerate(pivots):
        x[col] = M[r][n] & 0xff

    return bytes(x)


def main():
    elf = BIN.read_bytes()

    # These are file offsets as well as virtual offsets for this section layout.
    target = elf[0x32170:0x32170 + FLAG_LEN]
    wanted = bytes((~x) & 0xff for x in target)

    base = bytearray(b"A" * FLAG_LEN)
    f_base = run_and_dump_output(bytes(base))

    # Build coefficient matrix columns.
    columns = []
    for i in range(FLAG_LEN):
        probe = bytearray(base)
        probe[i] = (probe[i] + 1) & 0xff
        f_probe = run_and_dump_output(bytes(probe))
        columns.append([(f_probe[r] - f_base[r]) & 0xff for r in range(FLAG_LEN)])

    # Convert columns to rows for Gaussian elimination.
    A = [[columns[c][r] for c in range(FLAG_LEN)] for r in range(FLAG_LEN)]
    rhs = [(wanted[r] - f_base[r]) & 0xff for r in range(FLAG_LEN)]

    delta = solve_mod_256(A, rhs)
    flag = bytes((base[i] + delta[i]) & 0xff for i in range(FLAG_LEN))

    print(flag.decode())


if __name__ == "__main__":
    main()
```

The recovered flag is:

```text
GPNCTF{jusT_onE_onstrUc71oNs_1s_4ll_yOU_N3eD_MAYB3123979AFKfnDh}
```

---

## Verification

Run the original binary with the recovered flag:

```bash
./my-favorite-ingredient 'GPNCTF{jusT_onE_onstrUc71oNs_1s_4ll_yOU_N3eD_MAYB3123979AFKfnDh}'
```

Output:

```text
Correct flag!
```
