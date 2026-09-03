"""DB adapter helpers — migration runner shared by all schema-owning modules.

Ownership note (AD-11): each Postgres schema is owned by one module adapter
(``config`` -> ``src.adapters.config_store``, ``audit`` -> ``src.adapters.audit``);
this package owns only the cross-cutting ``schema_migrations`` bookkeeping and
the ordered runner that applies ``migrations/*.sql``.
"""
