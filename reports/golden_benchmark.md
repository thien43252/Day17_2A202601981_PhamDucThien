# Lab 17 Golden Set Report

- Implementation: `student`
- Kind: `golden`
- Cases: **20**
- Passed: **20/20**
- Evidence hit rate: **100.0%**
- Average retrieval latency: **892.3 ms**
- Average token reduction vs full source context: **6.3%**
- Golden bonus: **10/10** (100% required)

| Case | Layer | Pass | Latency ms | Retrieved tokens | Token reduction | Missing / Error |
| --- | --- | --- | ---: | ---: | ---: | --- |
| G01 | short_term | PASS | 0.2 | 227 | 0.0% |  |
| G02 | short_term | PASS | 0.0 | 133 | 0.0% |  |
| G08 | long_term | PASS | 1356.2 | 784 | 0.0% |  |
| G09 | long_term | PASS | 1251.5 | 1466 | 0.0% |  |
| G12 | semantic | PASS | 220.8 | 418 | 8.9% |  |
| G14 | semantic | PASS | 212.8 | 270 | 30.2% |  |
| G15 | semantic | PASS | 238.5 | 270 | 41.2% |  |
| G19 | mixed | PASS | 1386.5 | 581 | 0.0% |  |
| G03 | long_term | PASS | 1504.0 | 1478 | 0.0% |  |
| G04 | long_term | PASS | 1452.0 | 1459 | 0.0% |  |
| G05 | long_term | PASS | 1414.6 | 1440 | 0.0% |  |
| G10 | episodic | PASS | 237.4 | 487 | 0.0% |  |
| G11 | episodic | PASS | 213.8 | 491 | 0.0% |  |
| G13 | semantic | PASS | 218.9 | 416 | 26.4% |  |
| G16 | mixed | PASS | 1694.0 | 581 | 0.0% |  |
| G18 | mixed | PASS | 529.8 | 500 | 11.5% |  |
| G20 | mixed | PASS | 1939.1 | 831 | 0.0% |  |
| G06 | long_term | PASS | 1283.4 | 1458 | 0.0% |  |
| G07 | long_term | PASS | 1216.7 | 1473 | 0.0% |  |
| G17 | mixed | PASS | 1475.4 | 581 | 8.1% |  |

## Evidence excerpts

### G01 - short_term

`<SESSION_SUMMARY> user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. | assistant: Noted standup constraint. | user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. | assistant: Noted staging constraint. | user: Filler A about button padding. | assistant: Filler A. | user: Filler B about color tokens. | assistant: Filler B. | user: Filler C about copy tone. | assistant: Filler C. </SESSION_SUMMARY> <DURABLE_NOTES> - user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. - assistant: Noted standup constraint. - user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. - assistant: Noted staging constraint. </DURA`

### G02 - short_term

`<RECENT_TURNS> user: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. assistant: Da hieu: demo ca nhan ORCHID-27, uu tien Python, tranh Java, vi du ngan. user: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. assistant: Toi se uu tien timeline khi giai thich coroutine va Task. user: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. </RECENT_TURNS>`

### G08 - long_term

`<USER_SUMMARY> Lan's project is LOTUS-88. They prioritize Java and Spring Boot for backend examples and do not use Python in the backend. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-01 11:00:00     Source: message     Content: [user] {   "user_id": "lan-lab17",   "first_name": "Lan",   "last_name": "Tran",   "user_alias": "Lan Tran" }: Toi la Lan. Du an cua toi la LOTUS-88. Toi uu tien Java va Spring Boot, va khong dung Python trong vi du backend.   - Created At: 2026-08-01 11:00:20     Source: message     Content: Lab Assistant (assistant): Da hieu: LOTUS-88, Java + Spring Boot cho backend examples. </EPISODE`

### G09 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G12 - semantic

`EPISODE: {"id":"kb-payment-retry","entity":"Payment API Retry Policy","summary":"For POST /payments, every retryable request MUST send the same Idempotency-Key. Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after max-3-retries. Marker: PAYMENT-RULE-3.","source":"internal-api-guideline-v3","updated_at":"2026-08-10T00:00:00Z"} metadata= EPISODE: For POST /payments, every retryable request MUST send the same Idempotency-Key. Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after max-3-retries. Marker: PAYMENT-RULE-3. metadata= EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, epis`

### G14 - semantic

`EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodic 3 percent, semantic 3 percent; trim lower-priority memory first. Marker: BUDGET-10-4-3-3. metadata= EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL.","source":"memory-governance-policy","updated_at":"2026-08-12T00:00:00Z"} metadata= EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marke`

### G15 - semantic

`EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodic 3 percent, semantic 3 percent; trim lower-priority memory first. Marker: BUDGET-10-4-3-3. metadata= EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL.","source":"memory-governance-policy","updated_at":"2026-08-12T00:00:00Z"} metadata= EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marke`

### G19 - mixed

`<LONG_TERM> <USER_SUMMARY> Lan's project is LOTUS-88. They prioritize Java and Spring Boot for backend examples and do not use Python in the backend. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 05:10:42     Source: message     Content: [user] {   "user_id": "lan-lab17",   "first_name": "Lan",   "last_name": "Tran",   "user_alias": "Evaluation User" }: Lan uu tien stack backend nao cho LOTUS-88?   - Created At: 2026-08-01 11:00:20     Source: message     Content: Lab Assistant (assistant): Da hieu: LOTUS-88, Java + Spring Boot cho backend examples.   - Created At: 2026-08-01 11:00:00     Source: message     `

### G03 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G04 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G05 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G10 - episodic

`EPISODE: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. EPISODE: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. EPISODE: Toi se uu tien timeline khi giai thich coroutine va Task. EPISODE: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Hay kiem tra connection pool, lifecycle cua client va concurrency. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la connection ch`

### G11 - episodic

`EPISODE: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. EPISODE: Da hieu: demo ca nhan ORCHID-27, uu tien Python, tranh Java, vi du ngan. EPISODE: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. EPISODE: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Hay kiem tra connection pool, lifecycle cua client va concurrency. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh l`

### G13 - semantic

`EPISODE: {"id":"kb-async-http","entity":"Async HTTP Incident Playbook","summary":"When async HTTP calls time out, inspect connection pooling, downstream saturation and concurrency before increasing timeout. Reuse a long-lived client session where possible. Marker: CONN-POOL-FIRST.","source":"incident-playbook-2026","updated_at":"2026-08-11T00:00:00Z"} metadata= EPISODE: When async HTTP calls time out, inspect connection pooling, downstream saturation and concurrency before increasing timeout. Reuse a long-lived client session where possible. Marker: CONN-POOL-FIRST. metadata= EPISODE: Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodic 3 per`

### G16 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often`

### G18 - mixed

`<EPISODIC> EPISODE: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. EPISODE: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. EPISODE: Toi se uu tien timeline khi giai thich coroutine va Task. EPISODE: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Hay kiem tra connection pool, lifecycle cua client va concurrency. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la co`

### G20 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often`

### G06 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G07 - long_term

`<USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often confuses co`

### G17 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh is working on a benchmark report for an open loop LAB-REPORT-1600, due Friday at 4:00 PM. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used for this project's backend. Minh uses Python for personal demos, such as ORCHID-27. Minh is debugging async HTTP and found that reusing the aiohttp ClientSession and setting concurrency to 20 is an effective solution for connection churn, rather than increasing the timeout, which is related to the ASYNC-FIX-20 incident.  Minh prefers Python and dislikes Java. When explaining code, Minh prefers short examples. Minh is currently learning about async/await and often`
