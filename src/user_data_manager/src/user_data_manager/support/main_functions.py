
import logging
import json

import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from sqlalchemy import text


from support.cloud import AzureBlobStorageManager, AzureSQLManager
from support.procedures_calls import (
    insert_row_generic,
    update_row_generic,
    restore_previous_row_generic
)

####################################################################################################
# MARK: Process requests
def get_request_body(req: func.HttpRequest) -> func.HttpResponse | dict:
    
    # Extracting request body/params
    body = req.params
    if not body.get('check'):
        body = req.get_json()

    try:
        if int(body.get('check', 9999)) != 0:
            logging.error('Invalid checker argument. Call not authoriced & therefore rejected.')
            logging.warning(f"Value: {body.get('check', 9999)}")
            return func.HttpResponse(
                "\nInvalid request (2nd level).\n",
                status_code=401
            )
    except ValueError:
        logging.error('Invalid checker argument. Call not authoriced & therefore rejected.')
        logging.warning(f"Value: {body.get('check', 9999)}")
        return func.HttpResponse(
            "\nInvalid request (1st level).\n",
            status_code=401
        )

    return body


####################################################################################################
# MARK: Storage blobs

    # EXPLOTATIONS
def get_explotations_for_user(user: str) -> list:

    user_exploitations = AzureBlobStorageManager().get_blobs_list(
                                            container_name=f"user-{user}",
                                            path="exploitations")
    logging.info(len(user_exploitations))
    return user_exploitations


def get_explotation(user: str, explotation_name: str) -> dict | None:

    explotation_path = "exploitations/" + explotation_name
    logging.warning(f'Downloading "{explotation_path}"...')
    try:
        explotation = AzureBlobStorageManager().download_blob(
                                            container_name=f'user-{user}',
                                            blob_path=explotation_path
                                            )
    except ResourceNotFoundError:
        return func.HttpResponse(
            f"The selected explotation ({explotation_name}) does not exists\n",
            status_code=400
        )

    except:
        return func.HttpResponse(
            "Error during downloading process",
            status_code=400
        )

    explotation_json = json.loads(explotation.decode("utf-8"))

    return explotation_json


# MARK: Database interaction

    # GENERAL
def get_table_structure(table_name: str) -> list:
    """Retrieve the structure of a table from the database."""

    complex_query = f"""
            DECLARE @SchemaName SYSNAME = 'dbo';
            DECLARE @TableName  SYSNAME = '{table_name}';

            SELECT
                s.name AS SchemaName,
                t.name AS TableName,

                -- Identificación de columna
                c.column_id AS OrdinalPosition,
                c.name AS ColumnName,

                -- Tipo de dato
                ty.name AS DataType,
                CASE
                    WHEN ty.name IN ('varchar', 'char', 'varbinary', 'binary')
                        THEN CASE WHEN c.max_length = -1 THEN 'MAX'
                                ELSE CAST(c.max_length AS VARCHAR(10)) END
                    WHEN ty.name IN ('nvarchar', 'nchar')
                        THEN CASE WHEN c.max_length = -1 THEN 'MAX'
                                ELSE CAST(c.max_length / 2 AS VARCHAR(10)) END
                    WHEN ty.name IN ('decimal', 'numeric')
                        THEN CONCAT(c.precision, ',', c.scale)
                    WHEN ty.name IN ('datetime2', 'datetimeoffset', 'time')
                        THEN CAST(c.scale AS VARCHAR(10))
                    ELSE NULL
                END AS DataTypeSize,

                -- Longitud y precisión
                c.max_length AS MaxLengthBytes,
                c.precision AS NumericPrecision,
                c.scale AS NumericScale,

                -- Obligatoriedad
                c.is_nullable AS IsNullable,
                CASE WHEN c.is_nullable = 0 THEN 1 ELSE 0 END AS IsRequired,

                -- Valor por defecto
                dc.definition AS DefaultValue,

                -- Identidad (autoincremental)
                c.is_identity AS IsIdentity,
                ic.seed_value AS IdentitySeed,
                ic.increment_value AS IdentityIncrement,

                -- Clave primaria
                CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey,

                -- Columna calculada
                c.is_computed AS IsComputed,
                cc.definition AS ComputedDefinition,

                -- Otros atributos
                c.is_rowguidcol AS IsRowGuid,
                c.is_sparse AS IsSparse,
                c.is_hidden AS IsHidden,
                c.is_masked AS IsMasked,
                c.generated_always_type_desc AS GeneratedAlwaysType,

                -- Descripción funcional (si existe)
                CAST(ep.value AS NVARCHAR(MAX)) AS Description

            FROM sys.tables t
            INNER JOIN sys.schemas s
                ON s.schema_id = t.schema_id
            INNER JOIN sys.columns c
                ON c.object_id = t.object_id
            INNER JOIN sys.types ty
                ON ty.user_type_id = c.user_type_id

            LEFT JOIN sys.default_constraints dc
                ON dc.object_id = c.default_object_id

            LEFT JOIN sys.identity_columns ic
                ON ic.object_id = c.object_id
                AND ic.column_id = c.column_id

            LEFT JOIN sys.computed_columns cc
                ON cc.object_id = c.object_id
                AND cc.column_id = c.column_id

            LEFT JOIN (
                SELECT
                    ic.object_id,
                    ic.column_id
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic
                    ON ic.object_id = i.object_id
                    AND ic.index_id = i.index_id
                WHERE i.is_primary_key = 1
            ) pk
                ON pk.object_id = c.object_id
                AND pk.column_id = c.column_id

            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = c.object_id
                AND ep.minor_id = c.column_id
                AND ep.name = 'MS_Description'

            WHERE
                s.name = @SchemaName
                AND t.name = @TableName

            ORDER BY c.column_id;

        """


    query = f"""
            DECLARE @SchemaName SYSNAME = 'dbo';
            DECLARE @TableName  SYSNAME = '{table_name}';

            SELECT
                s.name AS SchemaName,
                t.name AS TableName,

                -- Identificación de columna
                c.column_id AS OrdinalPosition,
                c.name AS ColumnName,

                -- Tipo de dato
                ty.name AS DataType,
                CASE
                    WHEN ty.name IN ('varchar', 'char', 'varbinary', 'binary')
                        THEN CASE WHEN c.max_length = -1 THEN 'MAX'
                                ELSE CAST(c.max_length AS VARCHAR(10)) END
                    WHEN ty.name IN ('nvarchar', 'nchar')
                        THEN CASE WHEN c.max_length = -1 THEN 'MAX'
                                ELSE CAST(c.max_length / 2 AS VARCHAR(10)) END
                    WHEN ty.name IN ('decimal', 'numeric')
                        THEN CONCAT(c.precision, ',', c.scale)
                    WHEN ty.name IN ('datetime2', 'datetimeoffset', 'time')
                        THEN CAST(c.scale AS VARCHAR(10))
                    ELSE NULL
                END AS DataTypeSize,

                -- Longitud y precisión
                c.max_length AS MaxLengthBytes,
                c.precision AS NumericPrecision,
                c.scale AS NumericScale,

                -- Obligatoriedad
                c.is_nullable AS IsNullable,
                CASE WHEN c.is_nullable = 0 THEN 1 ELSE 0 END AS IsRequired,

                -- Valor por defecto
                dc.definition AS DefaultValue,

                -- Identidad (autoincremental)
                --c.is_identity AS IsIdentity,
                --ic.seed_value AS IdentitySeed,
                --ic.increment_value AS IdentityIncrement,

                -- Clave primaria
                CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey,

                -- Columna calculada
                c.is_computed AS IsComputed,
                --cc.definition AS ComputedDefinition,

                -- Otros atributos
                c.is_rowguidcol AS IsRowGuid,
                c.is_sparse AS IsSparse,
                c.is_hidden AS IsHidden,
                c.is_masked AS IsMasked,
                -- c.generated_always_type_desc AS GeneratedAlwaysType,

                -- Descripción funcional (si existe)
                CAST(ep.value AS NVARCHAR(MAX)) AS Description

            FROM sys.tables t
            INNER JOIN sys.schemas s
                ON s.schema_id = t.schema_id
            INNER JOIN sys.columns c
                ON c.object_id = t.object_id
            INNER JOIN sys.types ty
                ON ty.user_type_id = c.user_type_id

            LEFT JOIN sys.default_constraints dc
                ON dc.object_id = c.default_object_id

            LEFT JOIN sys.identity_columns ic
                ON ic.object_id = c.object_id
                AND ic.column_id = c.column_id

            LEFT JOIN sys.computed_columns cc
                ON cc.object_id = c.object_id
                AND cc.column_id = c.column_id

            LEFT JOIN (
                SELECT
                    ic.object_id,
                    ic.column_id
                FROM sys.indexes i
                INNER JOIN sys.index_columns ic
                    ON ic.object_id = i.object_id
                    AND ic.index_id = i.index_id
                WHERE i.is_primary_key = 1
            ) pk
                ON pk.object_id = c.object_id
                AND pk.column_id = c.column_id

            LEFT JOIN sys.extended_properties ep
                ON ep.major_id = c.object_id
                AND ep.minor_id = c.column_id
                AND ep.name = 'MS_Description'

            WHERE
                s.name = @SchemaName
                AND t.name = @TableName

            ORDER BY c.column_id;

        """
    try:
        if AzureSQLManager().engine is None:
            return func.HttpResponse(
                "Connection to database rejected. Check the logs for the reason.",
                status_code=400
            )
        with AzureSQLManager().engine.connect() as connection:
            result = connection.execute(text(query))
            table_structure = [dict(row._mapping) for row in result.fetchall()]
            return table_structure
    except Exception as e:
        logging.error(f"Database error: {e}")
        return func.HttpResponse(
            f"Error during database query",
            status_code=500
        )


def get_column_uniques(table_name: str, column_name: str) -> list:

    query = f"SELECT DISTINCT [{column_name}] FROM [{table_name}]"
    try:
        if AzureSQLManager().engine is None:
            return func.HttpResponse(
                "Connection to database rejected. Check the logs for the reason.",
                status_code=400
            ), AzureSQLManager().status

        with AzureSQLManager().engine.connect() as connection:
            result = connection.execute(
                text(query)
            )
            #uniques = result.fetchall()
            uniques = result.scalars().all()

            if uniques is None:
                return func.HttpResponse(
                    json.dumps(f"Error extracting uniques for '{table_name}.{column_name}'"),
                    status_code=200
                ), 404

            logging.warning(uniques)
            return func.HttpResponse(
                json.dumps(uniques, ensure_ascii=True),
                status_code=200
            ), 200

    except Exception as e:
        logging.error(f"Database error: {e}")
        return func.HttpResponse(
            "Error during database query. Check the logs for the reason.",
            status_code=500
        ), 500
    
            
#
    # USERS
def consult_user_data(user: str) -> dict | None:
    """Retrieve user data from the database."""
    try:
        if AzureSQLManager().engine is None:
            return func.HttpResponse(
                "Connection to database rejected. Check the logs for the reason.",
                status_code=400
            ), AzureSQLManager().status
        with AzureSQLManager().engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM dbo.[01_users] WHERE [code] = :username"),
                {"username": user}
            )
            user_data = result.fetchone()
            #logging.warning(f"User data retrieved for user '{user}': {user_data._mapping}")
            if user_data is None:
                return func.HttpResponse(
                                    #json.dumps({"result": f"User '{user}' not found in the database."}),
                                    json.dumps( f"User '{user}' not found in the database."),
                                    status_code=200
                                ), 404

            user_info = dict(user_data._mapping)
            for date_field in ["createdDate", "lastLoginDate", "updatedDate"]:
                if user_info.get(date_field):
                    user_info[date_field] = user_info[date_field].isoformat()
            return func.HttpResponse(
                    json.dumps(user_info, ensure_ascii=True),
                    status_code=200
                ), 200
    except Exception as e:
        logging.error(f"Database error: {e}")
        return func.HttpResponse(
            "Error during database query. Check the logs for the reason.",
            status_code=500
        ), 500



def insert_new_user(user_data: dict) -> None:
    """Insert a new user into the database."""

    try:
        insert_row_generic("01_users", user_data)
    except Exception as e:
        logging.error(f"Failed to insert new user: {e}")
        raise 
    