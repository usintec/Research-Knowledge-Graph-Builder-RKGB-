# Architecture

This document describes the high-level architecture of the Research Knowledge Graph Builder.

## Overview
- Application entry point lives in app/main.py.
- Core modules are organized under app/core.
- Domain-specific modules include ingestion, parsing, NLP, ontology, graph, query, and visualization.

## Design Goals
- Modular and extensible architecture.
- Clear separation between API, domain logic, and data layers.
- Support for future integration with external services and storage backends.
