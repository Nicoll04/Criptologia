"""
Ejercicio 1 - Actividad DES y Triple DES
-----------------------------------------
Con el algoritmo DES se cifra el mensaje dado y se genera todo el proceso
de generacion de las 16 subclaves a partir de la clave K, ambos entregados
en el PDF como matrices de 8x8 bits.

Ejecutar:
    python3 ejercicio1_des_subclaves.py
"""

import des

# ---------------------------------------------------------------------------
# Datos de entrada tomados del PDF (matrices de 8x8 bits, fila por fila)
# ---------------------------------------------------------------------------

MENSAJE_MATRIZ = [
    "11101101",
    "11001100",
    "00111100",
    "10111001",
    "11111111",
    "00110011",
    "00001111",
    "11101010",
]

CLAVE_MATRIZ = [
    "00010011",
    "00110100",
    "01010111",
    "01111001",
    "10011011",
    "10111100",
    "11011111",
    "11110001",
]

MENSAJE_BITS = ''.join(MENSAJE_MATRIZ)
CLAVE_BITS = ''.join(CLAVE_MATRIZ)


def linea(titulo=""):
    print("-" * 70 if not titulo else f"\n{'-' * 20} {titulo} {'-' * 20}")


def main():
    linea("DATOS DE ENTRADA")
    print(f"Mensaje (M), 64 bits : {MENSAJE_BITS}")
    print(f"Mensaje en hex       : {des.bits_to_hex(MENSAJE_BITS)}")
    print(f"Clave   (K), 64 bits : {CLAVE_BITS}")
    print(f"Clave en hex         : {des.bits_to_hex(CLAVE_BITS)}")

    # -----------------------------------------------------------------
    # Paso 1: PC-1 sobre la clave de 64 bits -> 56 bits -> C0 / D0
    # -----------------------------------------------------------------
    linea("PASO 1: PC-1 (64 -> 56 bits) y division en C0 / D0")
    key56 = des.permute(CLAVE_BITS, des.PC1)
    C0, D0 = key56[:28], key56[28:]
    print(f"K+ (PC-1)  : {key56}")
    print(f"C0 (28 bits): {C0}")
    print(f"D0 (28 bits): {D0}")

    # -----------------------------------------------------------------
    # Paso 2: 16 rotaciones + PC-2 -> subclaves K1..K16
    # -----------------------------------------------------------------
    linea("PASO 2: Generacion de las 16 subclaves (rotaciones + PC-2)")
    subkeys, history = des.generate_subkeys(CLAVE_BITS)

    print(f"{'Ronda':<6}{'Desplaz.':<9}{'C_i (28 bits)':<30}{'D_i (28 bits)':<30}")
    for i in range(1, 17):
        _, Ci, Di, _ = history[i]
        print(f"{i:<6}{des.SHIFTS[i-1]:<9}{Ci:<30}{Di:<30}")

    linea("SUBCLAVES K1..K16 (48 bits, binario y hex)")
    for i, k in enumerate(subkeys, start=1):
        print(f"K{i:<3} = {k}  (hex: {des.bits_to_hex(k)})")

    # -----------------------------------------------------------------
    # Paso 3: cifrado completo del mensaje usando las subclaves generadas
    # -----------------------------------------------------------------
    linea("PASO 3: Cifrado del mensaje con DES completo (16 rondas)")
    ip = des.permute(MENSAJE_BITS, des.IP)
    L0, R0 = ip[:32], ip[32:]
    print(f"IP(M)      : {ip}")
    print(f"L0         : {L0}")
    print(f"R0         : {R0}")

    L, R = L0, R0
    for i, k in enumerate(subkeys, start=1):
        L, R = R, des.xor(L, des.feistel(R, k))
        print(f"Ronda {i:<2} -> L{i} = {L}   R{i} = {R}")

    cifrado = des.permute(R + L, des.FP)
    linea("RESULTADO")
    print(f"Preciphertext (R16+L16) : {R + L}")
    print(f"Texto cifrado (bin)     : {cifrado}")
    print(f"Texto cifrado (hex)     : {des.bits_to_hex(cifrado)}")

    # Verificacion: descifrar debe devolver el mensaje original
    descifrado = des.decrypt_block(cifrado, CLAVE_BITS)
    print(f"\nComprobacion (descifrado) : {descifrado}")
    print(f"Coincide con el mensaje original? {'Si' if descifrado == MENSAJE_BITS else 'No'}")


if __name__ == "__main__":
    main()
