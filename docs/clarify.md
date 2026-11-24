# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| 1 | 2026-11-24 19:21 | (a) Nhóm 1 người được chấm phần Làm việc nhóm (25đ) thế nào? (b) `check_team.py` yêu cầu 4–6 người, CI cảnh báo — chấp nhận được không? | **Chờ giảng viên trả lời.** Giả định tạm cho (b): giữ nguyên `tools/check_team.py`; bước này đặt `continue-on-error: true` trong `ci.yml` nên chỉ cảnh báo, không chặn. (a): chưa có giả định. | Giảng viên |
| 2 | 2026-11-24 19:38 | PRD-0 chưa đọc được (lab board ghi "Chưa phát hành" khi không đăng nhập). Làm Phase 1 theo gì? | Theo đặc tả trong khung (TODO, schema, UI, test); các dòng 3–12 là **giả định tạm**, có PRD-0 thì theo PRD-0 | Nhóm (tạm) |
| 3 | 2026-11-24 19:38 | `data` của sự kiện chưa có trong khung? | Giả định: xem `docs/contracts/README.md` mục 3 | Nhóm (tạm) |
| 4 | 2026-11-24 19:38 | Tick làm oxy về 0 có tính vào đếm ngạt? | Giả định: không; `choke` đầu tiên sau đúng `choke_interval_ticks` tick kế tiếp. Lên mặt nước thì bộ đếm về 0 | Nhóm (tạm) |
| 5 | 2026-11-24 19:38 | Giỏ còn chỗ ít hơn sản lượng? | Giả định: lấy phần vừa, phát `gather`/`fish_caught` rồi `hold_full`; hết chỗ thì chỉ `hold_full`, nút/cá giữ nguyên, không hồi chiêu | Nhóm (tạm) |
| 6 | 2026-11-24 19:38 | Bắt hụt có hồi chiêu? Cá bắt xong? | Giả định: hụt không hồi chiêu, không sự kiện; đàn cá biến mất | Nhóm (tạm) |
| 7 | 2026-11-24 19:38 | Khách chọn món và bàn thế nào? | Giả định: món ngẫu nhiên (luồng `customer_order`) trong các món đủ nguyên liệu sau khi trừ giữ chỗ; bàn trống id nhỏ nhất; hết bàn thì bỏ lượt, không sự kiện | Nhóm (tạm) |
| 8 | 2026-11-24 19:38 | Nấu món nào, trừ kho lúc nào? | Giả định: nấu đơn pending có id khách nhỏ nhất; trừ kho khi bắt đầu nấu; khách bỏ đi thì nhả giữ chỗ, món đã nấu vẫn còn | Nhóm (tạm) |
| 9 | 2026-11-24 19:38 | Interact chọn đối tượng thế nào? | Giả định: gần nhất trong các đối tượng **đang dùng được**; bằng nhau thì bếp trước bàn, rồi id | Nhóm (tạm) |
| 10 | 2026-11-24 19:38 | Boa và uy tín cộng lúc nào? | Giả định: xét kiên nhẫn lúc phục vụ (>= ngưỡng), cộng tiền + uy tín khi `paid`; tip làm tròn nửa lên | Nhóm (tạm) |
| 11 | 2026-11-24 19:38 | Hết ca khi khách còn ăn/chờ? | Giả định: không thu tiền, không phạt | Nhóm (tạm) |
| 12 | 2026-11-24 19:38 | Mốc khách đến tính theo gì khi scenario đặt `time_left_ticks`? | Giả định: theo số tick từ đầu lượt chạy | Nhóm (tạm) |
