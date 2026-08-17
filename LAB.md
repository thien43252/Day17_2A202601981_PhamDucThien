---
title: "Lab 17 - Xay dung Multi-Memory Agent voi Zep"
description: "Xay dung va danh gia agent co short-term, long-term, episodic va semantic memory; thuc hanh cross-session recall, compaction, token budget, conflict handling va privacy."
author: "VinUni Codelab"
duration: 170
category: "AI Agents"
updated: "2026-08-17"
day: "17"
sequence: 1
keywords: ["AI Agents", "Memory", "Zep", "LangGraph", "Redis", "Qdrant", "Context Engineering"]
level: "intermediate"
requiresSubmission: true
workMode: "individual"
overview:
  summary: "Hoc vien hoan thien 4 memory layer tren mot starter kit da Docker hoa, dung Zep Cloud V3 lam managed memory backend va benchmark tren bo chat JSON co ground truth."
  knowledge:
    - "Phan biet working/short-term, declarative/long-term, episodic va semantic memory."
    - "Hieu cross-session memory, Context Block, graph search va standalone knowledge graph cua Zep."
    - "Quan ly context bang sliding window, compaction va token budget."
    - "Danh gia retrieval bang ground truth thay vi chi xem chat response."
    - "Ap dung recency, provenance, user isolation va right-to-be-forgotten."
  conceptFlow:
    - "Chat JSON -> ingest theo user/thread -> Zep user graph + standalone semantic graph"
    - "Query -> memory router -> 4 memory layer -> priority/token budget -> merged context"
    - "Ground truth -> evaluator -> memory hit rate, latency, token efficiency"
  phases:
    - time: "0-15 phut"
      owner: "Hoc vien"
      title: "Khoi dong moi truong va smoke test"
      description: "Build Docker, kiem tra Redis/Qdrant, cau hinh ZEP_API_KEY."
    - time: "15-45 phut"
      owner: "Hoc vien"
      title: "Short-term + compaction"
      description: "So sanh buffer, summary, sliding window; giu recent turns + durable notes."
    - time: "45-85 phut"
      owner: "Hoc vien"
      title: "Cross-session long-term voi Zep"
      description: "Tao user/thread, ingest messages, retrieve Context Block/facts va xu ly recency."
    - time: "85-110 phut"
      owner: "Hoc vien"
      title: "Episodic + semantic + router + benchmark E01-E11"
      description: "Hoan thien TODO 2-4, chay practice set, comparison, privacy, report."
    - time: "110-170 phut"
      owner: "Hoc vien"
      title: "Golden set + demo UI (60 phut cuoi)"
      description: "Giang vien phat 20 case an. 20/20 = +10. Mini-product UI hoac report dep = +10."
  outcomes:
    - "Practice set E01-E11 dat hit rate >= 80% (9/11)."
    - "Tran diem lab = 80. Golden 20/20 them +10. UI demo them +10. Tong toi da 100."
    - "Co benchmark report so sanh memory-enabled va no-memory baseline."
    - "Giai thich duoc tai sao mot query duoc route vao tung memory layer."
  reassurance: "Starter kit da lo Docker, data, ingestion, polling va report; phan code hoc vien can dien chi nam trong mot file nho."
---
## 1. Thuat ngu can biet

| Thuat ngu goc                      | Ban chat khai niem                                                                                      | Minh hoa truc quan                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `Short-term / Working Memory`    | Vung nho nong cua conversation hien tai; nhanh nhung bi gioi han context.                               | Nho 4-6 tin nhan gan nhat de hieu "no" dang tro den dieu gi.               |
| `Long-term / Declarative Memory` | Facts, preferences, decisions ben vung qua nhieu thread/session.                                        | User da noi tu hom qua rang thich Python; hom nay agent van nho.           |
| `Episodic Memory`                | Luu trai nghiem/trajectory va outcome co provenance, phuc vu "lan truoc da lam gi".                     | Lan truoc tang timeout khong hieu qua; reuse connection pool moi fix duoc. |
| `Semantic Memory`                | Tri thuc domain/doc duoc retrieval theo y nghia, khong phu thuoc mot user cu the.                       | Quy tac retry payment API duoc tim tu knowledge graph dung chung.          |
| `Context Block`                  | Context Zep lap rap tu user graph dua tren relevance; la long-term context de dua vao agent.            | Query moi ve coding style keo ra user summary + relevant facts.            |
| `Episode`                        | Mot don vi source da ingest vao Zep; raw source duoc giu de tim kiem va trace provenance.               | Mot message, mot event JSON, mot doan document.                            |
| `Compaction`                     | Giam raw transcript bang summary + recent turns + durable notes.                                        | 30 turn cu duoc co lai thanh 3 dong state/decision/TODO.                   |
| `Token Budget`                   | Han muc context cho tung memory layer; retrieval tot nhung qua nhieu van gay nhieu.                     | Short-term 10%, long-term 4%, episodic 3%, semantic 3%.                    |
| `Recency wins`                   | Khi fact cu va moi mau thuan, thong tin moi hon duoc uu tien va fact cu giu lai cho history/provenance. | User doi backend tu Python sang TypeScript.                                |
| `User-scoped namespace`          | Memory cua moi user phai tach biet; sai user_id la data-leak bug.                                       | Minh khong duoc recall preference cua Lan.                                 |

### Kien truc cua lab

```text
                     +---------------------------+
                     |  control_plane/*.md       |
                     | persona/rules/schema/tasks|
                     +-------------+-------------+
                                   |
JSON sessions -> LangGraph router -> retrieve(query)
                                   |
        +--------------------------+---------------------------+
        |                          |                           |
 short-term                 Zep user graph              Zep standalone graph
 buffer/summary/sliding     long-term + episodes        semantic/domain KB
        |                    context/facts/episodes             |
        +--------------------------+---------------------------+
                                   |
                         priority + token budget
                                   |
                              merged context
                                   |
                         evaluator / demo agent
```

### Quan trong ve Zep nam 2026

Lab nay dung **Zep Cloud V3 SDK**. Trong V3, conversation duoc goi la `thread`; flow co ban la `user.add -> thread.create -> thread.add_messages -> thread.get_user_context`. Zep Community Edition Docker compose cu khong duoc dung lam backend chinh cua bai lab. Docker trong starter kit chi dong goi **client code + Redis + Qdrant local baseline**.

Muc dich cua Redis/Qdrant la cho hoc vien nhin thay doi chieu "managed Zep" voi "tu build Redis + vector DB", khong phai de viet lai Zep trong 170 phut.

## 2. Muc tieu & dau ra

Ban hoan thanh khi:

1. `python -m src.evaluate --impl student --reuse-seeded` tao duoc `reports/benchmark.md`.
2. Chay du **11 evaluation cases** (E01-E11), phu 4 memory layer + 1 case mixed.
3. Retrieval hit rate cua memory-enabled agent dat **>= 80%** (toi thieu **9/11** case PASS).
4. User isolation test pass: query cua `lan-lab17` khong leak fact cua `minh-lab17` va nguoc lai (E09).
5. Ban giai thich duoc 1 case conflict/recency (E08) va 1 case compaction (E10).
6. Chay privacy drill xoa user sau khi benchmark va xac nhan memory khong con duoc retrieve.

**Dieu kien dat lab:** diem nen **>= 56/80**, hit rate practice **>= 80% (9/11)**, nop du artefact, khong commit secret. Golden va UI la diem cong, khong bat buoc de pass.

**Artefact nop:** xem [muc 6](#6-nop-bai). Bang diem chi tiet: [muc 5](#5-kiem-tra-ket-qua).

### 2.1. Tong hop task hoc vien

Chi **4 ham** trong `src/memory_student.py` can viet code. Cac task con lai la chay demo, doc control plane, benchmark va viet giai thich.

| #   | Task                                                                                            | Loai                       | File / lenh                                       | Pha                     |                                                         Diem (xem muc 5) |
| --- | ----------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------------- | ----------------------- | -----------------------------------------------------------------------: |
| T1  | Smoke test: Redis, Qdrant, dataset,`ZEP_API_KEY`                                              | Bat buoc chay              | `python -m src.smoke`                           | 0-15 phut               |                        Dieu kien tien quyet (0d, fail = khong cham duoc) |
| T2  | Seed 1 lan: 2 user + semantic graph                                                             | Bat buoc chay              | `python -m src.seed`                            | 0-15 phut               |                                                               Tien quyet |
| T3  | So sanh buffer / summary / sliding; giam`max_recent_messages` 6→4; xac nhan deadline van con | Bat buoc quan sat          | `src/demo_short_term.py`, `src/short_term.py` | Pha A                   |            E01+E10 =**9d**; giai thich compaction nam trong report |
| T4  | TODO 1/4:`retrieve_long_term` bang Context Block                                              | Bat buoc code              | `src/memory_student.py`                         | Pha B                   |                                           E02+E03+E08+E09 =**20d** |
| T5  | TODO 2/4:`retrieve_episodic` `scope="episodes"`                                             | Bat buoc code              | `src/memory_student.py`                         | Pha C                   |                                                   E04+E05 =**10d** |
| T6  | TODO 3/4:`retrieve_semantic` tren `graph_id` dung chung                                     | Bat buoc code              | `src/memory_student.py`                         | Pha D                   |                                                   E06+E11 =**11d** |
| T7  | TODO 4/4:`assemble_context` budget 10/4/3/3                                                   | Bat buoc code              | `src/memory_student.py`                         | Pha E                   |                                                        E07 =**6d** |
| T8  | Baseline no-memory + student benchmark + comparison                                             | Bat buoc chay              | `src.evaluate`, `src.compare_reports`         | Pha E                   |                        4 cau phan tich +`comparison.md` = **6d** |
| T9  | Doc control plane + chay heartbeat / compiled KB / episodic maintenance                         | Quan sat (khong viet code) | `control_plane/*`, demo scripts                 | Mini-drill              |                                   **0d** (phuc vu cau hoi nop bai) |
| T10 | Privacy: forget + verify-only                                                                   | Bat buoc chay              | `src.forget`                                    | Pha cuoi (truoc golden) |                                                             **6d** |
| T11 | Viet`README_submission.md` (3 cau) + screenshot 4 case + du file report                       | Bat buoc nop               | repo                                              | Truoc phut 110          |                                3 cau**6d** + artefact **6d** |
| T12 | Golden set 20 case (phat phut 110)                                                              | Cong, all-or-nothing       | `data/golden_eval.json` gitignore               | 60 phut cuoi            |                                          **+10 neu 20/20**, else 0 |
| T13 | Mini-product UI (load case + chat tiep) hoac report dep                                         | Cong                       | `src/demo_ui.py`                                | 60 phut cuoi            | **+10 UI du checklist**; report dep khong UI toi da **6/10** |

**Khong phai task coding:** `src/memory_reference.py`, ingestion/polling, Redis/Qdrant baseline, LangGraph demo. Do la starter kit / demo giang vien.

**Luu y cham diem:** E01 va E10 chay bang `ShortTermMemory` local, **khong** di qua 4 ham student. Van tinh diem vi hoc vien phai chay du benchmark. 4 TODO quyet dinh E02-E09, E07 va E11. Tong T1-T11 = **80d**. T12 golden va T13 UI nam ngoai tran 80.

## 3. Chuan bi

### 3.1. Yeu cau may

- Docker Desktop / Docker Engine + Docker Compose v2.
- RAM rong khoang 4 GB.
- Ket noi Internet cho Zep Cloud.
- 1 `ZEP_API_KEY`.
- Khong bat buoc OpenAI API key: benchmark mac dinh danh gia **retrieved evidence**, khong dung LLM de cham.

### 3.2. Khoi dong

```bash
cp .env.example .env
# Dien ZEP_API_KEY vao .env

docker compose build
docker compose up -d redis qdrant
docker compose run --rm app python -m src.smoke
```

Ket qua mong doi:

```text
[OK] Redis reachable
[OK] Qdrant reachable
[OK] sessions.json valid: >= 10 evaluations
[OK] ZEP_API_KEY is present
```

Seed Zep **mot lan** de tiet kiem thoi gian trong lop:

```bash
docker compose run --rm app python -m src.seed
```

`src.seed` reset 2 synthetic users, ingest toan bo session JSON, seed standalone semantic graph va doi den khi cac marker chinh searchable. Cac lenh evaluate sau do dung `--reuse-seeded` de khong ingest lai.

### 3.3. Hieu data truoc khi code

Mo `data/sessions.json`. Moi evaluation co cac truong. `data/consent.json` la consent registry cho cac synthetic lab user; ingestion se fail neu `memory_opt_in` khong bat.

Moi evaluation co cac truong:

```json
{
  "id": "E04",
  "expected_layer": "episodic",
  "query": "Lan truoc ta fix async HTTP timeout bang cach nao?",
  "must_contain_all": ["ClientSession", "concurrency=20"]
}
```

`must_contain_all` la ground truth evidence. Evaluator cham **retrieval text**, vi neu retrieval sai thi LLM van co the "noi nghe hop ly" va che lap bug memory.

## 4. Thuc hanh

### 4.1. Pha A - Short-term memory: buffer, summary, sliding window (30 phut)

Chay:

```bash
docker compose run --rm app python -m src.demo_short_term
```

Quan sat 3 strategy:

- **Buffer:** giu tat ca, token tang tuyen tinh.
- **Summary:** nen old turns thanh summary.
- **Sliding:** `system/state summary + last K turns`, la default cua lab.

Mo `src/short_term.py` va tim `detect_pressure`, `compact`, `extract_durable_notes`, `render`.

Viec can lam:

1. Chay demo mac dinh (`max_recent_messages=6` trong `src/demo_short_term.py`).
2. Sua tam constructor xuong `max_recent_messages=4`, chay lai. Sliding van phai giu `REVIEW-DEADLINE-1600` nho durable note, du raw turn da bi evict.
3. **Khong** can sua `src/evaluate.py`. E10 dung `fixture_messages` + compaction rieng; unit test `tests/test_short_term.py` da lock hanh vi nay.
4. Ghi 2-3 cau vao `README_submission.md`: compaction giu constraint nao, vi sao buffer khong du.

**Diem hoc thuat:** compaction khong phai "tom tat van hoa"; summary phai uu tien **state, decision, TODO, constraint**.

**Cham:** E01 (3d) + E10 (6d) tren `reports/benchmark.md`. Giai thich compaction cham o muc 5.2 (report), khong cong them o day.

### 4.2. Pha B - Long-term cross-session voi Zep (40 phut)

Mo `src/memory_student.py`, hoan thien `retrieve_long_term`.

Pseudo-code:

```python
context = client.thread.get_user_context(thread_id=thread_id)
return context.context
```

Ingestion da duoc starter kit lo:

```text
user.add
  -> thread.create
  -> thread.add_messages
  -> poll den khi graph co du lieu
```

Chay rieng nhom long-term:

```bash
docker compose run --rm app python -m src.evaluate \
  --impl student --reuse-seeded --only-layer long_term
```

Kiem tra cac case:

- preference qua thread moi,
- open loop/TODO,
- user isolation,
- **recency/conflict:** sau session cap nhat, TypeScript phai la preference hien tai cho project moi.

> Khong copy full transcript sang thread moi. Query chi duoc nhan recent turns + long-term context co relevance.

Checklist Pha B:

- [ ] `retrieve_long_term` goi `prime_eval_thread` (da co) roi `thread.get_user_context`.
- [ ] Return `context.context` (string), khong return object.
- [ ] E02 Python preference, E03 open loop `benchmark report` + `16:00` PASS.
- [ ] E08 recency: `BLUEBIRD-42` + `TypeScript` + `NestJS`.
- [ ] E09 isolation: Lan co `LOTUS-88` / `Java` / `Spring Boot`, **khong** co `ORCHID-27`.

**Cham:** E02 5d + E03 5d + E08 5d + E09 5d = 20d. Bonus long-term edges search khong cong diem nen (da chuyen sang golden/UI).

### 4.3. Pha C - Episodic memory (20 phut)

Hoan thien `retrieve_episodic` bang user graph search.

Goi y:

```python
results = client.graph.search(
    user_id=user_id,
    query=query,
    scope="episodes",
    limit=5,
)
```

Render `episode.content` + metadata/provenance neu co.

Chay:

```bash
docker compose run --rm app python -m src.evaluate \
  --impl student --reuse-seeded --only-layer episodic
```

Case bat buoc phai recall trajectory:

```text
tried: increase timeout -> failed
worked: reuse aiohttp ClientSession + concurrency=20
reflection: connection churn, khong phai timeout threshold, moi la van de
```

Checklist Pha C:

- [ ] Search bang `user_id`, **khong** bang `graph_id` semantic.
- [ ] `scope="episodes"`, `limit=5`, render bang `render_graph_search`.
- [ ] E04: `ClientSession`, `concurrency=20`, `ASYNC-FIX-20`.
- [ ] E05: `connection churn`, `timeout threshold`.

**Cham:** E04 6d + E05 4d = 10d.

### 4.4. Pha D - Semantic memory voi standalone graph (20 phut)

`data/knowledge.jsonl` la domain KB dung chung, khong thuoc rieng user nao.

Hoan thien `retrieve_semantic`:

```python
results = client.graph.search(
    graph_id=semantic_graph_id,
    query=query,
    scope="episodes",
    limit=8,
)
```

Dung `scope="episodes"` de giu marker literal (`PAYMENT-RULE-3`, `CONN-POOL-FIRST`). `scope="auto"` thuong chi tra entity/fact, mat marker. Fallback: `scope="nodes"`.

Chay:

```bash
docker compose run --rm app python -m src.evaluate \
  --impl student --reuse-seeded --only-layer semantic
```

Ground truth marker (khop hoa thuong): `Idempotency-Key`, `max-3-retries`, `exponential-backoff`, `connection pooling`, `CONN-POOL-FIRST`.

Checklist Pha D:

- [ ] Search `graph_id=semantic_graph_id`, **khong** `user_id`.
- [ ] E06 payment retry PASS; E11 incident playbook PASS.
- [ ] Neu query semantic ra preference user → sai scope, 0d ca 2 case.

**Cham:** E06 6d + E11 5d = 11d.

### 4.5. Pha E - Router + token budget + merged context (30 phut)

Hoan thien `assemble_context`.

Budget mac dinh cua lab bam theo ty le trong slide:

```text
short-term 10%
long-term   4%
episodic    3%
semantic    3%
```

Priority:

```text
1. short-term
2. long-term facts/preferences
3. relevant episodes
4. semantic knowledge
```

Chay full benchmark va baseline khong co durable memory:

```bash
docker compose run --rm app python -m src.evaluate --impl no_memory
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
docker compose run --rm app python -m src.compare_reports
```

Ket qua chinh: `reports/benchmark.md`; baseline: `reports/benchmark_no_memory.md`; bang so sanh: `reports/comparison.md`.

Mo `reports/benchmark.md` va `reports/comparison.md`. Bon cau sau **bat buoc** nam trong `README_submission.md` (cham o muc report):

1. Layer nao co hit rate thap nhat?
2. Query nao retrieve nhieu token nhat?
3. Case mixed (E07) can ket hop memory nao? Evidence nao bat buoc?
4. Token reduction so voi full source context, va vi sao no-memory co the co reduction cao nhung hit rate thap?

Checklist Pha E:

- [ ] `assemble_context` goi `self.budget.assemble(layers)` (hoac tu trim dung ty le 10/4/3/3 + thu tu priority).
- [ ] Return `(merged_text, breakdown)`.
- [ ] E07 PASS: retrieved co ca `Python` va `Idempotency-Key`.
- [ ] Co `reports/benchmark.md`, `reports/benchmark_no_memory.md`, `reports/comparison.md`.

**Cham:** E07 6d; phan tich 4 cau + comparison 6d (muc 5.2).

### 4.6. Mini-drill - Identity files, heartbeat, compiled KB (10 phut, code da co san)

Mo:

- `control_plane/AGENTS.md`: workflow/boundaries.
- `control_plane/CONTEXT_LAYERS.md`: 7 context layers va policy-protected trimming.
- `control_plane/SOUL.md`: persona/default behavior.
- `control_plane/MEMORY.md`: durable notes, recall priority, conflict rule.
- `control_plane/MEMORY_SCHEMA.md`: schema/provenance rules.
- `control_plane/TASKS.md`: open loops.

Demo episodic maintenance (LRU, importance decay, consolidation -> reusable strategy):

```bash
docker compose run --rm app python -m src.episodic_maintenance
```

Chay heartbeat dry-run:

```bash
docker compose run --rm app python -m src.heartbeat --dry-run
```

Heartbeat chi duoc:

- de-duplicate local notes,
- danh dau stale task,
- tao recap an toan,
- **khong** tu them instruction/quyen moi vao durable memory.

Demo compiled KB da curated:

```bash
docker compose run --rm app python -m src.compiled_kb --reset
```

`data/compiled_kb.jsonl` chua entity/decision pages, source IDs, contradictions va freshness. Day la minh hoa "compiled knowledge" da duoc chiet xuat/curate, thay vi moi query lai bat dau tu raw transcript.

Mini-drill **khong co diem rieng**. Dung de tra loi cau trade-off Context Block vs Redis/Qdrant va cau guardrail memory poisoning. Bo qua van co the dat diem code, nhung de mat diem report.

### 4.7. Privacy drill - consent + minimization + Right to be Forgotten (15 phut)

Truoc khi xoa, mo `data/consent.json` va `src/privacy_guard.py`. Starter kit yeu cau opt-in truoc durable ingestion va redact email/phone trong message content. Day la gate don gian de hoc vien thay Privacy-by-Design, khong phai policy engine production.

Sau khi da luu benchmark:

```bash
docker compose run --rm app python -m src.forget --user-id minh-lab17
```

Script xoa:

- Zep user (va user-scoped memory lien quan),
- Redis keys cua user.

Shared semantic/compiled KB khong bi xoa vi la domain knowledge dung chung va khong chua PII cua user demo.

Sau do chay query verification:

```bash
docker compose run --rm app python -m src.forget \
  --user-id minh-lab17 --verify-only
```

Ket qua mong doi:

```text
Zep user absent: True
Redis user keys remaining: 0
```

Checklist privacy:

- [ ] Da luu `reports/benchmark.md` **truoc** khi xoa.
- [ ] Chi xoa user lab (`minh-lab17`), khong xoa semantic graph dung chung.
- [ ] Chup terminal 2 lenh forget + verify-only.
- [ ] Sau forget, **khong** seed lai truoc khi nop screenshot privacy.

**Cham:** 6d (2d delete + 4d verify). Xoa truoc khi luu report → 0d khoi auto neu khong con `benchmark.md`. **Chay privacy TRUOC phut 110.** Sau do giu graph de chay golden; dung screenshot privacy, khong forget lan hai.

### 4.8. 60 phut cuoi - Golden set + demo product

Phut **110**: giang vien phat `data/golden_eval.json` (file nay **gitignore**, khong co san trong git). Copy vao dung path roi chay:

```bash
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
```

Ket qua: `reports/golden_benchmark.json` + `reports/golden_benchmark.md`.

- **20/20 PASS** → **+10**.
- Thieu 1 case → **0**. Khong chia nho.
- Khong duoc sua JSON golden. Giang vien re-run bang file goc.

Cung luc, bonus demo product (`make ui` / `src/demo_ui.py`):

1. Load test case tu `data/sessions.json` (duoc dung dataset co san; golden neu co thi tot).
2. Chon case → hien query, layer, user, thread.
3. Chay retrieval student, hien evidence tung layer + merged context.
4. Chat tiep tren dung `user_id` / `thread_id` do (history ngan + retrieve lai).

UI du 4 muc + nhin nhu mini product → **+10**. Report HTML/PDF dep, khong co chat UI → toi da **6/10**. Hai huong khong cong chong qua 10.

Khong nop `data/golden_eval.json` len git.

## 5. Kiem tra ket qua

Diem nen tran **80**. Golden +10. UI +10. Tong toi da **100**.

Mot case chi PASS khi **moi** marker `must_contain_all` xuat hien trong retrieved text (khong phan biet hoa thuong) va **khong** marker nao trong `must_not_contain` xuat hien. FAIL = 0d cho case do.

`pytest` lock starter kit. **Khong** cham implementation student. Fail pytest vi sua file ngoai `memory_student.py` / `demo_ui.py` → tru artefact.

**Phieu cham:**

| Khoi                       |         Toi da |    Diem |
| -------------------------- | -------------: | ------: |
| Auto E01-E11 (muc 5.1)     |             56 |         |
| Privacy drill              |              6 |         |
| Phan tich + comparison     |              6 |         |
| README_submission 3 cau    |              6 |         |
| Artefact                   |              6 |         |
| **Tran nen**         |   **80** |         |
| Golden 20/20 (T12)         |     +10 hoac 0 |         |
| UI demo / report dep (T13) |            +10 |         |
| Tru diem                   |                |         |
| **Tong**             |  **100** |         |
| Practice hit rate          |       9/11 can | __ / 11 |
| Golden                     |   20/20 de +10 | __ / 20 |
| Ket luan                   | Dat / Chua dat |         |

### 5.1. Bang diem tu dong — 56d

Nguon: `reports/benchmark.json` (`--impl student`). Khong dung golden de cham khoi nay.

| Case                | Layer      | Marker bat buoc (viet tat)                                      | Cam           | TODO             |         Diem |
| ------------------- | ---------- | --------------------------------------------------------------- | ------------- | ---------------- | -----------: |
| E01                 | short_term | `ORCHID-27`                                                   | —            | T3 (local STM)   |            3 |
| E10                 | short_term | `REVIEW-DEADLINE-1600`, `Friday`, `16:00`                 | —            | T3 compaction    |            6 |
| E02                 | long_term  | `Python`                                                      | —            | TODO 1           |            5 |
| E03                 | long_term  | `benchmark report`, `16:00`                                 | —            | TODO 1           |            5 |
| E08                 | long_term  | `BLUEBIRD-42`, `TypeScript`, `NestJS`                     | —            | TODO 1 recency   |            5 |
| E09                 | long_term  | `LOTUS-88`, `Java`, `Spring Boot`                         | `ORCHID-27` | TODO 1 isolation |            5 |
| E04                 | episodic   | `ClientSession`, `concurrency=20`, `ASYNC-FIX-20`         | —            | TODO 2           |            6 |
| E05                 | episodic   | `connection churn`, `timeout threshold`                     | —            | TODO 2           |            4 |
| E06                 | semantic   | `Idempotency-Key`, `max-3-retries`, `exponential-backoff` | —            | TODO 3           |            6 |
| E11                 | semantic   | `connection pooling`, `CONN-POOL-FIRST`                     | —            | TODO 3           |            5 |
| E07                 | mixed      | `Python`, `Idempotency-Key`                                 | —            | TODO 1+3+4       |            6 |
| **Tong auto** |            | **11 case**                                               |               |                  | **56** |

Hit rate practice = PASS / 11. Muc tieu: **>= 9/11 (80%)**.

### 5.2. Bang diem thu cong — 24d

#### Privacy drill — 6d

| Tieu chi                                                                                           | Bang chung            |       Diem |
| -------------------------------------------------------------------------------------------------- | --------------------- | ---------: |
| Da chay`python -m src.forget --user-id minh-lab17` sau khi luu benchmark, **truoc** golden | Screenshot/log delete |          2 |
| `--verify-only` in `Zep user absent: True` va `Redis user keys remaining: 0`                 | Screenshot/log verify |          4 |
| Bo verify                                                                                          |                       | toi da 2/6 |
| Khong lam / khong bang chung                                                                       |                       |          0 |

Neu da forget `minh-lab17`, **seed lai** truoc golden (graph Lan + semantic van can). Uu tien: chup privacy xong `python -m src.seed` ngay, roi cho golden.

#### Phan tich benchmark — 6d

| Tieu chi                                         | Diem |
| ------------------------------------------------ | ---: |
| Co`comparison.md` hit rate memory vs no-memory |    2 |
| Cau 1: layer hit rate thap nhat, co so           |    1 |
| Cau 2: case retrieve nhieu token nhat            |    1 |
| Cau 3: E07 = long-term + semantic                |    1 |
| Cau 4: token reduction khong thay hit rate       |    1 |

#### README_submission.md — 6d

Toi da **400 tu**. Thieu file = 0d ca khoi.

| Cau hoi bat buoc                                            | Day du | Thieu                     |
| ----------------------------------------------------------- | -----: | ------------------------- |
| Layer quan trong nhat**trong bo test nay** + chi case |      2 | 1 neu khong chi case      |
| Trade-off Context Block / Zep vs Redis+Qdrant               |      2 | 1 neu chi "Zep de hon"    |
| Guardrail chong memory poisoning                            |      2 | 0 neu khong lien quan lab |

#### Artefact & quy trinh — 6d

| Tieu chi                                                                    | Diem |
| --------------------------------------------------------------------------- | ---: |
| `memory_student.py` khong con `NotImplementedError` o 4 ham             |    2 |
| `reports/benchmark.md` + `reports/benchmark.json` tu `--impl student` |    2 |
| 4 bang chung: long-term, episodic, semantic, privacy                        |    2 |

### 5.3. Diem cong: Golden + UI

#### Golden — +10 hoac 0

Nguon: `reports/golden_benchmark.json` (`--golden`). Giang vien re-run file goc.

| Ket qua                                                                             |         Diem |
| ----------------------------------------------------------------------------------- | -----------: |
| 20/20 PASS,`summary.perfect == true`                                              | **10** |
| 19/20 tro xuong, thieu file, sua JSON, chay`--impl reference` roi nop nhu student |  **0** |

Khong partial. Khong dung E01-E11 thay golden.

#### Demo product / report dep — toi da +10

| Muc                                                                     |              Diem |
| ----------------------------------------------------------------------- | ----------------: |
| Load danh sach test case (dataset co san)                               |                 2 |
| Chon case, hien query / layer / user / thread                           |                 2 |
| Run retrieval, hien evidence (merged + tot nhat la tung layer)          |                 3 |
| Chat tiep tren cung user/thread, history con                            |                 3 |
| **Tong neu du 4 muc va UI dung duoc**                             |      **10** |
| Chi report HTML/PDF/Markdown dep, co bang case + screenshot, khong chat | toi da**6** |
| Chi`src/demo_ui.py` stub chua wire retrieve                           |       **0** |

Hai huong (UI va report dep) **khong cong chong**. Lay max.

### 5.4. Tru diem va thang dat

| Loi                                                          |                         Tru |
| ------------------------------------------------------------ | --------------------------: |
| Commit`.env` / `ZEP_API_KEY` / `data/golden_eval.json` | **-25** (toi thieu 0) |
| Khong nop`reports/benchmark.md`                            |             0d khoi auto 56 |
| Copy`memory_reference.py` ma khong giai thich duoc 1 ham   |     **-30** khoi auto |
| `--impl reference` doi ten thanh student / golden          |        0d khoi do; gian lan |
| Forget roi khong seed lai, golden fail hang loat             | 0d golden (dung rule 20/20) |

**Thang:**

| Tong (sau cong golden/UI) | Practice hit rate | Ket luan                         |
| ------------------------: | ----------------- | -------------------------------- |
|                    90-100 | >= 9/11           | Xuat sac (can golden va/hoac UI) |
|                     80-89 | >= 9/11           | Dat muc tieu + co diem cong      |
|                     56-79 | >= 9/11           | Dat (pass) neu du artefact       |
|                    Bat ky | < 9/11            | Chua dat muc tieu retrieval      |
|                      < 56 | —                | Khong dat                        |

**Pass:** diem nen **>= 56/80** **va** 9/11 **va** du 3 artefact cot loi **va** khong commit secret. Golden/UI khong bat buoc de pass.

### 5.5. Cong thuc diem

```bash
docker compose run --rm app pytest -q
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
# Golden: copy file giang vien phat vao data/golden_eval.json, roi:
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
```

```text
nen = auto56 + privacy6 + phan_tich6 + readme6 + artefact6   # cap 80
tong = min(100, nen + golden0or10 + ui0to10 - tru)
```

### 5.6. Lenh test local, khong ton Zep calls

```bash
docker compose run --rm app pytest -q
```

### 5.7. Loi thuong gap

| Trieu chung                       | Nguyen nhan thuong gap           | Cach xu ly                                    | Anh huong diem                |
| --------------------------------- | -------------------------------- | --------------------------------------------- | ----------------------------- |
| Vua ingest xong search khong thay | Zep graph ingestion bat dong bo. | Cho seed/evaluator polling.                   | FAIL hang loat                |
| Query semantic ra preference user | Scope sai.                       | Semantic dung`graph_id`.                    | E06/E11/E07 + golden semantic |
| Leak 2 user                       | Sai`user_id`.                  | User-scoped moi long-term/episodic call.      | E09 + G08/G09/G19             |
| Golden file not released          | Chua den phut 110.               | Cho giang vien phat`data/golden_eval.json`. | Exit code 2, 0d golden        |
| 2/11 PASS (chi E01, E10)          | Chua implement 4 TODO.           | Dien`memory_student.py`.                    | 9/56 auto                     |

## 6. Nop bai

Nop **mot** GitHub repo (public hoac invite giang vien). Commit cuoi cung truoc deadline la ban cham.

### 6.1. Artefact cot loi (thieu 1 = khong dat)

1. `src/memory_student.py` da hoan thien 4 ham.
2. `reports/benchmark.md` **va** `reports/benchmark.json` sinh tu `--impl student`.
3. `README_submission.md` (toi da 400 tu) gom:
   - 3 cau muc 5.2 (layer quan trong / trade-off / poisoning);
   - 4 cau phan tich benchmark (layer yeu, token, E07, reduction);
   - 2-4 cau ve E08 recency va E10 compaction (khuyen khich, giup bonus/tranh diem yeu cau 1).

### 6.2. Artefact minh chung (6d)

4. `reports/comparison.md` (sau `python -m src.compare_reports`).
5. `reports/benchmark_no_memory.md` (hoac json tuong ung).
6. Thu muc `submission/` hoac anh trong `README_submission.md`:
   - `long_term.png` (E02/E03/E08 PASS),
   - `episodic.png` (E04/E05 PASS),
   - `semantic.png` (E06/E11 PASS),
   - `privacy.png` (forget + verify-only).

### 6.3. Artefact diem cong

7. `reports/golden_benchmark.json` + `reports/golden_benchmark.md` neu tranh +10 golden.
8. UI: `src/demo_ui.py` (hoac app tuong duong) + 1 screenshot/video 30s. Hoac report dep neu khong lam UI.

### 6.4. Cam

- Khong nop `.env`, khong commit `ZEP_API_KEY`.
- **Khong commit `data/golden_eval.json`.** File nam trong `.gitignore`.
- Khong nop `src/memory_reference.py` nhu bai lam.
- Khong doi ten report reference thanh student.

Lenh nop de tu kiem:

```bash
docker compose run --rm app pytest -q
docker compose run --rm app python -m src.evaluate --impl no_memory
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded
docker compose run --rm app python -m src.compare_reports
# privacy screenshot, roi seed lai neu da xoa minh-lab17
# sau phut 110:
docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden
# optional: make ui
```
