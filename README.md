# AXIOM-Scientific-Graphing-Calculator
A feature-rich graphing calculator built with Python, Tkinter, and Matplotlib. Supports multi-curve plotting, live expression preview, calculation history, unit conversion across 6 categories, RAD/DEG toggle, and a built-in function reference  all wrapped in a custom warm terminal UI with no external frameworks.
# Graph Calc

A scientific graphing calculator built with Python and Tkinter. Supports expression evaluation, function plotting, and keyboard input with a dark themed interface.

---

## Preview

The calculator runs as a desktop window split into two panels. The left side has the display and keypad. The right side shows the plot canvas with adjustable x range controls.

---

## Features

**Calculator**
- Standard arithmetic with operator precedence
- Scientific functions: sin, cos, tan, sqrt, log, ln, exp, arcsin, arccos, arctan, cbrt
- Constants: pi, e, tau
- Superscript notation: x², x³, xʸ
- Keyboard input support
- Live result display after pressing equals

**Graphing**
- Plots any f(x) expression using numpy over a custom x range
- Adjustable x min and x max
- 3000 point resolution for smooth curves
- Fill under curve with transparency
- Grid lines, spine styling and zero axis lines
- Auto masks infinity values so tan(x) and 1/x do not break the axis limits

**Preset Functions**
- One click presets: y = x, Parabola, Cubic, Sine, Cosine, e^x

**Keyboard Shortcuts**
- Enter: calculate if numeric, graph if expression contains x
- Backspace: delete last character
- Escape: clear display

---

## Requirements

Python 3.8 or higher with the following packages:

```
numpy
matplotlib
tkinter
```

tkinter is included with most Python installations. If it is missing install it through your system package manager.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/graph-calc.git
cd graph-calc
```

Install dependencies:

```bash
pip install numpy matplotlib
```

Run the app:

```bash
python graphing_calculator.py
```

---

## Usage

Type any math expression into the display and press equals or hit Enter to evaluate.

To plot a function type an expression using x as the variable, for example:

```
sin(x)
x**2 + 2*x - 1
exp(x) / 10
sqrt(abs(x))
```

Set the x range using the min and max fields below the canvas then press GRAPH or Enter.

Use the preset buttons along the bottom to load common functions instantly.

---

## Supported Functions

| Function | Description |
|---|---|
| sin(x), cos(x), tan(x) | Trigonometric |
| arcsin(x), arccos(x), arctan(x) | Inverse trig |
| sqrt(x) | Square root |
| cbrt(x) | Cube root |
| log(x) | Base 10 logarithm |
| ln(x) | Natural logarithm |
| exp(x) | e raised to x |
| abs(x) | Absolute value |
| floor(x), ceil(x) | Rounding |
| pi, e, tau | Constants |

---

## Project Structure

```
graph-calc/
    graphing_calculator.py    main application
    README.md
```

---

## Tech Stack

Python · Tkinter · Matplotlib · NumPy

---

## License

MIT
