import subprocess


def format():
    subprocess.run(["black", "."])
    subprocess.run(["autoflake", "-r", "--remove-all-unused-imports", "mini_sedric"])
    subprocess.run(["isort", "."])
    subprocess.run(["flake8", "mini_sedric/", "tests/"])
    subprocess.run(["pylint", "mini_sedric/", "tests/"])
    subprocess.run(["mypy", "mini_sedric/", "tests/"])
