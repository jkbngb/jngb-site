#!/usr/bin/env python3
"""Merge 4 classification files + briefings into a single regulations.json."""

import json
import sys
from pathlib import Path

DATA_DIR = Path("/Users/jakob/Documents/Projects/RegulationRadar/data/processed")
OUT_PATH = Path("/Users/jakob/Documents/Projects/AgentStuff/PRStuff/site/public/data/regulations.json")

CLASSIFICATION_FILES = {
    "saul7b": DATA_DIR / "classifications_hf.co-mobeetle-Saul-7B-Instruct-v1-Q4_K_M-GGUF-latest_20260317_192032.json",
    "eurollm22b": DATA_DIR / "classifications_vllm-EuroLLM-22B-Instruct-2512_20260319_183218.json",
    "saul141b": DATA_DIR / "classifications_vllm-SaulLM-141B-Instruct_20260319_192849.json",
    "deepseek70b": DATA_DIR / "classifications_vllm-models--deepseek-ai--DeepSeek-R1-Distill-Llama-70B_20260319_202210.json",
}

BRIEFINGS_FILE = DATA_DIR / "briefings.json"


def load_classifications(path):
    """Load a classification file and return {celex: result_entry}."""
    with open(path) as f:
        data = json.load(f)
    return {r["celex"]: r for r in data["results"]}


def load_briefings(path):
    """Load briefings file and return {celex: briefing}."""
    with open(path) as f:
        data = json.load(f)
    return {b["celex"]: b for b in data["briefings"]}


def normalize_impact(val):
    """Normalize impact strings to HIGH/MODERATE/ROUTINE/UNKNOWN."""
    if val is None:
        return "UNKNOWN"
    v = str(val).strip().upper()
    if v in ("HIGH", "MODERATE", "ROUTINE", "UNKNOWN"):
        return v
    # Handle edge cases like numeric values or lowercase
    if v in ("MODERATE", "moderate"):
        return "MODERATE"
    return "UNKNOWN"


def extract_model_data(result):
    """Extract the fields we care about from a model's classification result."""
    sc = result.get("sector_classification", {})
    ic = result.get("impact_classification", {})

    domains = sc.get("domains", [])
    impact = normalize_impact(ic.get("impact"))
    confidence = ic.get("confidence")
    reasoning = ic.get("reasoning", "")

    return {
        "domains": domains,
        "impact": impact,
        "confidence": confidence,
        "reasoning": reasoning,
    }


def main():
    # Load all classification files
    model_data = {}
    all_celex = set()

    for model_key, path in CLASSIFICATION_FILES.items():
        print(f"Loading {model_key} from {path.name}...")
        model_data[model_key] = load_classifications(path)
        all_celex.update(model_data[model_key].keys())

    print(f"Total unique celex IDs: {len(all_celex)}")

    # Load briefings
    print(f"Loading briefings...")
    briefings = load_briefings(BRIEFINGS_FILE)
    print(f"Total briefings: {len(briefings)}")

    # Build merged records
    # Use the first model that has data for base fields
    records = []

    for celex in sorted(all_celex):
        # Get base fields from whichever model has this celex
        base = None
        for mk in CLASSIFICATION_FILES:
            if celex in model_data[mk]:
                base = model_data[mk][celex]
                break

        if base is None:
            continue

        record = {
            "celex": celex,
            "title": base["title"],
            "date": base["date"],
            "type": base["type"],
            "models": {},
        }

        # Add each model's classification
        for model_key in CLASSIFICATION_FILES:
            if celex in model_data[model_key]:
                record["models"][model_key] = extract_model_data(model_data[model_key][celex])

        # Add briefing if available
        if celex in briefings:
            b = briefings[celex]
            record["briefing"] = {
                "headline": b.get("headline", ""),
                "oneliner": b.get("oneliner", ""),
                "what": b.get("what", ""),
                "who_cares": b.get("who_cares", ""),
                "deadline": b.get("deadline", ""),
                "implications": b.get("implications", ""),
                "worst_case": b.get("worst_case", ""),
            }

        records.append(record)

    print(f"Total merged records: {len(records)}")

    # Save compact JSON
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(records, f, separators=(",", ":"), ensure_ascii=False)

    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"Written to {OUT_PATH} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
