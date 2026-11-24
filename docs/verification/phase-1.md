# Ma trận truy vết Phase 1

> Chưa có danh sách AC của PRD-0: cột AC là yêu cầu lấy từ khung. "Đạt" = đạt theo khung và giả định trong `docs/clarify.md`, **chưa đối chiếu PRD-0**.
> Bằng chứng: U = [unittest.txt](../proof/phase-1/unittest.txt), E = [events.txt](../proof/phase-1/events.txt) (tạo lại bằng `run_proof.py`).

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|
| Test Contract: mã thoát, tick 0, dòng end | `test_smoke_p1.Contract` | U | Đạt |
| Cùng seed giống từng byte | `test_con_02`; chạy 2 lần mỗi mode | U, E | Đạt |
| Bơi, chặn mép | `test_smoke_p1.Movement` | U | Đạt |
| Oxy, ngạt, ngất mất giỏ | `test_rules_p1.Gather` | U | Đạt (giả định 4) |
| Hái, mọc lại | `test_rules_p1.Gather` | U, E | Đạt |
| Bắt cá, hồi chiêu, giỏ đầy | `test_rules_p1.Gather` | U | Đạt (giả định 5, 6); không có trong lượt đầu–cuối |
| Cập bến, ghi kho, quán đọc kho | `test_smoke_p1.Integration`, lượt đầu–cuối | U, E | Đạt |
| Khách, giữ chỗ, bỏ đi, no_dish | `test_rules_p1.Quan` | U, E | Đạt (giả định 7, 8, 12) |
| Nấu, bưng, phục vụ, trả tiền, boa, uy tín | `test_rules_p1.Quan`, lượt đầu–cuối | U, E | Đạt (giả định 9–11) |
| Scenario mâu thuẫn → mã 2 | `test_scenario_mau_thuan` | U | Một phần: kiểm đến mức khung nêu |
| Đối chiếu AC của PRD-0 | – | – | **Chưa làm** (chưa có đề) |

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt: 54/54 test qua. Chạy trên Windows bằng bản sao có `headless_cmd` = `python`, vì `python3` trên máy là alias Store.
- Điều cần chỉnh cho phase sau: đọc PRD-0, xóa từng giả định; chưa chơi tay trên trình duyệt.
