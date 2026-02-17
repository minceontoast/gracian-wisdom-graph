"""Assign theme categories to each maxim via keyword matching."""
import json
import re
import os

THEME_KEYWORDS = {
    "Self-Knowledge": [
        "know thyself", "know yourself", "self", "fault", "faults", "mirror",
        "introspection", "weakness", "temperament", "nature", "defect", "defects",
        "know your", "self-knowledge", "own nature", "own character", "examine",
        "understand yourself", "personal", "inner", "disposition", "qualities"
    ],
    "Prudence": [
        "prudent", "prudence", "cautious", "careful", "restraint", "discretion",
        "foresight", "deliberate", "wary", "circumspect", "think before",
        "beforehand", "suspense", "reserve", "reserved", "guard", "guarded",
        "avoid", "prevent", "watch", "watchful", "heed", "thoughtful"
    ],
    "Social Strategy": [
        "friend", "friends", "ally", "allies", "enemy", "enemies", "court",
        "favour", "favor", "reputation", "esteem", "company", "associate",
        "society", "social", "dependence", "dependent", "patron", "please",
        "obligate", "obligation", "intercourse", "deal with", "dealing"
    ],
    "Leadership & Power": [
        "authority", "command", "govern", "governance", "rule", "ruler",
        "prince", "king", "superior", "subordinate", "power", "influence",
        "lead", "leader", "minister", "throne", "royal", "majesty",
        "dominion", "office", "employment", "position"
    ],
    "Character & Virtue": [
        "integrity", "honour", "honor", "virtue", "virtuous", "noble",
        "dignity", "character", "moral", "good", "goodness", "worthy",
        "upright", "merit", "excellence", "excellent", "perfect",
        "perfection", "complete", "greatness", "great man"
    ],
    "Intelligence & Wit": [
        "intellect", "intelligent", "wise", "wisdom", "wit", "clever",
        "judgment", "judgement", "reason", "knowledge", "learn", "learned",
        "sage", "sagacious", "thought", "think", "mind", "understanding",
        "insight", "discernment", "genius", "talent"
    ],
    "Communication": [
        "speech", "speak", "silence", "silent", "persuade", "persuasion",
        "conceal", "concealment", "word", "words", "tongue", "talk",
        "say", "tell", "express", "eloquent", "eloquence", "secret",
        "mystery", "mysterious", "declare", "hint", "listen"
    ],
    "Fortune & Timing": [
        "fortune", "luck", "lucky", "unlucky", "chance", "opportunity",
        "moment", "timing", "time", "season", "seize", "occasion",
        "fate", "destiny", "star", "stars", "born", "favourable",
        "favorable", "ill-luck", "good luck", "right moment"
    ],
    "Appearances": [
        "seem", "seeming", "appear", "appearance", "outside", "show",
        "display", "ostentation", "impression", "perceive", "perception",
        "surface", "outward", "visible", "eye", "eyes", "look",
        "spectacle", "ornament", "attire", "manner", "manners"
    ],
    "Ambition & Achievement": [
        "ambition", "ambitious", "achieve", "achievement", "excel",
        "distinction", "eminent", "eminence", "first", "highest",
        "success", "succeed", "accomplish", "fame", "glory", "immortal",
        "immortality", "renown", "triumph", "victory", "conquer", "hero",
        "enterprise", "endeavour", "endeavor", "effort"
    ],
    "Dealing with Others": [
        "fool", "fools", "bore", "bores", "vulgar", "crowd", "mob",
        "people", "men", "man", "person", "others", "companion",
        "companions", "neighbour", "neighbor", "acquaintance",
        "everyone", "world", "mankind", "human", "opponent"
    ],
    "Moderation & Balance": [
        "moderate", "moderation", "balance", "extreme", "extremes",
        "excess", "temperance", "middle", "mean", "adapt", "adaptable",
        "flexible", "equilibrium", "vary", "variety", "restrain",
        "proportion", "enough", "sufficient", "too much", "too little"
    ]
}

def score_maxim(maxim, theme_keywords):
    """Score a maxim against all themes. Returns dict of theme -> score."""
    text = (maxim['title'] + ' ' + maxim['body']).lower()
    scores = {}
    for theme, keywords in theme_keywords.items():
        score = 0
        for kw in keywords:
            # Count occurrences, weighted by keyword length (longer = more specific)
            count = len(re.findall(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE))
            weight = 1 + (len(kw.split()) - 1) * 0.5  # multi-word phrases get bonus
            score += count * weight
        # Also give bonus if keyword appears in title
        title_lower = maxim['title'].lower()
        for kw in keywords:
            if kw in title_lower:
                score += 3  # title match bonus
        scores[theme] = score
    return scores

def categorize(maxims):
    """Assign primary and secondary themes to each maxim."""
    for maxim in maxims:
        scores = score_maxim(maxim, THEME_KEYWORDS)
        sorted_themes = sorted(scores.items(), key=lambda x: -x[1])

        # Primary theme = highest scoring
        maxim['primaryTheme'] = sorted_themes[0][0]

        # Secondary themes = next themes that score above a threshold
        primary_score = sorted_themes[0][1]
        threshold = max(primary_score * 0.3, 1.0)  # at least 30% of primary or 1.0
        secondary = []
        for theme, score in sorted_themes[1:4]:  # up to 3 secondary
            if score >= threshold:
                secondary.append(theme)
        maxim['secondaryThemes'] = secondary

    return maxims

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')

    with open(os.path.join(data_dir, 'maxims_raw.json'), encoding='utf-8') as f:
        maxims = json.load(f)

    maxims = categorize(maxims)

    out_path = os.path.join(data_dir, 'maxims.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(maxims, f, ensure_ascii=False, indent=2)

    # Stats
    from collections import Counter
    primary_counts = Counter(m['primaryTheme'] for m in maxims)
    print(f"Categorized {len(maxims)} maxims into themes:")
    for theme, count in primary_counts.most_common():
        print(f"  {theme}: {count}")

    # Show a few examples
    print("\nExamples:")
    for m in maxims[:5]:
        print(f"  {m['numeral']}: {m['title'][:40]}...")
        print(f"    Primary: {m['primaryTheme']}, Secondary: {m['secondaryThemes']}")

if __name__ == '__main__':
    main()
