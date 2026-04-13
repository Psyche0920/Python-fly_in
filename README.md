*This project has been created as part of the 42 curriculum by wehan.*

---

# Description

This project implements a drone routing and simulation system that moves drones from a start zone to an end zone through a graph of interconnected zones.

The goal is to:
- minimize total simulation turns
- respect all movement constraints
- respect capacity violations(respect all movement, zone capacity, and connection capacity constraints)
- avoid conflicts (prevent invalid movements and conflicts between drones)

The system includes:
- a custom graph implementation (no external libraries)
- a parser for input files
- a pathfinding algorithm (Dijkstra-based)  
- a turn-based simulation engine
- a visual representation (terminal output and optional UI)

---

# Instructions

## Requirements

- Python 3.10+
- No external dependencies (only Python standard library)

---

## Installation

No installation is required. 
(Optional)
make install

---

## Run

Run the simulation with a map file:
python3 main.py <map_file_name>

Example:
python3 main.py maps/example.txt

If no map file is provided, the program uses the default file:
default.txt

You can also use:
make run

To lauch the graphical interface with the default map:
make run-ui

---
 
## Linting / Type Checking (optional)

make lint
make lint-strict

---

# Input Format

The input file describes:
- number of drones
- zones
- connections

---

## Drone Definition

nb_drones: <positive integer>

---

## Zone Definition

<type>: <name> <x> <y> [metadata]

Types:
- start_hub
- end_hub
- hub

---

### Zone Metadata (optional)

- zone = normal (default)
- max_drones = 1 (default)
- color = none (optional)

---

### Zone Types

- normal → cost 1
- restricted → cost 2 (takes 2 turns)
- priority → cost 1 (preferred in pathfinding)
- blocked → inaccessible

## Connection Definition

connection: <zone1>-<zone2> [metadata]
Metadata:
- max_link_capacity = 1 (default)

---

## Example

nb_drones: 2

start_hub: A 0 0
end_hub: C 2 2

hub: B 1 1 [zone=restricted]

connection: A-B
connection: B-C

---

# Output Format

The simulation prints one line per turn.

---

## Format

D<ID>-<zone>
or (restricted movement)
D<ID>-<zone1>-<zone2>

---

## Rules

- each line represents one simulation turn
- movements in the same turn are separated by spaces
- drones that do not move in a turn are omitted
- a drone entering a restricted zone is first printed as a transit - movement
- on the next turn, that drone is printed at arrival in the restricted zone
- drones reaching the end zone are considered delivered and are no longer tracked
- the simulation stops when all drones have reached the end zone

---

## Example Output

D1-A-B
D1-B D2-A-B
D1-C D2-B
D2-C

---

# Algorithm and Implementation Strategy

## Core Strategy: Dynamic Replanning with Dijkstra

This project uses a dynamic pathfinding strategy based on Dijkstra’s algorithm.

Instead of computing a fixed global plan, each drone makes decisions at every turn
based on the current state of the simulation.


## Initial Path (Baseline Validation)

At the start of the simulation, a shortest path from the start zone to the end zone is computed.

This ensures:
- the graph is reachable
- there exists at least one valid solution

---

## Dynamic Replanning (Main Mechanism)

At each turn, every drone recomputes its path using Dijkstra from:

- the start zone (initial turn)
- or its current position (subsequent turns)

This allows drones to dynamically adapt to congestion and changing conditions.

---

## Capacity-Aware Pathfinding

The algorithm considers real-time constraints using:

- `full_zones`: zones that are at capacity in the current turn
- `full_links`: connections that are saturated in the current turn

---

### Important Design Choice

These constraints are applied **only to the immediate next move**, not to the entire future path.

This means:

- A drone will not enter a full zone or saturated link **during the current turn**
- However, future zones are still considered reachable, because they may become free in later turns

This avoids overly conservative behavior and allows drones to:

- wait naturally when blocked
- continue progressing once capacity is freed
- maintain flow through the graph

## Movement Cost Model

Dijkstra is adapted to handle different zone types:

- normal → cost = 1
- restricted → cost = 2 (two turns)
- priority → cost = 1 (preferred)
- blocked → ignored (not traversable)

---

## Tie-breaking Strategy

Paths are compared using:

(cost, priority_score)

Where:

- cost = total travel time
- priority_score = number of priority zones

This ensures:

- deterministic behavior
- preference for priority zones when costs are equal

## Simulation Model

# Turn-Based Simulation Model

The simulation operates in discrete turns.

At each turn:

1. Drones in transit (restricted zones) complete their movement if needed
2. Other drones attempt to move one step
3. Capacity constraints are checked dynamically

Important properties:

- Drones moving out of a zone free capacity in the same turn
- A zone that is full in one turn may become available in the next
- All decisions are recalculated at every turn

---

## Constraint Handling

Constraints are handled at two levels:

1. Pathfinding level
- avoids invalid moves early:
	- full zones
	- full links
2. Execution level
- ensures correctness in sequential simulation:
	- final capacity validation
	- conflict prevention

## Design Philosophy

This implementation focuses on:

- correctness over global optimality
- simplicity and clarity
- deterministic behavior
- respecting all constraints strictly

It does not compute a globally optimal schedule, but produces efficient and valid solutions that respect all constraints.

## Intuition

The system behaves like a real traffic system:

- drones move forward when possible
- wait when temporarily blocked
- re-evaluate decisions continuously

# Visual Representation

The simulation provides both:
- terminal-based output
- graphical UI using Tkinter

---

## Features

- step-by-step movement visualization
- clear drone identifiers (D1, D2, ...)
- readable movement tracking
- optional support for zone colors

---

## Benefits

This improves:
- understanding of drone behavior  
- debugging of capacity constraints 
- validation of movement rules  
- overall clarity of the simulation

---

## Why not Pygame

Pygame was not used because:

it is an external dependency
it adds unnecessary complexity
the project only requires simple and clear visualization

Tkinter (standard library) and terminal output are sufficient and compliant with project requirements.

---

# Project Structure

main.py        # entry point  
parser.py      # input parsing  
graph.py       # graph implementation  
simulation.py  # simulation engine  
formatter.py   # output formatting  
ui.py          # visualization  

---

# Resources

- Dijkstra’s algorithm (https://www.youtube.com/watch?v=XB4MIexjvY0)
- Python heapq documentation (https://www.youtube.com/watch?v=HqPJF2L5h9U)
- Python tkinter documentation (https://www.youtube.com/watch?v=lyoyTlltFVU&list=PLZPZq0r_RZOOeQBaP5SeMjl2nwDcJaV0T)
- AI was used for:
    - learning heapq documentation
    - understanding UI design
    - reviewing edge cases and logic explanations
    - reduce repetitive or tedious tasks

