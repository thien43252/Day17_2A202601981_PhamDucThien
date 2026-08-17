# PLAN — Hoàn thiện Lab 17: Multi-Memory Agent với Zep

> Kế hoạch thực thi chi tiết cho `Day17-Track3-ZepMemory4Agent`.
> Mục tiêu tối thiểu: **≥ 56/80 điểm nền + hit rate ≥ 9/11**. Mục tiêu mở rộng: **100/100** (golden 20/20 + UI demo).

---

## 0. TL;DR — 6 việc quyết định điểm

| # | Việc                                                       |                     Điểm | Thời lượng ước tính |
| - | ----------------------------------------------------------- | -------------------------: | ------------------------- |
| 1 | Điền`ZEP_API_KEY` + smoke + seed                        |               tiên quyết | 15'                       |
| 2 | Viết 4 hàm trong`src/memory_student.py`                 | 47/56 (E02–E09, E11, E07) | 60–75'                   |
| 3 | Chạy benchmark student + no_memory + compare               |            6 (phân tích) | 10'                       |
| 4 | Privacy drill (forget + verify-only) + screenshot           |                          6 | 10'                       |
| 5 | `README_submission.md` (7 câu) + 4 screenshot            |                         12 | 25'                       |
| 6 | Bonus: golden 20/20 (+10) và UI`retrieve_for_case` (+10) |                        +20 | 45'                       |

---

## 1. Hiện trạng repo (đã kiểm tra)

**Đã có sẵn, không phải viết:** ingestion (`zep_common.py`), evaluator (`evaluate.py`), short-term (`short_term.py`), budget manager (`context_budget.py`), router, privacy guard, forget, compare, report HTML, LangGraph demo, UI shell.

**Còn thiếu / cần xử lý:**

| Phát hiện                                                                                                            | Ảnh hưởng                                           | Xử lý                               |
| ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------- |
| `.env` có `ZEP_API_KEY=` **rỗng**                                                                          | Mọi lệnh Zep fail ngay                               | Blocker#1 — điền key trước tiên |
| `.env` có `GEMINI_API_KEY=` **rỗng**                                                                       | Chat trong UI không sinh reply (retrieval vẫn chạy) | Chỉ cần nếu làm bonus UI          |
| `src/memory_student.py`: 4 `NotImplementedError`                                                                   | Mất 47/56 điểm auto                                 | Phase B–E                            |
| `src/demo_ui.py`: còn 1 `BONUS TODO` (`retrieve_for_case`) — **TODO thứ 5 mà README không liệt kê** | Bonus UI = 0 nếu để stub                            | Phase G                               |
| `reports/` chỉ có `EXPECTED_FORMAT.md`                                                                           | Chưa có artefact nào                                | Sinh ở Phase F                       |
| Chưa có`README_submission.md`, chưa có `submission/`                                                           | Mất 12đ + artefact                                   | Phase H                               |
| `main.py`, `pyproject.toml`, `uv.lock`, `.python-version` untracked; `Dockerfile`/`README.md` đã sửa    | Không ảnh hưởng chấm, nhưng nên commit gọn     | Phase I                               |
| Docker 29.6.2 + Compose v5.3.1**có sẵn**                                                                       | Chạy đúng đường docker của đề                 | OK                                    |

**Ràng buộc chấm điểm phải nhớ:**

- Chỉ được sửa `src/memory_student.py` và `src/demo_ui.py`. Sửa file khác làm fail `pytest` → trừ điểm artefact.
- Không copy `memory_reference.py` rồi đổi tên (−30 khối auto nếu không giải thích được).
- Không commit `.env`, `ZEP_API_KEY`, `data/golden_eval.json`.

---

## 2. Phase 0 — Môi trường (0–15 phút)

### 2.1 Blocker: điền API key

```powershell
# Mở .env, điền:
# ZEP_API_KEY=<key thật>
# (tuỳ chọn, chỉ cho bonus UI) GEMINI_API_KEY=<key Google AI Studio>
```

Kiểm tra `.env` vẫn đang bị `.gitignore` bắt (đã xác nhận có dòng `.env`), và `REDIS_URL=redis://redis:6379/0`, `QDRANT_URL=http://qdrant:6333` — hai giá trị này **chỉ đúng khi chạy trong Docker**.

### 2.2 Đường chạy chính (Docker — bám đúng đề)

```bash
docker compose build
docker compose up -d redis qdrant
docker compose run --rm app python -m src.smoke
```

Kỳ vọng 4 dòng `[OK]`: Redis, Qdrant, sessions.json ≥ 10 evaluations, `ZEP_API_KEY is present`.

### 2.3 Đường chạy phụ (local uv — dùng khi Docker build chậm/lỗi mạng)

Repo đã có `.venv` + `pyproject.toml` (uv). Nếu chạy local thì vẫn phải bật Redis/Qdrant bằng Docker và **override 2 URL**:

```powershell
docker compose up -d redis qdrant
$env:REDIS_URL="redis://localhost:6379/0"; $env:QDRANT_URL="http://localhost:6333"
uv run python -m src.smoke
```

> Lưu ý: `.env` được `config.py` load **sau** nên biến trong `.env` sẽ ghi đè? Không — `load_dotenv` mặc định **không** override biến môi trường sẵn có, nên `$env:` ở trên thắng. Nếu vẫn trỏ sai host, sửa tạm 2 dòng URL trong `.env` (file này gitignore, an toàn).

### 2.4 Seed Zep — chạy MỘT lần, chạy sớm

```bash
docker compose run --rm app python -m src.seed
```

Seed sẽ: reset 2 user (`minh-lab17`, `lan-lab17`), reset + nạp semantic graph từ `data/knowledge.jsonl`, rồi **poll** tới khi 4 marker searchable (`PAYMENT-RULE-3`, `CONN-POOL-FIRST`, `DELETE-VERIFY-ALL`, `BUDGET-10-4-3-3`) và ingest 3 stage hội thoại.

- Poll timeout mặc định 240s/probe (`ZEP_POLL_TIMEOUT`). Seed có thể mất vài phút → **bấm chạy rồi đọc code song song**, đừng ngồi chờ.
- Sau seed, mọi lệnh evaluate dùng `--reuse-seeded` để không ingest lại.

### 2.5 Chốt baseline offline ngay (không tốn Zep call)

```bash
docker compose run --rm app pytest -q                      # phải xanh 11/11
docker compose run --rm app python -m src.evaluate --impl no_memory
```

`--impl no_memory` không cần Zep → chạy được cả khi seed chưa xong. Nó sinh `reports/benchmark_no_memory.{json,md}` (kỳ vọng chỉ E01/E10 PASS).

**DoD Phase 0:** smoke 4/4 OK · seed in `Seed complete.` · `pytest -q` xanh · có `reports/benchmark_no_memory.json`.

---

## 3. Phase A — Short-term & compaction (15–35 phút, không viết code)

```bash
docker compose run --rm app python -m src.demo_short_term
```

Quan sát 3 panel: `buffer` (giữ hết, token tăng tuyến tính) · `summary` (nén cũ, giữ 2 turn cuối) · `sliding` (summary + durable notes + K turn cuối — default của lab).

**Thí nghiệm bắt buộc:** sửa tạm `max_recent_messages=6` → `4` trong [src/demo_short_term.py:20](src/demo_short_term.py#L20), chạy lại, xác nhận `sliding` **vẫn** giữ `REVIEW-DEADLINE-1600` nhờ `<DURABLE_NOTES>` dù raw turn đã bị evict. **Chạy xong revert lại 6** (giữ working tree sạch; `tests/test_short_term.py` đã lock hành vi này).

Đọc để hiểu cơ chế: [short_term.py:46](src/short_term.py#L46) `detect_pressure`, [short_term.py:51](src/short_term.py#L51) `extract_durable_notes` (regex `\b[A-Z][A-Z0-9-]{5,}\b` chính là thứ giữ được marker), [short_term.py:72](src/short_term.py#L72) `compact`, [short_term.py:104](src/short_term.py#L104) `render`.

**Ghi ngay 3 gạch đầu dòng vào nháp** cho `README_submission.md`: compaction giữ state/decision/TODO/constraint chứ không "tóm tắt văn học"; buffer không đủ vì token tuyến tính và bị cắt đầu khi tràn.

> E01 và E10 chấm bằng `ShortTermMemory` local trong `evaluate.py` (không đi qua `StudentMemory`) → 9 điểm này gần như "free", nhưng vẫn phải chạy full benchmark mới có trong report.

**DoD:** hiểu vì sao E10 PASS · đã revert `demo_short_term.py`.

---

## 4. Phase B — TODO 1/4 `retrieve_long_term` (35–70 phút) — 20 điểm

**File:** [src/memory_student.py:21](src/memory_student.py#L21). **Case:** E02 (5đ), E03 (5đ), E08 (5đ), E09 (5đ).

### Khung cần viết

```python
def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
    prime_eval_thread(self.client, user_id, thread_id, query)   # đã cho sẵn
    user_context = self.client.thread.get_user_context(thread_id=thread_id)
    context_block = getattr(user_context, "context", "") or ""
    # + phần fact search (xem "Vì sao phải thêm edges" bên dưới)
    return ...
```

### Vì sao **phải** thêm `graph.search(scope="edges")`

E03 yêu cầu đồng thời `"benchmark report"` **và** `"16:00"`. Context Block là bản tóm tắt do Zep sinh — nó rất hay giữ ý "còn open loop viết benchmark report" nhưng **rụng mốc giờ `16:00`**. Fact search trên `scope="edges"` trả về câu fact nguyên văn kèm `valid_at/invalid_at`, giữ được `16:00` và đồng thời phục vụ luôn phần giải thích recency cho E08.

Vì vậy công thức an toàn là: `context_block` **+** `render_graph_search(edges_results)`, nối bằng `join_nonempty([...], sep="\n\n")`.

Điểm cần tự quyết (đừng chép mù):

- `limit` cho edges: **≥ 20**. Limit thấp (5–10) hay miss fact deadline/open-loop → E03 FAIL.
- Bọc `cap_query(query)` trước mọi `graph.search` (Zep từ chối query > 400 ký tự; golden có query 450–600 ký tự → không bọc là chết cả khối golden).
- Bọc `try/except` quanh edges search: nếu Zep lỗi thì vẫn trả về context block thay vì ném exception (evaluate.py bắt exception → case tự động FAIL).

### Chạy riêng nhóm long-term

```bash
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --only-layer long_term
```

### Checklist đọc kết quả

- [ ] E02 có `Python` (preference xuyên thread mới `eval-e02`).
- [ ] E03 có cả `benchmark report` và `16:00`.
- [ ] E08 có `BLUEBIRD-42` + `TypeScript` + `NestJS` → recency/scope thắng preference Python cũ.
- [ ] E09 (user `lan-lab17`) có `LOTUS-88` + `Java` + `Spring Boot` và **không** có `ORCHID-27` → isolation. Nếu lộ `ORCHID-27` nghĩa là truyền sai `user_id`.

**Câu phải trả lời được khi vấn đáp:** tại sao cần `prime_eval_thread`? → Context Block chọn nội dung theo *relevance với thread hiện tại*; thread eval mới tinh, phải bơm chính câu query vào (với `ignore_roles=["user"]` để không làm bẩn graph) thì Zep mới biết lấy fact nào.

---

## 5. Phase C — TODO 2/4 `retrieve_episodic` (70–85 phút) — 10 điểm

**File:** [src/memory_student.py:31](src/memory_student.py#L31). **Case:** E04 (6đ), E05 (4đ).

```python
results = self.client.graph.search(
    user_id=user_id,              # KHÔNG phải graph_id
    query=cap_query(query),
    scope="episodes",
    limit=15,
)
return render_graph_search(results, episode_char_cap=180)
```

**Bẫy chính — `episode_char_cap`:** episode của user là message hội thoại dài dòng. Với budget episodic chỉ 3% (240 token ở `LAB_CONTEXT_TOKENS=8000`), 1–2 episode dài sẽ chiếm hết chỗ và đẩy episode chứa marker (`ASYNC-FIX-20`, `connection churn`, `timeout threshold`) ra khỏi context → E04/E05 FAIL. Cắt mỗi episode ~180 ký tự để giữ được nhiều episode phân biệt hơn. `limit` nên 10–15, không phải 5.

> Lưu ý: E04/E05 chạy ở nhánh `layer == "episodic"` nên **không** đi qua `assemble_context` (không bị trim). Nhưng cap vẫn cần vì nó quyết định *episode nào* lọt vào chuỗi render và độ nhiễu. Nếu FAIL, thử `limit=20`.

```bash
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --only-layer episodic
```

- [ ] E04: `ClientSession`, `concurrency=20`, `ASYNC-FIX-20`.
- [ ] E05: `connection churn`, `timeout threshold`.

---

## 6. Phase D — TODO 3/4 `retrieve_semantic` (85–100 phút) — 11 điểm

**File:** [src/memory_student.py:40](src/memory_student.py#L40). **Case:** E06 (6đ), E11 (5đ).

```python
q = cap_query(query)
try:
    results = self.client.graph.search(graph_id=graph_id, query=q, scope="episodes", limit=8)
except Exception:
    results = self.client.graph.search(graph_id=graph_id, query=q, scope="nodes", limit=8)
return render_graph_search(results)     # KHÔNG cap ký tự ở đây
```

**Ba bẫy:**

1. `graph_id=` chứ không `user_id=` — dùng `user_id` sẽ trả preference cá nhân → E06/E11/E07 cùng 0đ.
2. `scope="episodes"` giữ **text gốc** của document nên còn nguyên marker literal `PAYMENT-RULE-3`, `CONN-POOL-FIRST`. `scope="auto"` trả fact đã trích xuất, **rụng mã marker** → FAIL dù nội dung "đúng ý".
3. **Không** truyền `episode_char_cap` ở đây: marker nằm ở **cuối** mỗi document trong `knowledge.jsonl` (`... Marker: PAYMENT-RULE-3.`) — cắt đầu là mất marker.

```bash
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --only-layer semantic
```

- [ ] E06: `Idempotency-Key`, `max-3-retries`, `exponential-backoff`.
- [ ] E11: `connection pooling`, `CONN-POOL-FIRST`.

---

## 7. Phase E — TODO 4/4 `assemble_context` (100–110 phút) — 6 điểm

**File:** [src/memory_student.py:49](src/memory_student.py#L49). **Case:** E07 (mixed).

```python
def assemble_context(self, layers):
    return self.budget.assemble(layers)
```

`ContextBudgetManager` ([context_budget.py:38](src/context_budget.py#L38)) đã lo: thứ tự priority `short_term → long_term → episodic → semantic`, limit 10/4/3/3 (= 800/320/240/240 token), trim **giữ đầu bỏ đuôi**, và trả `(merged_text, breakdown)`.

Phải hiểu để giải thích: E07 mixed mặc định lấy `["long_term", "semantic"]` ([evaluate.py:116](src/evaluate.py#L116)) → cần `Python` từ long-term và `Idempotency-Key` từ semantic. Nếu TODO 1 hoặc TODO 3 sai thì E07 FAIL theo. Trim giữ phần đầu vì graph search xếp kết quả relevance cao lên trước — nếu tự viết trim mà cắt đuôi ngược lại, semantic sẽ mất marker.

**Không tự chế budget khác** — `tests/test_context_budget.py` lock đúng tỉ lệ 10/4/3/3 và thứ tự thẻ `<SHORT_TERM> … <SEMANTIC>`.

---

## 8. Phase F — Benchmark đầy đủ + comparison (110–120 phút) — 6 điểm phân tích

```bash
docker compose run --rm app python -m src.evaluate --impl no_memory                    # nếu chưa chạy
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
docker compose run --rm app python -m src.compare_reports
```

Sinh ra: `reports/benchmark.{json,md}`, `reports/benchmark_no_memory.{json,md}`, `reports/comparison.md`.

**Mục tiêu: 11/11. Ngưỡng đạt: 9/11.**

Trích số liệu ra nháp để viết report (đọc từ `reports/benchmark.json`):

| Cần lấy                          | Lấy ở đâu                                   |
| ---------------------------------- | ----------------------------------------------- |
| Layer có hit rate thấp nhất     | nhóm`results[].layer` + `passed`           |
| Case retrieve nhiều token nhất   | `max(results[].retrieved_tokens)`             |
| Token reduction trung bình 2 impl | `summary.avg_token_reduction` của cả 2 file |
| Latency trung bình                | `summary.avg_latency_ms`                      |
| Breakdown budget của E07          | `results[E07].budget_breakdown`               |

**Bonus report đẹp (đường an toàn cho +6 nếu không kịp UI):**

```bash
docker compose run --rm app python -m src.report_html --all --log reports/run.log
# hoặc: make student-report  (chạy benchmark + tee log + render HTML một phát)
```

**Chốt chặn:** commit `reports/` **trước** khi sang Phase G. Xoá user mà chưa có `benchmark.md` = 0 điểm khối auto.

---

## 9. Phase G — Privacy drill (120–130 phút) — 6 điểm

Đọc trước `data/consent.json` và [src/privacy_guard.py](src/privacy_guard.py) (opt-in gate + redact email/phone trước khi ingest).

```bash
docker compose run --rm app python -m src.forget --user-id minh-lab17          # chụp màn hình
docker compose run --rm app python -m src.forget --user-id minh-lab17 --verify-only   # chụp màn hình
```

Kỳ vọng in ra:

```
Zep user absent: True
Redis user keys remaining: 0
```

**Thứ tự bắt buộc — sai là mất điểm:**

1. Đã commit `reports/benchmark.md` ✅
2. Forget → chụp `privacy.png` (2đ delete + 4đ verify; bỏ verify chỉ còn tối đa 2/6)
3. **Chụp xong, seed lại NGAY**: `docker compose run --rm app python -m src.seed` — vì golden vẫn cần graph của Minh. Quên seed lại → golden fail hàng loạt → 0 điểm cộng.
4. Không forget lần hai; dùng lại screenshot cũ.

Chỉ xoá user lab, **không** đụng semantic graph dùng chung (đó là domain knowledge, không chứa PII) — đây chính là ý cần viết trong report.

---

## 10. Phase H — Artefact nộp bài (130–145 phút) — 12 điểm

### 10.1 `README_submission.md` — tối đa **400 từ**, phải đủ 7 câu

Khung viết (mỗi câu 2–3 câu văn, bám số liệu thật từ `benchmark.json`):

**Nhóm 3 câu thực hành (6đ):**

1. *Layer quan trọng nhất trong bộ test này + chỉ rõ case* → long-term (4/11 case: E02, E03, E08, E09 = 20/56 điểm auto, và còn gánh một nửa E07). **Bắt buộc chỉ tên case**, không chỉ = mất 1đ.
2. *Trade-off Context Block (Zep) vs Redis+Qdrant tự build* → Zep lo extraction fact/episode, temporal validity (`valid_at/invalid_at`), user isolation, relevance-based context; đổi lại là ingestion bất đồng bộ (phải poll), phụ thuộc vendor, khó kiểm soát nội dung tóm tắt. Redis+Qdrant rẻ, latency thấp, kiểm soát hoàn toàn schema nhưng phải **tự** viết extraction, conflict/recency, TTL, quyền xoá. Trả lời kiểu "Zep dễ hơn" = 1/2đ.
3. *Guardrail chống memory poisoning* → bám đúng lab: consent gate `require_memory_consent` + `minimize_pii` trước ghi; `heartbeat` chỉ được dedupe/mark stale/recap, **không** được tự thêm instruction hay quyền mới vào durable memory; provenance bắt buộc (`source`, `timestamp`, `confidence` theo `control_plane/MEMORY_SCHEMA.md`); conflict theo recency + scope, không xoá fact cũ; ghi durable chỉ từ nguồn tin cậy chứ không từ mọi câu user nói.

**Nhóm 4 câu phân tích benchmark (6đ, cần kèm `comparison.md`):**
4. Layer nào hit rate thấp nhất (kèm con số).
5. Case nào retrieve nhiều token nhất (kèm `retrieved_tokens`).
6. E07 cần kết hợp layer nào, evidence bắt buộc là gì (long-term `Python` + semantic `Idempotency-Key`).
7. Token reduction so với full source, và vì sao no-memory reduction cao mà hit rate thấp (không retrieve gì thì reduction ~100% nhưng sai) → reduction chỉ có nghĩa khi đọc **cùng** hit rate.

**Khuyến khích thêm 2–4 câu** về E08 (recency: constraint mới theo scope `BLUEBIRD-42` đè preference cũ mà không xoá preference cho `ORCHID-27`) và E10 (compaction giữ constraint trong durable notes).

### 10.2 Screenshot — thư mục `submission/`

| File              | Nội dung                       |
| ----------------- | ------------------------------- |
| `long_term.png` | Terminal E02/E03/E08(/E09) PASS |
| `episodic.png`  | E04/E05 PASS                    |
| `semantic.png`  | E06/E11 PASS                    |
| `privacy.png`   | forget + verify-only            |

### 10.3 Danh sách file nộp

**Cốt lõi (thiếu 1 = không đạt):** `src/memory_student.py` · `reports/benchmark.md` + `reports/benchmark.json` · `README_submission.md`.
**Minh chứng (6đ):** `reports/comparison.md` · `reports/benchmark_no_memory.md` · 4 screenshot.
**Cộng:** `reports/golden_benchmark.{json,md}` · `src/demo_ui.py` + screenshot/video 30s.

---

## 11. Phase I — Bonus (60 phút cuối)

### 11.1 Golden set (+10, all-or-nothing)

Phút 110 giảng viên phát `data/golden_eval.json` (gitignore). Copy đúng path rồi:

```bash
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
```

Điều kiện +10: `summary.perfect == true` **và** `passed == 20`. 19/20 = 0.

**Chuẩn bị trước để golden không tạch:**

- ✅ Đã `cap_query()` trong cả 3 hàm search (golden có query dài > 400 ký tự — đây là lý do #1 làm golden fail).
- ✅ Đã seed lại sau khi forget `minh-lab17`.
- ✅ Không hardcode `user_id`/`thread_id`/`graph_id`; luôn dùng tham số truyền vào (golden có case của Lan và case isolation G08/G09/G19).
- ✅ `limit` đủ rộng (edges ≥ 20, episodic 15, semantic 8).
- ❌ Không sửa file golden. Không chạy `--impl reference` rồi nộp như student.

### 11.2 UI demo (+10) — viết `retrieve_for_case`

**File:** [src/demo_ui.py:87](src/demo_ui.py#L87). Đây là TODO thứ 5 (README không nhắc). Shell, badge, metric budget, chat Gemini đã wire sẵn — chỉ cần trả về đúng dict.

```python
def retrieve_for_case(memory, case, extra_messages):
    layers = {"short_term": "", "long_term": "", "episodic": "", "semantic": ""}

    # 1) short-term: fixture_messages nếu có, else message của thread trong sessions.json,
    #    rồi append extra_messages (lịch sử chat trong UI)
    stm = ShortTermMemory(strategy="sliding", max_recent_messages=6, pressure_tokens=450)
    # ... stm.add(role, content) cho từng message ...
    layers["short_term"] = stm.render()

    # 2) chọn layer durable theo case["retrieve_layers"] (mixed) hoặc case["expected_layer"]
    #    -> memory.retrieve_long_term(user_id, thread_id, query) / retrieve_episodic(user_id, query)
    #       / retrieve_semantic(settings.semantic_graph_id, query)

    merged, budget = memory.assemble_context(layers)
    return {"merged_context": merged, "layers": layers, "budget": budget}
```

Gợi ý: dùng `load_dataset()` để tìm user/thread khi case không có `fixture_messages` (E01 dùng thread `minh-s1`); nên gọi cả 3 layer durable khi ở chế độ chat tự do để demo "nhìn như mini product".

Checklist 4 mục ăn đủ 10đ: (1) load list case ✓ có sẵn · (2) hiện query/layer/user/thread ✓ có sẵn · (3) chạy retrieval + hiện evidence từng layer ← **phần bạn viết** · (4) chat tiếp đúng user/thread, giữ history ← cần `GEMINI_API_KEY`, không có key thì UI fallback hiện context (vẫn chạy được nhưng yếu hơn khi demo).

```bash
make ui     # http://localhost:8501
```

Nếu không kịp UI: chỉ report HTML đẹp → **tối đa 6/10**. Hai hướng không cộng chồng.

---

## 12. Bảng debug nhanh

| Triệu chứng                                                           | Nguyên nhân                                             | Xử lý                                                 |
| ----------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------- |
| Chỉ E01, E10 PASS (2/11)                                               | Chưa implement 4 TODO                                    | Phase B–E                                              |
| Mọi case Zep FAIL,`error` = `RuntimeError: ZEP_API_KEY is missing` | `.env` rỗng                                            | Phase 0.1                                               |
| `TimeoutError: Zep ingestion/search did not become ready`             | Ingestion bất đồng bộ chưa xong                      | Chờ, hoặc tăng`ZEP_POLL_TIMEOUT` trong `.env`    |
| E03 thiếu`16:00`                                                     | Chỉ dùng Context Block                                  | Thêm`graph.search(scope="edges", limit>=20)`         |
| E04/E05 thiếu marker                                                   | Episode dài chiếm chỗ                                  | `episode_char_cap=180`, tăng `limit`               |
| E06/E11 thiếu`PAYMENT-RULE-3`/`CONN-POOL-FIRST`                    | Dùng`scope="auto"` hoặc cap ký tự                   | `scope="episodes"`, bỏ cap                           |
| E06/E11 trả về preference cá nhân                                   | Search bằng`user_id`                                   | Đổi sang`graph_id`                                  |
| E09 dính`ORCHID-27`                                                  | Sai`user_id`                                            | Luôn truyền`user_id` từ case                       |
| Golden FAIL nhiều case dài                                            | Query > 400 ký tự                                       | `cap_query()` ở cả 3 hàm                           |
| Golden FAIL hàng loạt sau privacy                                     | Quên seed lại                                           | `python -m src.seed`                                  |
| `pytest` đỏ                                                         | Đã sửa file ngoài`memory_student.py`/`demo_ui.py` | `git checkout` file đó                              |
| Redis/Qdrant unreachable khi chạy local                                | URL trỏ hostname docker                                  | Override`REDIS_URL`/`QDRANT_URL` sang `localhost` |

---

## 13. Vệ sinh Git & kiểm tra cuối

```bash
git status --short                 # KHÔNG được thấy .env hay data/golden_eval.json
git check-ignore -v .env data/golden_eval.json    # cả 2 phải bị ignore
git log --oneline -3
```

Untracked hiện tại (`main.py`, `pyproject.toml`, `uv.lock`, `.python-version`) — commit chung vào một commit "local dev setup" hoặc bỏ; không ảnh hưởng chấm. `Dockerfile` (python 3.12→3.13, thêm `--default-timeout`) và `README.md` (reformat bảng) đã sửa: giữ được, nhưng ghi 1 dòng lý do trong commit message để không bị hiểu là sửa starter kit tuỳ tiện.

**Lệnh tự kiểm trước khi nộp (chạy tuần tự, phải xanh hết):**

```bash
docker compose run --rm app pytest -q
docker compose run --rm app python -m src.evaluate --impl no_memory
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
docker compose run --rm app python -m src.compare_reports
# (đã có screenshot privacy + đã seed lại)
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
```

---

## 14. Checklist tổng hợp

**Tiên quyết**

- [ ] `ZEP_API_KEY` điền vào `.env`
- [ ] `python -m src.smoke` → 4 × `[OK]`
- [ ] `python -m src.seed` → `Seed complete.`
- [ ] `pytest -q` xanh

**Code (47đ)**

- [ ] TODO 1 `retrieve_long_term`: prime → `get_user_context` → `.context` + edges(limit≥20) + `cap_query`
- [ ] TODO 2 `retrieve_episodic`: `user_id`, `scope="episodes"`, `limit≥10`, `episode_char_cap=180`
- [ ] TODO 3 `retrieve_semantic`: `graph_id`, `scope="episodes"`, fallback `nodes`, không cap
- [ ] TODO 4 `assemble_context`: `self.budget.assemble(layers)`
- [ ] Không còn `NotImplementedError` trong `memory_student.py`

**Benchmark (56đ auto)**

- [ ] `reports/benchmark.json` ≥ 9/11 PASS (mục tiêu 11/11)
- [ ] `reports/benchmark_no_memory.md`
- [ ] `reports/comparison.md`

**Thủ công (24đ)**

- [ ] Privacy: forget + verify-only + screenshot + **seed lại**
- [ ] `README_submission.md` ≤ 400 từ, đủ 3 câu thực hành + 4 câu phân tích
- [ ] 4 screenshot trong `submission/`
- [ ] Không commit secret / golden

**Cộng (+20)**

- [ ] Golden 20/20 → `reports/golden_benchmark.json` với `perfect: true`
- [ ] `retrieve_for_case` trong `demo_ui.py` chạy được + screenshot/video 30s
