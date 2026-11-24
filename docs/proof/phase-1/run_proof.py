"""Chạy lại bằng chứng Phase 1: python docs/proof/phase-1/run_proof.py  (từ gốc repo)

gather (preset, không scenario) -> kho.json -> quan; mỗi lượt chạy 2 lần để so từng byte.
Ghi events.txt cạnh file này (JSONL đầy đủ để ở thư mục tạm).
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def frames(*rows):
    return {"frames": [dict(tick=t, **kw) for t, kw in rows]}


ON, OFF = {"interact": True}, {"interact": False}
GATHER = frames((0, {"move": [1, 0]}), (635, ON), (636, OFF), (875, {**ON, "move": [-1, 0]}), (876, OFF), (1750, ON))
QUAN = frames((0, {"move": [-1, 0.5]}), (95, {"move": [0, 0]}), (125, ON), (126, OFF), (380, ON), (381, OFF),
              (382, {"move": [0.76, -0.65]}), (515, {"move": [0, 0]}), (525, ON), (526, OFF))


def main():
    lines = []
    with tempfile.TemporaryDirectory() as d:
        inv = os.path.join(d, "kho.json")
        for mode, fr, extra in (("gather", GATHER, ["--inventory-out", inv]), ("quan", QUAN, ["--inventory", inv])):
            inp = os.path.join(d, mode + ".in.json")
            with open(inp, "w", encoding="utf-8") as f:
                json.dump(fr, f)
            raw = []
            for i in (1, 2):
                out = os.path.join(d, f"{mode}{i}.jsonl")
                subprocess.run([sys.executable, "-m", "chonoi.headless", "--mode", mode, "--seed", "1", "--ticks",
                                "10800", "--inputs", inp, "--out", out, *extra], check=True)
                with open(out, "rb") as f:
                    raw.append(f.read())
            lines.append(f"== {mode} (seed 1) — hai lần giống từng byte: {raw[0] == raw[1]}")
            lines += [r for r in raw[0].decode("utf-8").splitlines() if '"type":"event"' in r or '"type":"end"' in r]
            if mode == "gather":
                with open(inv, encoding="utf-8") as f:
                    lines.append("kho.json: " + f.read().strip())
    with open(os.path.join(HERE, "events.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
