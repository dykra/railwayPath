
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Magdalena Nowak
-- Create date: 8.09.2018
-- Description:	Procedure to get all columns which have at least one NULL value. 
-- =============================================
CREATE OR ALTER PROCEDURE GetColumnsWithNullValues 
	@Table_Name nvarchar(255) = 'PARCEL_VECTORS'
	
AS
BEGIN
	
	SET NOCOUNT ON;

    IF object_id('tempdb..#COLUMNS_WITH_NULL') IS NOT NULL  --Columns with at least one NULL value.
       DROP TABLE #COLUMNS_WITH_NULL
	
	DECLARE @sqlInsertString as nvarchar(max)=''	

	SELECT @sqlInsertString +='SET NOCOUNT ON; IF EXISTS (select * from ' + c.TABLE_NAME + ' where ' + 
	c.COLUMN_NAME + ' is null) INSERT #COLUMNS_WITH_NULL (TABLE_NAME, COLUMN_NAME) VALUES(' + 
	QUOTENAME(c.TABLE_NAME, '''') + ',' + QUOTENAME(c.COLUMN_NAME, '''') + ') ' + CHAR(13)
	FROM information_schema.columns c WHERE table_name = @Table_Name

	CREATE TABLE #COLUMNS_WITH_NULL (TABLE_NAME nvarchar(2000), COLUMN_NAME nvarchar(2000));
	EXEC sp_executesql @sqlInsertString

	SELECT * FROM #COLUMNS_WITH_NULL

	DROP TABLE #COLUMNS_WITH_NULL
END
GO

-- EXEC GetColumnsWithNullValues @Table_Name = 'PARCEL_VECTORS' 