"""Entry point for the Sample Dashboard (Streamlit + Vega Altair). Run from project root: python run.py"""

import os
import subprocess
import sys


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root, "src")
    app_path = os.path.join(src_dir, "app.py")
    if not os.path.isfile(app_path):
        print(f"Error: app not found at {app_path}", file=sys.stderr)
        sys.exit(1)
    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")
    sys.exit(
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_path, *sys.argv[1:]],
            cwd=root,
            env=env,
        ).returncode
    )


if __name__ == "__main__":
    main()
