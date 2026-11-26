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

La estructura final se ajustará a la implementación acordada por el equipo.
Como punto de partida, organizaremos el código por responsabilidades:

```text
.
├── diagramas/  # Diagrama de clases y otros diagramas del diseño
├── reportes/   # Reporte técnico y reporte de uso de modelo de lenguaje
├── src/
│   ├── model/       # Estado del tablero y reglas independientes de la interfaz
│   ├── view/        # Ventana y componentes gráficos
│   └── controller/  # Eventos del ratón y comunicación entre modelo y vista
├── tests/      # Pruebas unitarias del motor y pruebas adicionales
├── Proyecto2_MyP20271.pdf
└── README.md
```

## Ejecución

El lenguaje y la biblioteca gráfica todavía están por acordarse. En cuanto
estén definidos e implementados, aquí se documentarán los requisitos de
instalación y el comando exacto para iniciar el juego.

## Preparación y pruebas

Las instrucciones para instalar dependencias y ejecutar las pruebas unitarias
se agregarán cuando se elijan el lenguaje, las herramientas y el framework de
pruebas. Las pruebas cubrirán el motor sin depender de la interfaz gráfica.

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
