"""
FI9 – 512-State Spatial Encoding Architecture
Reference implementation of the paper by Said Hassan Ameeny Poor.

Cell layout (row-major):
  1 2 3
  4 5 6
  7 8 9

State number = integer whose binary representation (LSB = cell 1) indicates
occupied cells.  This yields a perfect bijection with the 512 possible
spatial configurations.
"""

from typing import List, Tuple, Union
import hashlib


class FI9:
    """Deterministic FI9 encoder / decoder and codebook utilities."""

    N_CELLS = 9
    N_STATES = 1 << N_CELLS  # 512

    def __init__(self):
        # Pre-compute the visual matrix for every state (optional cache)
        self._matrices = [self.state_to_matrix(s) for s in range(self.N_STATES)]

    # ------------------------------------------------------------------
    # Core conversion
    # ------------------------------------------------------------------
    @staticmethod
    def state_to_bits(state: int) -> List[int]:
        """Return 9 bits (cell 1 … cell 9) for a given state (0-511)."""
        if not 0 <= state < 512:
            raise ValueError(f"State must be in [0, 511], got {state}")
        return [(state >> i) & 1 for i in range(9)]

    @staticmethod
    def bits_to_state(bits: List[int]) -> int:
        """Convert 9 bits back to a state number."""
        if len(bits) != 9:
            raise ValueError("Exactly 9 bits required")
        state = 0
        for i, b in enumerate(bits):
            if b not in (0, 1):
                raise ValueError("Bits must be 0 or 1")
            state |= (b & 1) << i
        return state

    @staticmethod
    def state_to_matrix(state: int) -> List[List[int]]:
        """Return a 3×3 matrix of 0/1 for visualization."""
        bits = FI9.state_to_bits(state)
        return [
            [bits[0], bits[1], bits[2]],
            [bits[3], bits[4], bits[5]],
            [bits[6], bits[7], bits[8]],
        ]

    def matrix(self, state: int) -> List[List[int]]:
        return self._matrices[state]

    # ------------------------------------------------------------------
    # Encoding / Decoding (Region I – bytes 0-255)
    # ------------------------------------------------------------------
    def encode_byte(self, byte: int) -> int:
        """Map a single byte (0-255) to its FI9 state (identical value)."""
        if not 0 <= byte <= 255:
            raise ValueError("Byte must be in [0, 255]")
        return byte  # Region I identity mapping

    def decode_byte(self, state: int) -> int:
        """Recover the original byte from a Region-I state."""
        if not 0 <= state <= 255:
            raise ValueError("Only states 0-255 encode ordinary bytes")
        return state

    def encode(self, data: Union[bytes, str]) -> List[int]:
        """Encode a bytes object or UTF-8 string into a list of FI9 states."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return [self.encode_byte(b) for b in data]

    def decode(self, states: List[int]) -> bytes:
        """Decode a list of FI9 states (0-255) back to bytes."""
        return bytes(self.decode_byte(s) for s in states)

    def decode_str(self, states: List[int], encoding: str = "utf-8") -> str:
        return self.decode(states).decode(encoding)

    # ------------------------------------------------------------------
    # Graphical Token (Version-1 = 32 consecutive symbols)
    # ------------------------------------------------------------------
    def make_token(self, data: Union[bytes, str], length: int = 32) -> List[int]:
        """
        Create a Version-1 graphical token of `length` FI9 symbols.
        If data is shorter it is padded with zeros; if longer it is truncated.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        data = (data + b"\x00" * length)[:length]
        return self.encode(data)

    # ------------------------------------------------------------------
    # Graphical Hash (map any conventional hash into FI9 symbols)
    # ------------------------------------------------------------------
    def graphical_hash(self, data: Union[bytes, str], algorithm: str = "sha256") -> List[int]:
        """
        Compute a conventional cryptographic hash and represent each byte
        as an FI9 symbol (Region I).  This realises the “Graphical Hash”
        concept of Section 7 without inventing a new cryptographic primitive.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        h = hashlib.new(algorithm, data).digest()
        return self.encode(h)

    # ------------------------------------------------------------------
    # Native FI Hash (proposed construction for Section 7.1)
    # ------------------------------------------------------------------
    def native_fi_hash(self, data: Union[bytes, str],
                       out_len: int = 32,
                       rounds: int = 16) -> List[int]:
        """
        Native FI Hash – operates entirely inside the 512-state spatial
        symbol space (no intermediate conversion to classical binary
        streams beyond the 9-bit cell vectors themselves).

        Construction (research prototype, NOT cryptographically proven):

          • Internal state  : 16 FI9 symbols (144 bits)
          • Absorption      : message symbols XORed into the state
          • Round function  : 9-bit nonlinear substitution + spatial
                              diffusion that mixes the 3×3 cell geometry
                              across neighbouring state words
          • Output          : squeeze `out_len` symbols (default 32)

        Security analysis is left as future work (paper §7.1).
        This implementation is deterministic and intended for
        experimental evaluation by reviewers.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        # Map every input byte into Region-I FI9 state
        msg = [b & 0xFF for b in data]

        # Round constants (keep inside 0..511)
        RC = [(i * 37 + 11) & 511 for i in range(rounds * 16 + 64)]

        def rotl9(x: int, n: int) -> int:
            n %= 9
            return ((x << n) | (x >> (9 - n))) & 511

        def rotr9(x: int, n: int) -> int:
            n %= 9
            return ((x >> n) | (x << (9 - n))) & 511

        # Nonlinear substitution on a single 9-bit FI state
        def sbox(x: int) -> int:
            x = (x + 0x1A3) & 511
            x = rotl9(x, 3)
            x ^= rotl9(x, 1)
            x = (x * 3 + 0x05B) & 511          # odd multiplier → bijective mod 2^k
            x = rotl9(x, 2)
            x ^= (x >> 4)
            return x & 511

        # Spatial diffusion across neighbouring state words
        # (each word exchanges information with left/right neighbours
        #  using rotations that emulate the 3×3 cell geometry)
        def diffuse(state: List[int]) -> None:
            n = len(state)
            tmp = state[:]
            for i in range(n):
                left  = tmp[(i - 1) % n]
                right = tmp[(i + 1) % n]
                state[i] = (tmp[i]
                            ^ rotl9(left, 1)
                            ^ rotr9(right, 2)
                            ^ rotl9(tmp[i], 4)) & 511

        # Initialise 16-symbol internal state
        STATE_SIZE = 16
        state = [(i * 0x11 + 0x2A) & 511 for i in range(STATE_SIZE)]

        # Padding: domain separator (protocol region) + length symbol
        msg = msg + [0x100] + [len(data) & 511]

        # Absorb message in blocks
        for block_start in range(0, len(msg), STATE_SIZE):
            block = msg[block_start:block_start + STATE_SIZE]
            for i, m in enumerate(block):
                state[i] = (state[i] ^ m) & 511
            for r in range(rounds):
                for i in range(STATE_SIZE):
                    state[i] = sbox(state[i] ^ RC[r * STATE_SIZE + i])
                diffuse(state)

        # Squeeze output symbols
        out: List[int] = []
        while len(out) < out_len:
            for r in range(4):
                for i in range(STATE_SIZE):
                    state[i] = sbox(state[i] ^ RC[(r * 7 + i) % len(RC)])
                diffuse(state)
            out.extend(state[:min(8, out_len - len(out))])

        return out[:out_len]

    # ------------------------------------------------------------------
    # Protocol region helpers (states 256-511)
    # ------------------------------------------------------------------
    def is_protocol_state(self, state: int) -> bool:
        return 256 <= state <= 511

    def protocol_state(self, index: int) -> int:
        """Map a protocol index 0-255 onto states 256-511."""
        if not 0 <= index <= 255:
            raise ValueError("Protocol index must be 0-255")
        return 256 + index

    # ------------------------------------------------------------------
    # Pretty-print helpers
    # ------------------------------------------------------------------
    def render_ascii(self, state: int, filled: str = "●", empty: str = "·") -> str:
        """Return a 3-line ASCII art of the symbol."""
        m = self.matrix(state)
        lines = []
        for row in m:
            lines.append(" ".join(filled if c else empty for c in row))
        return "\n".join(lines)

    def render_token_ascii(self, states: List[int], cols: int = 8) -> str:
        """Render a sequence of symbols as a multi-line ASCII grid."""
        blocks = [self.render_ascii(s).splitlines() for s in states]
        rows_out = []
        for i in range(0, len(blocks), cols):
            chunk = blocks[i : i + cols]
            for line_idx in range(3):
                rows_out.append("   ".join(b[line_idx] for b in chunk))
            rows_out.append("")  # blank line between rows of symbols
        return "\n".join(rows_out)


# Convenience singleton
fi9 = FI9()


if __name__ == "__main__":
    # Quick self-test
    e = FI9()
    msg = "The position of a point is the information."
    states = e.encode(msg)
    recovered = e.decode_str(states)
    assert recovered == msg
    print("Round-trip OK")
    print("First 8 symbols of the message:")
    print(e.render_token_ascii(states[:8], cols=8))

    # Native FI Hash demo
    h1 = e.native_fi_hash(msg)
    h2 = e.native_fi_hash(msg)
    h3 = e.native_fi_hash(msg + "!")
    assert h1 == h2, "Native FI Hash must be deterministic"
    assert h1 != h3, "Different inputs must produce different hashes"
    print("\nNative FI Hash (32 symbols) of the message:")
    print(h1)
    print(e.render_token_ascii(h1[:8], cols=8))
