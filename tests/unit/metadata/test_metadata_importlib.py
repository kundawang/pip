from pathlib import Path
from unittest import mock

import pytest

from pip._internal.exceptions import InstallationError
from pip._internal.metadata.importlib._dists import Distribution


def test_iter_entry_points_throws_on_invalid_entry_point(tmp_path: Path) -> None:
    """A ValueError from importlib.metadata entry point parsing (Python 3.15+
    validates entry points while parsing) is surfaced as InstallationError."""
    dist_info = tmp_path / "simple-1.0.dist-info"
    dist_info.mkdir()
    dist_info.joinpath("METADATA").write_text("Name: simple\nVersion: 1.0\n")
    dist_info.joinpath("entry_points.txt").write_text(
        "[console_scripts]\nhello = hello:\n"
    )
    dist = Distribution.from_directory(str(dist_info))

    with mock.patch.object(
        type(dist._dist), "entry_points", new_callable=mock.PropertyMock
    ) as mock_entry_points:
        mock_entry_points.side_effect = ValueError(
            "'hello = hello:' is not a valid entry point"
        )
        with pytest.raises(InstallationError) as e:
            list(dist.iter_entry_points())

    assert "simple" in str(e.value)
    assert "hello = hello:" in str(e.value)
