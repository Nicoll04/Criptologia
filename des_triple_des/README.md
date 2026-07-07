# Actividad DES y Triple DES

Implementación en Python (sin librerías externas de criptografía) de:

1. **`des.py`** — motor DES completo: tablas oficiales (IP, FP, E, P, PC-1, PC-2,
   S-Cajas), generación de las 16 subclaves y cifrado/descifrado de un bloque
   de 64 bits.
2. **`reporte_html.py`** — utilidades para construir el reporte visual (tablas
   y diagramas SVG) que generan los dos ejercicios.
3. **`ejercicio1_des_subclaves.py`** — Punto 1: cifra el mensaje del PDF con la
   clave K dada y genera un reporte HTML (`ejercicio1_reporte.html`) con todo
   el proceso hasta generar las 16 subclaves.
4. **`ejercicio2_3des.py`** — Punto 2: implementación de 3DES (EDE, tres claves)
   que cifra y descifra un mensaje de texto, generando un reporte HTML
   (`ejercicio2_reporte.html`) con el procedimiento bloque a bloque.

Requiere solo Python 3 (sin dependencias). Los scripts **no imprimen el
proceso en la consola**: generan un archivo HTML autocontenido (tablas +
diagramas SVG) y lo abren automáticamente en el navegador por defecto.

```bash
python3 ejercicio1_des_subclaves.py   # genera y abre ejercicio1_reporte.html
python3 ejercicio2_3des.py            # genera y abre ejercicio2_reporte.html
```

Si el navegador no se abre automáticamente (por ejemplo, en un entorno sin
interfaz gráfica), abre manualmente el archivo `.html` generado con doble
clic o arrastrándolo a cualquier navegador.

## Punto 1 — DES: mensaje, clave y generación de subclaves

### Datos de entrada (matrices del PDF, convertidas a cadenas de 64 bits)

- Mensaje `M` = `1110110111001100001111001011100111111111001100110000111111101010`
  (hex `EDCC3CB9FF330FEA`)
- Clave `K` = `0001001100110100010101110111100110011011101111001101111111110001`
  (hex `133457799BBCDFF1`)

### Procedimiento

1. **PC-1**: la clave de 64 bits se reduce a 56 bits (se descartan los bits de
   paridad) y se divide en `C0` (28 bits) y `D0` (28 bits).
2. **16 rondas de rotación + PC-2**: en cada ronda `i`, `C(i-1)` y `D(i-1)` se
   rotan a la izquierda según la tabla de desplazamientos
   `[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]`. La concatenación `Ci+Di` se pasa por
   `PC-2` (56→48 bits) para obtener la subclave `Ki`.
3. Con las 16 subclaves generadas se aplica el algoritmo DES completo al
   mensaje: `IP` → 16 rondas de Feistel (`L(i)=R(i-1)`, `R(i)=L(i-1) XOR f(R(i-1),Ki)`)
   → intercambio final `R16+L16` → `FP`.

### Resultado (subclaves K1..K16, en hexadecimal)

| Ronda | Subclave (hex) |
|---|---|
| K1  | 1B02EFFC7072 |
| K2  | 79AED9DBC9E5 |
| K3  | 55FC8A42CF99 |
| K4  | 72ADD6DB351D |
| K5  | 7CEC07EB53A8 |
| K6  | 63A53E507B2F |
| K7  | EC84B7F618BC |
| K8  | F78A3AC13BFB |
| K9  | E0DBEBEDE781 |
| K10 | B1F347BA464F |
| K11 | 215FD3DED386 |
| K12 | 7571F59467E9 |
| K13 | 97C5D1FABA41 |
| K14 | 5F43B7F2E73A |
| K15 | BF918D3D3F0A |
| K16 | CB3D8B0E17F5 |

(Nota: la clave `K = 133457799BBCDFF1` corresponde al ejemplo clásico de DES
usado en la literatura — p. ej. Stallings, *Cryptography and Network
Security* —, por lo que estas subclaves coinciden con los valores publicados
en dicho ejemplo, lo cual sirvió para validar la implementación.)

### Mensaje cifrado

- Texto cifrado (binario): `0101100000000101000010000001011000000001111011100101101000110110`
- Texto cifrado (hex): **`5805081601EE5A36`**
- Verificación: al descifrar el resultado con la misma clave `K` se recupera
  exactamente el mensaje original de 64 bits.

El detalle ronda a ronda (`L0..L16`, `R0..R16`) se imprime al ejecutar
`ejercicio1_des_subclaves.py`.

## Punto 2 — Triple DES (3DES)

### Esquema utilizado

3DES en modo **EDE** (Encrypt-Decrypt-Encrypt) con tres claves independientes
de 64 bits, reutilizando el mismo `des.py` del punto 1 como bloque de
construcción:

- Cifrado:    `C = E(K3, D(K2, E(K1, M)))`
- Descifrado: `M = D(K1, E(K2, D(K3, C)))`

El mensaje de texto se convierte a bytes (UTF-8), se rellena con **PKCS7**
hasta ser múltiplo de 8 bytes (64 bits) y se procesa **bloque a bloque en
modo ECB**, aplicando el esquema EDE anterior a cada bloque con `des.py`.

### Claves usadas

- `K1` = `133457799BBCDFF1` (la misma clave del punto 1)
- `K2` = `531BA672CD1EB963`
- `K3` = `C59C35D35A788F2A`

### Procedimiento (resumen, ver salida completa del script)

Mensaje: `"Actividad de DES y Triple DES - Criptologia"` (44 bytes → 6 bloques
de 64 bits tras el relleno PKCS7).

Para cada bloque se muestra:

```
Bloque N: <bloque en claro>
  E(K1,.) = ...
  D(K2,.) = ...
  E(K3,.) = ...   <- cifrado del bloque
```

y en el descifrado el proceso inverso `D(K3,.) -> E(K2,.) -> D(K1,.)`.

### Resultados

- Texto cifrado (hex):
  `e3bdfe742af922e09250f1df7b36c62c38d1a61c497ad99d03bc5b3aa1d37a929de2f2f05affcce7a95b5182a676ede9`
- Texto descifrado: `"Actividad de DES y Triple DES - Criptologia"`
- Coincide con el mensaje original: **Sí**

El script también valida el resultado con las funciones de alto nivel
`triple_des_encrypt_text` / `triple_des_decrypt_text`, confirmando que
cifrado y descifrado son consistentes.
