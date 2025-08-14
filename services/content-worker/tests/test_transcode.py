import subprocess
import time
from pathlib import Path

import pytest

import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))
from tasks.transcode import transcode_video  # noqa: E402


class DummyClient:
    def __init__(self):
        self.calls = []

    def update_asset(self, asset_id, data):
        self.calls.append((asset_id, data))


def test_transcode_success(monkeypatch, tmp_path):
    def fake_run(cmd, check, stdout, stderr):
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    client = DummyClient()
    src = tmp_path / "video.mp4"
    src.write_text("fake")
    out = transcode_video("asset1", str(src), "hls-720p", client=client)
    assert out.endswith("_hls-720p.m3u8")
    assert client.calls == [
        ("asset1", {"status": "ready", "renditions": {"hls-720p": out}})
    ]


def test_transcode_retry_failure(monkeypatch, tmp_path):
    attempts = {"n": 0}

    def fake_run(cmd, check, stdout, stderr):
        attempts["n"] += 1
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    client = DummyClient()
    src = tmp_path / "video.mp4"
    src.write_text("fake")
    with pytest.raises(subprocess.CalledProcessError):
        transcode_video("asset1", str(src), "hls-720p", client=client)
    assert attempts["n"] == 4
    assert client.calls[-1][1]["status"] == "failed"
