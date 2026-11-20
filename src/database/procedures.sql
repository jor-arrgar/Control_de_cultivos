/* t-SQL */

IF OBJECT_ID(N'dbo.sp_insert_row_generic', N'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_insert_row_generic;
GO

CREATE PROCEDURE dbo.sp_insert_row_generic
    @table_name NVARCHAR(128),
    @column_list NVARCHAR(MAX),
    @value_list NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    IF @table_name IS NULL OR LTRIM(RTRIM(@table_name)) = ''
        THROW 50001, 'The table_name parameter is required.', 1;

    DECLARE @sql NVARCHAR(MAX);
    SET @sql = N'
        INSERT INTO ' + QUOTENAME(@table_name) + N' (' + @column_list + N')
        VALUES (' + @value_list + N');';

    EXEC sys.sp_executesql @sql;
END;
GO

IF OBJECT_ID(N'dbo.sp_update_row_generic', N'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_update_row_generic;
GO

CREATE PROCEDURE dbo.sp_update_row_generic
    @table_name NVARCHAR(128),
    @code NVARCHAR(50),
    @update_assignments NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    IF @table_name IS NULL OR LTRIM(RTRIM(@table_name)) = ''
        THROW 50002, 'The table_name parameter is required.', 1;

    IF @code IS NULL OR LTRIM(RTRIM(@code)) = ''
        THROW 50003, 'The code parameter is required.', 1;

    DECLARE @main_table NVARCHAR(128) = QUOTENAME(@table_name);
    DECLARE @history_table NVARCHAR(128) = QUOTENAME(@table_name + '_history');
    DECLARE @history_columns NVARCHAR(MAX);
    DECLARE @snapshot_columns NVARCHAR(MAX);
    DECLARE @code_literal NVARCHAR(100) = '''' + REPLACE(@code, '''', '''''') + '''';
    DECLARE @sql NVARCHAR(MAX);

    SELECT @history_columns = STRING_AGG(QUOTENAME(COLUMN_NAME), ',')
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = @table_name + '_history'
      AND COLUMN_NAME <> 'id'
    GROUP BY TABLE_NAME;

    SELECT @snapshot_columns = STRING_AGG(
        CASE
            WHEN COLUMN_NAME = 'id' THEN NULL
            WHEN COLUMN_NAME = 'updatedDate' THEN 'GETDATE()'
            ELSE QUOTENAME(COLUMN_NAME)
        END,
        ','
    )
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = @table_name
      AND COLUMN_NAME NOT IN ('id', 'createdDate', 'code')
    GROUP BY TABLE_NAME;

    SET @snapshot_columns = N'[' + STUFF((
        SELECT ', ' + CASE
            WHEN c.COLUMN_NAME = 'id' THEN NULL
            WHEN c.COLUMN_NAME = 'updatedDate' THEN 'GETDATE()'
            ELSE QUOTENAME(c.COLUMN_NAME)
        END
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_NAME = @table_name
          AND c.COLUMN_NAME NOT IN ('id', 'createdDate', 'code')
        ORDER BY c.ORDINAL_POSITION
        FOR XML PATH(''), TYPE
    ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') + ']';

    IF @snapshot_columns IS NULL
        SET @snapshot_columns = N'';

    SET @sql = N'
        UPDATE ' + @main_table + N'
        SET ' + @update_assignments + N'
        WHERE [code] = ' + @code_literal + N';

        INSERT INTO ' + @history_table + N' (' + @history_columns + N')
        SELECT ' + @history_columns + N'
        FROM ' + @main_table + N'
        WHERE [code] = ' + @code_literal + N';';

    EXEC sys.sp_executesql @sql;
END;
GO

IF OBJECT_ID(N'dbo.sp_restore_previous_row_generic', N'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_restore_previous_row_generic;
GO

CREATE PROCEDURE dbo.sp_restore_previous_row_generic
    @table_name NVARCHAR(128),
    @code NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    IF @table_name IS NULL OR LTRIM(RTRIM(@table_name)) = ''
        THROW 50004, 'The table_name parameter is required.', 1;

    IF @code IS NULL OR LTRIM(RTRIM(@code)) = ''
        THROW 50005, 'The code parameter is required.', 1;

    DECLARE @main_table NVARCHAR(128) = QUOTENAME(@table_name);
    DECLARE @history_table NVARCHAR(128) = QUOTENAME(@table_name + '_history');
    DECLARE @code_literal NVARCHAR(100) = '''' + REPLACE(@code, '''', '''''') + '''';
    DECLARE @update_columns NVARCHAR(MAX);
    DECLARE @sql NVARCHAR(MAX);

    SELECT @update_columns = STRING_AGG(QUOTENAME(c.COLUMN_NAME) + N' = h.' + QUOTENAME(c.COLUMN_NAME), ', ')
    FROM INFORMATION_SCHEMA.COLUMNS c
    WHERE c.TABLE_NAME = @table_name
      AND c.COLUMN_NAME NOT IN ('id', 'createdDate', 'code')
    GROUP BY c.TABLE_NAME;

    SET @sql = N'
        WITH last_version AS (
            SELECT TOP (1) *
            FROM ' + @history_table + N'
            WHERE [code] = ' + @code_literal + N'
            ORDER BY [updatedDate] DESC, [id] DESC
        )
        UPDATE target
        SET
            ' + @update_columns + N',
            target.[updatedDate] = GETDATE()
        FROM ' + @main_table + N' AS target
        INNER JOIN last_version AS h
            ON target.[code] = h.[code];

        DELETE FROM ' + @history_table + N'
        WHERE [id] IN (
            SELECT TOP (1) [id]
            FROM ' + @history_table + N'
            WHERE [code] = ' + @code_literal + N'
            ORDER BY [updatedDate] DESC, [id] DESC
        );';

    EXEC sys.sp_executesql @sql;
END;
GO
