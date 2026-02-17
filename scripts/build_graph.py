"""Build graph.json with nodes and TF-IDF similarity edges for vis-network."""
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

THEME_COLORS = {
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
}

def truncate(s, max_len=25):
    return s[:max_len-1] + '…' if len(s) > max_len else s

def build_graph(maxims, similarity_threshold=0.15, max_edges_per_node=8):
    # Build TF-IDF matrix
    corpus = [m['title'] + ' ' + m['body'] for m in maxims]
    tfidf = TfidfVectorizer(stop_words='english', max_features=500)
    matrix = tfidf.fit_transform(corpus)
    sim_matrix = cosine_similarity(matrix)

    # Build nodes
    nodes = []
    for m in maxims:
        nodes.append({
            "id": m['id'],
            "label": f"{m['numeral'].upper()}\n{truncate(m['title'])}",
            "title": m['title'],  # tooltip
            "group": m['primaryTheme'],
            "fullTitle": m['title'],
            "body": m['body'],
            "numeral": m['numeral'],
            "primaryTheme": m['primaryTheme'],
            "secondaryThemes": m['secondaryThemes']
        })

    # Build edges using TF-IDF similarity
    # First, collect all candidate edges with scores
    candidates = []
    for i in range(len(maxims)):
        for j in range(i + 1, len(maxims)):
            score = sim_matrix[i][j]
            if score > similarity_threshold:
                themes_i = set([maxims[i]['primaryTheme']] + maxims[i]['secondaryThemes'])
                themes_j = set([maxims[j]['primaryTheme']] + maxims[j]['secondaryThemes'])
                shared = themes_i & themes_j
                label = sorted(shared)[0] if shared else "related"
                candidates.append({
                    "from": maxims[i]['id'],
                    "to": maxims[j]['id'],
                    "score": float(score),
                    "label": label,
                    "sharedThemes": list(shared)
                })

    # Sort by score descending
    candidates.sort(key=lambda e: -e['score'])

    # Limit edges per node to prevent hairball
    edge_count = {}
    edges = []
    edge_id = 0
    for c in candidates:
        from_id = c['from']
        to_id = c['to']
        from_count = edge_count.get(from_id, 0)
        to_count = edge_count.get(to_id, 0)
        if from_count < max_edges_per_node and to_count < max_edges_per_node:
            edges.append({
                "id": edge_id,
                "from": from_id,
                "to": to_id,
                "label": c['label'],
                "title": f"Similarity: {c['score']:.2f}\nShared: {', '.join(c['sharedThemes'])}",
            })
            edge_count[from_id] = from_count + 1
            edge_count[to_id] = to_count + 1
            edge_id += 1

    return {"nodes": nodes, "edges": edges}

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    with open(os.path.join(data_dir, 'maxims.json'), encoding='utf-8') as f:
        maxims = json.load(f)

    graph = build_graph(maxims, similarity_threshold=0.12, max_edges_per_node=8)

    out_path = os.path.join(data_dir, 'graph.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    # Stats
    n_nodes = len(graph['nodes'])
    n_edges = len(graph['edges'])
    connected = set()
    for e in graph['edges']:
        connected.add(e['from'])
        connected.add(e['to'])
    isolated = n_nodes - len(connected)

    print(f"Graph built: {n_nodes} nodes, {n_edges} edges")
    print(f"Isolated nodes (no edges): {isolated}")
    if isolated > 0:
        iso_ids = [n['id'] for n in graph['nodes'] if n['id'] not in connected]
        print(f"  IDs: {iso_ids[:20]}...")

    # Edge distribution
    from collections import Counter
    label_counts = Counter(e['label'] for e in graph['edges'])
    print("\nEdges by theme:")
    for label, count in label_counts.most_common():
        print(f"  {label}: {count}")

if __name__ == '__main__':
    main()
