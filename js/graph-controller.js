function GraphController(containerEl, options) {
  this.container = containerEl;
  this.options = options;
  this.network = null;
  this.allNodes = null;
  this.allEdges = null;
  this.originalNodeOptions = {};
  this.activeFilters = new Set(Object.keys(THEME_COLORS));
  this.isHighlighted = false;
}

GraphController.prototype.init = function() {
  var self = this;
  return fetch("data/graph.json")
    .then(function(r) { return r.json(); })
    .then(function(graphData) {
      self.allNodes = new vis.DataSet(graphData.nodes);
      self.allEdges = new vis.DataSet(graphData.edges);

      // Store original options for reset
      self.allNodes.forEach(function(node) {
        self.originalNodeOptions[node.id] = {
          opacity: 1,
          font: { size: 10 }
        };
      });

      self.network = new vis.Network(
        self.container,
        { nodes: self.allNodes, edges: self.allEdges },
        self.options
      );

      self.network.on("click", function(params) { self.onNodeClick(params); });

      self.network.on("stabilizationProgress", function(params) {
        var pct = Math.round((params.iterations / params.total) * 100);
        document.getElementById("loading-text").textContent =
          "Stabilizing graph… " + pct + "%";
      });

      self.network.on("stabilizationIterationsDone", function() {
        document.getElementById("loading-overlay").style.display = "none";
        self.network.setOptions({ physics: { enabled: false } });
      });
    });
};

GraphController.prototype.onNodeClick = function(params) {
  if (params.nodes.length === 0) {
    UIController.closePanel();
    return;
  }

  var nodeId = params.nodes[0];
  var node = this.allNodes.get(nodeId);
  var connectedNodes = this.network.getConnectedNodes(nodeId);

  var self = this;
  var connections = connectedNodes.map(function(id) {
    var n = self.allNodes.get(id);
    return { id: n.id, title: n.fullTitle, numeral: n.numeral };
  });

  // Sort connections by numeral
  connections.sort(function(a, b) { return a.id - b.id; });

  UIController.showDetail(node, connections);
  this.highlightNeighborhood(nodeId, connectedNodes);
};

GraphController.prototype.focusNode = function(nodeId) {
  this.network.selectNodes([nodeId]);
  this.onNodeClick({ nodes: [nodeId] });
  this.network.focus(nodeId, { scale: 1.2, animation: { duration: 500 } });
};

GraphController.prototype.highlightNeighborhood = function(selectedId, connectedIds) {
  this.isHighlighted = true;
  var updates = [];
  var connSet = new Set(connectedIds);

  this.allNodes.forEach(function(node) {
    if (node.id === selectedId) {
      updates.push({ id: node.id, opacity: 1.0, font: { size: 14 } });
    } else if (connSet.has(node.id)) {
      updates.push({ id: node.id, opacity: 0.9, font: { size: 10 } });
    } else {
      updates.push({ id: node.id, opacity: 0.12, font: { size: 0 } });
    }
  });

  this.allNodes.update(updates);

  // Also dim non-connected edges
  var connectedEdges = new Set(this.network.getConnectedEdges(selectedId));
  var edgeUpdates = [];
  this.allEdges.forEach(function(edge) {
    if (connectedEdges.has(edge.id)) {
      edgeUpdates.push({ id: edge.id, color: { opacity: 0.8 }, width: 2 });
    } else {
      edgeUpdates.push({ id: edge.id, color: { opacity: 0.03 }, width: 0.5 });
    }
  });
  this.allEdges.update(edgeUpdates);
};

GraphController.prototype.resetHighlighting = function() {
  if (!this.isHighlighted) return;
  this.isHighlighted = false;

  var updates = [];
  this.allNodes.forEach(function(node) {
    updates.push({ id: node.id, opacity: 1.0, font: { size: 10 } });
  });
  this.allNodes.update(updates);

  var edgeUpdates = [];
  this.allEdges.forEach(function(edge) {
    edgeUpdates.push({ id: edge.id, color: { opacity: 0.3 }, width: 0.8 });
  });
  this.allEdges.update(edgeUpdates);

  this.network.unselectAll();
};

GraphController.prototype.filterByThemes = function(activeThemes) {
  var updates = [];
  this.allNodes.forEach(function(node) {
    var visible = activeThemes.has(node.primaryTheme);
    updates.push({ id: node.id, hidden: !visible });
  });
  this.allNodes.update(updates);
};

GraphController.prototype.search = function(query) {
  if (!query) {
    this.resetHighlighting();
    return [];
  }

  var q = query.toLowerCase();
  var matches = [];

  this.allNodes.forEach(function(node) {
    var text = (node.fullTitle + " " + node.body + " " + node.numeral).toLowerCase();
    if (text.indexOf(q) !== -1) {
      matches.push(node.id);
    }
  });

  if (matches.length > 0) {
    var matchSet = new Set(matches);
    var updates = [];
    this.allNodes.forEach(function(node) {
      if (matchSet.has(node.id)) {
        updates.push({ id: node.id, opacity: 1.0, font: { size: 12 } });
      } else {
        updates.push({ id: node.id, opacity: 0.08, font: { size: 0 } });
      }
    });
    this.allNodes.update(updates);

    var edgeUpdates = [];
    this.allEdges.forEach(function(edge) {
      if (matchSet.has(edge.from) && matchSet.has(edge.to)) {
        edgeUpdates.push({ id: edge.id, color: { opacity: 0.5 }, width: 1 });
      } else {
        edgeUpdates.push({ id: edge.id, color: { opacity: 0.02 }, width: 0.3 });
      }
    });
    this.allEdges.update(edgeUpdates);

    this.isHighlighted = true;
    this.network.fit({ nodes: matches, animation: { duration: 500 } });
  }

  return matches;
};
