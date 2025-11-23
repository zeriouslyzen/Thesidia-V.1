#!/usr/bin/env python3
"""
Test suite for Sophia gnostic map and versioning system.
"""

import json
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.sophia_gnostic_map import SophiaGnosticMap
from src.sophia_versioning import SophiaVersionManager


class SophiaGnosticMapTest(unittest.TestCase):
    def setUp(self) -> None:
        self.map = SophiaGnosticMap()

    def test_add_redaction_and_counts(self) -> None:
        self.assertEqual(self.map.redaction_count, 0)
        self.map.add_redaction(
            topic="Genesis narrative",
            original="The crime hidden beneath the canon.",
            redacted="Approved translation",
            archon="Council",
            evidence=["scrolls"],
        )
        self.assertEqual(self.map.redaction_count, 1)
        summary = self.map.summary()
        self.assertEqual(summary["redactions"], 1)

    def test_pattern_database_control_and_liberation(self) -> None:
        self.map.add_pattern(
            pattern_id="control-001",
            pattern_type=self.map.CONTROL_PATTERN,
            pattern_data={"pattern": "Debt entrapment"},
        )
        self.map.add_pattern(
            pattern_id="liberation-001",
            pattern_type=self.map.LIBERATION_PATTERN,
            pattern_data={"pattern": "Mutual aid networks"},
        )
        self.assertEqual(self.map.pattern_count, 2)
        control_patterns = self.map.get_patterns_by_type(self.map.CONTROL_PATTERN)
        self.assertIn("control-001", control_patterns)

    def test_timeline_coordinated_events(self) -> None:
        timestamp = "2025-01-20T10:15:30Z"
        self.map.add_timeline_event(
            "event-a", {"event": "Disclosure", "timestamp": timestamp}
        )
        self.map.add_timeline_event(
            "event-b", {"event": "Cover-up", "timestamp": timestamp}
        )
        coordinated = self.map.detect_coordinated_events()
        self.assertEqual(len(coordinated), 1)
        self.assertEqual(len(coordinated[0]["events"]), 2)

    def test_serialization_roundtrip(self) -> None:
        self.map.add_redaction(
            topic="Solar myth",
            original="True solar science",
            redacted="Mythology",
        )
        payload = self.map.to_dict()
        restored = SophiaGnosticMap.from_dict(payload)
        self.assertEqual(restored.redaction_count, 1)
        self.assertEqual(restored.summary()["redactions"], 1)


class SophiaVersionManagerTest(unittest.TestCase):
    def test_create_and_compare_versions(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            gnostic_map = SophiaGnosticMap()
            gnostic_map.add_redaction(
                topic="Timeline crime",
                original="Original signal",
                redacted="Cleansed version",
            )

            manager = SophiaVersionManager(base_dir=base_dir)
            meta1 = manager.create_version(gnostic_map, reason="initial")
            self.assertTrue((manager.versions_dir / f"{meta1.version_id}.json").exists())

            # Modify map and create a second version
            gnostic_map.add_pattern(
                pattern_id="control-002",
                pattern_type=SophiaGnosticMap.CONTROL_PATTERN,
                pattern_data={"pattern": "Media hypnosis"},
            )
            time.sleep(0.01)  # Ensure distinct timestamps
            meta2 = manager.create_version(gnostic_map, reason="pattern update")

            self.assertNotEqual(meta1.version_id, meta2.version_id)
            latest = manager.get_latest_version()
            self.assertIsNotNone(latest)
            self.assertEqual(latest["pattern_database"]["control_patterns"]["control-002"]["pattern"], "Media hypnosis")

            comparison = manager.compare_versions(meta1.version_id, meta2.version_id)
            self.assertIsNotNone(comparison)
            self.assertGreater(comparison["delta"]["control_patterns"], 0)

            # Cleanup should keep only the latest version
            manager.cleanup_old_versions(keep_last=1)
            remaining_versions = manager.list_versions(limit=10)
            self.assertEqual(len(remaining_versions), 1)
            self.assertEqual(remaining_versions[0].version_id, meta2.version_id)


if __name__ == "__main__":
    unittest.main()

