from abc import ABC, abstractmethod
from typing import Generic, List, Set, Tuple, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from domain.ports import LoggerPort
from domain.ports.base_repository_port import SqlAlchemyRepositoryBasePort
from infrastructure.config import Config
from infrastructure.helpers.list_flattener import ListFlattener
from infrastructure.models.base_model import BaseModel

T = TypeVar("T")  # T any DTO.
K = TypeVar("K")  # Primary key type (e.g., str, int)


class SqlAlchemyRepositoryBase(SqlAlchemyRepositoryBasePort[T, K], ABC, Generic[T, K]):
    """
    Contract - Interface genérica para repositórios de leitura/escrita.
    Pode ser especializada para qualquer tipo de DTO.
    """

    def __init__(self, config: Config, logger: LoggerPort) -> None:
        """Initialize the repository infrastructure: engine, session, and schema.

        This constructor sets up the SQLite engine with threading support,
        configures the session factory for ORM transactions, and ensures
        that all declared models are created in the database.

        Args:
            config (Config): Application configuration containing the database connection string.
            logger (LoggerPort): Logger used for emitting repository lifecycle messages.
        """
        # Store configuration and logger for use throughout the repository
        self.config = config
        self.logger = logger

        # Create SQLAlchemy engine for SQLite with thread-safe settings
        self.engine = create_engine(
            config.database.connection_string,
            connect_args={"check_same_thread": False},  # allow usage from multiple threads
            future=True,
        )

        # Enable Write-Ahead Logging mode to support concurrent reads/writes
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))

        # Create a session factory for managing DB transactions
        self.Session = sessionmaker(
            bind=self.engine,
            autoflush=True,
            expire_on_commit=True,
        )

        # Automatically create all tables defined in the SQLAlchemy models
        BaseModel.metadata.create_all(self.engine)

        # self.logger.log(f"Create Instance Base Class {self.__class__.__name__}", level="info")

    @abstractmethod
    def get_model_class(self) -> Tuple:
        """Return the SQLAlchemy model class associated with the DTO.

        This method must be implemented by subclasses to specify which
        SQLAlchemy ORM model corresponds to the generic DTO type `T`.

        Returns:
            type: The SQLAlchemy ORM model class.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        # Must be implemented by subclass to define the ORM mapping
        raise NotImplementedError

    def save_all(self, items: List[T]) -> None:
        """Persist a list of DTOs in bulk.

        Args:
            items (List[T]): A list (possibly nested) of DTOs to be persisted.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Retrieve the SQLAlchemy model class associated with the DTO type
        model, pk_column = self.get_model_class()

        try:
            # Flatten nested lists into a single-level list of DTOs
            flat_items = ListFlattener.flatten(items)

            # Remove any None values from the list
            valid_items = [
                item for item in flat_items
                if item is not None
            ]

            # Merge each DTO into the current session (insert or update)
            for dto in valid_items:
                session.merge(model.from_dto(dto))

            # Commit the transaction to persist all changes
            session.commit()

            # Log the number of successfully saved items
            if len(valid_items) > 0:
                self.logger.log(
                    f"Saved {len(valid_items)} items",
                    level="info",
                )
        except Exception as e:
            # Roll back the transaction in case of error
            session.rollback()

            # Log the failure reason
            self.logger.log(
                f"Failed to save items: {e}",
                level="error",
            )

            # Re-raise the exception to propagate the error
            raise
        finally:
            # Ensure the session is always closed after execution
            session.close()

    def get_all(self) -> List[T]:
        """Retrieve all persisted DTOs from the database.

        This method loads all records from the table corresponding to the DTO's
        associated ORM model and converts them into DTO instances.

        Returns:
            List[T]: A list of DTOs retrieved from the database.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Get the SQLAlchemy model class linked to the current DTO type
        model, pk_column = self.get_model_class()

        try:
            # Query all rows from the corresponding table
            results = session.query(model).order_by(pk_column).all()

            # Convert each ORM instance into a DTO
            return [model.to_dto() for model in results]
        finally:
            # Ensure the session is closed even if an error occurs
            session.close()

    def has_item(self, identifier: K) -> bool:
        """Check if a record with the given identifier exists in the database.

        This method queries the repository by primary key (e.g., CVM code)
        to determine if a matching entry is already persisted.

        Args:
            identifier (str): The unique identifier (e.g., CVM code) to check for existence.

        Returns:
            bool: True if the record exists, False otherwise.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Get the SQLAlchemy model class linked to the current DTO type
        model, pk_column = self.get_model_class()

        try:
            # Perform a filtered query and check if any result is found
            return (
                session.query(model)
                .filter_by(cvm_code=str(identifier))
                .first()
                is not None
            )
        finally:
            # Always close the session after the query
            session.close()

    def get_by_id(self, identifier: K) -> T:
        """Retrieve a DTO by its unique identifier (e.g., CVM code).

        This method performs a lookup in the database using the primary key
        and returns the corresponding DTO. Raises an error if not found.

        Args:
            id (str): The unique identifier (e.g., CVM code) of the entity to retrieve.

        Returns:
            T: The DTO object associated with the given identifier.

        Raises:
            ValueError: If no record is found with the specified ID.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Get the SQLAlchemy model class linked to the current DTO type
        model, pk_column = self.get_model_class()

        try:
            # Query the database for the entry with the specified ID
            obj = session.query(model).filter(pk_column == str(identifier)).first()

            # Raise an error if the object is not found
            if not obj:
                raise ValueError(f"CompanyData not found: {identifier}")

            # Convert the ORM model to a DTO and return it
            return obj.to_dto()
        finally:
            # Ensure the session is closed in all cases
            session.close()

    def get_all_primary_keys(self) -> Set[K]:
        """Retrieve all unique primary keys from the database.

        This method queries the repository for all distinct identifiers
        (e.g., CVM codes) of the persisted records.

        Returns:
            Set[str]: A set containing all unique primary keys currently stored.
        """
        # Create a new SQLAlchemy session
        session = self.Session()

        # Get the SQLAlchemy model class linked to the current DTO type
        model, pk_column = self.get_model_class()

        try:
            # Execute a distinct query for the primary key column
            results = session.query(pk_column).distinct().order_by(pk_column).all()

            # Extract and collect non-null keys into a set
            return {row[0] for row in results if row[0]}

        finally:
            # Ensure session is always closed
            session.close()

    def get_existing_by_column(self, column_name: str) -> Set[K]:
        """Return the distinct values for the given column in
        tbl_raw_statements.

        e.g. repo.get_existing_by_column("nsd") -> {94790, 12345, …}
        """
        session = self.Session()

        # Retrieve the SQLAlchemy model class associated with the DTO type
        model, pk_column = self.get_model_class()

        try:
            # dynamically access the ORM attribute
            column_attr = getattr(model, column_name)
            rows = session.query(column_attr).distinct().all()
            results = {row[0] for row in rows if row[0] is not None}
            return results
        finally:
            session.close()
