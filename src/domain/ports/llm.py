"""LLM port: the single port for all LLM roles.

Governing decisions: AD-1, AD-2 (all externals behind ports), AD-5.
Owning module: ``llm`` — adapter home is ``src/adapters/llm/`` (implementation
lands with Epic 6).

One port covers all three LLM roles — narrator, structured-output classifier,
and bounded dialogue partner — so the provider can be swapped behind the port
without touching callers. The port never returns figures it wasn't handed:
all numbers come from the deterministic engine (AD-1); the LLM only narrates.

# TODO (Epic 6): narration / classification / dialogue method signatures evolve
# with their implementing stories — deliberately not invented here.
"""

from typing import Protocol


class LlmPort(Protocol):
    """Single abstraction over all LLM calls (AD-1, AD-2, AD-5).

    Roles: narrator / structured-output classifier / bounded dialogue partner.
    """
