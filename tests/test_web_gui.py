import unittest
from fastapi.testclient import TestClient
from web.server import app

class TestWebGui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_static_index_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("MSA Pipeline Studio", response.text)
        self.assertIn("msa-matrix-container", response.text)
        self.assertIn("tree-visualizer-container", response.text)

    def test_static_assets(self):
        assets = [
            "/css/style.css",
            "/js/app.js",
            "/js/msa_viewer.js",
            "/js/tree_viewer.js",
            "/js/benchmark_charts.js"
        ]
        for asset in assets:
            response = self.client.get(asset)
            self.assertEqual(response.status_code, 200, f"Failed to fetch {asset}")
            self.assertGreater(len(response.text), 50)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["executable_found"])

    def test_presets_list(self):
        response = self.client.get("/api/presets")
        self.assertEqual(response.status_code, 200)
        presets = response.json()
        self.assertEqual(len(presets), 6)
        preset_ids = {p["id"] for p in presets}
        self.assertEqual(preset_ids, {"rv11", "rv12", "hemoglobin", "long_seq", "large_20", "large_40"})
        for p in presets:
            self.assertTrue(p["available"], f"Preset {p['id']} not available")

    def test_get_each_preset_content(self):
        for pid in ["rv11", "rv12", "hemoglobin", "long_seq", "large_20", "large_40"]:
            response = self.client.get(f"/api/preset/{pid}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertGreater(len(data["content"].strip()), 0)
            self.assertEqual(data["id"], pid)

    def test_align_rv11_standard(self):
        payload = {
            "preset_id": "rv11",
            "mode": "standard",
            "threads": 1,
            "gap_open": -10,
            "gap_extend": -1
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["aligned_sequences"]), 4)
        self.assertEqual(data["metrics"]["alignment_length"], 60)
        self.assertAlmostEqual(data["metrics"]["sp_score"], 0.9405, delta=0.005)
        self.assertAlmostEqual(data["metrics"]["tc_score"], 0.9107, delta=0.005)
        self.assertIsNotNone(data["tree"])
        self.assertIn("1aab_", data["tree_newick"])

    def test_align_rv12_standard(self):
        payload = {
            "preset_id": "rv12",
            "mode": "standard",
            "threads": 2
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["aligned_sequences"]), 3)
        self.assertEqual(data["metrics"]["alignment_length"], 65)
        self.assertIsNotNone(data["tree"])

    def test_align_hemoglobin_family(self):
        payload = {
            "preset_id": "hemoglobin",
            "mode": "standard",
            "threads": 4
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["aligned_sequences"]), 5)
        seq_ids = [s["id"] for s in data["aligned_sequences"]]
        self.assertTrue(any("HBA_HUMAN" in sid for sid in seq_ids))
        self.assertTrue(any("HBB_HUMAN" in sid for sid in seq_ids))
        self.assertIsNotNone(data["tree"])

    def test_baseline_comparison_long_sequence(self):
        payload = {
            "preset_id": "long_seq",
            "mode": "baseline",
            "threads": 1
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        baseline = data["baseline_comparison"]
        self.assertIsNotNone(baseline)
        self.assertTrue(baseline["score_identity"])
        self.assertEqual(baseline["gotoh"]["score"], baseline["myers_miller"]["score"])
        self.assertGreater(baseline["memory_reduction_ratio"], 500.0)

    def test_benchmark_mode_rv11(self):
        payload = {
            "preset_id": "rv11",
            "mode": "benchmark"
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        bench = data["benchmark_data"]
        self.assertIsNotNone(bench)
        self.assertGreaterEqual(len(bench["results"]), 3)
        threads = [r["threads"] for r in bench["results"]]
        self.assertIn(1, threads)
        self.assertIn(2, threads)
        self.assertIn(4, threads)

    def test_custom_raw_fasta_alignment(self):
        fasta = """>seqA
MKVILLFVL
>seqB
MKVILMFVL
>seqC
MKVILLLVL
"""
        payload = {
            "raw_content": fasta,
            "mode": "standard",
            "threads": 1
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["aligned_sequences"]), 3)
        self.assertIsNotNone(data["tree"])

    def test_empty_input_rejected(self):
        payload = {
            "raw_content": "",
            "mode": "standard"
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_malformed_fasta_rejected(self):
        payload = {
            "raw_content": "THIS_IS_NOT_A_VALID_FASTA_FILE",
            "mode": "standard"
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_single_sequence_alignment(self):
        payload = {
            "raw_content": ">single_seq\nMKVILLFVL\n",
            "mode": "standard"
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["aligned_sequences"]), 1)
        self.assertEqual(data["aligned_sequences"][0]["id"], "single_seq")
        self.assertIsNotNone(data["tree"])
        self.assertEqual(data["tree"]["clade_size"], 1)

    def test_tree_json_keys_and_newick(self):
        payload = {
            "preset_id": "rv11",
            "mode": "standard"
        }
        response = self.client.post("/api/align", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        tree = data["tree"]
        self.assertIn("id", tree)
        self.assertIn("name", tree)
        self.assertIn("height", tree)
        self.assertIn("branch_length", tree)
        self.assertIn("clade_size", tree)
        self.assertIn("children", tree)
        self.assertGreater(len(tree["children"]), 0)
        self.assertTrue(data["tree_newick"].endswith(";"))

    def test_preset_large_20_content(self):
        response = self.client.get("/api/preset/large_20")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "large_20")
        self.assertIn("309807.SRU_1450", data["content"])

    def test_preset_large_40_content(self):
        response = self.client.get("/api/preset/large_40")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "large_40")
        self.assertIn("309807.SRU_1450", data["content"])
        self.assertEqual(data["content"].count(">"), 40)

    def test_nonexistent_preset(self):
        response = self.client.get("/api/preset/does_not_exist")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
