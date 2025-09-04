# Pansens

Pansens is a pointer speed converter between different platforms. Currently it supports conversion between Windows and KDE.

It's called Pansens because it has a similar approach to Pandoc for converting between sensitivities.

## Usage

```sh
❯ python main.py --help
usage: main.py [-h] {windows,kde} {windows,kde} value

Convert mouse sensitivity between platforms.

positional arguments:
  {windows,kde}  Source platform
  {windows,kde}  Target platform
  value          Sensitivity value (tick for Windows, float for KDE)

options
  -h, --help     show this help message and exit
```

## Examples

Convert Windows sensitivity 10 to KDE:

```sh
❯ python main.py windows kde 7
Converted sensitivity: KDESensitivity(value=-0.375)
```

Convert KDE sensitivity 1.0 to Windows:

```sh
❯ python main.py kde windows -0.375
Converted sensitivity: WindowsSensitivity(tick=7)
```
