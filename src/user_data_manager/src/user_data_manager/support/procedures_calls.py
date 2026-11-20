from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from sqlalchemy import text

from support.cloud import AzureSQLManager


def _normalize_table_name(table_name: str) -> str:
    if not isinstance(table_name, str):
        raise TypeError("table_name must be a string")

    table_name = table_name.strip()
    if not table_name:
        raise ValueError("table_name cannot be empty")

    table_name = table_name.replace("[", "").replace("]", "")
    return table_name


def _sql_identifier(column_name: str) -> str:
    column_name = str(column_name).strip()
    if not column_name:
        raise ValueError("column names cannot be empty")
    return "[" + column_name.replace("]", "]]") + "]"


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return "'" + value.isoformat() + "'"
    return "'" + str(value).replace("'", "''") + "'"


def _column_assignments(data: Mapping[str, Any], exclude: set[str] | None = None) -> str:
    exclude = exclude or set()
    assignments = []
    for column_name, value in data.items():
        if column_name in exclude:
            continue
        assignments.append(f"{_sql_identifier(column_name)} = {_sql_literal(value)}")
    if not assignments:
        raise ValueError("No valid columns available after exclusions")
    return ", ".join(assignments)


def insert_row_generic(table_name: str, row_data: Mapping[str, Any]) -> None:
    """Insert a full row into a table using a generic procedure."""
    if not row_data:
        raise ValueError("row_data cannot be empty")

    table_name = _normalize_table_name(table_name)
    columns = ", ".join(_sql_identifier(name) for name in row_data.keys())
    values = ", ".join(_sql_literal(value) for value in row_data.values())

    statement = text(
        """
        EXEC dbo.sp_insert_row_generic
            @table_name = :table_name,
            @column_list = :column_list,
            @value_list = :value_list
        """
    )
    try:
        with AzureSQLManager().engine.begin() as connection:
            connection.execute(
                statement,
                {
                    "table_name": table_name,
                    "column_list": columns,
                    "value_list": values,
                },
            )
    except Exception as e:
        raise RuntimeError(f"Failed to insert row for table '{table_name}': {e}") from e


def update_row_generic(table_name: str, row_data: Mapping[str, Any]) -> None:
    """Update a row in a table and save the previous state into the related history table."""
    if not row_data:
        raise ValueError("row_data cannot be empty")

    table_name = _normalize_table_name(table_name)

    if "code" not in row_data:
        raise ValueError("The row_data dictionary must include the code column used to identify the row")

    update_data = {key: value for key, value in row_data.items() if key not in {"id", "createdDate", "code"}}
    if not update_data:
        raise ValueError("No editable columns remain after excluding id, createdDate and code")

    update_assignments = _column_assignments(update_data)
    statement = text(
        """
        EXEC dbo.sp_update_row_generic
            @table_name = :table_name,
            @code = :code,
            @update_assignments = :update_assignments
        """
    )
    try:
        with AzureSQLManager().engine.begin() as connection:
            connection.execute(
                statement,
                {
                    "table_name": table_name,
                    "code": row_data["code"],
                    "update_assignments": update_assignments,
                },
            )
    except Exception as e:
        raise RuntimeError(f"Failed to update row for table '{table_name}' and code '{row_data['code']}': {e}") from e


def restore_previous_row_generic(table_name: str, code: Any) -> None:
    """Restore the last known version from the history table to the main table."""
    table_name = _normalize_table_name(table_name)
    statement = text(
        """
        EXEC dbo.sp_restore_previous_row_generic
            @table_name = :table_name,
            @code = :code
        """
    )
    try:
        with AzureSQLManager().engine.begin() as connection:
            connection.execute(statement, {"table_name": table_name, "code": code})

    except Exception as e:
        raise RuntimeError(f"Failed to restore previous row for table '{table_name}' and code '{code}': {e}") from e


__all__ = [
    "insert_row_generic",
    "update_row_generic",
    "restore_previous_row_generic",
]
