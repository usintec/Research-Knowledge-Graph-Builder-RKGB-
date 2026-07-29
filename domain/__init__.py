"""Domain layer — the core business model of RKGB.

This layer has zero dependencies on outer layers (application,
infrastructure, presentation). All repository interfaces are defined
here as abstract contracts; concrete implementations live in
``infrastructure/repositories/``.
"""
