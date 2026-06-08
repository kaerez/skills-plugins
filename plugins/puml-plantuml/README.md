# puml-plantuml (Claude Code plugin)

A full-stack **PlantUML** expert, packaged as a Claude Code plugin. It bundles the
`puml-plantuml` skill, which provides:

- **Authoring** — turn natural-language descriptions into valid PUML.
- **Image → PUML** — reverse-engineer an existing diagram image back into PUML (vision).
- **Local rendering** — render `.puml` to PNG/SVG/PDF **offline**, no internet required.
  Auto-installs PlantUML + Java on first use (macOS / Windows / Linux).
- **Reference coverage** — all 27 chapters of the PlantUML Language Reference Guide
  v1.2025.0 (Sequence, Class, Activity, State, Component, Deployment, Gantt, MindMap,
  C4/AWS/Azure/K8s stdlib, and more).

## Installation

This plugin is published via the marketplace at the root of
[`kaerez/skills-plugins`](https://github.com/kaerez/skills-plugins):

```
/plugin marketplace add kaerez/skills-plugins
/plugin install puml-plantuml@kaerez-skills-plugins
```

To test locally without a marketplace, point Claude Code at this plugin directory:

```
claude --plugin-dir /path/to/skills-plugins/plugins/puml-plantuml
```

## Usage

Once installed, the skill is invoked as:

```
/puml-plantuml:puml-plantuml
```

It also activates automatically when you ask Claude to draw a diagram, create PUML,
convert an image to PUML, render a `.puml` file, or debug PlantUML syntax.

## Prerequisites

- **Python 3.9+** (standard library only — no pip packages needed).
- **Java (JRE 11+)** and **PlantUML** are auto-installed/auto-detected on first render
  (Azul/Zulu, Temurin/Adoptium, OpenJDK, Microsoft JDK, SDKMAN, or Homebrew).

## License

The bundled skill is licensed **AGPL-3.0-only** (see
`skills/puml-plantuml/LICENSE`). PlantUML itself is GPL/LGPL/etc. depending on the
distribution you install.

## Author

Erez Kalman / KSEC · kaerez@gmail.com
