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

En vez de imprimir el proceso en la consola, este script genera un reporte
visual en HTML (tablas + diagramas) en el archivo `ejercicio2_reporte.html`.

Ejecutar:
    python3 ejercicio2_3des.py
"""

import os
import webbrowser

import des
import reporte_html as rh

BLOCK_BYTES = 8

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejercicio2_reporte.html")


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


def main():
    # Claves de 64 bits. K1 es la misma clave K entregada en el punto 1 del PDF;
    # K2 y K3 son claves adicionales de ejemplo para completar el esquema 3DES.
    K1 = "00010011" "00110100" "01010111" "01111001" "10011011" "10111100" "11011111" "11110001"
    K2 = "01010011" "00011011" "10100110" "01110010" "11001101" "00011110" "10111001" "01100011"
    K3 = "11000101" "10011100" "00110101" "11010011" "01011010" "01111000" "10001111" "00101010"

    mensaje = "Actividad de DES y Triple DES - Criptologia"

    secciones = []

    # -----------------------------------------------------------------
    # Explicacion del proceso (antes de las tablas)
    # -----------------------------------------------------------------
    contenido = rh.card("""
        <p><b>Esquema EDE (Encrypt-Decrypt-Encrypt)</b> con tres claves
        independientes K1, K2, K3:</p>
        <ul>
            <li><b>Cifrar:</b> <code>E(K1, M) &rarr; D(K2, .) &rarr; E(K3, .)</code>.
            Se cifra con K1, se "descifra" con K2 (esto no revierte nada real, solo
            aplica otra capa distinta) y se vuelve a cifrar con K3.</li>
            <li><b>Descifrar:</b> el proceso exactamente inverso:
            <code>D(K3, C) &rarr; E(K2, .) &rarr; D(K1, .)</code>.</li>
        </ul>
        <p class="section-note">Usar tres claves distintas (en vez de una sola
        clave DES aplicada 3 veces) es lo que le da a 3DES su seguridad extra
        frente al DES simple: amplia efectivamente el espacio de claves.</p>
    """) + rh.card("""
        <p><b>Manejo de un mensaje de texto</b> (mas largo que un bloque de 64 bits):</p>
        <ol>
            <li><b>Relleno PKCS7:</b> si el mensaje no es multiplo de 8 bytes (64 bits),
            se agregan bytes de relleno cuyo valor indica cuantos se agregaron, para
            poder quitarlos exactamente al descifrar.</li>
            <li><b>Particion en bloques:</b> el mensaje ya relleno se divide en bloques
            de 8 bytes (64 bits).</li>
            <li><b>Modo ECB:</b> cada bloque se cifra/descifra por separado con el
            esquema EDE anterior, sin encadenarlo con el bloque anterior.</li>
        </ol>
    """)
    secciones.append(rh.section("&iquest;Como funciona el algoritmo 3DES?", contenido))

    # -----------------------------------------------------------------
    # Claves y mensaje
    # -----------------------------------------------------------------
    contenido = rh.card(f"""
        <p><b>K1</b> (misma clave K del ejercicio 1):</p>{rh.mono(K1)}
        <p>hex: {rh.mono(des.bits_to_hex(K1))}</p>
        <p><b>K2:</b></p>{rh.mono(K2)}
        <p>hex: {rh.mono(des.bits_to_hex(K2))}</p>
        <p><b>K3:</b></p>{rh.mono(K3)}
        <p>hex: {rh.mono(des.bits_to_hex(K3))}</p>
    """) + rh.card(f"""
        <p><b>Mensaje original:</b></p>{rh.mono(mensaje)}
        <p><b>Bytes (hex):</b></p>{rh.mono(mensaje.encode('utf-8').hex())}
    """)
    secciones.append(rh.section("1. Claves y mensaje original", contenido))

    # -----------------------------------------------------------------
    # Esquema 3DES EDE
    # -----------------------------------------------------------------
    contenido = rh.card(f"""
        <p>3DES en modo <b>EDE</b> (Encrypt-Decrypt-Encrypt) con tres claves independientes:</p>
        {rh.svg_3des_scheme(des.bits_to_hex(K1), des.bits_to_hex(K2), des.bits_to_hex(K3))}
        <p class="section-note">El mensaje se convierte a bytes UTF-8, se rellena con PKCS7 hasta
        ser multiplo de 8 bytes y se procesa bloque a bloque (64 bits) en modo ECB.</p>
    """)
    secciones.append(rh.section("2. Esquema 3DES (EDE)", contenido))

    # -----------------------------------------------------------------
    # Cifrado bloque a bloque
    # -----------------------------------------------------------------
    data = pad(mensaje.encode("utf-8"))
    cifrado = bytearray()
    filas_cifrado = []
    for idx in range(0, len(data), BLOCK_BYTES):
        bloque = data[idx:idx + BLOCK_BYTES]
        bloque_bits = des.bytes_to_bits(bloque)
        cbits, (p1, p2, p3) = triple_des_encrypt_block(bloque_bits, K1, K2, K3)
        nbloque = idx // BLOCK_BYTES + 1
        filas_cifrado.append((
            nbloque,
            des.bits_to_hex(bloque_bits),
            des.bits_to_hex(p1),
            des.bits_to_hex(p2),
            des.bits_to_hex(p3),
        ))
        cifrado += des.bits_to_bytes(cbits)

    tabla_cifrado = rh.table(
        ["Bloque", "Texto plano (hex)", "E(K1,.)", "D(K2,.)", "E(K3,.) = cifrado"],
        filas_cifrado,
    )
    contenido = rh.card(f"{tabla_cifrado}") + rh.card(f"""
        <p><b>Texto cifrado completo (hex):</b></p>{rh.mono(bytes(cifrado).hex())}
    """)
    secciones.append(rh.section("3. Proceso de cifrado, bloque a bloque", contenido))

    # -----------------------------------------------------------------
    # Descifrado bloque a bloque
    # -----------------------------------------------------------------
    plano = bytearray()
    filas_descifrado = []
    for idx in range(0, len(cifrado), BLOCK_BYTES):
        bloque = bytes(cifrado[idx:idx + BLOCK_BYTES])
        bloque_bits = des.bytes_to_bits(bloque)
        pbits, (p1, p2, p3) = triple_des_decrypt_block(bloque_bits, K1, K2, K3)
        nbloque = idx // BLOCK_BYTES + 1
        filas_descifrado.append((
            nbloque,
            des.bits_to_hex(bloque_bits),
            des.bits_to_hex(p1),
            des.bits_to_hex(p2),
            des.bits_to_hex(p3),
        ))
        plano += des.bits_to_bytes(pbits)

    texto_recuperado = unpad(bytes(plano)).decode("utf-8")
    ok = texto_recuperado == mensaje

    tabla_descifrado = rh.table(
        ["Bloque", "Cifrado (hex)", "D(K3,.)", "E(K2,.)", "D(K1,.) = texto plano"],
        filas_descifrado,
    )
    contenido = rh.card(f"{tabla_descifrado}") + rh.card(f"""
        <p><b>Texto recuperado:</b></p>{rh.mono(texto_recuperado)}
        <p><b>Verificacion:</b>
        {rh.badge_ok('Coincide con el mensaje original' if ok else 'ERROR: no coincide', ok)}</p>
    """)
    secciones.append(rh.section("4. Proceso de descifrado, bloque a bloque", contenido))

    html = rh.page(
        "Ejercicio 2 &mdash; Triple DES (3DES)",
        "Actividad DES y Triple DES &mdash; cifrado y descifrado de un mensaje con 3DES (EDE, tres claves).",
        secciones,
    )
    rh.write(OUTPUT_FILE, html)
    print(f"Reporte generado: {OUTPUT_FILE}")

    try:
        webbrowser.open(f"file://{OUTPUT_FILE}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
