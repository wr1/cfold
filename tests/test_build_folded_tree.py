from cfold.tree.build_folded import build_folded_tree


def test_build_folded_tree(tmp_path):
    """Test generating folded tree."""
    files = [tmp_path / "src" / "main.py", tmp_path / "docs" / "index.md"]
    tree = build_folded_tree(files, tmp_path)
    assert tree.label == "Folded files tree (total lines: 0)"
