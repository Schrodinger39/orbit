# ORBIT / The Quiet Station

Andrew ID: **kangjiey** | Python + CMU Graphics MVC | Version 2

An original visual programming game with **11 missions**, a draggable card editor, an answer archive,
connected jump arrows, an illustrated workshop and measurable optimization goals.
All interface text, source comments and documentation are in English.

## Run

Open `hw7_kangjiey` on your Desktop in Kiro. In the project terminal:

```sh
python3 -m pip install -r requirements.txt
python3 main.py
```

Tested with Python 3.12 and CMU Graphics 2.0.5 on macOS. Use a real terminal if an
IDE's noninteractive output panel closes the CMU Graphics console immediately.
Dependencies are installed separately and are not included in the submission ZIP.

## Build a program by dragging

1. Select a mission on the map. All missions are available for practice.
2. Drag READ from the toolbox into the program. Drag SEND below it.
3. Drag JUMP below SEND. Drag the small dot on the JUMP card onto the READ row.
   The arrow now points back to READ. This solves mission 1.
4. Drag existing cards to reorder them. Drop in the upper/lower half of a row to
   insert before/after it. Drop a card on DELETE, or select it and press Delete.
5. For STORE, LOAD, ADD or SUB, select the card and click a memory address, click
   a memory tile in the workshop, or press a number from 0 through 7. Choosing
   an address before dragging also sets the operand of a new memory card.
6. Drag any jump dot again to change its destination. Connections follow the
   target card when cards are inserted or reordered. Deleting a target leaves
   the jump unconnected and produces a helpful error until you reconnect it.
7. Use the up/down controls or arrow keys to scroll long programs. Hold a dragged
   card or jump wire near the top/bottom edge to auto-scroll to off-screen rows.

RUN / Space runs or pauses. STEP / S executes one instruction. RESET / R restores
the input and machine state, keeping your code. FAST/SLOW changes animation speed.
TEST 1/2/3 selects a sample queue. VERIFY ALL / V validates all three queues and
opens the performance report. RESET cancels verification. H opens help; Esc closes
an overlay or cancels a drag. HINT shows a mission-specific clue.

Editing requires pausing and letting the current movement finish. Programs are
limited to 64 cards and each test has a 5,000-instruction safety limit. Programs,
certifications and personal bests are kept only for the current app session.

## Instruction rules

| Instruction | Meaning |
| --- | --- |
| READ | Take the next input, replacing the held value. Empty input ends and checks the run. |
| SEND | Send the held value, then empty the hand. |
| STORE | Copy the held value into memory; keep the held value. |
| LOAD | Copy memory into the hand; leave memory unchanged. |
| ADD / SUB | Add/subtract the selected memory value from the held value. |
| JUMP | Follow the connected arrow unconditionally. |
| ZERO | Follow the arrow only if the held value is zero. |
| NEG | Follow the arrow only if the held value is negative. |

READ/SEND correspond to INBOX/OUTBOX; STORE/LOAD correspond to COPYTO/COPYFROM;
ZERO/NEG correspond to JUMPIFZERO/JUMPIFNEG.

Memory starts as **[0, 1, 3, empty, empty, empty, empty, empty]** for every test.
All eight cells are writable. If you overwrite a constant, it stays overwritten
until reset. Empty-hand operations and reads from empty memory produce errors.
All input must be consumed, and the output must match exactly in order and length.
The gold marker shows the last animated instruction; the teal triangle shows
where execution will continue. Displayed rows start at 1; internal indices at 0.

## Campaign and difficulty

The campaign has **11 original missions**, arranged as circular stations along
an orbital path rather than a rectangular grid. All are available for practice.
Each has three fixed queues, including relevant edge cases.

| Mission | Main concepts |
| --- | --- |
| 1. First Contact | READ, SEND and a reusable loop |
| 2. Solar Amplifier | Memory and doubling |
| 3. Positive Channel | Negative/zero filtering |
| 4. Delta Array | Ordered pair subtraction |
| 5. Valley Selector | Comparing and preserving two values |
| 6. Accumulator | State across multiple inputs |
| 7. Product Reactor | Repeated addition and zero shortcuts |
| 8. Division Engine | Repeated subtraction and quotient counting |
| 9. Fibonacci Relay | Multiple counters and intermediate values |
| 10. Prime Observatory | Nested loops and trial division |
| 11. Three-Body Sort | A compare/swap sorting network |

The final missions are significantly harder. The sorting reference uses 43 cards;
the prime reference uses 35 cards and executes 781 instructions across its queues.
These are original missions, not reproductions of HRM's official level content.

## Answer Archive

Click ANSWER ARCHIVE on the map or ANSWERS in a mission. Every mission has:

- An explanation of the solution's algorithm.
- Its complete instruction sequence, with human-readable jump line numbers.
- Measured code size and average instruction count across all three tests.
- A LOAD THIS SOLUTION button for stepping through or experimenting with it.

Use PREV/NEXT to change missions and the up/down buttons or keys to scroll long
answers. Viewing an answer never changes your program. Loading a solution
**replaces the selected mission's program** with editable cards and connected
arrows. RETURN TO MY PROGRAM keeps your existing code.

These are efficient, tested reference solutions, **not proven globally fastest
solutions**. Two references were improved after measurement: multiplication from
226 to 192 total instructions, and prime testing from 942 to 781. Their extra
branches trade code size for fewer executed instructions. You can still try to
beat them; the report preserves your own best costs separately.

## Understand the optimization report

A single sample passing is not enough for certification. Click VERIFY ALL:

- **Code size:** number of cards, including unreachable/unused ones. Lower is better.
- **Average steps/test:** total executed instructions across the three queues,
  divided by three. Lower is better. The final empty-READ termination check is
  excluded from the step count.
- **Packets/100 steps:** 100 times total correct output packets divided by total
  executed instructions. Higher is better **within the same mission**. Missions
  with different output requirements should not be compared by this number.
- **Reference:** measured costs from a working reference program.
- **Session best:** your lowest measured code size and execution cost. These are
  tracked independently and may come from different versions of your program.
- **Change from best:** the total instruction difference from your previous best.

These are algorithmic costs, not wall-clock speed or hardware benchmarks.
FAST/SLOW and robot animation do not affect them. Editing clears the current
program's certification but keeps past bests for comparison. Fixed tests are
finite checks, not a proof that a solution works for all possible inputs.

## Code structure and explainability

- **main.py:** MVC setup, input handlers, drag/drop editing, stable jump links,
  animation, incremental verification, mission map, workshop and results drawing.
- **machine.py:** the interpreter. `newMachine` creates a list of state fields.
  Named index constants (`PC`, `HELD`, etc.) explain each field. `stepMachine`
  executes one instruction using if/elif and returns an animation event.
- **levels.py:** 11 mission records, reference solutions and `expectedFor`, which computes the correct
  output using beginner arithmetic, loops, conditions and lists.

A card is `[command, operand, identity]`. The identity is a unique integer that
stays with the card during reordering. A jump stores its target's identity.
`findLine` scans the program to find that identity's current row. This avoids
silently breaking loops when lines move, without requiring dictionaries or classes.

The verifier uses the same interpreter as animated execution. `verificationFrame`
executes at most 100 instructions per frame, so even an endless loop does not
freeze the window. Drawing functions read model data without changing it.

Drawing coordinates are scaled at the drawing boundary to fit a 1152 x 738
window. Mouse input is converted back to the same logical layout coordinates.

No custom classes, dictionaries, recursion, external GUI framework, image assets
or sound files are required. CMU Graphics supplies `app` and the drawing functions.

## Five-minute submission video

Use **VIDEO_SCRIPT.md** for the full English narration, screen directions,
function locations, and rehearsal checks. The goal is to help beginners practice
computer science thinking through visible program execution.

- **0:00-1:00:** Demonstrate doubling in Solar Amplifier, STEP, and VERIFY ALL.
- **1:00-2:00:** Explain MVC and the roles of levels.py, machine.py, and main.py.
- **2:00-2:20:** Show levels.py lines 277-278: expected-output calculation.
- **2:20-2:55:** Explain machine.py assignments for card fields, STORE, and ADD.
- **2:55-3:20:** Explain mouse coordinates and rowAt in main.py.
- **3:20-4:15:** Trace the jump-target assignment at main.py line 428 and findLine.
- **4:15-5:00:** Explain the animation formula and elif branches line by line.

The script includes exact code excerpts plus additional study notes that are not
part of the spoken recording.

Six highlighted existing AI records are indexed in **ai_prompts/README.txt**.
The original records remain in its archive; selection does not narrow AI's actual
contributions or replace the course requirement to retain all AI exchanges.

Record your own video and put its real accessible URL in `video_link`. Fill in
only your actual student work in `time_log`; agent runtime is not student effort.
Check your instructor's complete current specification. After updating these
files, re-create the ZIP from the **hw7_kangjiey folder**, excluding dependencies,
virtual environments, caches and backup folders.
