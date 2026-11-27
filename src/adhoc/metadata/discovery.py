from adhoc.connectors.base import DatabaseConnector
from adhoc.core.exceptions import MetaDataError
from adhoc.metadata.schema import DatabaseMetadata


class MetadataDiscovery:
    def discover(self, connector: DatabaseConnector) -> DatabaseMetadata:
        """
        Descr: Discover and normalize metadata from a database connector
        """

        try:
            raw_metadata = connector.get_schema()

            if not isinstance(raw_metadata, dict):
                raise MetaDataError("Connector returned invalid metadata.")

            if "dialect" not in raw_metadata:
                raise MetaDataError("Metadata is missing the database dialect.")

            return DatabaseMetadata.from_dict(raw_metadata)

        except MetaDataError:
            raise 

        except Exception as exc:
            raise MetaDataError(
                f"Failed to discover database metadata: {exc}"
            ) from exc
