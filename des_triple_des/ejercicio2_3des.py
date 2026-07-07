"""
Ejercicio 2 - Actividad DES y Triple DES
-----------------------------------------
Algoritmo Triple DES (3DES) en modo EDE (Encrypt-Decrypt-Encrypt) con tres
claves independientes K1, K2, K3, construido sobre el modulo des.py
(implementacion propia de DES, sin librerias externas de criptografia).

Cifrado :  C = E(K3, D(K2, E(K1, M)))
Descifrado: M = D(K1, E(K2, D(K3, C)))

El mensaje de texto se convierte a bits, se agrupa en bloques de 64 bits
(8 bytes) rellenando con PKCS7 y se procesa bloque a bloque en modo ECB.

Ejecutar:
    python3 ejercicio2_3des.py
"""

import des

BLOCK_BYTES = 8


# ---------------------------------------------------------------------------
# Relleno PKCS7 para que el mensaje sea multiplo de 8 bytes (64 bits)
# ---------------------------------------------------------------------------

def pad(data: bytes) -> bytes:
    faltan = BLOCK_BYTES - (len(data) % BLOCK_BYTES)
    return data + bytes([faltan] * faltan)


def unpad(data: bytes) -> bytes:
    faltan = data[-1]
    return data[:-faltan]


# ---------------------------------------------------------------------------
# Triple DES sobre un solo bloque de 64 bits (EDE)
# ---------------------------------------------------------------------------

def triple_des_encrypt_block(block_bits, k1, k2, k3):
    paso1 = des.encrypt_block(block_bits, k1)   # E(K1, M)
    paso2 = des.decrypt_block(paso1, k2)        # D(K2, .)
    paso3 = des.encrypt_block(paso2, k3)        # E(K3, .)
    return paso3, (paso1, paso2, paso3)


def triple_des_decrypt_block(block_bits, k1, k2, k3):
    paso1 = des.decrypt_block(block_bits, k3)   # D(K3, C)
    paso2 = des.encrypt_block(paso1, k2)        # E(K2, .)
    paso3 = des.decrypt_block(paso2, k1)        # D(K1, .)
    return paso3, (paso1, paso2, paso3)


# ---------------------------------------------------------------------------
# Triple DES sobre un mensaje de texto completo (modo ECB)
# ---------------------------------------------------------------------------

def triple_des_encrypt_text(mensaje: str, k1, k2, k3):
    data = pad(mensaje.encode("utf-8"))
    cifrado = bytearray()
    for i in range(0, len(data), BLOCK_BYTES):
        bloque_bits = des.bytes_to_bits(data[i:i + BLOCK_BYTES])
        cbits, _ = triple_des_encrypt_block(bloque_bits, k1, k2, k3)
        cifrado += des.bits_to_bytes(cbits)
    return bytes(cifrado)


def triple_des_decrypt_text(cifrado: bytes, k1, k2, k3):
    plano = bytearray()
    for i in range(0, len(cifrado), BLOCK_BYTES):
        bloque_bits = des.bytes_to_bits(cifrado[i:i + BLOCK_BYTES])
        pbits, _ = triple_des_decrypt_block(bloque_bits, k1, k2, k3)
        plano += des.bits_to_bytes(pbits)
    return unpad(bytes(plano)).decode("utf-8")


def linea(titulo=""):
    print("-" * 70 if not titulo else f"\n{'-' * 20} {titulo} {'-' * 20}")


def main():
    # Claves de 64 bits. K1 es la misma clave K entregada en el punto 1 del PDF;
    # K2 y K3 son claves adicionales de ejemplo para completar el esquema 3DES.
    K1 = "00010011" "00110100" "01010111" "01111001" "10011011" "10111100" "11011111" "11110001"
    K2 = "01010011" "00011011" "10100110" "01110010" "11001101" "00011110" "10111001" "01100011"
    K3 = "11000101" "10011100" "00110101" "11010011" "01011010" "01111000" "10001111" "00101010"

    mensaje = "Actividad de DES y Triple DES - Criptologia"

    linea("CLAVES UTILIZADAS (64 bits cada una)")
    print(f"K1 (bin): {K1}  (hex: {des.bits_to_hex(K1)})")
    print(f"K2 (bin): {K2}  (hex: {des.bits_to_hex(K2)})")
    print(f"K3 (bin): {K3}  (hex: {des.bits_to_hex(K3)})")

    linea("MENSAJE ORIGINAL")
    print(f"Texto plano : {mensaje!r}")
    print(f"Bytes       : {mensaje.encode('utf-8').hex()}")

    linea("PROCESO DE CIFRADO (por bloque de 64 bits): E(K3, D(K2, E(K1, M)))")
    data = pad(mensaje.encode("utf-8"))
    cifrado = bytearray()
    for idx in range(0, len(data), BLOCK_BYTES):
        bloque = data[idx:idx + BLOCK_BYTES]
        bloque_bits = des.bytes_to_bits(bloque)
        cbits, (p1, p2, p3) = triple_des_encrypt_block(bloque_bits, K1, K2, K3)
        nbloque = idx // BLOCK_BYTES + 1
        print(f"\nBloque {nbloque}: {bloque_bits}  (hex: {des.bits_to_hex(bloque_bits)})")
        print(f"  E(K1,.) = {p1}  (hex: {des.bits_to_hex(p1)})")
        print(f"  D(K2,.) = {p2}  (hex: {des.bits_to_hex(p2)})")
        print(f"  E(K3,.) = {p3}  (hex: {des.bits_to_hex(p3)})  <- cifrado del bloque")
        cifrado += des.bits_to_bytes(cbits)

    linea("RESULTADO DEL CIFRADO")
    print(f"Texto cifrado (hex): {bytes(cifrado).hex()}")

    linea("PROCESO DE DESCIFRADO (por bloque de 64 bits): D(K1, E(K2, D(K3, C)))")
    plano = bytearray()
    for idx in range(0, len(cifrado), BLOCK_BYTES):
        bloque = bytes(cifrado[idx:idx + BLOCK_BYTES])
        bloque_bits = des.bytes_to_bits(bloque)
        pbits, (p1, p2, p3) = triple_des_decrypt_block(bloque_bits, K1, K2, K3)
        nbloque = idx // BLOCK_BYTES + 1
        print(f"\nBloque {nbloque}: {bloque_bits}  (hex: {des.bits_to_hex(bloque_bits)})")
        print(f"  D(K3,.) = {p1}  (hex: {des.bits_to_hex(p1)})")
        print(f"  E(K2,.) = {p2}  (hex: {des.bits_to_hex(p2)})")
        print(f"  D(K1,.) = {p3}  (hex: {des.bits_to_hex(p3)})  <- bloque en claro")
        plano += des.bits_to_bytes(pbits)

    texto_recuperado = unpad(bytes(plano)).decode("utf-8")
    linea("RESULTADO DEL DESCIFRADO")
    print(f"Texto recuperado: {texto_recuperado!r}")
    print(f"Coincide con el mensaje original? {'Si' if texto_recuperado == mensaje else 'No'}")

    # Verificacion adicional usando las funciones de alto nivel
    linea("VERIFICACION CON FUNCIONES DE ALTO NIVEL")
    c = triple_des_encrypt_text(mensaje, K1, K2, K3)
    m = triple_des_decrypt_text(c, K1, K2, K3)
    print(f"triple_des_encrypt_text -> {c.hex()}")
    print(f"triple_des_decrypt_text -> {m!r}")
    assert m == mensaje
    print("Cifrado y descifrado consistentes.")


if __name__ == "__main__":
    main()
