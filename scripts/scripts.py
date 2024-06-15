import subprocess


def format():
    subprocess.run(["black", "."])
    subprocess.run(["isort", "."])
    subprocess.run(["flake8", "mini_sedric/", "tests/"])
    subprocess.run(
        [
            "autoflake",
            "-r",
            "--remove-all-unused-imports",
            "--ignore-init-module-imports",
            "mini_sedric",
            "tests",
        ]
    )
    subprocess.run(["pylint", "mini_sedric/", "tests/"])
    subprocess.run(["mypy", "mini_sedric/", "tests/"])
