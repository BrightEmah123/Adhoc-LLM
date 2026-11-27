from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass
class ColumnMetadata:
    name: str
    data_type: str 
    nullable: bool = True 
    default: Any = None 
    primary_key: bool = False 

    @classmethod 
    def from_dict(cls, data: dict[str, Any]) -> "ColumnMetadata":
        return cls(
            name=data["name"],
            data_type=str(data.get("data_type", data.get("type", "UNKNOWN"))),
            nullable=data.get("nullable", True),
            default=data.get("default"),
            primary_key=data.get("primary_key", False),
        )


@dataclass 
class ForeignKeyMetadata:
    columns: list[str]
    referred_schema: str | None
    referred_table: str 
    referred_columns: list[str]

    @classmethod 
    def from_dict(cls, data:dict[str, Any]) -> "ForeignKeyMetadata":
        return cls(
            columns=data.get("constrained_columns", data.get("columns", [])),
            referred_schema=data.get("referred_schema"),
            referred_table=data["referred_table"],
            referred_columns=data.get("referred_columns", []),
        )


@dataclass
class TableMetadata:
    name: str 
    schema_name: str 
    columnns: list[ColumnMetadata] = field(default_factory=list)
    primary_keys: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKeyMetadata] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], schema_name: str) -> "TableMetadata":
        return cls(
            name=data["name"],
            schema_name=schema_name,
            columns=[
                ColumnMetadata.from_dict(column)
                for column in data.get("columns", [])
            ],
            primary_key=data.get("primary_key", []),
            foreign_keys=[
                ForeignKeyMetadata.from_dict(fk)
                for fk in data.get("foreign_keys", [])
            ],
        )


@dataclass
class SchemaMetadata:
    name: str 
    tables: list[TableMetadata] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data:dict[str, Any]) -> "SchemaMetadata":
        name = data["name"]

        return cls(
            name=name,
            tables=[
                TableMetadata.from_dict(table, schema_name=name)
                for table in data.get("tables", [])
            ],
        )

@dataclass
class DatabaseMetadata:
    dialect: str 
    schemas: list[SchemaMetadata] = field(default_factory=list)
    discovered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DatabaseMetadata":
        discovered_at = data.get("discovered_at")

        return cls(
            dialect=data["dialect"],
            schemas=[
                SchemaMetadata.from_dict(schema)
                for schema in data.get("schemas", [])
            ],
            discovered_at=(
                datetime.fromisoformat(discovered_at)
                if discovered_at
                else datetime.now(timezone.utc)
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dialect": self.dialect,
            "discovered_at": self.discovered_at.isoformat(),
            "schemas": [
                {
                    "name": schema.name,
                    "tables": [
                        {
                            "name": table.name, 
                            "schema_name": table.schema_name,
                            "primary_key": table.primary_key,
                            "columns": [
                                {
                                    "name": column.name,
                                    "data_type": column.data_type,
                                    "nullable": column.nullable,
                                    "default": column.default,
                                    "primary_key": column.primary_key
                                }
                                for column in table.columns
                            ],
                            "foreign_keys": [
                                {
                                    "columns": fk.columns,
                                    "referred_schema": fk.referred_schema,
                                    "referred_table": fk.referred_table,
                                    "referred_columns": fk.referred_columns,
                                }
                                for fk in table.foreign_keys
                            ],
                        }
                        for table in schema.tables
                    ],
                }
                for schema in self.schemas
            ],
        }