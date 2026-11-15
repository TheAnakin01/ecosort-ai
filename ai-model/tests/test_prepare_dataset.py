"""Tests for scripts/prepare_dataset.py. Run from ai-model/:  pytest"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from prepare_dataset import fallback_split, map_class, source_key, to_box_line  # noqa: E402


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Paper", "paper"),
        ("Card Board Paper", "paper"),
        ("News Paper", "paper"),
        ("PET Bottle", "plastic"),
        ("HDPE Plastic", "plastic"),
        ("Single-Use-Plastic", "plastic"),
        ("plastic_bag", "plastic"),
        ("Can/Metal", "metal"),
        ("Aluminium foil", "metal"),
        ("organic_waste", "organic"),
        ("Food (Biodegradable)", "organic"),
        ("banana peel", "organic"),
        ("Food waste", "organic"),
        # Packaging that held food is not organic waste. These three were
        # mapped wrongly in the first real merge.
        ("Disposable food container", None),
        ("Foam food container", None),
        ("Food Can", "metal"),
        ("Fruit juice carton", "paper"),
        ("Glass Bottle", None),
        ("battery can", None),
        ("e-waste", None),
        ("general_waste", None),
        ("trash", None),
        ("Bottle", None),  # could be glass or plastic
        ("candy", None),  # "can" must match as a whole word
        ("Paper Plastic cup", None),  # two materials
    ],
)
def test_map_class_by_keyword(name, expected):
    assert map_class(name, {}) == expected


# Class names shown for GARBAGE CLASSIFICATION 3 (ginas-workspace), added
# 2026-11-15. BIODEGRADABLE -> organic was approved by the product owner.
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("BIODEGRADABLE", "organic"),
        ("CARDBOARD", "paper"),
        ("PAPER", "paper"),
        ("PLASTIC", "plastic"),
        ("METAL", "metal"),
        ("GLASS", None),
        ("CLOTH", None),
    ],
)
def test_garbage_classification_3_classes(name, expected):
    assert map_class(name, {"cardboard": "paper"}) == expected


def test_overrides_win_over_keywords():
    assert map_class("Bottle", {"bottle": "plastic"}) == "plastic"
    assert map_class("Paper", {"paper": "drop"}) is None
    with pytest.raises(ValueError):
        map_class("Bottle", {"bottle": "glass"})


def test_polygon_label_becomes_box():
    line = to_box_line("7 0.2 0.2 0.6 0.2 0.6 0.4 0.2 0.4".split(), 1)
    assert line == "1 0.400000 0.300000 0.400000 0.200000"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        # Sticks out past the right edge: clipped to the image.
        ("0 0.95 0.5 0.2 0.2", "2 0.925000 0.500000 0.150000 0.200000"),
        ("0 0.5 0.5 0 0.2", None),  # no width
        ("0 1.5 0.5 0.2 0.2", None),  # entirely outside the image
        ("0 0.5 abc 0.2 0.2", None),  # not a number
        ("0 0.5 0.5 0.2", None),  # too few values
        ("0 0.1 0.1 0.9 0.1 0.9", None),  # odd number of polygon values
    ],
)
def test_invalid_boxes_are_clipped_or_rejected(line, expected):
    assert to_box_line(line.split(), 2) == expected


def test_source_key_groups_roboflow_copies():
    assert source_key("bottle_12_jpg.rf.abc123.jpg") == "bottle_12_jpg"
    assert source_key("bottle_12_jpg.rf.zzz999.jpg") == "bottle_12_jpg"
    assert source_key("plain_photo.jpg") == "plain_photo"


def test_fallback_split_keeps_copies_of_one_photo_together():
    for photo in range(40):
        splits = {fallback_split(f"photo{photo}_jpg.rf.{copy}.jpg") for copy in ("aa", "bb", "cc")}
        assert len(splits) == 1
    used = {fallback_split(f"photo{photo}_jpg.rf.aa.jpg") for photo in range(200)}
    assert used == {"train", "val", "test"}


def make_source(root: Path, names: list[str], splits: dict[str, dict[str, str]]) -> Path:
    (root / "data.yaml").parent.mkdir(parents=True)
    (root / "data.yaml").write_text(yaml.safe_dump({"names": names}))
    for split, files in splits.items():
        (root / split / "images").mkdir(parents=True)
        (root / split / "labels").mkdir(parents=True)
        for stem, label in files.items():
            # Different bytes per file: identical files are treated as duplicates.
            (root / split / "images" / f"{stem}.jpg").write_bytes(f"fake image {root.name}/{split}/{stem}".encode())
            (root / split / "labels" / f"{stem}.txt").write_text(label)
    return root


def test_merges_two_sources_into_ecosort_layout(tmp_path):
    first = make_source(
        tmp_path / "trashnet",
        ["cardboard", "glass", "metal"],
        {
            "train": {"a": "0 0.5 0.5 0.2 0.2\n1 0.1 0.1 0.1 0.1\n", "only_glass": "1 0.5 0.5 0.2 0.2\n"},
            "valid": {"b": "2 0.3 0.3 0.1 0.1\n"},
        },
    )
    second = make_source(
        tmp_path / "neat",
        ["organic", "PET Bottle"],
        {"test": {"a": "0 0.5 0.5 0.3 0.3\n1 0.2 0.2 0.1 0.1\n"}},
    )
    out = tmp_path / "ecosort"
    overrides = tmp_path / "overrides.yaml"
    overrides.write_text("cardboard: paper\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "prepare_dataset.py"),
            str(first),
            str(second),
            "--out",
            str(out),
            "--overrides",
            str(overrides),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    # cardboard -> paper (0); the glass box is removed from the same photo.
    assert (out / "labels/train/trashnet__a.txt").read_text() == "0 0.500000 0.500000 0.200000 0.200000\n"
    # A photo with only dropped items is left out entirely.
    assert not (out / "images/train/trashnet__only_glass.jpg").exists()
    # "valid" is renamed to "val"; metal is class 2.
    assert (out / "labels/val/trashnet__b.txt").read_text().startswith("2 ")
    # Same file name in two sources does not collide; organic is 3, plastic is 1.
    assert (out / "labels/test/neat__a.txt").read_text().split("\n")[:2] == [
        "3 0.500000 0.500000 0.300000 0.300000",
        "1 0.200000 0.200000 0.100000 0.100000",
    ]
    assert (out / "images/test/neat__a.jpg").exists()
    assert "glass" in result.stdout and "DROPPED" in result.stdout

    # The build record matches what was written.
    report = json.loads((out / "dataset_report.json").read_text())
    assert report["sources"] == ["trashnet", "neat"]
    assert report["class_mapping"]["trashnet"] == {"cardboard": "paper", "glass": None, "metal": "metal"}
    assert report["boxes_per_class"] == {"paper": 1, "plastic": 1, "metal": 1, "organic": 1}
    assert report["boxes_per_class_by_split"]["test"] == {"paper": 0, "plastic": 1, "metal": 0, "organic": 1}
    assert report["images_per_split"] == {"train": 1, "val": 1, "test": 1}
    assert report["boxes_dropped_by_source_class"] == {"trashnet: glass": 2}
    assert report["images_skipped_all_items_dropped"] == 1


def test_invalid_source_boxes_are_removed_and_counted(tmp_path):
    source = make_source(
        tmp_path / "src",
        ["paper"],
        {"train": {"a": "0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0 0.2\n0 2.0 2.0 0.1 0.1\n"}},
    )
    out = tmp_path / "ecosort"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "prepare_dataset.py"), str(source), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    labels = list((out / "labels").rglob("src__a.txt"))
    assert len(labels) == 1
    assert labels[0].read_text() == "0 0.500000 0.500000 0.200000 0.200000\n"
    assert json.loads((out / "dataset_report.json").read_text())["invalid_boxes_removed"] == 2
    assert "Invalid boxes removed" in result.stdout


def test_dry_run_copies_nothing(tmp_path):
    source = make_source(tmp_path / "src", ["paper"], {"train": {"a": "0 0.5 0.5 0.2 0.2\n"}})
    out = tmp_path / "ecosort"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "prepare_dataset.py"), str(source), "--out", str(out), "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert not out.exists()
    assert "paper" in result.stdout


def run_prepare(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / "prepare_dataset.py"), *args], capture_output=True, text=True)


def test_identical_files_are_kept_once_even_across_sources(tmp_path):
    """Public datasets contain each other's photos under different names."""
    first = make_source(tmp_path / "one", ["paper"], {"train": {"a": "0 0.5 0.5 0.2 0.2\n"}})
    second = make_source(
        tmp_path / "two",
        ["paper", "plastic"],
        {
            "valid": {
                "renamed": "0 0.5 0.5 0.2 0.2\n",
                "relabelled": "1 0.5 0.5 0.2 0.2\n",
                "own": "1 0.3 0.3 0.2 0.2\n",
            }
        },
    )
    original = (first / "train/images/a.jpg").read_bytes()
    (second / "valid/images/renamed.jpg").write_bytes(original)
    (second / "valid/images/relabelled.jpg").write_bytes(original)
    out = tmp_path / "ecosort"

    result = run_prepare(str(first), str(second), "--out", str(out))
    assert result.returncode == 0, result.stderr

    written = sorted(p.name for p in (out / "images").rglob("*.jpg"))
    assert written == ["one__a.jpg", "two__own.jpg"]
    report = json.loads((out / "dataset_report.json").read_text())
    assert report["identical_images_removed"] == 2
    assert report["identical_images_with_different_labels"] == 1
    assert report["boxes_per_class"] == {"paper": 1, "plastic": 1, "metal": 0, "organic": 0}
    assert "Identical image files removed: 2" in result.stdout


def test_a_box_listed_twice_is_kept_once(tmp_path):
    source = make_source(tmp_path / "src", ["paper"], {"train": {"a": "0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0.2 0.2\n"}})
    out = tmp_path / "ecosort"
    assert run_prepare(str(source), "--out", str(out)).returncode == 0

    label = next((out / "labels").rglob("src__a.txt"))
    assert label.read_text() == "0 0.500000 0.500000 0.200000 0.200000\n"
    assert json.loads((out / "dataset_report.json").read_text())["repeated_boxes_removed"] == 1


def test_same_file_name_in_two_folders_of_a_source_is_not_overwritten(tmp_path):
    source = make_source(
        tmp_path / "src",
        ["paper"],
        {"train": {"photo": "0 0.5 0.5 0.2 0.2\n"}, "valid": {"photo": "0 0.3 0.3 0.2 0.2\n"}},
    )
    out = tmp_path / "ecosort"
    # With a fresh split both files share one original-photo name, so they land in one folder.
    assert run_prepare(str(source), "--out", str(out), "--resplit").returncode == 0

    images = sorted(p.name for p in (out / "images").rglob("*.jpg"))
    assert images == ["src__photo.jpg", "src__photo_2.jpg"]
    labels = sorted(p.read_text() for p in (out / "labels").rglob("*.txt"))
    assert labels == ["0 0.300000 0.300000 0.200000 0.200000\n", "0 0.500000 0.500000 0.200000 0.200000\n"]


def boxes(count: int, cls: int = 0) -> str:
    return "".join(f"{cls} {0.05 + 0.03 * i:.2f} 0.5 0.02 0.02\n" for i in range(count))


def test_max_share_leaves_out_the_most_crowded_single_class_photos(tmp_path):
    # Labels in the source: 0 = food (organic), 1 = PET bottle (plastic).
    source = make_source(
        tmp_path / "src",
        ["food", "PET bottle"],
        {
            "train": {
                "pile": boxes(20),  # crowded, organic only: left out first
                "few": boxes(3),  # organic only, smaller: left out next if still needed
                "mixed": boxes(10) + boxes(2, cls=1),  # also shows plastic: always kept
                "bottles": boxes(6, cls=1),
            }
        },
    )
    out = tmp_path / "ecosort"
    result = run_prepare(str(source), "--out", str(out), "--max-share", "organic=0.6")
    assert result.returncode == 0, result.stderr

    # 33 of 41 boxes are organic. Without "pile": 13 of 21 (62%), still too many.
    # Without "few" as well: 10 of 18 (56%). "mixed" is never left out.
    written = {p.stem for p in (out / "labels").rglob("*.txt")}
    assert written == {"src__mixed", "src__bottles"}
    report = json.loads((out / "dataset_report.json").read_text())
    assert report["max_share"]["organic"] == {
        "max_share": 0.6,
        "images_left_out": 2,
        "boxes_left_out": 23,
        "share_after": round(10 / 18, 4),
        "limit_reached": True,
    }
    assert report["boxes_per_class"]["plastic"] == 8
    assert "--max-share organic=0.6" in result.stdout


def test_max_share_stops_as_soon_as_the_share_is_reached(tmp_path):
    source = make_source(
        tmp_path / "src",
        ["food", "PET bottle"],
        {"train": {"pile": boxes(20), "few": boxes(3), "bottles": boxes(6, cls=1)}},
    )
    out = tmp_path / "ecosort"
    result = run_prepare(str(source), "--out", str(out), "--max-share", "organic=0.5")
    assert result.returncode == 0, result.stderr
    # Without "pile": 3 organic of 9 boxes = 33%, under 50%, so "few" stays.
    assert {p.stem for p in (out / "labels").rglob("*.txt")} == {"src__few", "src__bottles"}
    cap = json.loads((out / "dataset_report.json").read_text())["max_share"]["organic"]
    assert cap["limit_reached"] is True
    assert cap["share_after"] == round(3 / 9, 4)


def test_max_share_rejects_bad_values(tmp_path):
    source = make_source(tmp_path / "src", ["food"], {"train": {"a": boxes(1)}})
    for bad in ("glass=0.3", "organic=1.5", "organic=lots"):
        result = run_prepare(str(source), "--out", str(tmp_path / f"out_{bad}"), "--max-share", bad, "--dry-run")
        assert result.returncode != 0
