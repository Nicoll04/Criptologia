"""
Ejercicio 1 - Actividad DES y Triple DES
-----------------------------------------
Con el algoritmo DES se cifra el mensaje dado y se genera todo el proceso
de generacion de las 16 subclaves a partir de la clave K, ambos entregados
en el PDF como matrices de 8x8 bits.

En vez de imprimir el proceso en la consola, este script genera un reporte
visual en HTML (tablas + diagramas) en el archivo `ejercicio1_reporte.html`.

Ejecutar:
    python3 ejercicio1_des_subclaves.py
"""

import os
import webbrowser

import des
import reporte_html as rh

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

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejercicio1_reporte.html")


def main():
    secciones = []

    # -----------------------------------------------------------------
    # Explicacion del proceso (antes de las tablas)
    # -----------------------------------------------------------------
    contenido = rh.card("""
        <p><b>Tablas del estandar (IP, FP, E, P, PC-1, PC-2, S-cajas):</b>
        son tablas fijas definidas por el estandar DES (FIPS 46-3), no se calculan.
        Todas las permutaciones (IP, FP, E, P, PC-1, PC-2) son la misma operacion
        generica: reordenar/seleccionar bits segun una tabla de indices.</p>
    """) + rh.card("""
        <p><b>Generacion de las 16 subclaves</b> (a partir de la clave K de 64 bits):</p>
        <ol>
            <li><b>PC-1:</b> la clave de 64 bits pasa por PC-1, que descarta los 8 bits
            de paridad y deja 56 bits.</li>
            <li>Esos 56 bits se parten en dos mitades de 28 bits: <code>C0</code> y
            <code>D0</code>.</li>
            <li>Por cada una de las 16 rondas: <code>C</code> y <code>D</code> se rotan
            a la izquierda (1 o 2 bits, segun la tabla de desplazamientos) y la
            concatenacion <code>C_i + D_i</code> pasa por <b>PC-2</b>, que selecciona
            48 de esos 56 bits &rarr; esa es la subclave <code>K_i</code>.</li>
        </ol>
    """) + rh.card("""
        <p><b>Funcion Feistel f(R, K)</b> &mdash; el corazon de cada ronda:</p>
        <ol>
            <li><b>Expansion (E):</b> la mitad derecha (32 bits) se expande a 48 bits
            repitiendo algunos bits.</li>
            <li><b>XOR con la subclave:</b> los 48 bits expandidos se mezclan (XOR)
            con la subclave de esa ronda.</li>
            <li><b>S-cajas:</b> los 48 bits se dividen en 8 grupos de 6 bits. En cada
            grupo, el primer y ultimo bit forman la fila (0-3) y los 4 bits del medio
            forman la columna (0-15) de la S-caja correspondiente; el valor encontrado
            se convierte a 4 bits. Es la unica parte no lineal del algoritmo, y reduce
            48 bits de vuelta a 32.</li>
            <li><b>Permutacion (P):</b> una permutacion final mezcla esos 32 bits.</li>
        </ol>
    """) + rh.card("""
        <p><b>Cifrado del bloque completo (64 bits):</b></p>
        <ol>
            <li><b>IP:</b> permutacion inicial del bloque (mensaje o cifrado).</li>
            <li>Se parte en <code>L</code> (izquierda, 32 bits) y <code>R</code>
            (derecha, 32 bits).</li>
            <li>Por cada una de las 16 subclaves: <code>L_i = R_(i-1)</code> y
            <code>R_i = L_(i-1) XOR f(R_(i-1), K_i)</code>. Esta es la estructura
            Feistel.</li>
            <li>Al terminar las 16 rondas se intercambian <code>L</code> y
            <code>R</code> una ultima vez y se aplica <b>FP</b> (permutacion final,
            inversa de IP).</li>
        </ol>
        <p class="section-note">Para <b>descifrar</b> se usa exactamente el mismo
        proceso, pero con las 16 subclaves en <b>orden inverso</b>
        (K16 &rarr; K1 en vez de K1 &rarr; K16). Por eso la estructura Feistel
        permite cifrar y descifrar con el mismo circuito.</p>
    """)
    secciones.append(rh.section("&iquest;Como funciona el algoritmo DES?", contenido))

    # -----------------------------------------------------------------
    # Datos de entrada
    # -----------------------------------------------------------------
    contenido = f"""
    <div class="card">
        <p><b>Mensaje (M)</b> &mdash; matriz 8x8 tal como aparece en el PDF:</p>
        {rh.bit_grid(MENSAJE_BITS)}
        <p><b>M en binario:</b></p>{rh.mono(MENSAJE_BITS)}
        <p><b>M en hexadecimal:</b></p>{rh.mono(des.bits_to_hex(MENSAJE_BITS))}
    </div>
    <div class="card">
        <p><b>Clave (K)</b> &mdash; matriz 8x8 tal como aparece en el PDF:</p>
        {rh.bit_grid(CLAVE_BITS)}
        <p><b>K en binario:</b></p>{rh.mono(CLAVE_BITS)}
        <p><b>K en hexadecimal:</b></p>{rh.mono(des.bits_to_hex(CLAVE_BITS))}
    </div>
    """
    secciones.append(rh.section("1. Datos de entrada", contenido))

    # -----------------------------------------------------------------
    # Paso 1: PC-1 y division en C0/D0
    # -----------------------------------------------------------------
    key56 = des.permute(CLAVE_BITS, des.PC1)
    C0, D0 = key56[:28], key56[28:]
    contenido = rh.card(f"""
        <p><b>K+ = PC-1(K)</b> (64 &rarr; 56 bits):</p>{rh.mono(key56)}
        {rh.flow(["K (64 bits)", "PC-1", "K+ (56 bits)"])}
        <p><b>C0</b> (primeros 28 bits):</p>{rh.mono(C0)}
        <p><b>D0</b> (ultimos 28 bits):</p>{rh.mono(D0)}
    """)
    secciones.append(rh.section("2. PC-1 y division en C0 / D0", contenido))

    # -----------------------------------------------------------------
    # Paso 2: 16 rotaciones + PC-2
    # -----------------------------------------------------------------
    subkeys, history = des.generate_subkeys(CLAVE_BITS)

    filas_rot = []
    for i in range(1, 17):
        _, Ci, Di, _ = history[i]
        filas_rot.append((i, des.SHIFTS[i - 1], rh.mono(Ci), rh.mono(Di)))
    tabla_rotaciones = rh.table(
        ["Ronda", "Desplazamiento", "C_i (28 bits)", "D_i (28 bits)"],
        filas_rot,
    )

    filas_sub = []
    for i, k in enumerate(subkeys, start=1):
        filas_sub.append((f"K{i}", rh.mono(k), des.bits_to_hex(k)))
    tabla_subclaves = rh.table(["Subclave", "Binario (48 bits)", "Hex"], filas_sub)

    contenido = rh.card(f"""
        <p>Cada ronda rota <code>C</code> y <code>D</code> a la izquierda segun la tabla de
        desplazamientos <code>[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]</code> y aplica <code>PC-2</code>
        (56&rarr;48 bits) sobre <code>C_i + D_i</code> para obtener <code>K_i</code>.</p>
        {tabla_rotaciones}
    """) + rh.card(f"<p><b>Subclaves generadas K1..K16:</b></p>{tabla_subclaves}")
    secciones.append(rh.section("3. Generacion de las 16 subclaves (rotaciones + PC-2)", contenido))

    # -----------------------------------------------------------------
    # Paso 3: cifrado completo del mensaje
    # -----------------------------------------------------------------
    ip = des.permute(MENSAJE_BITS, des.IP)
    L0, R0 = ip[:32], ip[32:]

    filas_rondas = []
    L, R = L0, R0
    for i, k in enumerate(subkeys, start=1):
        L, R = R, des.xor(L, des.feistel(R, k))
        filas_rondas.append((i, rh.mono(L), rh.mono(R)))
    tabla_rondas = rh.table(["Ronda", "L_i (32 bits)", "R_i (32 bits)"], filas_rondas)

    cifrado = des.permute(R + L, des.FP)

    contenido = rh.card(f"""
        <p><b>Esquema de una ronda Feistel</b> (se aplica 16 veces con K1..K16):</p>
        {rh.svg_feistel_round()}
        {rh.flow(["M", "IP", "L0 / R0", "16 rondas", "R16+L16", "FP", "C"])}
        <p><b>IP(M):</b></p>{rh.mono(ip)}
        <p><b>L0:</b></p>{rh.mono(L0)}
        <p><b>R0:</b></p>{rh.mono(R0)}
    """) + rh.card(f"<p><b>Valores por ronda:</b></p>{tabla_rondas}") + rh.card(f"""
        <p><b>Texto cifrado (binario):</b></p>{rh.mono(cifrado)}
        <p><b>Texto cifrado (hex):</b></p>{rh.mono(des.bits_to_hex(cifrado))}
    """)
    secciones.append(rh.section("4. Cifrado del mensaje (DES completo, 16 rondas)", contenido))

    html = rh.page(
        "Ejercicio 1 &mdash; DES: cifrado y generacion de subclaves",
        "Actividad DES y Triple DES &mdash; proceso completo hasta las 16 subclaves y cifrado del mensaje.",
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
