const UIController = {
  showDetail(node, connections) {
    const panel = document.getElementById("detail-panel");
    panel.classList.remove("collapsed");

    document.getElementById("detail-numeral").textContent =
      "Maxim " + node.numeral.toUpperCase();
    document.getElementById("detail-title").textContent = node.fullTitle;
    document.getElementById("detail-body").textContent = node.body;

    // Theme badges
    const themesEl = document.getElementById("detail-themes");
    themesEl.innerHTML = "";
    themesEl.appendChild(this.createBadge(node.primaryTheme, true));
    (node.secondaryThemes || []).forEach(function(t) {
      themesEl.appendChild(UIController.createBadge(t, false));
    });

    // Connections list
    const connEl = document.getElementById("detail-connections");
    connEl.innerHTML = "";
    const header = document.getElementById("connections-header");
    header.textContent = "Connected Maxims (" + connections.length + ")";

    connections.forEach(function(c) {
      const item = document.createElement("div");
      item.className = "connection-item";

      const numSpan = document.createElement("span");
      numSpan.className = "connection-numeral";
      numSpan.textContent = c.numeral.toUpperCase();

      item.appendChild(numSpan);
      item.appendChild(document.createTextNode(c.title));

      item.addEventListener("click", function() {
        if (window.graphController) {
          window.graphController.focusNode(c.id);
        }
      });

      connEl.appendChild(item);
    });
  },

  closePanel() {
    document.getElementById("detail-panel").classList.add("collapsed");
    if (window.graphController) {
      window.graphController.resetHighlighting();
    }
  },

  createBadge(theme, isPrimary) {
    const badge = document.createElement("span");
    badge.className = "theme-badge " + (isPrimary ? "primary" : "secondary");
    badge.style.backgroundColor = (THEME_COLORS[theme] || "#666") + (isPrimary ? "" : "88");
    badge.textContent = theme;
    return badge;
  },

  buildThemeFilters() {
    const container = document.getElementById("theme-filters");
    container.innerHTML = "";

    for (const [theme, color] of Object.entries(THEME_COLORS)) {
      const chip = document.createElement("div");
      chip.className = "theme-chip active";
      chip.dataset.theme = theme;

      const dot = document.createElement("span");
      dot.className = "theme-dot";
      dot.style.backgroundColor = color;

      chip.appendChild(dot);
      chip.appendChild(document.createTextNode(theme));
      container.appendChild(chip);
    }
  },

  buildLegend() {
    const legend = document.getElementById("legend");
    legend.innerHTML = "";

    for (const [theme, color] of Object.entries(THEME_COLORS)) {
      const item = document.createElement("span");
      item.className = "legend-item";

      const dot = document.createElement("span");
      dot.className = "legend-dot";
      dot.style.backgroundColor = color;

      item.appendChild(dot);
      item.appendChild(document.createTextNode(theme));
      legend.appendChild(item);
    }
  }
};
