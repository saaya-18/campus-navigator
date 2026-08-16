// script.js
// Fetches the campus graph from the Flask API, draws it as an SVG diagram,
// and calls /api/route (which runs the explicit Dijkstra implementation in
// graph.py) to find and highlight the shortest path between two locations.

const edgesLayer = document.getElementById("edges-layer");
const nodesLayer = document.getElementById("nodes-layer");
const sourceSelect = document.getElementById("source");
const destinationSelect = document.getElementById("destination");
const findRouteBtn = document.getElementById("find-route");
const resetBtn = document.getElementById("reset-route");
const resultPanel = document.getElementById("result-panel");
const traceList = document.getElementById("trace-list");

let locations = [];
let edges = [];
let locationsById = {};

async function init() {
  const [locationsRes, edgesRes] = await Promise.all([
    fetch("/api/locations"),
    fetch("/api/edges"),
  ]);
  locations = await locationsRes.json();
  edges = await edgesRes.json();
  locationsById = Object.fromEntries(locations.map((loc) => [loc.id, loc]));

  populateSelects();
  drawGraph();
}

function populateSelects() {
  for (const select of [sourceSelect, destinationSelect]) {
    select.innerHTML = "";
    for (const loc of locations) {
      const option = document.createElement("option");
      option.value = loc.id;
      option.textContent = loc.name;
      select.appendChild(option);
    }
  }
  // Default to two different locations for a sensible first view.
  if (locations.length > 1) {
    sourceSelect.value = locations[0].id;
    destinationSelect.value = locations[1].id;
  }
}

function edgeId(u, v) {
  return [u, v].sort().join("__");
}

function drawGraph() {
  edgesLayer.innerHTML = "";
  nodesLayer.innerHTML = "";

  // Draw edges first so nodes sit on top.
  for (const edge of edges) {
    const from = locationsById[edge.from];
    const to = locationsById[edge.to];
    if (!from || !to) continue;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", from.x);
    line.setAttribute("y1", from.y);
    line.setAttribute("x2", to.x);
    line.setAttribute("y2", to.y);
    line.setAttribute("class", "edge-line");
    line.dataset.id = edgeId(edge.from, edge.to);
    edgesLayer.appendChild(line);

    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2;
    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", midX);
    label.setAttribute("y", midY - 4);
    label.setAttribute("class", "edge-weight");
    label.dataset.id = edgeId(edge.from, edge.to);
    label.textContent = `${edge.distance} m`;
    edgesLayer.appendChild(label);
  }

  // Draw nodes.
  for (const loc of locations) {
    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", loc.x);
    circle.setAttribute("cy", loc.y);
    circle.setAttribute("r", 6);
    circle.setAttribute("class", "node-circle");
    circle.dataset.id = loc.id;

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", loc.x + 10);
    label.setAttribute("y", loc.y + 4);
    label.setAttribute("class", "node-label");
    label.textContent = loc.name;

    group.appendChild(circle);
    group.appendChild(label);
    nodesLayer.appendChild(group);
  }
}

function clearHighlight() {
  document.querySelectorAll(".edge-line, .edge-weight").forEach((el) => el.classList.remove("on-path"));
  document.querySelectorAll(".node-circle").forEach((el) => {
    el.classList.remove("on-path", "endpoint");
    el.setAttribute("r", 6);
  });
}

function highlightPath(path) {
  clearHighlight();

  for (let i = 0; i < path.length - 1; i++) {
    const id = edgeId(path[i], path[i + 1]);
    document.querySelectorAll(`[data-id="${id}"]`).forEach((el) => el.classList.add("on-path"));
  }

  path.forEach((nodeId, index) => {
    const circle = document.querySelector(`.node-circle[data-id="${nodeId}"]`);
    if (!circle) return;
    if (index === 0 || index === path.length - 1) {
      circle.classList.add("endpoint");
      circle.setAttribute("r", 9);
    } else {
      circle.classList.add("on-path");
      circle.setAttribute("r", 7);
    }
  });
}

function renderResult(data) {
  if (data.error) {
    resultPanel.innerHTML = `<p class="error">${data.error}</p>`;
    traceList.innerHTML = "";
    return;
  }

  const distanceHtml = `<p class="result-distance">${data.distance_m} m<span>total distance</span></p>`;
  const routeHtml = `<ol class="result-route">${data.path_names
    .map((name) => `<li>${name}</li>`)
    .join("")}</ol>`;
  resultPanel.innerHTML = distanceHtml + routeHtml;

  const pathSet = new Set(data.path);
  traceList.innerHTML = data.visit_order_names
    .map((name, i) => {
      const nodeId = data.visit_order[i];
      const cls = pathSet.has(nodeId) ? "on-path" : "";
      return `<li class="${cls}">${i + 1}. ${name}</li>`;
    })
    .join("");
}

async function findRoute() {
  const source = sourceSelect.value;
  const destination = destinationSelect.value;

  if (source === destination) {
    resultPanel.innerHTML = `<p class="error">Please choose two different locations.</p>`;
    return;
  }

  resultPanel.innerHTML = `<p class="placeholder">Computing shortest path&hellip;</p>`;

  const res = await fetch(`/api/route?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}`);
  const data = await res.json();

  renderResult(data);
  if (data.path) highlightPath(data.path);
}

findRouteBtn.addEventListener("click", findRoute);
resetBtn.addEventListener("click", () => {
  clearHighlight();
  resultPanel.innerHTML = `<p class="placeholder">Select a start and a destination, then find the shortest route.</p>`;
  traceList.innerHTML = "";
});

init();
