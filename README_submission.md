# Lab 17 — Zep Memory Submission

Số liệu: `reports/benchmark.json` (student), `benchmark_no_memory.json`, 11 case.

## Phân tích

**Hit rate thấp nhất.** Memory-enabled: 11/11 pass, mọi layer 100% (TB 719.5 ms). Điểm yếu chỉ lộ ở baseline no-memory: `long_term` tệ nhất, 0/4 (E02, E03, E08, E09); baseline 2/11 = 18.2%, chỉ E01 và E10 sống vì evidence còn trong thread. `long_term` cũng đắt nhất: 1168–1295 ms, 807–1536 token, reduction 0%.

**Query nặng token nhất.** E02 (*ngon ngu uu tien*) — 1536 token trên full source 221: Context Block phình context, không nén. Kế đó E03 1530, E08 1516.

**E07.** Ghép `long_term` + `semantic`. Hai evidence bắt buộc: `Python` (preference cá nhân, từ user summary) và `Idempotency-Key` (PAYMENT-RULE-3, từ KB dùng chung). 485/565 token, reduction 14.2%.

**Token reduction.** TB 14.2%, rất lệch: E11 74.2% (146 token), E06 67.8%, còn 4 case long_term đều 0%. No-memory 81.8% chỉ vì retrieve **0 token**: 9/11 case reduction 100% và đều fail. Reduction chỉ có nghĩa khi đọc kèm hit rate.

## Reflection

**Layer quan trọng nhất: `long_term`** — gánh 4/11 case và một nửa E07. Rõ nhất ở E09: trả đúng `LOTUS-88 / Java / Spring Boot` trong khi `ORCHID-27` bị cấm; chỉ scope theo `user_id` mới vừa nhớ vừa cách ly.

**Trade-off.** Context Block cho fact đã hợp nhất, sẵn entity resolution + recency (E08 pass không cần logic riêng), đổi lại 1.2–1.3 s và block lớn không cắt được. Redis + Qdrant rẻ, sắc hơn (E01 0.0 ms, E11 213.9 ms) nhưng compaction, ranking, xung đột phải tự lo.

**Guardrail.** Ghi durable qua `require_memory_consent` + allowlist `allowed_memory_types` (`data/consent.json`), PII minimize trước khi ghi. Background write không tự cấp quyền: `prime_eval_thread` add query với `ignore_roles=["user"]` nên nội dung retrieve không leo ngược vào user graph. Xoá theo DELETE-VERIFY-ALL: `src.forget` xoá, `--verify-only` replay trên Zep lẫn Redis.

**E08 & E10.** E08 là scope-specific conflict: Minh thích Python, nhưng backend BLUEBIRD-42 bắt buộc TypeScript + NestJS — memory phải trả ràng buộc mới nhất theo scope dự án, không phải preference toàn cục. E10 là durable constraint: sau 6 lượt filler, `REVIEW-DEADLINE-1600` vẫn phải nằm trong `<DURABLE_NOTES>`, không trôi khỏi sliding window. Nhớ nhiều không bằng nhớ đúng scope và không quên ràng buộc.

## Evidence

Ảnh trong `submission/` (có command + kết quả): `long_term.png` (E09, E02, E03, E08 PASS) · `episodic.png` (E04, E05 PASS) · `semantic.png` (E06, E11 PASS) · `privacy.png` (`src.forget` delete + `--verify-only`).
