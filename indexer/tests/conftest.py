"""
Pytest configuration for the indexer test suite.

Tests that load the SentenceTransformer model and build a full ChromaDB index
are marked as integration tests. They are skipped by default unless the
``INDEXER_INTEGRATION_TESTS`` environment variable is set to ``1``.

To run integration tests locally::

    INDEXER_INTEGRATION_TESTS=1 pytest indexer/tests/
"""

import os
import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require the embedding model and full index "
        "(skipped unless INDEXER_INTEGRATION_TESTS=1)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.environ.get("INDEXER_INTEGRATION_TESTS") == "1":
        return
    skip_integration = pytest.mark.skip(
        reason="Set INDEXER_INTEGRATION_TESTS=1 to run integration tests"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
