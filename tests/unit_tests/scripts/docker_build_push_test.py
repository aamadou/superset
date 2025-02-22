import re
import subprocess
from unittest import mock
from unittest.mock import patch

import pytest

from tests.unit_tests.fixtures.bash_mock import BashMock

original_run = subprocess.run


def wrapped(*args, **kwargs):
    return original_run(*args, **kwargs)


@pytest.mark.parametrize(
    "tag, target, platform, expected_output, branch",
    [
        ("1.0.0", "lean", "linux/amd64", "LATEST_TAG is master", "master"),
        ("2.1.0", "lean", "linux/amd64", "LATEST_TAG is master", "master"),
        ("2.1.1", "lean", "linux/amd64", "LATEST_TAG is latest", "master"),
        ("3.0.0", "lean", "linux/amd64", "LATEST_TAG is latest", "master"),
        ("2.1.0rc1", "lean", "linux/amd64", "LATEST_TAG is 2.1.0", "2.1.0"),
        ("", "lean", "linux/amd64", "LATEST_TAG is foo", "foo"),
        ("2.1", "lean", "linux/amd64", "LATEST_TAG is 2.1", "2.1"),
        (
            "does_not_exist",
            "lean",
            "linux/amd64",
            "LATEST_TAG is does-not-exist",
            "does_not_exist",
        ),
    ],
)
def test_tag_latest_release(tag, target, platform, expected_output, branch):
    with mock.patch(
        "tests.unit_tests.fixtures.bash_mock.subprocess.run", wraps=wrapped
    ) as subprocess_mock:
        result = BashMock.docker_build_push(tag, target, platform, branch)

        cmd = f'./scripts/docker_build_push.sh "{tag}" "{target}" "{platform}"'
        subprocess_mock.assert_called_once_with(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={"TEST_ENV": "true", "GITHUB_REF": f"refs/heads/{branch}"},
        )
        assert re.search(expected_output, result.stdout.strip(), re.MULTILINE)
