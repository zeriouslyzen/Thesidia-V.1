#!/usr/bin/env python3
"""
Eval runner suite for Thesidia.

Runs conversational + gnostic/deep suites twice:
- baseline (pressure off)
- pressure on

Outputs JSON artifacts to data/evals/.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.metrics.emergence_scoring import score_compression


JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class EvalCase:
    id: str
    suite: str  # "conversational" | "gnostic"
    prompt: str
    fast_mode: bool
    research_depth: int


def default_cases() -> List[EvalCase]:
    return [
        EvalCase(id="conv_hi", suite="conversational", prompt="hi", fast_mode=True, research_depth=1),
        EvalCase(id="conv_funfact", suite="conversational", prompt="tell me a random fun fact about octopuses", fast_mode=True, research_depth=1),
        EvalCase(id="conv_opinion", suite="conversational", prompt="what do you think about consciousness", fast_mode=True, research_depth=1),
        EvalCase(id="gnostic_genesis", suite="gnostic", prompt="decode genesis. what was redacted and who benefited", fast_mode=False, research_depth=3),
        EvalCase(id="gnostic_forensic", suite="gnostic", prompt="what's really going on with pharmaceutical lobbying in the US? keep it evidence-first", fast_mode=False, research_depth=3),
    ]


class EvalRunner:
    def __init__(self, base_dir: Path, thesidia):
        self.base_dir = base_dir
        self.thesidia = thesidia
        self.evals_dir = self.base_dir / "data" / "evals"
        self.evals_dir.mkdir(parents=True, exist_ok=True)

    def run(self, cases: Optional[List[EvalCase]] = None) -> JsonDict:
        cases = cases or default_cases()
        run_id = f"eval_{int(time.time())}"

        baseline = self._run_variant(run_id=run_id, variant="baseline", pressure=False, cases=cases)
        pressured = self._run_variant(run_id=run_id, variant="pressure", pressure=True, cases=cases)

        report = {
            "run_id": run_id,
            "ts": time.time(),
            "variants": {
                "baseline": baseline,
                "pressure": pressured,
            },
        }

        latest_path = self.evals_dir / "latest.json"
        latest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (self.evals_dir / f"{run_id}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    def _run_variant(self, run_id: str, variant: str, pressure: bool, cases: List[EvalCase]) -> JsonDict:
        # Toggle via env for simplicity (process-level); Thesidia reads env in process().
        os.environ["THESIDIA_USE_SYNTHESIS_PRESSURE"] = "1" if pressure else "0"

        results = []
        compression_scores = []
        for c in cases:
            t0 = time.time()
            # Generate baseline output (pressure off also used to compute compression against pressured output)
            res = self.thesidia.process(
                input_data=c.prompt,
                context={
                    "format_mode": "natural",
                    "research_depth": c.research_depth,
                    "fast_mode": c.fast_mode,
                    # avoid user memory in eval
                    "user_id": None,
                    "session_id": None,
                },
            )
            dt = time.time() - t0
            out = res.get("output", "") if isinstance(res, dict) else str(res)
            meta = res.get("metadata", {}) if isinstance(res, dict) else {}

            results.append(
                {
                    "id": c.id,
                    "suite": c.suite,
                    "prompt": c.prompt,
                    "latency_s": dt,
                    "output_preview": out[:240],
                    "output_chars": len(out),
                    "metadata": meta,
                }
            )

        # Score compression by pairing baseline vs pressured later in aggregator (UI)
        return {
            "variant": variant,
            "pressure_enabled": pressure,
            "results": results,
        }


def compute_compression_between(baseline_text: str, pressured_text: str) -> JsonDict:
    s = score_compression(baseline_text, pressured_text)
    return s.to_dict()




