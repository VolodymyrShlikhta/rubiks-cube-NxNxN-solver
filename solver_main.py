"""
Sidecar JSON wrapper for the dwalton76 NxN solver.
Called by the Godot game via OS.execute().

Usage:
    python solver_main.py --state <kociemba_string> --size <2|3|4|5|6|7> [--json]
"""
import argparse
import json
import os
import sys
import time

# When frozen by PyInstaller, prepend the bundle's temp dir to PATH so child
# processes (ida_search_via_graph.exe, kociemba.exe) can be found.
if getattr(sys, "frozen", False):
    _bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    os.environ["PATH"] = _bundle_dir + os.pathsep + os.environ.get("PATH", "")


CUBE_CLASSES = {
    2: ("rubikscubennnsolver.RubiksCube222", "RubiksCube222"),
    3: ("rubikscubennnsolver.RubiksCube333", "RubiksCube333"),
    4: ("rubikscubennnsolver.RubiksCube444", "RubiksCube444"),
    5: ("rubikscubennnsolver.RubiksCube555", "RubiksCube555"),
    6: ("rubikscubennnsolver.RubiksCube666", "RubiksCube666"),
    7: ("rubikscubennnsolver.RubiksCube777", "RubiksCube777"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--order", default="URFDLB")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        if args.size not in CUBE_CLASSES:
            raise ValueError(f"unsupported size {args.size}; supported: {sorted(CUBE_CLASSES)}")

        module_name, class_name = CUBE_CLASSES[args.size]
        module = __import__(module_name, fromlist=[class_name])
        CubeClass = getattr(module, class_name)

        cube = CubeClass(args.state, args.order, None)
        cube.sanity_check()

        t0 = time.time()
        cube.solve([])
        elapsed_ms = int((time.time() - t0) * 1000)

        moves = [str(m) for m in cube.solution if not str(m).startswith("COMMENT")]
        result = {
            "moves": moves,
            "solve_time_ms": elapsed_ms,
            "move_count": len(moves),
        }
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e), "type": type(e).__name__}))
        sys.exit(1)


if __name__ == "__main__":
    main()
