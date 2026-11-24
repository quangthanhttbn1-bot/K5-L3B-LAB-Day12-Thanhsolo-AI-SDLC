"""Test luật Phase 1 của nhóm (bước sim trực tiếp, số liệu đọc từ preset)."""

import copy
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.inputs import LiveInputs
from chonoi.runner import Session

T = load_contract()["tuning"]
G, Q, MENU = T["gather"], T["quan"], T["menu"]


def session(mode, scenario, tuning=T, seed=1):
    return Session(mode, copy.deepcopy(tuning), copy.deepcopy(scenario), seed)


def run(s, n, move=None, **press):
    """Chạy n tick; nút bấm chỉ có cạnh lên ở tick đầu. Trả list event."""
    li, out = LiveInputs(), []
    li.set(move, **press)
    for _ in range(n):
        out += s.step(li.advance())
        if s.done:
            break
    return out


def names(ev):
    return [e["name"] for e in ev]


def timed(ev):
    return [(e["name"], e["tick"]) for e in ev]


class Gather(unittest.TestCase):
    def test_oxy_giam_hoi_va_kep(self):
        s = session("gather", {"player": {"pos": [50, 10]}})
        run(s, 10)
        self.assertEqual(s.sim.oxygen_ticks, G["oxygen_max_s"] * 60 - 10)
        s = session("gather", {"player": {"pos": [50, 0], "oxygen_ticks": 1}})
        run(s, 2)
        self.assertEqual(s.sim.oxygen_ticks, 1 + 2 * G["oxygen_refill_per_tick"])
        run(s, 1000)
        self.assertEqual(s.sim.oxygen_ticks, s.sim.oxygen_max)

    def test_bien_mat_nuoc_tinh_la_mat_nuoc(self):
        s = session("gather", {"player": {"pos": [50, G["surface_depth"]]}})
        run(s, 5)
        self.assertEqual(s.sim.oxygen_ticks, s.sim.oxygen_max)

    def test_dive_surface(self):
        s = session("gather", {"player": {"pos": [50, 0]}})
        self.assertEqual(names(run(s, 30, move=[0, 1])), ["dive"])
        self.assertEqual(names(run(s, 60, move=[0, -1])), ["surface"])

    def test_ngat_roi_xiu_mat_gio(self):
        s = session("gather", {"player": {"pos": [50, 10], "oxygen_ticks": 1}, "hold": ["ca_loc"]})
        ev = run(s, 10_000)
        self.assertEqual(names(ev), ["oxygen_empty"] + ["choke"] * G["hp_max"] + ["faint", "gather_end"])
        self.assertEqual([e["tick"] for e in ev if e["name"] == "choke"],
                         [1 + G["choke_interval_ticks"] * i for i in range(1, G["hp_max"] + 1)])
        self.assertEqual(ev[-1]["data"], {"reason": "fainted", "inventory": {"items": {}}})
        self.assertEqual(s.sim.hp, 0)

    def test_hai_va_moc_lai(self):
        n = G["nodes"][0]
        s = session("gather", {"player": {"pos": n["pos"]}})
        self.assertEqual(names(run(s, 1, interact=True)), ["gather"])
        self.assertEqual(s.sim.hold, [n["kind"]] * G["node_yield"])
        self.assertEqual(run(s, 1, interact=True), [], "nút chưa mọc lại thì không hái được")
        regrow = int(G["regrow_s"] * 60)
        self.assertEqual(timed(run(s, regrow)), [("node_regrown", 1 + regrow)])

    def test_khong_hai_khi_o_duoi_nuoc(self):
        s = session("gather", {"player": {"pos": [G["nodes"][0]["pos"][0], 1]}})
        self.assertEqual(run(s, 1, interact=True), [])

    def test_bang_nhau_lay_id_nho(self):
        nodes = [{"id": i, "kind": "bong_sung", "pos": [x, 0]} for i, x in (("N10", 49), ("N2", 51))]
        s = session("gather", {"player": {"pos": [50, 0]}, "nodes": nodes})
        self.assertEqual(run(s, 1, interact=True)[0]["data"]["node_id"], "N2")

    def test_bat_ca_hoi_chieu(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [50, 10]}, {"id": "F2", "kind": "ca_loc", "pos": [51, 10]}]
        s = session("gather", {"player": {"pos": [50, 10]}, "fish": fish})
        self.assertEqual(names(run(s, 1, catch=True)), ["fish_caught"])
        self.assertEqual(s.sim.hold, ["ca_linh"] * G["fish_yield"]["ca_linh"])
        self.assertEqual(run(s, int(G["catch_cooldown_s"] * 60) - 1, catch=True), [], "đang hồi chiêu")
        self.assertEqual(names(run(s, 1, catch=True)), ["fish_caught"])
        self.assertEqual(s.sim.fish, [])

    def test_bat_hut_va_mat_nuoc(self):
        s = session("gather", {"player": {"pos": [50, 25]}})
        self.assertEqual(run(s, 1, catch=True), [])
        self.assertEqual(s.sim.catch_cd_ticks, 0)
        s = session("gather", {"player": {"pos": [50, 0.5]}, "fish": [{"id": "F1", "kind": "ca_loc", "pos": [50, 1]}]})
        self.assertEqual(run(s, 1, catch=True), [])

    def test_gio_day(self):
        cap = G["hold_capacity"]
        base = {"player": {"pos": [50, 10]}, "fish": [{"id": "F1", "kind": "ca_linh", "pos": [50, 10]}]}
        s = session("gather", {**base, "hold": ["ca_loc"] * cap})
        self.assertEqual(names(run(s, 1, catch=True)), ["hold_full"])
        self.assertEqual(len(s.sim.fish), 1)
        s = session("gather", {**base, "hold": ["ca_loc"] * (cap - 1)})
        self.assertEqual(names(run(s, 1, catch=True)), ["fish_caught", "hold_full"])
        self.assertEqual(len(s.sim.hold), cap)

    def test_cap_ben_truoc_hai(self):
        nodes = [{"id": "N1", "kind": "bong_sung", "pos": G["dock_pos"]}]
        s = session("gather", {"player": {"pos": G["dock_pos"]}, "nodes": nodes})
        self.assertEqual(names(run(s, 1, interact=True)), ["gather_end"])


STOVE, TABLE = Q["stoves"][0], Q["tables"][0]
DISH = "goi_bong_sung"
RECIPE = MENU[DISH]["recipe"]


def cust(**kw):
    return {"id": "C1", "table_id": TABLE["id"], "dish_id": DISH, **kw}


def quan(tuning=T, **sc):
    return session("quan", {"random_customers": False, **sc}, tuning)


class Quan(unittest.TestCase):
    def test_khach_den_dung_lich_va_giu_cho(self):
        s = quan(random_customers=True, stock=RECIPE)
        self.assertEqual(timed(run(s, Q["first_customer_tick"])), [("customer_arrived", Q["first_customer_tick"])])
        c = s.snapshot()["customers"][0]
        self.assertEqual((c["dish_id"], c["reserved"]), (DISH, RECIPE))
        self.assertEqual(s.snapshot()["stock"], RECIPE, "giữ chỗ chưa trừ kho")

    def test_khong_co_mon(self):
        self.assertEqual(names(run(quan(random_customers=True), Q["first_customer_tick"])), ["no_dish"])

    def test_tat_khach(self):
        self.assertEqual(run(quan(stock=RECIPE), 2000), [])

    def test_tron_vong(self):
        s = quan(stock=RECIPE, customers=[cust()], player={"pos": STOVE["pos"]})
        self.assertEqual(names(run(s, 1, interact=True)), ["cook_started"])
        self.assertEqual(s.snapshot()["stock"], {})
        cook = MENU[DISH]["cook_s"] * 60
        self.assertEqual(timed(run(s, cook)), [("dish_ready", 1 + cook)])
        self.assertEqual(names(run(s, 1, interact=True)), ["dish_picked"])
        self.assertEqual(s.snapshot()["hand"], DISH)
        s.sim.pos = list(TABLE["pos"])
        self.assertEqual(names(run(s, 1, interact=True)), ["served"])
        self.assertEqual(names(run(s, int(Q["eat_s"] * 60))), ["paid"])
        price = MENU[DISH]["price"]
        self.assertEqual(s.sim.money, price + int(price * Q["tip_rate"]))
        self.assertAlmostEqual(s.sim.reputation, Q["reputation_initial"] + Q["tip_reputation"])
        self.assertEqual(s.sim.customers, [])

    def test_boa_theo_nguong_kien_nhan(self):
        edge = int(Q["patience_s"] * 60 * Q["tip_min_patience_ratio"])
        for left, tip in ((edge + 1, True), (edge, False)):  # bước này trừ 1 trước khi phục vụ
            s = quan(hand=DISH, player={"pos": TABLE["pos"]},
                     customers=[cust(order_state="assigned", patience_ticks_left=left)])
            run(s, 1, interact=True)
            self.assertEqual(s.sim.customers[0]["tip"] > 0, tip, left)

    def test_bo_di_nha_giu_cho_giam_uy_tin(self):
        s = quan(stock=RECIPE, customers=[cust(patience_ticks_left=2)])
        self.assertEqual(timed(run(s, 2)), [("customer_left", 2)])
        self.assertEqual(s.sim.reputation, Q["reputation_initial"] + Q["left_reputation_delta"])
        self.assertEqual(s.sim._available(), RECIPE)

    def test_uy_tin_kep_bien(self):
        s = quan(reputation=Q["reputation_min"], stock=RECIPE, customers=[cust(patience_ticks_left=1)])
        run(s, 1)
        self.assertEqual(s.sim.reputation, Q["reputation_min"])

    def test_sai_mon_khong_phuc_vu(self):
        s = quan(stock=RECIPE, hand="ca_loc_nuong_trui", player={"pos": TABLE["pos"]}, customers=[cust()])
        self.assertEqual(run(s, 1, interact=True), [])
        self.assertEqual(s.sim.hand, "ca_loc_nuong_trui")

    def test_mon_cua_khach_khac_thi_doi_don(self):
        t = copy.deepcopy(T)
        t["quan"]["tables"].append({"id": "T2", "pos": [12, 2]})
        s = quan(t, stock=RECIPE, hand=DISH, player={"pos": [12, 2]},
                 customers=[cust(order_state="assigned"), cust(id="C2", table_id="T2")])
        self.assertEqual(names(run(s, 1, interact=True)), ["served"])
        c1, c2 = s.sim.customers
        self.assertEqual((c1["order_state"], c1["reserved"], c2["state"]), ("pending", RECIPE, "eating"))

    def test_scenario_mau_thuan(self):
        for sc in ({"customers": [cust()]},  # giữ chỗ quá kho
                   {"customers": [cust(order_state="assigned")]},
                   {"customers": [cust(state="eating")]},
                   {"customers": [cust(dish_id="la")]},
                   {"stoves": [{"id": STOVE["id"], "state": "ready"}]},
                   {"hand": "la"}):
            with self.assertRaises(BadInput, msg=sc):
                quan(**sc)

    def test_het_ca(self):
        self.assertEqual(timed(run(quan(time_left_ticks=3), 10)), [("quan_end", 3)])


if __name__ == "__main__":
    unittest.main()
