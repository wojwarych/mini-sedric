import subprocess


def format():
    subprocess.run(["black", "."])
    subprocess.run(["isort", "mini_sedric/", "tests/"])
    subprocess.run(["flake8", "mini_sedric/", "tests/"])
    subprocess.run(
        [
            "autoflake",
            "-r",
            "-cd",
            "--remove-all-unused-imports",
            "--ignore-init-module-imports",
            "mini_sedric",
            "tests",
        ]
    )
    subprocess.run(["pylint", "mini_sedric/", "tests/"])
    subprocess.run(["mypy", "mini_sedric/", "tests/"])


def check():
    subprocess.run(["black", "--check", "."])
    subprocess.run(["isort", "--check", "."])
    subprocess.run(["flake8", "mini_sedric/", "tests/"])
    subprocess.run(
        [
            "autoflake",
            "-r",
            "-c",
            "--remove-all-unused-imports",
            "--ignore-init-module-imports",
            "mini_sedric",
            "tests",
        ]
    )
    subprocess.run(["pylint", "mini_sedric/", "tests/"])
    subprocess.run(["mypy", "mini_sedric/", "tests/"])
