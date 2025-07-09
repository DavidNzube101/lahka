import os
try:
    from bech32 import bech32_encode, bech32_decode, convertbits
    BECH32_AVAILABLE = True
except ImportError:
    BECH32_AVAILABLE = False
    print("[WARNING] bech32 module not available, using simple address format")

HRP = 'lakha'


def generate_address(pubkey_bytes=None):
    """Generate a new Bech32 address from pubkey bytes or random bytes."""
    if pubkey_bytes is None:
        pubkey_bytes = os.urandom(20)  # 160 bits, like Ethereum
    
    if BECH32_AVAILABLE:
        data = convertbits(pubkey_bytes, 8, 5)
        return bech32_encode(HRP, data)
    else:
        # Fallback: simple hex address with prefix
        return f"lakha{pubkey_bytes.hex()}"


def is_valid_address(address):
    """Check if the address is a valid Lahka address."""
    if BECH32_AVAILABLE:
        hrp, data = bech32_decode(address)
        if hrp != HRP or data is None:
            return False
        # Convert back to bytes to check length
        decoded = convertbits(data, 5, 8, False)
        return decoded is not None and len(decoded) == 20
    else:
        # Fallback: check if it starts with 'lakha' and has valid hex
        if not address.startswith('lakha'):
            return False
        try:
            hex_part = address[5:]  # Remove 'lakha' prefix
            bytes.fromhex(hex_part)
            return len(hex_part) == 40  # 20 bytes = 40 hex chars
        except:
            return False


def encode_address(pubkey_bytes):
    """Encode pubkey bytes to a Lahka address."""
    if BECH32_AVAILABLE:
        data = convertbits(pubkey_bytes, 8, 5)
        return bech32_encode(HRP, data)
    else:
        return f"lakha{pubkey_bytes.hex()}"


def decode_address(address):
    """Decode a Lahka address to bytes. Returns None if invalid."""
    if BECH32_AVAILABLE:
        hrp, data = bech32_decode(address)
        if hrp != HRP or data is None:
            return None
        decoded = convertbits(data, 5, 8, False)
        if decoded is None or len(decoded) != 20:
            return None
        return bytes(decoded)
    else:
        # Fallback: decode from hex
        if not address.startswith('lakha'):
            return None
        try:
            hex_part = address[5:]  # Remove 'lakha' prefix
            return bytes.fromhex(hex_part)
        except:
            return None 