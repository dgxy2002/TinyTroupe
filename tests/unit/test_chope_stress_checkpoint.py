import threading
from pathlib import Path

from examples.chope_stress_test import run_checkpoint_path
from tinytroupe.clients.openrouter_client import OpenRouterClient


def test_run_checkpoint_has_an_experiment_local_path():
    assert run_checkpoint_path(Path("experiment"), "chope-001") == Path(
        "experiment/checkpoints/chope-001.json"
    )


def test_openrouter_call_records_can_be_restored_without_aliasing():
    llm_client = OpenRouterClient.__new__(OpenRouterClient)
    llm_client._call_records = []
    llm_client._call_records_lock = threading.RLock()
    source = [{"sequence": 99, "generation_id": "generation-1"}]

    llm_client.restore_call_records(source)
    source[0]["generation_id"] = "changed"

    assert llm_client.get_call_records() == [
        {"sequence": 0, "generation_id": "generation-1"}
    ]
