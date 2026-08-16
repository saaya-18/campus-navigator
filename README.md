# Smart Campus Navigation System

A web-based capstone prototype that models a campus as a weighted graph and
uses **Dijkstra's shortest-path algorithm** (implemented explicitly, not via
an external routing library) to find the shortest walking route between two
campus locations.

- **Frontend:** HTML, CSS, JavaScript (vanilla, no framework)
- **Backend:** Python + Flask
- **Algorithm:** Dijkstra's algorithm, implemented by hand in `graph.py`
- **Data structure:** Weighted graph using an adjacency list
- **Priority queue:** Python's `heapq` (binary min-heap)
- No database, no React/Node/Firebase/MongoDB.

## Project structure

```
campus-nav/
├── app.py              # Flask app and API routes
├── graph.py             # Graph class + explicit Dijkstra implementation + campus data
├── requirements.txt
├── templates/
│   └── index.html       # Single-page frontend
└── static/
    ├── style.css
    └── script.js         # Draws the map and calls the API
```

## Setup and run

### Easiest: double-click launcher
If you have Python installed, you don't need to touch the terminal at all:
- **Windows:** double-click `run.bat`
- **Mac/Linux:** double-click `run.sh` (or run `./run.sh` in a terminal if
  double-click doesn't work — some systems open `.sh` files in a text editor
  by default instead of running them)

Either script installs Flask if it isn't already installed and starts the
app. Your browser will open to the app automatically after a second or two.

### Manual (2 commands, no virtual environment)
```bash
pip install -r requirements.txt
python3 app.py
```
Then open **http://127.0.0.1:5000** (or just wait — the app now opens your
browser for you automatically).

### If you don't have Python installed at all
Install Python 3 from [python.org/downloads](https://www.python.org/downloads/)
first (tick "Add Python to PATH" on the Windows installer), then use one of
the options above.

### If you'd rather use a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

## How it works

1. `graph.py` defines the campus locations (`LOCATIONS`) and the walkable
   pathways between them (`EDGES`), and implements a `Graph` class with an
   adjacency-list representation and a `dijkstra()` method written from
   scratch using `heapq`.
2. `app.py` builds the graph once at startup and exposes three JSON
   endpoints: `/api/locations`, `/api/edges`, and `/api/route`.
3. `script.js` fetches the locations and edges, draws them as an SVG diagram,
   and — when you pick a start and destination and click **Find shortest
   route** — calls `/api/route`, which runs Dijkstra's algorithm and returns
   the shortest path, its total distance, and the order in which the
   algorithm finalized each vertex (shown in the **Algorithm Trace** panel).

## About the distance data

The locations shown are the buildings visible in the supplied campus layout
image. The **edge distances are not official survey measurements.** They
were estimated by measuring pixel distances between connected buildings on
the layout image and converting to metres using an approximate scale
(~0.6 m/pixel) derived from the campus's stated size of ~100 acres. This is
good enough to demonstrate the algorithm correctly, but before this
prototype could be used for real navigation, the distances would need to be
replaced with data from an actual GPS/field survey of the campus pathways.
This assumption is also stated on the webpage itself and in `graph.py`.

## Extending the project

Some natural next steps, in rough order of effort:
- Replace the estimated distances with field-measured or GPS-derived data.
- Add more campus locations and pathways to `LOCATIONS` / `EDGES`.
- Add an A* implementation (needs real coordinates for a useful heuristic)
  and let the user compare it against Dijkstra.
- Add accessibility-weighted edges (e.g. avoiding stairs) for wheelchair
  routing.
- Deploy behind a real webserver (e.g. gunicorn) instead of Flask's
  development server.

## Deploying it online (Render, free tier)

1. Push this folder to a GitHub repository (see steps below if you haven't
   used git before).
2. Go to [render.com](https://render.com) and sign up (GitHub sign-in is
   fastest).
3. Click **New +** &rarr; **Web Service**, and connect your GitHub repo.
4. Render will detect Python automatically. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click **Create Web Service**. The first deploy takes a couple of
   minutes — you'll get a live URL like `https://your-app.onrender.com`.
6. That's it — anyone with the link can open it. (Free-tier services on
   Render sleep after inactivity and take ~30–60 seconds to wake up on the
   next visit — worth knowing if you're demoing live in class, see the
   presentation notes.)

`Procfile`, `requirements.txt` (now includes `gunicorn`), and the
`PORT`-aware code in `app.py` are already set up for this — no changes
needed.

### First time using git/GitHub?
```bash
cd campus-nav
git init
git add .
git commit -m "Initial commit"
```
Then create an empty repository on [github.com/new](https://github.com/new)
(don't initialize it with a README), and run the two commands it shows you,
which will look like:
```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```
