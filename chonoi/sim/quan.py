"""Buổi tối — Mở Quán. Khách đến theo lịch, giữ chỗ nguyên liệu, nấu, bưng, phục vụ, trả tiền, uy tín.

Khách: state `waiting` -> `eating`. Đơn (`order_state`): `pending` (đang giữ chỗ nguyên liệu) -> `assigned`
(đã bắt đầu nấu, nguyên liệu đã trừ kho) -> `served`. Giả định của luật: xem docs/clarify.md.
"""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


def _ticks(seconds):
    return int(round(seconds * TICK))


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = list(p.get("pos", t["start_pos"]))
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        hand = scenario.get("hand")
        self.hand = hand.get("dish_id") if isinstance(hand, dict) else hand
        self.hand_for = None  # id khách mà món trên tay được nấu cho (nội bộ, không xuất)
        self.random_customers = scenario.get("random_customers", True)
        self.tick = 0
        self.patience_max = _ticks(t["patience_s"])
        self.time_left_ticks = scenario.get("time_left_ticks", _ticks(t["duration_s"]))
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = sort_by_id([self._load_customer(c) for c in scenario.get("customers", [])])
        self._link_dishes()
        for e in self.customers:
            ids.reserve(e["id"])
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    # --- dựng từ scenario -------------------------------------------------------
    def _load_customer(self, c):
        cid, dish, state = c["id"], c.get("dish_id"), c.get("state", "waiting")
        order = c.get("order_state", "pending")
        if not isinstance(dish, str) or dish not in self.menu:
            raise BadInput(f"customers.{cid}: dish_id phải là món trong menu")
        if state not in ("waiting", "eating") or (state == "waiting" and order not in ("pending", "assigned")):
            raise BadInput(f"customers.{cid}: state/order_state không hợp lệ")
        out = {"id": cid, "table_id": c["table_id"], "state": state, "order_state": order, "dish_id": dish,
               "patience_ticks_left": c.get("patience_ticks_left", self.patience_max),
               "eat_ticks_left": c.get("eat_ticks_left", 0), "reserved": {},
               "price": c.get("price", 0), "tip": c.get("tip", 0)}
        for key in ("patience_ticks_left", "eat_ticks_left", "price", "tip"):
            if isinstance(out[key], bool) or not isinstance(out[key], int) or out[key] < 0:
                raise BadInput(f"customers.{cid}.{key} phải là số nguyên không âm")
        if state == "eating":
            if not {"price", "tip", "eat_ticks_left"} <= set(c) or out["eat_ticks_left"] < 1:
                raise BadInput(f"customers.{cid}: khách eating cần price, tip, eat_ticks_left >= 1")
            out["order_state"] = "served"
        elif out["patience_ticks_left"] < 1:
            raise BadInput(f"customers.{cid}: khách waiting cần patience_ticks_left >= 1")
        elif order == "pending":
            out["reserved"] = dict(self.menu[dish]["recipe"])
        return out

    def _check_stove(self, s):
        for key in ("cook_ticks_left", "ready_ticks"):
            if isinstance(s[key], bool) or not isinstance(s[key], int) or s[key] < 0:
                raise BadInput(f"stoves.{s['id']}.{key} phải là số nguyên không âm")
        if s["state"] not in ("idle", "cooking", "ready"):
            raise BadInput(f"stoves.{s['id']}: state không hợp lệ")
        if s["state"] == "idle":
            if s["dish"] is not None:
                raise BadInput(f"stoves.{s['id']}: bếp idle không có món")
        elif not isinstance(s["dish"], str) or s["dish"] not in self.menu:
            raise BadInput(f"stoves.{s['id']}: món không có trong menu")
        if (s["state"] == "cooking") != (s["cook_ticks_left"] > 0):
            raise BadInput(f"stoves.{s['id']}: cook_ticks_left không khớp state")

    def _link_dishes(self):
        """Kiểm bếp/tay/giữ chỗ; gắn mỗi khách assigned với đúng một món cùng loại (tay trước, rồi bếp theo id)."""
        for s in self.stoves:
            self._check_stove(s)
            s["for"] = None
        if self.hand is not None and (not isinstance(self.hand, str) or self.hand not in self.menu):
            raise BadInput("hand phải là món trong menu")
        for c in self.customers:
            if c["order_state"] != "assigned":
                continue
            if self.hand == c["dish_id"] and self.hand_for is None:
                self.hand_for = c["id"]
                continue
            s = next((s for s in self.stoves if s["for"] is None and s["dish"] == c["dish_id"]), None)
            if s is None:
                raise BadInput(f"customers.{c['id']}: đơn assigned nhưng không có món trên bếp/tay")
            s["for"] = c["id"]
        for k, n in self._available().items():
            if n < 0:
                raise BadInput(f"khách giữ chỗ quá kho: {k}")

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        self.tick += 1
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        # 1. bếp, rồi khách (theo id): chín, trả tiền, hết kiên nhẫn
        self._advance_stoves(events)
        self._advance_customers(events)
        # 2. đi lại; 3. tối đa một interact
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        # 4. hết ca, hoặc khách mới theo lịch
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        elif self.random_customers and self._arrival_due():
            self._arrive(events)
        return events

    # --- luật -------------------------------------------------------------------
    def _available(self):
        """Kho trừ phần khách pending đang giữ chỗ."""
        free = dict(self.stock)
        for c in self.customers:
            for k, n in c["reserved"].items():
                free[k] = free.get(k, 0) - n
        return free

    def _add_reputation(self, delta):
        value = min(self.t["reputation_max"], max(self.t["reputation_min"], self.reputation + delta))
        self.reputation = round(value, 6)  # tránh sai số cộng dồn làm lệch floor() khi tính điểm

    def _advance_stoves(self, events):
        for s in self.stoves:
            if s["state"] == "ready":
                s["ready_ticks"] += 1
            elif s["state"] == "cooking":
                s["cook_ticks_left"] -= 1
                if s["cook_ticks_left"] == 0:
                    s["state"], s["ready_ticks"] = "ready", 0
                    events.append(("dish_ready", {"stove_id": s["id"], "dish_id": s["dish"]}))

    def _advance_customers(self, events):
        for c in sort_by_id(self.customers):
            info = {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"]}
            if c["state"] == "eating":
                c["eat_ticks_left"] -= 1
                if c["eat_ticks_left"] == 0:
                    total = c["price"] + c["tip"]
                    self.money += total
                    self.earned += total
                    self.shift_earned += total
                    if c["tip"] > 0:
                        self._add_reputation(self.t["tip_reputation"])
                    self.customers.remove(c)
                    events.append(("paid", {**info, "price": c["price"], "tip": c["tip"]}))
            else:
                c["patience_ticks_left"] -= 1
                if c["patience_ticks_left"] == 0:
                    self._add_reputation(self.t["left_reputation_delta"])
                    self.customers.remove(c)  # giữ chỗ (nếu có) tự nhả vì nằm trên khách
                    events.append(("customer_left", info))

    def _interact(self, events):
        """Một đối tượng DÙNG ĐƯỢC gần nhất trong interact_radius (bằng nhau: bếp trước bàn, rồi id)."""
        found = []
        for rank, objs, action_of in ((0, self.stoves, self._stove_action), (1, self.tables, self._table_action)):
            for o in objs:
                dist = math.dist(self.pos, o["pos"])
                action = action_of(o) if dist <= self.t["interact_radius"] else None
                if action:
                    found.append((dist, rank, id_key(o["id"]), action))
        if found:
            min(found, key=lambda c: c[:3])[3](events)

    def _stove_action(self, s):
        if s["state"] == "ready" and self.hand is None:
            return lambda events: self._pick(s, events)
        if s["state"] == "idle":
            c = next((c for c in sort_by_id(self.customers) if c["order_state"] == "pending"), None)
            if c:
                return lambda events: self._cook(s, c, events)
        return None

    def _table_action(self, tb):
        c = next((c for c in self.customers if c["table_id"] == tb["id"]), None)
        if c and c["state"] == "waiting" and self.hand == c["dish_id"]:
            return lambda events: self._serve(c, events)
        return None

    def _cook(self, s, c, events):
        for k, n in c["reserved"].items():
            self.stock[k] -= n
        c["reserved"], c["order_state"] = {}, "assigned"
        s.update({"state": "cooking", "dish": c["dish_id"], "ready_ticks": 0, "for": c["id"],
                  "cook_ticks_left": max(1, _ticks(self.menu[c["dish_id"]]["cook_s"]))})
        events.append(("cook_started", {"stove_id": s["id"], "dish_id": c["dish_id"], "customer_id": c["id"]}))

    def _pick(self, s, events):
        self.hand, self.hand_for = s["dish"], s["for"]
        s.update({"state": "idle", "dish": None, "ready_ticks": 0, "for": None})
        events.append(("dish_picked", {"stove_id": s["id"], "dish_id": self.hand}))

    def _serve(self, c, events):
        if self.hand_for != c["id"]:
            self._swap_order(c)
        dish = self.menu[c["dish_id"]]
        happy = c["patience_ticks_left"] >= self.t["tip_min_patience_ratio"] * self.patience_max
        c.update({"state": "eating", "order_state": "served", "reserved": {},
                  "eat_ticks_left": max(1, _ticks(self.t["eat_s"])), "price": dish["price"],
                  "tip": math.floor(dish["price"] * self.t["tip_rate"] + 0.5) if happy else 0})
        self.hand = self.hand_for = None
        events.append(("served", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"]}))

    def _swap_order(self, c):
        """Món trên tay nấu cho khách khác (hoặc khách đã đi): người đó nhận lại giữ chỗ / món đang nấu của `c`."""
        owner = next((o for o in self.customers if o["id"] == self.hand_for and o["state"] == "waiting"), None)
        if owner:
            owner["order_state"], owner["reserved"] = c["order_state"], c["reserved"]
        for s in self.stoves:
            if s["for"] == c["id"]:
                s["for"] = owner["id"] if owner else None

    def _arrival_due(self):
        since = self.tick - self.t["first_customer_tick"]
        return since >= 0 and since % max(1, _ticks(self.t["customer_interval_s"])) == 0

    def _arrive(self, events):
        taken = {c["table_id"] for c in self.customers}
        table = next((tb for tb in self.tables if tb["id"] not in taken), None)
        if table is None:
            return
        free = self._available()
        dishes = [d for d in sorted(self.menu)
                  if all(free.get(k, 0) >= n for k, n in self.menu[d]["recipe"].items())]
        if not dishes:
            events.append(("no_dish", {}))
            return
        dish = self.rng.get("customer_order").choice(dishes)
        c = {"id": self.ids.new("C"), "table_id": table["id"], "state": "waiting", "order_state": "pending",
             "dish_id": dish, "patience_ticks_left": self.patience_max, "eat_ticks_left": 0,
             "reserved": dict(self.menu[dish]["recipe"]), "price": 0, "tip": 0}
        self.customers.append(c)
        events.append(("customer_arrived", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": dish}))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
