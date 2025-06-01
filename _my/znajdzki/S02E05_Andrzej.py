import base64

# Zakodowany tekst
encoded = "GhUiPj1fKTM3NCY1KSUmNxkP"

# Dekoduj base64
decoded_bytes = base64.b64decode(encoded)

# Klucz
key = "Andrzej"
key_bytes = key.encode()

# XOR dekodowanie
def xor_decrypt(data, key):
    key_len = len(key)
    return bytes([b ^ key[i % key_len] for i, b in enumerate(data)])

# Odszyfrowanie
decrypted_bytes = xor_decrypt(decoded_bytes, key_bytes)
decrypted_text = decrypted_bytes.decode(errors="replace")  # replace unknown chars

print(decrypted_text)
