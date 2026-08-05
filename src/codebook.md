# FI9 Reference Codebook Mapping

## Cell Layout

```
Position numbers (row-major):

  1  2  3
  4  5  6
  7  8  9
```

## Bit Assignment

- Cell 1 = bit 0 (least-significant bit)
- Cell 2 = bit 1
- …
- Cell 9 = bit 8 (most-significant bit)

State number = integer value of the 9-bit vector.

## Region Allocation (as defined in the paper)

| Range       | Purpose                                      |
|-------------|----------------------------------------------|
| 0 – 255     | Region I – direct one-byte values (ASCII/UTF-8 compatible) |
| 256 – 511   | Region II – protocol control, graphical hashes, blockchain instructions, future extensions |

## Examples

| State | Binary (c1…c9)     | Visual (● = occupied) |
|-------|--------------------|-----------------------|
| 0     | 000000000          | · · · / · · · / · · · |
| 1     | 100000000          | ● · · / · · · / · · · |
| 2     | 010000000          | · ● · / · · · / · · · |
| 4     | 001000000          | · · ● / · · · / · · · |
| 65    | (ASCII 'A')        | see interactive demo  |
| 511   | 111111111          | ● ● ● / ● ● ● / ● ● ● |

The interactive demo (`index.html`) lets you browse every state visually.
