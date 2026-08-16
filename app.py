"""
app.py
------
Flask backend for the Smart Campus Navigation System capstone project.

Routes:
  GET  /                  -> serves the single-page frontend
  GET  /api/locations     -> list of campus locations (graph vertices)
  GET  /api/edges         -> list of walkable pathways (graph edges)
  GET  /api/route         -> runs Dijkstra's algorithm between two
                              locations and returns the shortest path
"""

import os
import threading
import webbrowser

from flask import Flask, render_template, jsonify, request

from graph import LOCATIONS, EDGES, build_campus_graph

app = Flask(__name__)

# Build the graph once at startup; it is small and static for this prototype.
campus_graph = build_campus_graph()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/locations")
def get_locations():
    locations = [
        {"id": location_id, "name": data["name"], "x": data["x"], "y": data["y"]}
        for location_id, data in LOCATIONS.items()
    ]
    locations.sort(key=lambda loc: loc["name"])
    return jsonify(locations)


@app.route("/api/edges")
def get_edges():
    edges = [
        {"from": u, "to": v, "distance": weight}
        for u, v, weight in EDGES
    ]
    return jsonify(edges)


@app.route("/api/route")
def get_route():
    source = request.args.get("source")
    destination = request.args.get("destination")

    if not source or not destination:
        return jsonify({"error": "Both 'source' and 'destination' query parameters are required."}), 400

    if source not in LOCATIONS or destination not in LOCATIONS:
        return jsonify({"error": "Unknown location id supplied."}), 400

    if source == destination:
        return jsonify({"error": "Source and destination must be different locations."}), 400

    result = campus_graph.dijkstra(source, destination)

    if not result["path"]:
        return jsonify({"error": f"No walkable path found between the selected locations."}), 404

    return jsonify({
        "path": result["path"],
        "path_names": [LOCATIONS[node_id]["name"] for node_id in result["path"]],
        "distance_m": result["distance"],
        "visit_order": result["visit_order"],
        "visit_order_names": [LOCATIONS[node_id]["name"] for node_id in result["visit_order"]],
    })


if __name__ == "__main__":
    # PORT is set by hosting platforms (Render, Railway, etc.) but not when
    # running locally, so we use its presence to decide whether to open a
    # browser window automatically -- convenient locally, meaningless on a
    # server with no display.
    port = int(os.environ.get("PORT", 5000))
    running_on_host = "PORT" in os.environ

    if not running_on_host and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()

    app.run(host="0.0.0.0", port=port, debug=not running_on_host)
