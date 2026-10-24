
import subprocess
import sys


def test_monitor_stops_when_collection_returns_no_listings(tmp_path):
    project_folder = tmp_path

    (project_folder / "collector.py").write_text(
        "def collect_listings():\n"
        "    return []\n"
        "\n"
        "def get_transaction_type(title):\n"
        "    return 'unknown'\n",
        encoding="utf-8"
    )

    (project_folder / "database.py").write_text(
        "def create_tables():\n"
        "    pass\n"
        "\n"
        "def get_all_listings():\n"
        "    raise AssertionError('Database should not be read')\n"
        "\n"
        "def save_listing(listing):\n"
        "    raise AssertionError('Listings should not be saved')\n"
        "\n"
        "def save_event(*args):\n"
        "    raise AssertionError('Events should not be saved')\n",
        encoding="utf-8"
    )

    # Copy the actual monitor.py into the isolated test folder.
    import monitor

    import pathlib
    source_file = pathlib.Path(monitor.__file__)

    (project_folder / "monitor.py").write_text(
        source_file.read_text(encoding="utf-8"),
        encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, "monitor.py"],
        cwd=project_folder,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0
    assert "No listings were collected" in result.stderr
