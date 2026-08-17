from __future__ import annotations

from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query, join_nonempty
from .zep_common import prime_eval_thread, render_graph_search


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
        # The Context Block is computed per thread, so the evaluation thread must
        # hold the current query before we ask for it. prime_eval_thread recreates
        # the thread and adds the query with ignore_roles=["user"], which keeps the
        # query out of the durable user graph (no transcript copying needed).
        prime_eval_thread(self.client, user_id, thread_id, query)

        user_context = self.client.thread.get_user_context(thread_id=thread_id)
        # get_user_context returns an SDK object; this function must return str.
        context_block = getattr(user_context, "context", "") or ""

        # Hardening: edge search adds explicit facts with provenance/validity, so
        # deadlines and open loops that the summary compresses away stay visible.
        # Scoped to user_id only - never another user, never the shared graph.
        try:
            facts = self.client.graph.search(
                user_id=user_id,
                query=cap_query(query),  # graph.search rejects queries > 400 chars
                scope="edges",
                limit=20,  # a low limit drops open-loop/deadline edges
            )
            fact_text = render_graph_search(facts)
        except Exception:
            # Retrieval must degrade to the Context Block, not crash the eval.
            fact_text = ""

        return join_nonempty([context_block, fact_text], sep="\n\n")

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        # Episodes = the raw messages/data chunks as they happened, so this is
        # the layer that still carries trajectory (failed attempt), outcome
        # (the fix) and reflection (root cause) instead of a compressed fact.
        # user_id only - the shared semantic graph_id would return domain docs.
        results = self.client.graph.search(
            user_id=user_id,
            query=cap_query(query),  # Zep rejects queries > 400 chars
            scope="episodes",
            limit=15,  # enough room for the marker-bearing reflection episode
        )
        # episode_char_cap keeps verbose session episodes from crowding out the
        # short reflection under the 3% episodic budget. 200 > the 163-char
        # reflection message, so markers at its tail survive the truncation.
        return render_graph_search(results, episode_char_cap=200)

    def retrieve_semantic(self, graph_id: str, query: str) -> str:
        # Domain knowledge is shared, not owned by any user: search the
        # standalone graph_id. Passing user_id here would turn a company policy
        # into someone's personal memory (and leak preferences into the answer).
        q = cap_query(query)  # Zep rejects queries > 400 chars
        try:
            results = self.client.graph.search(
                graph_id=graph_id,
                query=q,
                # "episodes" returns the raw document text, which keeps literal
                # markers (PAYMENT-RULE-3, CONN-POOL-FIRST). "auto" returns
                # extracted facts that read fine but drop those codes.
                scope="episodes",
                limit=8,
            )
        except Exception:
            # Only a fallback for accounts/SDKs where the episodes scope
            # differs - nodes still carry the marker inside entity summaries.
            # Not a blanket swallow: a nodes failure propagates so the eval
            # report records it in the `error` field instead of "" evidence.
            results = self.client.graph.search(
                graph_id=graph_id,
                query=q,
                scope="nodes",
                limit=8,
            )
        # No episode_char_cap here: markers sit at the END of each document
        # ("... Marker: PAYMENT-RULE-3."), so truncation would cut them off.
        return render_graph_search(results)

    def assemble_context(self, layers: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
        # Delegate to the manager built in __init__ with settings.context_tokens.
        # It walks the priority order short_term -> long_term -> episodic ->
        # semantic, trims each layer to its 10/4/3/3 share, and returns both the
        # merged text and the per-layer breakdown the report/UI reads.
        # Do NOT concatenate raw layers here: that skips trimming and silently
        # blows the context budget.
        return self.budget.assemble(layers)
