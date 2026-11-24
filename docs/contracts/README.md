# Hợp đồng tích hợp — contract v1.0

Chốt theo khung `chonoi/` và `tests/test_smoke_p1.py`, **trước khi đọc PRD-0**. Ký hiệu:
**[chốt]** = code/test trong repo đã thể hiện; **[chờ PRD]** = chưa có nguồn, không đoán, điền khi mở đề.
PRD-0 khác bảng này thì **theo PRD-0**, sửa file này và ghi lý do trong commit hoặc `docs/adr/`.

## 1. File kho [chốt]

Mẫu: [`inventory.sample.json`](inventory.sample.json). Code: `chonoi/inventory.py`.

```json
{"items":{"bong_sung":2,"ca_loc":1}}
```

| Quy tắc | Chi tiết |
|---|---|
| Khóa gốc | Đúng một khóa `items` (object); thừa hoặc thiếu → mã thoát 2 |
| Id hợp lệ | `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`; id lạ → mã 2 |
| Số lượng | Số nguyên ≥ 0 (không nhận boolean, số thực); sai → mã 2. Đọc: bỏ mục bằng 0 |
| Ghi | Khóa xếp theo id, bỏ mục bằng 0, JSON gọn UTF-8, kết thúc `\n`, qua file tạm rồi thay thế |
| Khi nào ghi | Một lần khi `gather` kết thúc và có `--inventory-out`; hết `--ticks` trước thì không đụng file đích |
| Giỏ rỗng | `{"items":{}}` (ví dụ ngất, mất toàn bộ giỏ) |
| Đọc | `quan --inventory`; dùng cùng `quan.stock` trong scenario → mã 2 |

## 2. Giao diện sim ↔ UI [chốt]

UI **chỉ đọc** snapshot và gửi input; không đổi trạng thái sim, không chứa luật. UI bỏ qua trường chưa có.
Sim không đọc đồng hồ thật. Headless và live cùng dùng `runner.Session`.

### Lệnh UI gửi vào

| API (`chonoi.live`) | Body | Ghi chú |
|---|---|---|
| `POST /input` | `{"move":[a,b],"interact":bool,"catch":bool}` | Trạng thái phím **đang giữ**; `move` mỗi số trong [-1, 1]; sai → 400. Sim tự chuẩn hóa vector và lấy cạnh lên |
| `POST /restart` | rỗng | Chơi lại, cùng seed và scenario |
| `GET /state` | – | Snapshot + các trường live bên dưới |

`move`: `gather` = `[x, d]` (d dương = xuống); `quan` = `[x, z]` (z dương = lên/bắc).

### Trạng thái UI được đọc

| Phạm vi | Trường |
|---|---|
| Chung | `type`, `tick`, `sim_tick`, `mode`, `phase`, `phase_tick`, `state` (`playing`/`finished`), `time_left_ticks`, `money`, `earned`, `reputation`, `score` |
| Chỉ live | `meta` (= `tuning[mode]`), `events` (tối đa 40 dòng gần nhất), `finished`, `reason`, `error` |
| `gather` | `player{pos, vel, heading_deg, oxygen_ticks, oxygen_max_ticks, hp, hp_max, zero_oxy_ticks, invuln_ticks, catch_cd_ticks, at_surface}`, `hold` (thứ tự nhặt, cuối = mới nhất), `hold_count`, `hold_capacity`, `nodes[]{id, pos, kind, ready, regrow_ticks}`, `fish[]{id, pos, kind, heading_deg}` |
| `quan` | `player{pos}`, `stock`, `hand`, `stoves[]{id, pos, state, dish, cook_ticks_left, ready_ticks}`, `tables[]{id, pos, customer_id}`, `customers[]` |

Mảng thực thể xếp bằng `sort_by_id`. UI hiện đọc ở khách: `id`, `table_id`, `state`, `dish_id`, `patience_ticks_left`.
**[chờ PRD]**: đủ trường và các giá trị `state` của khách; kiểu của `hand` (UI tạm nhận chuỗi hoặc `{dish_id}`).

## 3. Sự kiện

Dòng JSONL [chốt]: `{"type":"event","tick":k+1,"phase":…,"name":…,"data":{…}}`. Sim phát, theo thứ tự xử lý trong bước;
headless ghi ra JSONL (test đọc), live đưa vào `events` (UI chỉ hiển thị). UI không phát sự kiện.

| Phát | Tên | `data` | Khi nào |
|---|---|---|---|
| gather | `node_regrown` | `{node_id}` [chốt] | `regrow_ticks` về 0 |
| gather | `gather_end` | `{reason, inventory:{items}}` [chốt] | `reason`: `docked`, `time`, `fainted` (`fainted`: luật chưa viết) |
| gather | `dive`, `surface` | `pos` theo TODO trong khung; định dạng [chờ PRD] | Đổi phân vùng dưới nước / mặt nước |
| gather | `oxygen_empty` | [chờ PRD] | Oxy từ dương xuống 0 |
| gather | `choke` | [chờ PRD] | Đủ `choke_interval_ticks` ngạt, -1 Máu |
| gather | `faint` | [chờ PRD] | Máu về 0, phát trước `gather_end` |
| gather | `gather` | [chờ PRD] | Hái nút ở mặt nước |
| gather | `fish_caught` | [chờ PRD] | Bắt được đàn cá |
| gather | `hold_full` | [chờ PRD] | Giỏ đầy khi hái hoặc bắt |
| quan | `quan_end` | `{reason, money, earned, shift_earned, reputation}` [chốt] | Hết ca (`reason`: `time`) |
| quan | `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid` | [chờ PRD] | Nấu → chín → bưng → phục vụ → trả tiền |
| quan | `customer_left`, `no_dish` | [chờ PRD] | Khách bỏ đi / không có món nấu được |

Tên sự kiện chưa có `data` lấy từ TODO trong `chonoi/sim/`; tên sự kiện khách đến (nếu có) [chờ PRD].
