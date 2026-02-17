document.addEventListener("DOMContentLoaded", function() {
  var container = document.getElementById("graph-container");
  var gc = new GraphController(container, NETWORK_OPTIONS);
  window.graphController = gc;

  // Build UI
  UIController.buildThemeFilters();
  UIController.buildLegend();

  // Close panel button
  document.getElementById("close-panel").addEventListener("click", function() {
    UIController.closePanel();
  });

  // Search with debounce
  var searchInput = document.getElementById("search-input");
  var searchTimeout;
  searchInput.addEventListener("input", function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
      var val = e.target.value.trim();
      var matches = gc.search(val);
      var countEl = document.getElementById("search-count");
      countEl.textContent = val ? matches.length + " found" : "";
    }, 300);
  });

  // Escape to clear search and close panel
  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape") {
      searchInput.value = "";
      document.getElementById("search-count").textContent = "";
      UIController.closePanel();
    }
  });

  // Theme filter clicks
  document.getElementById("theme-filters").addEventListener("click", function(e) {
    var chip = e.target.closest(".theme-chip");
    if (!chip) return;

    chip.classList.toggle("active");

    var active = new Set();
    document.querySelectorAll(".theme-chip.active").forEach(function(el) {
      active.add(el.dataset.theme);
    });
    gc.filterByThemes(active);
  });

  // Initialize graph
  gc.init();
});
