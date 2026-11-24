# Task — việc cần làm để hoàn thiện lab Day 12 (nhóm 1 người: Thanhsolo)

> Nguồn: `README.md`, `AGENTS.md`, `TEAM.md`, `docs/`, `tools/check_team.py`.
> Đề chi tiết từng phase **không có trong repo**, mở theo giờ trên lab board: https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg
> Tick `[x]` khi xong.

## 0. Chuẩn bị máy (Windows, Python 3.13)

- [ ] Không cần venv: khung `chonoi/` chỉ dùng thư viện chuẩn.
- [ ] Kiểm `python3 --version` in ra 3.x thật (không phải Microsoft Store). Nếu không: tắt alias python3 trong *Settings → Apps → App execution aliases* hoặc tạm đổi `headless_cmd` sang `python` (không commit thay đổi này).
- [ ] Chạy smoke test (PowerShell):
  ```powershell
  $env:PYTHONPATH = "tests;."
  python -m unittest discover -s tests -v
  ```
- [ ] Thử cửa sổ chơi: `python -m chonoi.live --mode gather` rồi mở http://127.0.0.1:8000/

## 1. Thiết lập repo (làm trước khi code)

- [ ] Đổi tên repo trên GitHub thành `K5-L3B-LAB-Day12-AI-SDLC-Thanhsolo` (*Settings → General → Repository name*), cập nhật `git remote set-url origin ...`.
- [ ] Repo để **public**.
- [ ] Xác định tài khoản GitHub dùng để commit; `git config user.name` / `user.email` khớp tài khoản đó.
- [ ] `TEAM.md`:
  - [ ] Sửa lỗi gõ `**Số người:*` → `**Số người:** 1`.
  - [ ] Điền GitHub handle (đúng tài khoản commit).
  - [ ] Module chính: tất cả (`sim/gather`, `sim/quan`, `client/ui`, `qa`); Vai quy trình: PO + Integrator + QA lead + Scrum/Release (kiêm).
  - [ ] Xóa 3 dòng thành viên trống.
  - [ ] Viết thỏa thuận làm việc (≤ 10 dòng) phù hợp làm một mình: push thẳng `main`, tự gắn tag, tự review code AI trước khi push, quy tắc khi vướng > 10 phút (hỏi trợ giảng AI / giảng viên)...
- [ ] `game.contract.json`: `"team_size": 4` → `1`.
- [x] `docs/clarify.md`: ghi câu hỏi #1 cho giảng viên — *"Nhóm 1 người được chấm phần Làm việc nhóm (25đ) thế nào?"* và *"check_team.py yêu cầu 4–6 người, CI cảnh báo — chấp nhận được không?"*. Ghi câu trả lời khi có. (đã ghi câu hỏi; còn chờ trả lời)
- [x] `docs/contracts/`: chốt schema file kho (`inventory.sample.json`), giao diện sim ↔ UI, danh sách sự kiện. (phần [chờ PRD] điền khi mở đề Phase 1)
- [x] Commit + push phần thiết lập. (1c7ae5f)

## 2. Phase 1 (PRD-0) — tag `phase-1` trước 1:00

- [ ] Đọc đề Phase 1 trên lab board; chỗ mơ hồ ghi vào `docs/clarify.md`. (CHƯA: PRD-0 chưa đọc được; giả định ở clarify 2–12)
- [x] `docs/plan/phase-1.md`: mục tiêu, việc, rủi ro.
- [x] Viết luật `chonoi/sim/gather.py` (tìm `TODO(nhóm)`); số liệu đọc từ `game.contract.json`, RNG qua `Streams`, id qua `IdAllocator`/`sort_by_id`.
- [x] Phần `quan` nếu Phase 1 yêu cầu (`chonoi/sim/quan.py`).
- [x] Smoke test xanh; headless chạy được: `python -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl`.
- [x] `docs/verification/phase-1.md`: bảng AC → cách kiểm → bằng chứng (`docs/proof/phase-1/...`) → kết quả trung thực.
- [x] `docs/ai-usage-log.md`: dòng Phase 1.
- [x] Cập nhật `AGENTS.md` nếu có quy ước mới.
- [ ] Commit, push, gắn tag: `git tag phase-1 && git push origin phase-1`. (đã commit + push, CHƯA gắn tag)

## 3. Phase 2 — tag `phase-2` trước 1:55

- [ ] Đọc đề Phase 2 (có thể có **đổi yêu cầu**); cập nhật `docs/clarify.md`, `docs/contracts/` nếu đổi hợp đồng (ghi lý do / ADR trong `docs/adr/`).
- [ ] `docs/plan/phase-2.md`.
- [ ] Code + test (test ẩn kiểm cả phase trước — đừng làm hỏng Phase 1).
- [ ] `docs/verification/phase-2.md` + bằng chứng `docs/proof/phase-2/`.
- [ ] `docs/retro.md` — mục Phase 2 (tốt / tệ / 1 hành động cho Phase 3).
- [ ] `docs/ai-usage-log.md`: dòng Phase 2.
- [ ] Commit, push, tag `phase-2`.

## 4. Phase 3 — tag `phase-3` trước 2:30

- [ ] Đọc đề Phase 3; cập nhật clarify / contracts.
- [ ] `docs/plan/phase-3.md`.
- [ ] Code + test, không phá phase cũ.
- [ ] `docs/verification/phase-3.md` + `docs/proof/phase-3/`.
- [ ] `docs/ai-usage-log.md`: dòng Phase 3.
- [ ] Commit, push, tag `phase-3`.

## 5. Phase 4 — tag `phase-4` + Release `v1.0.0` trước 3:00

- [ ] Đọc đề Phase 4; hoàn thiện game.
- [ ] `docs/plan/phase-4.md`.
- [ ] `docs/verification/phase-4.md` + `docs/proof/phase-4/`.
- [ ] `docs/retro.md` — mục Phase 4: rà hành động Phase 2, tốt/tệ, số liệu (số commit, token), một lần AI sai và cách phát hiện, nếu làm lại đổi gì. Ghi rõ là làm một mình.
- [ ] `docs/members/<handle>.md` (≤ 200 từ): đã làm (link commit), đã review (tự đọc lại code AI), AI sai ở đâu, học được gì.
- [ ] `docs/ai-usage-log.md`: dòng Phase 4.
- [ ] `CHANGELOG.md`: tóm tắt thay đổi theo phase.
- [ ] Commit, push, tag `phase-4`; tạo GitHub Release `v1.0.0`.

## 6. Harness AI (10 điểm) — làm dần qua các phase

- [ ] `AGENTS.md` được cập nhật qua nhiều phase (lịch sử git phải thấy).
- [ ] Tự viết **≥ 2 skill/hook/command** trong `.agents/skills/` (ví dụ: skill "chạy test + headless + ghi proof", skill "viết verification phase-n"); ghi tên và khi nào dùng ở mục "Skills / hooks" trong `AGENTS.md`.
- [ ] `docs/ai-usage-log.md` có đủ dòng cho mọi phase.

## 7. Sáng tạo (tùy chọn, sau khi lõi đúng)

- [ ] Thêm nội dung mới (nhân vật, cá, món, đồ họa...) nhưng **tắt ở headless**.
- [ ] Ghi mục **"Sáng tạo của nhóm"** trong `README.md`.
- [ ] Asset ngoài chỉ CC0/CC-BY/MIT hoặc tự tạo; ghi nguồn trong `CREDITS.md`.

## 8. Kiểm tra cuối & demo (5 điểm)

- [ ] Mỗi tag `phase-1`…`phase-4` checkout ra đều chạy được và test xanh.
- [ ] ≥ 3 commit có nội dung từ tài khoản trong `TEAM.md` (nên nhiều, đều theo phase).
- [ ] Không commit API key, token, `.env`, `.venv`, `out.jsonl` rác.
- [ ] Chuẩn bị demo ngắn: chơi `gather` → `quan` (`--inventory-out kho.json` rồi `--inventory kho.json`), chỉ bằng chứng và retro.

## Ghi chú riêng cho nhóm 1 người

- Phần Làm việc nhóm (25đ) không làm đúng như đề cho 4–6 người được → thể hiện bằng: commit đều theo phase, tag đúng hạn, TEAM.md + retro ghi rõ kiêm mọi vai, clarify ghi câu trả lời của giảng viên.
- CI sẽ luôn cảnh báo ở bước `check_team.py` (yêu cầu 4–6 người) — cảnh báo không chặn; ghi lý do trong `docs/clarify.md`.
- Không cần nhánh/PR; `standup.md` tùy chọn (mỗi phase 1 dòng là đủ).
