"""
graph.py
--------
Core data structure and shortest-path algorithm for the Smart Campus
Navigation System capstone project.

IMPORTANT NOTE ON DISTANCE DATA:
The location coordinates below (x, y) are pixel positions read off the
campus layout image supplied for this project. The edge distances are
NOT official survey measurements. They were estimated by:
  1. Measuring the pixel distance between two connected buildings on the
     layout image.
  2. Converting pixels to metres using an approximate scale derived from
     the campus's stated size (~100 acres), i.e. roughly 0.6 metres per
     pixel on the source image.
This gives plausible, in-the-right-ballpark walking distances for
demonstrating the algorithm, but they should be replaced with real
GPS/field-survey data before this prototype is used for actual navigation.

Everything below is implemented explicitly in plain Python — no external
graph or routing library is used for the core algorithm.
"""

import heapq
from collections import defaultdict

# ---------------------------------------------------------------------------
# Campus locations (vertices of the graph)
# x, y are pixel coordinates from the supplied campus layout image, reused
# here only to lay the nodes out on the on-screen map in roughly the same
# arrangement as the real campus.
# ---------------------------------------------------------------------------
LOCATIONS = {
    "school_of_education":       {"name": "Amrita School of Education", "x": 105,  "y": 165},
    "vysha_bhavan":               {"name": "Vysha Bhavan",               "x": 380,  "y": 242},
    "bed_block":                  {"name": "BEd Block",                  "x": 372,  "y": 419},
    "canteen":                    {"name": "Canteen",                    "x": 639,  "y": 281},
    "school_of_computing":        {"name": "School of Computing",        "x": 797,  "y": 277},
    "civil_block":                {"name": "Civil Block",                "x": 781,  "y": 149},
    "additional_block_1":         {"name": "Additional Block 1",         "x": 938,  "y": 218},
    "prahlada_bhavan":            {"name": "Prahlada Bhavan",            "x": 1037, "y": 257},
    "cse_block":                  {"name": "CSE Block",                  "x": 795,  "y": 354},
    "additional_block_2":         {"name": "Additional Block 2",         "x": 956,  "y": 431},
    "science_humanities_block":   {"name": "Science and Humanities Block", "x": 679, "y": 474},
    "ece_block":                  {"name": "ECE Block",                  "x": 801,  "y": 519},
    "administrative_block":       {"name": "Administrative Block",       "x": 685,  "y": 665},
}

# ---------------------------------------------------------------------------
# Walkable pathways (edges of the graph) with approximate distances in
# metres. See the module docstring above for how these were estimated.
# ---------------------------------------------------------------------------
EDGES = [
    ("school_of_education", "vysha_bhavan", 171),
    ("vysha_bhavan", "bed_block", 106),
    ("bed_block", "canteen", 180),
    ("canteen", "school_of_computing", 95),
    ("canteen", "civil_block", 116),
    ("civil_block", "additional_block_1", 103),
    ("additional_block_1", "prahlada_bhavan", 64),
    ("school_of_computing", "cse_block", 46),
    ("cse_block", "additional_block_2", 107),
    ("additional_block_1", "additional_block_2", 128),
    ("cse_block", "science_humanities_block", 100),
    ("science_humanities_block", "ece_block", 78),
    ("ece_block", "additional_block_2", 107),
    ("science_humanities_block", "administrative_block", 115),
]


class Graph:
    """A weighted, undirected graph stored as an adjacency list."""

    def __init__(self):
        # adjacency[u] -> list of (v, weight) tuples
        self.adjacency = defaultdict(list)
        self.vertices = set()

    def add_vertex(self, vertex_id):
        self.vertices.add(vertex_id)
        if vertex_id not in self.adjacency:
            self.adjacency[vertex_id] = []

    def add_edge(self, u, v, weight):
        """Pathways are walkable in both directions, so the edge is added
        symmetrically."""
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].append((v, weight))
        self.adjacency[v].append((u, weight))

    def dijkstra(self, source, destination):
        """
        Explicit implementation of Dijkstra's single-source shortest-path
        algorithm using a binary min-heap (Python's heapq) as the priority
        queue. Runs in O((V + E) log V) time.

        Returns a dict with:
          - path:      list of vertex ids from source to destination
                       (empty list if no path exists)
          - distance:  total path distance in metres (None if unreachable)
          - visit_order: list of vertex ids in the order Dijkstra finalized
                       their shortest distance (useful for showing how the
                       algorithm explores the graph)
        """
        if source not in self.vertices or destination not in self.vertices:
            return {"path": [], "distance": None, "visit_order": []}

        # Step 1: initialize distances -- 0 for the source, infinity for
        # every other vertex.
        distances = {v: float("inf") for v in self.vertices}
        distances[source] = 0

        # previous[v] lets us reconstruct the shortest path once we are done.
        previous = {v: None for v in self.vertices}

        visited = set()
        visit_order = []

        # Min-heap of (tentative_distance, vertex). Starting with the source
        # at distance 0.
        priority_queue = [(0, source)]

        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)

            if current_vertex in visited:
                # A stale, outdated queue entry -- skip it.
                continue

            visited.add(current_vertex)
            visit_order.append(current_vertex)

            # Early exit once the destination's shortest distance is finalized.
            if current_vertex == destination:
                break

            # Step 2: relax every edge leaving the current vertex.
            for neighbour, weight in self.adjacency[current_vertex]:
                if neighbour in visited:
                    continue
                candidate_distance = current_distance + weight
                if candidate_distance < distances[neighbour]:
                    distances[neighbour] = candidate_distance
                    previous[neighbour] = current_vertex
                    heapq.heappush(priority_queue, (candidate_distance, neighbour))

        # Step 3: reconstruct the path by walking backwards from the
        # destination through the `previous` pointers recorded above.
        if distances[destination] == float("inf"):
            return {"path": [], "distance": None, "visit_order": visit_order}

        path = []
        node = destination
        while node is not None:
            path.append(node)
            node = previous[node]
        path.reverse()

        return {
            "path": path,
            "distance": distances[destination],
            "visit_order": visit_order,
        }


def build_campus_graph():
    """Builds and returns the Graph instance for the current campus data."""
    campus_graph = Graph()
    for location_id in LOCATIONS:
        campus_graph.add_vertex(location_id)
    for u, v, weight in EDGES:
        campus_graph.add_edge(u, v, weight)
    return campus_graph


if __name__ == "__main__":
    # Simple manual smoke test: run `python3 graph.py`
    g = build_campus_graph()
    result = g.dijkstra("school_of_education", "administrative_block")
    print("Path:", " -> ".join(LOCATIONS[p]["name"] for p in result["path"]))
    print("Distance: {} m".format(result["distance"]))
    print("Visit order:", result["visit_order"])
