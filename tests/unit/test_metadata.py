import pytest
from adhoc.core.exceptions import MetadataError
from adhoc.metadata import (
    DatabaseMetadata,
    MetadataCatalog,
    MetadataDiscovery,
)


SAMPLE_SCHEMA = {
    "dialect": "postgresql",
    "schemas": [
        {
            "name": "public",
            "tables": [
                {
                    "name": "customers",
                    "primary_key": ["customer_id"],
                    "columns": [
                        {
                            "name": "customer_id",
                            "type": "INTEGER",
                            "nullable": False,
                            "primary_key": True,
                        },
                        {
                            "name": "name",
                            "type": "VARCHAR",
                            "nullable": True,
                        },
                    ],
                    "foreign_keys": [],
                },
                {
                    "name": "orders",
                    "primary_key": ["order_id"],
                    "columns": [
                        {
                            "name": "order_id",
                            "type": "INTEGER",
                            "nullable": False,
                            "primary_key": True,
                        },
                        {
                            "name": "customer_id",
                            "type": "INTEGER",
                            "nullable": False,
                        },
                    ],
                    "foreign_keys": [
                        {
                            "constrained_columns": ["customer_id"],
                            "referred_schema": "public",
                            "referred_table": "customers",
                            "referred_columns": ["customer_id"],
                        }
                    ],
                },
            ],
        }
    ],
}


class FakeConnector:
    def get_schema(self):
        return SAMPLE_SCHEMA


def test_metadata_discovery():
    discovery = MetadataDiscovery()

    metadata = discovery.discover(FakeConnector())

    assert isinstance(metadata, DatabaseMetadata)
    assert metadata.dialect == "postgresql"
    assert len(metadata.schemas) == 1
    assert len(metadata.schemas[0].tables) == 2


def test_metadata_models_normalize_foreign_keys():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)

    orders = metadata.schemas[0].tables[1]

    assert orders.foreign_keys[0].referred_table == "customers"
    assert orders.foreign_keys[0].columns == ["customer_id"]


def test_catalog_register_and_get():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)
    catalog = MetadataCatalog()

    catalog.register("test_db", metadata)

    retrieved = catalog.get("test_db")

    assert retrieved.dialect == "postgresql"


def test_catalog_list_tables():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)
    catalog = MetadataCatalog()

    catalog.register("test_db", metadata)

    tables = catalog.list_tables("test_db")

    assert len(tables) == 2
    assert {table.name for table in tables} == {
        "customers",
        "orders",
    }


def test_catalog_search_tables():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)
    catalog = MetadataCatalog()

    catalog.register("test_db", metadata)

    results = catalog.search_tables(
        "test_db",
        "customer",
    )

    assert any(table.name == "customers" for table in results)


def test_catalog_prompt_context():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)
    catalog = MetadataCatalog()

    catalog.register("test_db", metadata)

    context = catalog.get_prompt_context(
        "test_db",
        ["customers", "orders"],
    )

    assert "customers" in context
    assert "orders" in context
    assert "customer_id" in context
    assert "Foreign key" in context


def test_catalog_missing_connection():
    catalog = MetadataCatalog()

    with pytest.raises(MetadataError):
        catalog.get("unknown_database")


def test_catalog_remove():
    metadata = DatabaseMetadata.from_dict(SAMPLE_SCHEMA)
    catalog = MetadataCatalog()

    catalog.register("test_db", metadata)

    assert catalog.remove("test_db") is True
    assert catalog.remove("test_db") is False
