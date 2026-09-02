"""CRM port: read-only, one-way access to the external CRM.

Governing decisions: AD-2 (all externals behind ports), AD-3, AD-9, AD-12.
Owning module: ``crm_sync`` — adapter home is ``src/adapters/crm_adapter/``
(fixture CRM placeholder here; real implementation lands with Story 1.10,
sync jobs in ``src/worker/`` land with Epic 2).

The port exposes the canonical model — ``Master``, ``Client``, ``Appointment``,
``Visit``, ``CheckLine``, ``VisitComment`` — with freshness visible via
``synced_at`` and surrogate IDs assigned at ingestion. The CRM is never written
to: data flow is strictly one-way into the mirror (AD-3).

# TODO (Story 1.10 / Epic 2): entity fetch and replay method signatures evolve
# with their implementing stories — deliberately not invented here.
"""

from typing import Protocol


class CrmPort(Protocol):
    """Read-only window onto the external CRM (AD-2, AD-3, AD-9, AD-12)."""
