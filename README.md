*This project has been created as part of the 42 curriculum by wehan.*

---

## Description

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

## Instructions

### Requirements

- Python 3.10+
- No external dependencies (only Python standard library)

---

### Installation

No installation is required. 
(Optional)
make install

---

### Run

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
 
### Linting / Type Checking (optional)

make lint
make lint-strict

---

## Input Format

The input file describes:
- number of drones
- zones
- connections

---

### Drone Definition

nb_drones: <positive integer>

---

### Zone Definition

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

### Connection Definition

connection: <zone1>-<zone2> [metadata]
Metadata:
- max_link_capacity = 1 (default)

---

### Example

nb_drones: 2

start_hub: A 0 0
end_hub: C 2 2

hub: B 1 1 [zone=restricted]

connection: A-B
connection: B-C

---

## Output Format

The simulation prints one line per turn.

---

### Format

D<ID>-<zone>
or (restricted movement)
D<ID>-<zone1>-<zone2>

---

### Rules

- each line represents one simulation turn
- movements in the same turn are separated by spaces
- drones that do not move in a turn are omitted
- a drone entering a restricted zone is first printed as a transit - movement
- on the next turn, that drone is printed at arrival in the restricted zone
- drones reaching the end zone are considered delivered and are no longer tracked
- the simulation stops when all drones have reached the end zone

---

### Example Output

D1-A-B
D1-B D2-A-B
D1-C D2-B
D2-C

---

## Algorithm and Implementation Strategy

### Pathfinding Approach

The project uses a Dijkstra-based algorithm to compute the shortest path from start to end.

This is required because movement costs are not uniform:
- normal / priority zones → 1 turn  
- restricted zones → 2 turns
- blocked zones → inaccessible

A simple BFS would treat all movements as equal-cost and would not correctly handle weighted movement costs.

---

### Tie-breaking Strategy

Priority zones do not reduce cost.

Instead, paths are compared using:
(cost, priority_score)

This ensures:
- consistent path selection
- deterministic behavior due to consistent tie-breaking and processing order
- preference for priority zones when costs are equal

### Simulation Design

The system is divided into two layers:
1. Pathfinding layer
    - computes optimal path

2. Simulation layer
- enforces:
    - zone capacity
    - connection capacity
    - movement scheduling (applies turn-by-turn movement rules)
    - conflict avoidance (prevents invalid simultaneous moves)

---

### Turn Structure

Each turn has two phases:
1. Finish transit
    - drones moving into restricted zones arrive
2. Move drones
    - all other drones attempt movement

### How Different Zone Types Behave

- normal zone:
entered in one turn
printed as D<ID>-<zone>

- priority zone:
entered in one turn
same movement cost as normal
preferred when path costs are equal

- restricted zone:
entered over two turns
first turn: the drone starts transit and is printed as D<ID>-<from>-<to>
second turn: the drone arrives and is printed as D<ID>-<zone>
the drone cannot wait inside the connection

- blocked zone:
cannot be entered
ignored by pathfinding

---

### Design Decisions

    - restricted zones are implemented as multi-turn movements
    - drones cannot wait inside connections
    - capacity constraints are strictly enforced
    - behavior is deterministic due to consistent processing order and tie-breaking

---

## Visual Representation

The simulation provides both:
- terminal-based output
- graphical UI using Tkinter

---

### Features

- step-by-step movement visualization
- clear drone identifiers (D1, D2, ...)
- readable movement tracking
- optional support for zone colors

---

### Benefits

This improves:
- understanding of drone behavior  
- debugging of capacity constraints 
- validation of movement rules  
- overall clarity of the simulation

---

### Why not Pygame

Pygame was not used because:

it is an external dependency
it adds unnecessary complexity
the project only requires simple and clear visualization

Tkinter (standard library) and terminal output are sufficient and compliant with project requirements.

---

## Project Structure

main.py        # entry point  
parser.py      # input parsing  
graph.py       # graph implementation  
simulation.py  # simulation engine  
formatter.py   # output formatting  
ui.py          # visualization  

---

## Resources

- Dijkstra’s algorithm (https://www.youtube.com/watch?v=XB4MIexjvY0)
- Python heapq documentation (https://www.youtube.com/watch?v=HqPJF2L5h9U)
- Python tkinter documentation (https://www.youtube.com/watch?v=lyoyTlltFVU&list=PLZPZq0r_RZOOeQBaP5SeMjl2nwDcJaV0T)
- AI was used for:
    - learning heapq documentation
    - understanding UI design
    - reviewing edge cases and logic explanations
    - reduce repetitive or tedious tasks

