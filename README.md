# 🖥️ InsideOS

**An interactive, educational Operating Systems lab that analyzes your *real* computer: real processes, real RAM, real swap files and real file permissions — visualized step by step. Python + Tkinter (Windows).**

InsideOS is a single-file desktop application built to teach core Operating Systems concepts by letting the learner interact with their own machine instead of watching a static diagram. Open a real program and watch the request travel through the OS; see how a CPU scheduler (Round Robin) would share time between your open windows; fill a 12-block RAM map and trigger real **swap files** on disk; let a FIFO policy close your oldest window; and play with read/write/execute “locks” on real files. A final dashboard audits the whole session.

> The project was designed as an interactive **stand/exhibit** (“stand” appears throughout the code): levels unlock progressively, every concept is explained in plain language, and a glossary explains the jargon.

---

## Table of Contents

1. [Features at a Glance](#-features-at-a-glance)
2. [Project Requirements](#-project-requirements)
3. [Installation](#-installation)
4. [Running the Application](#-running-the-application)
5. [Learning Path: the 6 Levels](#-learning-path-the-6-levels)
6. [How Real vs. Simulated Works](#-how-real-vs-simulated-works)
7. [Key Parameters and Formulas](#-key-parameters-and-formulas)
8. [Files and Folders Created at Runtime](#-files-and-folders-created-at-runtime)
9. [Project Structure](#-project-structure)
10. [Architecture and Design Notes](#-architecture-and-design-notes)
11. [Safety Notes and Limitations](#-safety-notes-and-limitations)
12. [Troubleshooting](#-troubleshooting)
13. [Author, Repository and License](#-author-repository-and-license)

---

## ✨ Features at a Glance

- **Six progressive levels** (locked tabs 🔒 that unlock as you complete the previous one) covering process creation, CPU scheduling, memory management, process control, file protection and a final audit.
- **Real-system integration:** launches actual applications, reads the real process table and real physical RAM via PowerShell, closes real processes with `taskkill`, writes real swap files and sets real read-only file attributes.
- **Animated visualizations** drawn on Tkinter canvases: a 6-stage OS pipeline, ready queue and CPU cards, a live **Gantt chart**, a 12-block RAM map, padlock diagrams, a traffic-light dashboard and RAM bars.
- **Teaching tools:** step-by-step mode, speed slider, pause, plain-language “kitchen” analogies, a **clickable glossary** and explanatory pop-ups on every dashboard element.
- **Safe demo options:** a “demonstration” button in Level 4 shows the warning flow without closing anything real.
- **Full session audit** (text report + interactive dashboard) with counters of everything you did.
- **Zero third-party dependencies** — only the Python standard library.

---

## 📋 Project Requirements

### Functional requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Present six levels in a tabbed interface; each level stays locked (🔒) until the previous one is completed. |
| FR-02 | **Level 1:** let the user pick a program (Chrome, Word, Excel, VS Code, Notepad, Calculator, Paint — or type a custom command), launch it for real and animate the 6-stage path *User → OS → Disk → Kernel → Process Table → RAM*. |
| FR-03 | Detect the launched program’s window, show its **PID** and real **RAM usage (KB)**, map it onto 12 RAM cells, keep monitoring it and detect when it closes. |
| FR-04 | Allow closing the launched application from the app (real termination) and show the freed memory. |
| FR-05 | **Level 2:** scan real windows, derive a CPU burst from each one’s memory usage and simulate **Round Robin** with selectable quantum (1, 2 or 3 s). |
| FR-06 | Provide speed control, pause/resume and a step-by-step mode for the scheduler, plus an explanation of the concept occurring at every step. |
| FR-07 | Display a live Gantt chart, ready queue/CPU animation, quantum bar, and a result table (burst, turnaround, waiting time, average waiting, context switches, total time). |
| FR-08 | Provide a clickable **glossary** (Burst, Quantum, Ready Queue, Context Switch, Preemption, Termination, Round Robin). |
| FR-09 | **Level 3:** map real windows onto a 12-block RAM, scanning cell by cell; when RAM is full, trigger virtual memory and **write real swap-page files** to disk with an animated transfer. |
| FR-10 | **Level 4:** activate a “Real Control Mode” that watches the desktop every 1.5 s, keeps a maximum of **3 windows** and, when a 4th appears, warns **once** and (if accepted) really closes the **oldest** one (**FIFO**). |
| FR-11 | Ignore windows that were already open before activation and never repeat the warning for the same window; offer a safe demonstration mode. |
| FR-12 | **Level 5:** create two real files (a text document and a Python program) and let the user toggle read / write / execute padlocks and administrator privileges. |
| FR-13 | Apply five ready-made permission scenarios (read-only user, no permissions, full-permission user, system administrator, protected system file). |
| FR-14 | Perform real **VIEW**, **SAVE** (append) and **EXECUTE** operations on the files, allowing or denying them according to the padlocks and the real read-only attribute; animate the permission check. |
| FR-15 | Track a mission (try VIEW, SAVE and EXECUTE and obtain at least one GRANTED and one DENIED result) to unlock the final level. |
| FR-16 | **Final level:** scan the system and generate a text report plus an interactive dashboard (level traffic light, simulated vs. real RAM bars, session counters) where every element opens an explanation. |
| FR-17 | Show a congratulation pop-up whenever a level is completed. |
| FR-18 | On exit, restore normal permissions on the demo files. |

### Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | **Desktop GUI** in Tkinter/ttk with a dark theme (Catppuccin-like palette) and a default window of 1250 × 900. |
| NFR-02 | **Responsiveness:** long operations (launching apps, scheduling, monitoring, swapping) run in background threads so the interface stays usable. |
| NFR-03 | **Educational clarity:** every step is accompanied by a plain-language explanation and, when relevant, a technical one. |
| NFR-04 | **Graceful degradation:** if PowerShell queries fail or too few windows exist, fallback/example processes are used so demos still work. |
| NFR-05 | **Self-cleaning:** swap pages are deleted when re-run and demo files are restored to normal permissions on exit. |
| NFR-06 | **No external packages**; scrollable levels with mouse-wheel support. |
| NFR-07 | **Language:** user interface and explanations are in **Spanish**. |

### Software requirements

| Requirement | Details |
|-------------|---------|
| **Operating system** | **Windows 10/11** — the application uses PowerShell (`Get-Process`, `Get-CimInstance`), `taskkill`, the `start` command and Windows executable names. |
| **Python** | 3.8 or newer (standard installer from python.org). |
| **Tkinter** | Included with the official Windows Python installer (“tcl/tk and IDLE” option). |
| **Standard library modules** | `tkinter`, `subprocess`, `threading`, `time`, `random`, `os`, `sys`, `stat`, `tempfile`, `math` — nothing to `pip install`. |
| **PowerShell** | Available by default in Windows (`powershell` must be on `PATH`). |
| **Optional apps** | Chrome, Word, Excel, VS Code, Notepad, Calculator, Paint — whichever you want to open in Level 1. |
| **Display** | Recommended ≥ 1250 × 900 px. |

---

## 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/ChristopherVP/ProyectoInsideOS.git
cd ProyectoInsideOS

# 2. (Optional) verify Python and Tkinter
python --version
python -m tkinter       # opens a small test window if Tkinter works
```

No dependencies to install.

---

## ▶️ Running the Application

```bash
python ProyectoInsideOS.py
```

Before starting, it is recommended to **save your work and have a few applications open** (browser, editor, etc.) so Levels 2–4 have real windows to analyze.

---

## 🎓 Learning Path: the 6 Levels

### Level 1 — Open and Start Processes
Choose an app and press **“¡Abrir Programa Real!”**. The OS “pipeline” lights up one stage at a time while a token travels through it:

1. **You (User)** — the request enters the OS.
2. **Operating System** — it looks the program up (PATH / Registry).
3. **Hard Disk** — locates and reads the `.exe`.
4. **Kernel (fork / exec)** — creates the process and its **PCB** (Process Control Block).
5. **Process Table (PID)** — assigns a unique PID and marks it READY/RUNNING.
6. **RAM** — reserves memory cells one by one.

You also get a detailed explanation of the current step, live telemetry (**PID** and **RAM in KB**), a technical log, and a **12-cell RAM map** that keeps updating while the app runs. Close the app from InsideOS to free the memory and open another one.
**Unlocks Level 2:** open a real program successfully and watch the sequence.

### Level 2 — CPU Algorithms with Your Apps (Round Robin)
Uses the “one cook, many orders” analogy: your real windows become processes competing for one CPU. The simulator scans your windows, assigns each a **burst time** based on its RAM, builds the **ready queue** and runs **Round Robin** with your chosen **quantum**. You see cards moving between queue and CPU, a quantum progress bar, a growing **Gantt chart** (context switches are marked) and, at the end, a table of **burst, turnaround and waiting time** with the average waiting time and the number of context switches.
Controls: quantum (1/2/3 s), speed (0.5×–3×), pause, step-by-step mode. A **glossary** explains Burst, Quantum, Ready Queue, Context Switch, Preemption, Termination and Round Robin.
**Unlocks Level 3:** let the simulation reach the end.

### Level 3 — RAM + Hard Disk (Swap)
The memory has only **12 blocks**. Press **“Mapear consumo actual de mis Ventanas”**: the Memory Manager checks each cell (“LIBRE → assigning…”) and reserves blocks for every window. When the RAM is full, **virtual memory** kicks in: an animation moves a page to the disk and a **real `.swap` file** is written (random bytes) in a temporary folder, with its real size reported. The log also explains the “page map” and **swap-in**.
**Unlocks Level 4:** let the mapping finish.

### Level 4 — Real Window Control (FIFO)
Activate **“Modo de Control Real”**: the stand watches your desktop in the background (every 1.5 s) and enforces a **maximum of 3 windows**. When a 4th window appears you get **one warning** asking if you want to really close the **oldest** window (FIFO — it ignores how much RAM it uses). If you accept, it is terminated; if you decline, you are not asked again about that window. Windows open *before* activating the mode are ignored. A **“Simular ventana nueva (demostración segura)”** button shows the whole flow without closing anything.
**Unlocks Level 5:** activate the mode and answer one limit warning (Yes or No).

### Level 5 — File Padlocks (Permissions)
Think of a file as a box with three padlocks: **READ**, **WRITE** and **EXECUTE** (+ **Administrator** that opens all three). InsideOS creates two real files — `informe_confidencial.txt` (document) and `programa_saludo.py` (program) — and you toggle the padlocks or apply a ready-made scenario:

- Normal user — read-only
- Normal user — no permission
- User with full permission
- System administrator
- Protected system file (locked)

Then press **VER / GUARDAR / EJECUTAR**: a permission-check animation plays and the OS really reads, appends to or runs the file — or denies it. The write padlock also toggles the file’s **real read-only attribute**. Executing the `.py` file spawns a real process that prints its own PID and time.
**Mission to unlock the final level:** try VIEW, SAVE and EXECUTE, get at least one **GRANTED** and one **DENIED**. A “Restore files” button resets the demo files and a button opens the folder in Explorer.

### Final Level — General Diagnosis
Press **“¡Escanear y Generar Auditoría del Sistema!”** to produce:

- A text report of the visible windows (name, PID, RAM), the **simulated RAM** (12 blocks × 15,000 KB) versus the **real physical RAM** of the PC, session statistics (time used, processes created/closed, swap pages written, windows expelled, warnings rejected) and levels completed, plus the history of programs you opened.
- An **interactive dashboard**: a traffic-light for the 5 levels, two RAM bars (simulated vs. real) and counters — **click any circle, bar or counter** to get a plain-language explanation and its link to the corresponding level.

---

## 🔬 How Real vs. Simulated Works

| Concept | Real (on your PC) | Simulated / didactic |
|---------|-------------------|----------------------|
| Opening programs | Launched with `start <command>` | Pipeline stages are narrated with pauses |
| Process list, PID, memory | `Get-Process` through PowerShell | Memory is mapped to 12 teaching cells |
| Physical RAM | `Win32_OperatingSystem` (total/free) | Compared to the 12-block simulated RAM |
| CPU scheduling | Burst derived from each real window’s memory | Round Robin runs inside the app (not the real Windows scheduler) |
| Swap | Real `.swap` files written to a temp folder | Page-fault policy is simplified |
| Window control | Real `taskkill /F` (with confirmation) | FIFO policy for the “oldest” window |
| File permissions | Real files, real read-only attribute, real execution | Padlock logic and scenarios |

---

## 📐 Key Parameters and Formulas

| Item | Value / formula |
|------|-----------------|
| RAM cells (Levels 1, 3, final) | **12 blocks**; each represents **15,000 KB** in the dashboard |
| Level 1 blocks used | `min(12, max(1, mem_KB // 15000))` |
| Level 3 blocks per window | `max(1, min(4, mem_KB // 25000))` |
| Level 2 burst (seconds) | `max(3, min(7, mem_KB // 40000 + 2))`; if fewer than 3 windows, example programs (`explorer`, `notepad`, `spotify`) are added with a random 3–6 s burst |
| Quantum options | 1, 2 or 3 seconds; speed 0.5×–3.0× |
| Turnaround time | completion time of each process |
| Waiting time | `turnaround − burst` |
| Average waiting time | `Σ waiting / number of processes` |
| Level 4 limit | **3 windows**, polling every **1.5 s**, FIFO eviction of the oldest |
| Level 5 write rule | file is writable if **Modify** or **Admin** is on; otherwise it is set to read-only |
| Execution timeout (Level 5) | 15 seconds |
| Level 1 monitoring interval | 1.5 s |

---

## 📁 Files and Folders Created at Runtime

| Path | Purpose | Cleanup |
|------|---------|---------|
| `%TEMP%\InsideOS_Swap\pagina_<process>_<n>.swap` | Real swap pages written in Level 3 | Deleted when Level 3 is run again |
| `%TEMP%\InsideOS_Archivos\informe_confidencial.txt` | Demo document for Level 5 | Recreated by *Restore*; permissions normalized on exit |
| `%TEMP%\InsideOS_Archivos\programa_saludo.py` | Demo program for Level 5 | Same as above |

Nothing is written inside the project folder.

---

## 🧱 Project Structure

```text
ProyectoInsideOS/
└── ProyectoInsideOS.py          # The whole application (≈2,200 lines)
    ├── GLOSARIO_N2              # Glossary texts for Level 2
    ├── CONTENIDO_ARCHIVOS_N5    # Contents of the demo files for Level 5
    └── class InsideOSVentanasReales
        ├── Infrastructure       # __init__, styles, layout, tab locking, scroll areas, pop-ups
        ├── System queries       # obtener_procesos_ventanas_reales(), obtener_ram_fisica_real()
        ├── Level 1              # pipeline, launch thread, monitoring, RAM drawing
        ├── Level 2              # Round Robin simulation, Gantt, cards, glossary
        ├── Level 3              # RAM mapping, swap animation and real swap files
        ├── Level 4              # window monitor thread, FIFO warning, demo mode
        ├── Level 5              # padlocks, scenarios, flow animation, real file operations
        └── Level 6 (final)      # audit report + traffic light, bars and counters
```

---

## 🏗 Architecture and Design Notes

- **Single class, one tab per level:** `InsideOSVentanasReales` builds every level with `construir_nivel_N()` and unlocks the next tab through boolean flags (`nivelN_usado`) and `completar_nivel()`.
- **Threads for the real world:** launching apps, monitoring a process, the scheduler and the window watcher run in daemon threads; UI updates from those threads use `root.after(...)` where needed.
- **Scheduler control with events:** the Round Robin simulation uses a `threading.Event` for step-by-step mode plus pause and speed controls.
- **Canvas-drawn graphics:** all icons (person, gears, disk, card, chip, padlocks), Gantt chart, RAM cells and gauges are drawn with `tk.Canvas`; no image files.
- **Defensive programming:** every call to PowerShell, `taskkill` or file operations is wrapped in `try/except` with fallbacks.
- **Didactic layering:** each step has a *technical* sentence and a *simple* analogy (“the cook”, “the kitchen window”, “the box with padlocks”).

---

## ⚠️ Safety Notes and Limitations

- **This app can close real programs.** In Level 1 (“Cerrar Aplicación Actual”) and Level 4 (accepting the FIFO warning) it runs `taskkill /F`, which **terminates a process without saving**. Save your work first, and use the **demonstration button** in Level 4 if you do not want anything closed.
- **Windows only.** PowerShell, `start`, `taskkill` and `.exe` names make it unsuitable for Linux/macOS without porting.
- **Windows with visible titles only:** the real process list is built from processes that have a main window title; background services are not included.
- **Simulated components:** the Round Robin scheduler and the 12-block RAM are teaching models and do not reflect the real Windows scheduler or memory manager.
- **Permissions are demonstrative:** the read-only attribute is real, but the “Execute” and “Admin” padlocks are enforced by the application’s own logic.
- **Application names are hard-coded** (e.g., `chrome.exe`, `WINWORD.EXE`). Apps that are not installed will produce a “not found” message.
- Some antivirus/EDR tools may flag programmatic process termination or random swap files; they are harmless demo operations.

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| “Programa No Encontrado” in Level 1 | The app is not installed or does not create a main window. Choose another program or type a valid command. |
| Level 2/3/4 show example processes | Too few windows were detected. Open a few real applications first. |
| RAM data shows “No se pudo consultar la RAM física real” | PowerShell/CIM is blocked or unavailable; check execution policy and that `powershell` is on `PATH`. |
| Level 5 save is denied even with write enabled | Re-apply the scenario or press the restore button; check that the folder `%TEMP%\InsideOS_Archivos` is writable. |
| A tab is locked 🔒 | Complete the previous level’s unlock condition (shown in each level’s introduction). |
| Window too large for the screen | The default size is 1250 × 900; reduce the Windows display scaling or resize the window. |
| Nothing opens on Linux/macOS | The app is Windows-specific (see requirements). |

---

## 👤 Author, Repository and License

- **Author:** Christopher Josué Villón Peralta
- **Repository:** <https://github.com/ChristopherVP/ProyectoInsideOS>
- **Context:** university project for an Operating Systems course.
- **License:** *not specified yet* — add a `LICENSE` file (e.g., MIT) if you want others to reuse the code.
