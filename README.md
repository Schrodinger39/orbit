# ORBIT

*A quiet space station. A small set of instructions. Eleven puzzles to think through.*

ORBIT is a visual programming puzzle game built with Python and CMU Graphics. Drag instruction cards into a program, connect jumps, and watch a robot process packets of numbers. Each mission asks you to turn an input sequence into the correct output using memory, arithmetic, loops, and conditions.

## Why I designed ORBIT

I wanted to help beginners practice computational thinking through a game where they can see a program run. Instruction cards make the logic tangible: you can rearrange a sequence, follow a loop, and watch how each step changes the value in the robot's hand or in memory.

The space-station setting gives those abstract operations a playful context. The missions gradually move from forwarding packets to comparing values, building sequences, testing primes, and sorting. My goal is to encourage experimentation: build an idea, step through it, understand what went wrong, and try again.

Getting the right answer is only the beginning. ORBIT also lets players compare program length and execution cost, exploring how different solutions can trade fewer cards for fewer steps. The answer archive makes working examples available to study and modify along the way.

## Start the game

Use Python 3.12, the version used during development. Download or clone this repository, then open a terminal in the folder containing the three Python files:

```sh
python3 -m pip install cmu-graphics==2.0.5
python3 main.py
```

CMU Graphics opens the game in a desktop window. Keep `main.py`, `machine.py`, and `levels.py` together in the same folder.

## Your first mission

1. Select **First Contact** on the orbital map. Your goal is to forward every incoming packet in its original order.
2. Drag **READ** from the toolbox into your program, then place **SEND** below it.
3. Add **JUMP**. Drag the small dot on its card onto the **READ** row to connect the loop.
4. Press **STEP** to follow the program one instruction at a time, or **RUN** to watch it execute.
5. Select **VERIFY ALL** to check your program against all three test queues.

You have made a loop: read a packet, send it, and return for the next one. An empty input ends the run when the program next tries to read.

## Build and edit programs

- Drag cards to insert or reorder them. Jump connections follow their target cards when you move them.
- For **STORE**, **LOAD**, **ADD**, and **SUB**, select a card and choose memory cell **0–7** by clicking a memory tile or pressing its number.
- Connect **JUMP**, **ZERO**, and **NEG** by dragging their dots onto a destination row. Reconnect a jump if you delete its destination.
- Drop a card on **DELETE**, or select it and press **Delete** or **Backspace**, to remove it.
- Pause execution and let the current animation finish before editing. Use the arrow keys to scroll longer programs.

### The instruction set

| Card | What it does |
| --- | --- |
| READ | Takes the next input packet into the robot's hand. |
| SEND | Sends the held value to the output, then empties the hand. |
| STORE | Copies the held value into the selected memory cell. |
| LOAD | Copies a memory cell's value into the hand. |
| ADD | Adds a memory cell's value to the held value. |
| SUB | Subtracts a memory cell's value from the held value. |
| JUMP | Always jumps to its connected destination. |
| ZERO | Jumps if the held value is zero; otherwise continues. |
| NEG | Jumps if the held value is negative; otherwise continues. |

Memory starts as **[0, 1, 3, empty, empty, empty, empty, empty]** on each reset. All eight cells are writable. Reading empty memory or using an instruction that needs a value when the hand is empty causes an error.

## Controls

| Control | Action |
| --- | --- |
| RUN / Space | Run or pause. |
| STEP / S | Execute one instruction. |
| RESET / R | Reset the input and machine while keeping your program. |
| VERIFY ALL / V | Check all three test queues and open the results. |
| TEST 1 / 2 / 3 buttons | Choose a sample input queue. |
| FAST / SLOW | Change animation speed. |
| H | Toggle help. |
| Esc | Close an overlay or cancel a drag. |
| HINT | Show a clue for the current mission. |

## Explore all eleven missions

All missions are available from the map, so you can practice in order or choose a challenge.

| Mission | Challenge |
| --- | --- |
| First Contact | Forward every packet in order. |
| Solar Amplifier | Double each value. |
| Positive Channel | Keep only strictly positive values. |
| Delta Array | Subtract the second value of each pair from the first. |
| Valley Selector | Choose the smaller value from each pair. |
| Accumulator | Produce a running total. |
| Product Reactor | Multiply pairs through repeated addition. |
| Division Engine | Compute integer division by three. |
| Fibonacci Relay | Generate the requested Fibonacci values. |
| Prime Observatory | Determine whether each number is prime. |
| Three-Body Sort | Sort groups of three values. |

## Learn, verify, and improve

A successful program must consume all input and produce the exact expected output in the correct order. **VERIFY ALL** checks all three fixed test queues. Its report shows your card count, average executed steps per test, reference costs, and your best results for the current session. Smaller programs and faster programs are separate goals; try different approaches to explore the tradeoff. Animation speed does not change these measurements.

Open **ANSWER ARCHIVE** on the map or **ANSWERS** inside a mission to read an algorithm explanation and inspect a working solution. **LOAD THIS SOLUTION** replaces that mission's current program with editable cards, so you can step through it and experiment. Viewing an answer alone does not replace your work.

Programs are limited to 64 cards and each test to 5,000 instructions. Passing the supplied tests is useful feedback, not a proof for every possible input. Programs and personal bests are stored only for the current session and are lost when you close the game.
