import re
from typing import Any 
from adhoc.core.exceptions import MetaDataError
from adhoc.metadata.schema import DatabaseMetadata, TableMetadata

class MetadataCatalog:
    """
    Descr: In-memory catalog for discovered database metadata
           Metadata is indexed by connection name
    """

    def __init__(self) -> None:
        self._databases: dict[str, DatabaseMetadata] = {}

    def register(self, connection_name: str, metadata: DatabaseMetadata) -> None:
        if not connection_name.strip():
            raise MetaDataError("Connection name cannot be empty.")

        self._databases[connection_name] = metadata 

    def get(self, connection_name:str) -> DatabaseMetadata:
        metadata = self._databases.get(connection_name)

        if metadata is None:
            raise MetaDataError(
                f"No metadata found for connection: {connection_name}"
            )

        return metadata

    def remove(self, connection_name: str) -> bool:
        return self._databases.pop(connection_name, None) is not None

    def list_connections(self) -> list[str]:
        return list(self._databases.keys())

    def list_tables(self, connection_name: str) -> list[TableMetadata]:
        metadata = self.get(connection_name)

        return [table for schema in metadata.schemas for table in schema.tables]

    def search_tables(self, connection_name: str, query: str, limit: int = 10) -> list[TableMetadata]:
        """
        Find tables using basic keyword matching.
        Note: This is an initial retrieval strategy, not semantic search
        """
        if limit < 1:
            return []

        tables = self.list_tables(connection_name)
        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        scored_tables: list[tuple[int, TableMetadata]] = []

        for table in tables:
            searchable_text = " ".join(
                [
                    table.name, 
                    table.schema_name,
                    *(column.name for column in table.columns),
                ]
            )

            table_tokens = self._tokenize(searchable_text)

            score = len(query_tokens.intersection(table_tokens))

            if score > 0:
                scored_tables.append((score, table))

        scored_tables.sort(
            key=lambda item: (-item[0], item[1].name)
        )

        return [table for _, table in scored_tables[:limit]]


    def get_prompt_context(self, connection_name: str, table_names: list[str] | None = None) -> str:
        """
        Produce a compact schema representation for an LLM prompt
        """
        metadata = self.get(connection_name)
        selected_names = (
            {name.lower() for name in table_names}
            if table_names is not None 
            else None
        )

        selected_tables = [
            table 
            for schema in metadata.schemas 
            for table in schema.tables 
            if selected_names is None 
            or table.name.lower() in selected_names
        ]

        if not selected_tables:
            raise MetaDataError(
                "No matching tables found for prompt context"
            )

        lines = [
            f"Database dialect: {metadata.dialect}",
            "",
            "Available tables:"
        ]

        for table in selected_tables:
            full_name = f"{table.schema_name}.{table.name}"

            lines.append(f"\nTable: {full_name}")
            lines.append("Columns:")

            for column in table.columns:
                details = [
                    column.data_type,
                    "NULL" if column.nullable else "NOT NULL",
                ]

                if column.primary_key:
                    details.append("PRIMARY KEY")

                lines.append(
                    f"  - {column.name}: {', '.join(details)}"
                )

            if table.primary_key:
                lines.append(
                    f"Primary key: {', '.join(table.primary_key)}"
                )

            for fk in table.foreign_keys:
                target_schema = (
                    f"{fk.referred_schema}."
                    if fk.referred_schema
                    else ""
                )

                source_columns = ", ".join(fk.columns)
                target_columns = ", ".join(fk.referred_columns)

                lines.append(
                    f"Foreign key: {source_columns} -> "
                    f"{target_schema}{fk.referred_table}"
                    f"({target_columns})"
                )

        return "\n".join(lines)


    @staticmethod
    def _tokenize(value: str) -> set[str]:
        tokens = re.findall(r"[a-z0-9]+", value.lower())

        # Basic singular/plural normalization
        return {
            token[:-1] if len(token) > 3 and token.endswith("s") else token
            for token in tokens
        }