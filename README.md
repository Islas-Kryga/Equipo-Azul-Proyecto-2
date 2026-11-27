# Equipo Azul — Proyecto 2: Buscaminas

Proyecto de Modelado y Programación para desarrollar una versión gráfica del
juego Buscaminas. La consigna completa se encuentra en
[`Proyecto2_MyP20271.pdf`](Proyecto2_MyP20271.pdf).

## Nombre del equipo

Equipo Azul

## Objetivo

Desarrollar un Buscaminas para una persona con interfaz gráfica y control por
ratón. El motor del juego debe estar separado de la interfaz, de modo que las
reglas puedan probarse sin abrir la ventana del juego.

El programa ofrecerá al menos estas dificultades:

| Nivel | Tablero | Minas |
|---|---:|---:|
| Fácil | 9 × 9 | 10 |
| Medio | 16 × 16 | 40 |
| Difícil | 16 × 30 | 99 |

Durante una partida se podrán descubrir casillas, colocar y quitar banderas,
ver la expansión automática de las casillas vacías y consultar el temporizador.
La partida termina al descubrir una mina o al revelar todas las casillas sin
mina.

## Estructura prevista

El código se organiza separando el motor de las capas de interfaz:

```text
.
├── diagramas/  # Diagrama de clases y otros diagramas del diseño
├── reportes/   # Reporte técnico y reporte de uso de modelo de lenguaje
├── src/
│   └── buscaminas/
│       ├── model/       # Estado del tablero y reglas independientes de Tkinter
│       ├── view/        # Ventana y componentes gráficos
│       └── controller/  # Eventos y comunicación entre modelo y vista
├── tests/      # Pruebas unitarias del motor
├── .gitignore
├── Proyecto2_MyP20271.pdf
└── README.md
```

## Tecnologías

- **Python 3:** permite mantener las reglas del motor claras y fáciles de probar.
- **Tkinter:** biblioteca gráfica estándar de Python para construir la ventana
  y recibir eventos del ratón, sin agregar dependencias gráficas externas.
- **pytest:** herramienta de desarrollo para ejecutar las pruebas unitarias.

El modelo no importa Tkinter. La interfaz se comunica con el motor mediante
acciones y snapshots; el modelo publica cambios a observadores registrados sin
depender de una ventana concreta.

## Ejecución

El motor y sus pruebas ya están en desarrollo. El punto de entrada de la
interfaz gráfica se agregará cuando se integre el trabajo de vista y
controlador; entonces se documentará aquí el comando para iniciar el juego.

## Preparación y pruebas

Se necesita Python 3. Para instalar las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Para ejecutar las pruebas del motor desde la raíz del repositorio:

```bash
python -m pytest -q
```

Las pruebas del motor no necesitan abrir la interfaz gráfica.

## Motor del juego

`MinesweeperGame` recibe filas, columnas y posiciones de minas, de modo que
puede usarse con la estrategia aleatoria de la partida o con posiciones fijas
en pruebas. Su API principal es:

- `reveal(row, column)`: descubre una casilla, expande los espacios vacíos y
  actualiza el estado de victoria o derrota.
- `toggle_flag(row, column)`: coloca o quita una bandera en una casilla cubierta.
- `snapshot()`: devuelve una vista inmutable del tablero sin revelar la ubicación
  de minas ocultas.
- `subscribe(callback)`: registra un observador para recibir snapshots después
  de cambios; devuelve una función para cancelar la suscripción.

`MoveResult` informa si la acción cambió el tablero, qué casillas se
descubrieron y si fue la primera jugada. Esto permite que el controlador inicie
el temporizador al primer descubrimiento y lo detenga al finalizar la partida.

## Integrantes

- Julio César Islas Espino
- Jesús Eliuth Martínez Mendoza
- Miroslava Mora Espinosa
- Tintos Fabela Leonardo R.

## Entregables

- Código fuente del juego.
- Pruebas unitarias del motor.
- README con instrucciones para instalar, ejecutar y probar.
- [Reporte técnico](reportes/reporte_tecnico.md), que incluirá los patrones
  seleccionados y el diagrama de clases MVC.
- [Reporte de uso de modelo de lenguaje](reportes/reporte_lm.md).
- [Consigna del proyecto](Proyecto2_MyP20271.pdf).

Los reportes y diagramas se agregarán a sus carpetas conforme avance el
proyecto.

## Cómo colaborar

1. Clona el repositorio:

   ```bash
   git clone https://github.com/Islas-Kryga/Equipo-Azul-Proyecto-2.git
   cd Equipo-Azul-Proyecto-2
   ```

2. Crea una rama para tu parte:

   ```bash
   git checkout -b nombre-de-tu-rama
   ```

3. Guarda los cambios y crea un commit:

   ```bash
   git add .
   git commit -m "Describe el cambio"
   ```

4. Sube la rama y abre un Pull Request hacia `main`:

   ```bash
   git push -u origin nombre-de-tu-rama
   ```

Para facilitar la integración, acuerden las interfaces entre el modelo, la
vista y el controlador antes de conectar sus módulos. No trabajen directamente
en `main`; integren los cambios mediante Pull Requests revisados por el equipo.
