# Image → PUML: Visual Analysis Guide

Step-by-step guide for converting an image or screenshot of a diagram into PlantUML code.

## Step 1: Identify Diagram Type

| Visual Features | Diagram Type |
|-----------------|-------------|
| Vertical dashed lifelines, horizontal arrows, activation boxes | **Sequence** |
| Rectangles with 2-3 compartments (name / fields / methods) | **Class** |
| Rounded rectangles + diamonds + arrows with flow labels | **Activity / Flowchart** |
| Oval shapes + stick figures + `<<include>>` / `<<extend>>` | **Use Case** |
| Rectangles with PK/FK labels, crow's foot notation on lines | **Entity Relationship** |
| Boxes inside larger boxes (servers, packages, clouds) + ball-socket connectors | **Component** |
| Boxes inside nodes/clouds + artifact icons | **Deployment** |
| Rounded boxes + `[*]` start/end circles + labelled transitions | **State** |
| Central node + radiating branches | **Mind Map** |
| Horizontal bars on a date timeline | **Gantt** |
| Form-like grid: input fields, buttons, checkboxes, dropdowns | **Wireframe (Salt)** |

## Step 2: Extract Elements by Type

### Sequence
1. Participants (left-to-right order): `actor`, `participant`, `database`, etc.
2. Arrow direction and type (solid=sync, dashed=response, x=lost)
3. Message labels on each arrow
4. Groups/boxes: `alt/else/end`, `loop`, `opt`, `par`, `group`
5. Notes and dividers

### Class
1. All class/interface/abstract/enum names
2. For each: visibility (+/-/#/~), attribute `name:Type`, method `name(params):return`
3. Stereotypes: `<<interface>>`, `<<abstract>>`, `<<service>>` etc.
4. Relationships and their types (see table below)
5. Multiplicities at relationship ends: `1`, `0..*`, `1..*`, `0..1`

**Class relationship identification:**
| Visual | PlantUML | Meaning |
|--------|----------|---------|
| Solid line + hollow triangle at parent | `<|--` | Inheritance / extends |
| Dashed line + hollow triangle | `<|..` | Realization / implements |
| Solid line + hollow diamond at whole | `o--` | Aggregation |
| Solid line + filled diamond at whole | `*--` | Composition |
| Dashed arrow | `..>` or `-->` | Dependency / usage |
| Solid line (no diamond/triangle) | `--` | Association |

### Activity / Flowchart
1. Start and end points
2. All action rectangles (in order)
3. Decision diamonds: condition text + branch labels (yes/no, true/false)
4. Loop structures: where they begin and end, exit condition
5. Parallel branches: fork and join points
6. Swimlane labels (column/row headers)

### Entity Relationship
1. All entity names
2. For each attribute: name, data type, PK/FK/not-null markers
3. Relationship lines: cardinality notation at each end
4. Relationship labels / verbs

**ER cardinality reading:**
| Visual notation | PlantUML |
|-----------------|---------|
| Single vertical bar `|` | `||` (exactly one) |
| Circle + bar `o|` | `o|` (zero or one) |
| Crow's foot + circle `>{o` | `o{` (zero or many) |
| Crow's foot + bar `>|{` | `|{` (one or many) |

### Component / Deployment
1. All component/node names and their stereotypes
2. Grouping hierarchy: which components are inside which packages/nodes/clouds
3. Connection types: plain arrow, ball-socket, dependency
4. Connection labels and directions

### State
1. Initial `[*]` and final `[*]` markers
2. All state names
3. Each transition: source, target, trigger/event label
4. Nested states (states within states)
5. Entry/exit actions if shown

## Step 3: Generate PUML

Rules:
- Start with `@startuml` and `title [original title if visible]`
- Add `skinparam shadowing false` for clean output
- Reproduce element **names exactly** as shown in the image
- For ambiguous arrow types → default to `->` (sync); use `-->` for returns
- Maintain the spatial ordering (left-to-right, top-to-bottom) of the original
- Do NOT invent structure not visible in the image

## Step 4: Validate & Compare

```bash
# Validate syntax
python3 scripts/render.py /tmp/generated.puml --check

# Render
python3 scripts/render.py /tmp/generated.puml -f svg -o /tmp/

# View and compare with original
```

## Step 5: Iterative Refinement

If rendered output differs from original:
1. **Layout differs** → Add `left to right direction`, `skinparam nodesep 60`, `skinparam ranksep 80`
2. **Missing elements** → Re-examine image; add skipped nodes/relationships
3. **Wrong arrow type** → Cross-check the relationship table above
4. **Grouping wrong** → Re-check which elements are inside which containers

## Ambiguity Handling

| Situation | Resolution |
|-----------|-----------|
| Arrow type unclear | Use `->` and note it may be `-->` |
| Relationship type unclear in class diagram | Use `--` (plain association) with label |
| Multiplicity not visible | Omit (don't guess) |
| Partial diagram / cut off | Generate what is visible; note truncation |
| Hand-drawn / sketchy style | Still parse as structural diagram; apply `skinparam handwritten true` |

## Output Quality Checklist

- [ ] Diagram type correctly identified
- [ ] All visible participants/entities/classes captured
- [ ] All relationships with correct types
- [ ] Labels and names transcribed accurately
- [ ] Correct `@start` / `@end` pair used
- [ ] Syntax validated (`--check`)
- [ ] Rendered and compared visually to original

---

## Addendum: Additional Diagram Types (Visual Identification)

| Visual Features | Diagram Type | Tag |
|-----------------|-------------|-----|
| ASCII art boxes with `+--+` borders | Ditaa | `@startditaa` |
| Labeled boxes with ArchiMate colour bands (Business=yellow, App=blue, Tech=green) | Archimate | `@startuml` + `archimate` kw |
| Network topology with server/cloud icons and labeled segments | Network nwdiag | `@startuml` + `nwdiag {}` |
| Horizontal bars on labelled timeline (days/weeks/months) | Gantt | `@startgantt` |
| Tree with work packages and hierarchy | WBS | `@startwbs` |
| Central node with radiating tree branches | MindMap | `@startmindmap` |
| Form layout: input boxes, buttons, checkboxes, dropdowns | Wireframe (Salt) | `@startsalt` |
| Structured JSON/key-value display | JSON | `@startjson` |
| YAML-format hierarchical key-value | YAML | `@startyaml` |
| Mathematical formula / LaTeX notation | Maths | `@startmath` / `@startlatex` |
| Old-style activity with `(*) -->` and rounded rectangles | Activity Legacy | `@startuml` (legacy syntax) |
| Vertical lifelines with clock ticks and state transitions | Timing | `@startuml` (robust/concise/binary/clock/analog) |
