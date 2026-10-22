<!-- repository-badges:start -->
<div align="center">

[![Contributors](https://img.shields.io/github/contributors/Psyche0920/Python-fly_in?style=for-the-badge)](https://github.com/Psyche0920/Python-fly_in/graphs/contributors)
[![Forks](https://img.shields.io/github/forks/Psyche0920/Python-fly_in?style=for-the-badge)](https://github.com/Psyche0920/Python-fly_in/forks)
[![Stars](https://img.shields.io/github/stars/Psyche0920/Python-fly_in?style=for-the-badge)](https://github.com/Psyche0920/Python-fly_in/stargazers)
[![Issues](https://img.shields.io/github/issues/Psyche0920/Python-fly_in?style=for-the-badge)](https://github.com/Psyche0920/Python-fly_in/issues)
[![License](https://img.shields.io/badge/license-not_specified-lightgrey?style=for-the-badge)](https://github.com/Psyche0920/Python-fly_in)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Weijia_Han-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/weijia-han-6162581b5/)

</div>
<!-- repository-badges:end -->

# 🚁 Fly.in

<p align="center">
  <b>Dynamic Drone Routing & Simulation System</b><br>
  <i>Graph · Dijkstra · Real-Time Simulation · Constraint Optimization</i>
</p>

<p align="center">
  <!-- 🔥 Replace with your actual GIF -->
  <img src="assets/demo.gif" width="700"/>
</p>

---

## 📌 Overview

**Fly.in** is a drone routing and simulation system that transports multiple drones from a **start zone** to an **end zone** across a graph of interconnected zones.

The system is designed to:

* 🚀 minimize total simulation turns
* 🚫 avoid conflicts between drones
* 📦 respect zone and connection capacity constraints
* 🔁 dynamically adapt to congestion in real time

---

## 🧠 Core Concept

> **Dynamic Replanning with Dijkstra at every turn**

Instead of computing a fixed global route, each drone:

* recalculates its path every turn
* adapts to current congestion
* makes locally optimal decisions

---

## ⚙️ Key Features

### 🔹 Graph-Based Routing

* custom graph implementation
* nodes = zones
* edges = connections

---

### 🔹 Dynamic Pathfinding

* Dijkstra algorithm adapted for:

  * weighted zones
  * real-time constraints

---

### 🔹 Capacity-Aware System

Handles:

* full zones (`max_drones`)
* saturated links (`max_link_capacity`)

📌 Constraints are applied only to the **next move**, not the full path.

---

### 🔹 Turn-Based Simulation

* discrete time steps
* simultaneous drone movements
* conflict-safe execution

---

### 🔹 Visualization

* 🖥️ terminal output
* 🎨 optional Tkinter UI

---

## 🔄 System Flow

```txt
                ┌──────────────────────┐
                │     Input File       │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │   Parsing (parser)   │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │ Graph Construction   │
                │     (graph.py)       │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │ Initial Path Check   │
                │     (Dijkstra)       │
                └─────────┬────────────┘
                          │
                          ▼
                ┌────────────────────────────┐
                │      Simulation Loop       │
                └─────────┬──────────────────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Pathfinding     │ │ Constraints    │ │ Execution      │
│ (Dijkstra)      │ │ Checking       │ │ (movement)     │
└───────┬────────┘ └───────┬────────┘ └───────┬────────┘
        │                  │                  │
        └──────────┬───────┴───────┬──────────┘
                   ▼               ▼
             ┌────────────────────────┐
             │    Output / Display    │
             │ formatter + UI         │
             └────────────────────────┘
```

---

## 🧩 Architecture

```txt
            +------------------+
            |     parser.py     |
            +--------+---------+
                     |
                     v
            +------------------+
            |     graph.py      |
            +--------+---------+
                     |
                     v
            +------------------+
            |  simulation.py    |
            +--------+---------+
                     |
      +--------------+--------------+
      |                             |
      v                             v
formatter.py                   ui.py
(output)                     (visual)
```

---

## 🔄 Turn Execution Logic

```txt
        TURN N
          │
          ▼
 ┌──────────────────────┐
 │ Complete transitions │
 │ (restricted zones)   │
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │ Recompute paths      │
 │ (Dijkstra per drone) │
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │ Check constraints     │
 │ (zones + links)       │
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │ Execute movements     │
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │ Print turn output     │
 └──────────────────────┘
```

---

## 🧠 Decision Model

```txt
current_position
        │
        ▼
Run Dijkstra
        │
        ▼
Compute best path
        │
        ▼
Check NEXT move only
        │
        ▼
Move or wait
```

---

## 🚀 Usage

```bash
python3 main.py maps/example.txt
```

Default:

```bash
python3 main.py
```

---

## 🎮 UI Mode

```bash
make run-ui
```

---

## 📥 Input Example

```txt
nb_drones: 2

start_hub: A 0 0
end_hub: C 2 2

hub: B 1 1 [zone=restricted]

connection: A-B
connection: B-C
```

---

## 📤 Output Example

```txt
D1-A-B
D1-B D2-A-B
D1-C D2-B
D2-C
```

---

## 🎨 Visualization

### Terminal

* step-by-step movement
* clean readable output

### UI (Tkinter)

* real-time simulation
* drone tracking
* optional zone colors

---

## 🧠 Design Philosophy

* ✔ correctness over global optimality
* ✔ dynamic adaptation
* ✔ deterministic behavior
* ✔ strict constraint enforcement

---

## 🌍 Real-World Analogy

> behaves like a traffic system

* drones move when possible
* wait when blocked
* re-evaluate continuously

---

## 🎯 Learning Outcomes

* graph algorithms (Dijkstra)
* dynamic systems design
* constraint-based simulation
* real-time decision making
* modular Python architecture

---

## 👤 Author

**wehan / Psyche0920**
🔗 https://github.com/Psyche0920

---

<p align="center">
  ⭐ If you like this project, give it a star!
</p>
