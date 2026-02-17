const THEME_COLORS = {
  "Self-Knowledge":         "#E2504C",
  "Prudence":               "#4DA6FF",
  "Social Strategy":        "#FFA726",
  "Leadership & Power":     "#AB47BC",
  "Character & Virtue":     "#66BB6A",
  "Intelligence & Wit":     "#FFEE58",
  "Communication":          "#26C6DA",
  "Fortune & Timing":       "#EC407A",
  "Appearances":            "#8D6E63",
  "Ambition & Achievement": "#FF7043",
  "Dealing with Others":    "#78909C",
  "Moderation & Balance":   "#9CCC65"
};

function lighten(hex, pct) {
  const num = parseInt(hex.slice(1), 16);
  const r = Math.min(255, ((num >> 16) & 0xFF) + Math.round(255 * pct / 100));
  const g = Math.min(255, ((num >> 8) & 0xFF) + Math.round(255 * pct / 100));
  const b = Math.min(255, (num & 0xFF) + Math.round(255 * pct / 100));
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

const GROUPS = {};
for (const [theme, color] of Object.entries(THEME_COLORS)) {
  GROUPS[theme] = {
    color: {
      background: color,
      border: color,
      highlight: { background: lighten(color, 20), border: "#ffffff" },
      hover: { background: lighten(color, 10), border: "#cccccc" }
    },
    font: { color: "#ffffff", size: 10, face: "Segoe UI, arial" },
    shape: "dot",
    size: 16,
    borderWidth: 2
  };
}

const NETWORK_OPTIONS = {
  groups: GROUPS,
  nodes: {
    shape: "dot",
    font: {
      color: "#e0e0e0",
      size: 10,
      face: "Segoe UI, arial",
      strokeWidth: 3,
      strokeColor: "#1a1a2e"
    },
    borderWidth: 2,
    shadow: { enabled: true, color: "rgba(0,0,0,0.5)", size: 8, x: 2, y: 2 }
  },
  edges: {
    color: {
      color: "#3a3a5c",
      highlight: "#ffffff",
      hover: "#8888aa",
      opacity: 0.3
    },
    font: {
      color: "#666666",
      size: 8,
      face: "arial",
      strokeWidth: 0,
      align: "middle"
    },
    width: 0.8,
    smooth: {
      type: "continuous",
      roundness: 0.5
    },
    hoverWidth: 0.5,
    selectionWidth: 1,
    hidden: false
  },
  physics: {
    enabled: true,
    solver: "forceAtlas2Based",
    forceAtlas2Based: {
      gravitationalConstant: -60,
      centralGravity: 0.01,
      springLength: 120,
      springConstant: 0.02,
      damping: 0.4,
      avoidOverlap: 0.5
    },
    stabilization: {
      enabled: true,
      iterations: 300,
      updateInterval: 25
    },
    maxVelocity: 50,
    minVelocity: 0.75
  },
  interaction: {
    hover: true,
    tooltipDelay: 200,
    hideEdgesOnDrag: true,
    hideEdgesOnZoom: true,
    multiselect: false,
    navigationButtons: false,
    keyboard: { enabled: true }
  },
  layout: {
    improvedLayout: false
  }
};
