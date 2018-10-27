-- =============================================
-- Author:  Joanna Palewicz
-- Create date: 01.09.2018
-- Description: Procedures which needs to be run before running price estimation component
-- =============================================


-- ===============================================
-- Procedure to get training data
-- ===============================================

CREATE PROCEDURE dbo.GetDateToTrainClassificationModel
    @LimitDate nvarchar(30),
    @ExcludedList nvarchar(MAX)
AS
SELECT OBJECTID, Price_Group_int, Residential, Special_Purposes_Plan, Agricultural, Commercial,
       Manufacturing, Price_Per_Single_Area_Unit, IMPROVE_Curr_Value, PARCEL_TYP,
       LAND_Curr_Value, PERIMETER, PARCEL_TYP, CENTER_X, CENTER_Y,
       CENTER_LAT, CENTER_LON, Parcel_Area, LAND_Curr_Roll_Yr,
       IMPROVE_Curr_Roll_YR, BD_LINE_1_Yr_Built, BD_LINE_1_Sq_Ft_of_Main_Improve,
       City_int, Current_improvement_base_value, cluster_location, cluster_type
FROM PARCEL_VECTORS
WHERE LS1_Sale_Date > @LimitDate
      AND LS1_Sale_Amount not in (SELECT value FROM STRING_SPLIT(@ExcludedList, ';'))
GO


-- EXEC dbo.GetDateToTrainClassificationModel @LimitDate = '20150000', @list='0;9'

-- ============================================================================
-- Procedure to get minimum an maximum object ID for parcels to calculate price
-- ============================================================================


CREATE PROCEDURE dbo.GetMinimumAndMaxumimObjectID
    @LimitDate nvarchar(30),
    @ExcludedList nvarchar(MAX)
AS
SELECT min(OBJECTID) 'MinimumObjectID', max(OBJECTID) as 'MaximumObjectID'
FROM PARCEL_VECTORS
WHERE LS1_Sale_Date <= @LimitDate
      AND
      LS1_Sale_Amount IN (SELECT value FROM STRING_SPLIT(@ExcludedList, ';'))
GO


-- =======================================================
-- Procedure to get data to calculate price group for them
-- =======================================================

CREATE PROCEDURE dbo.GetDataToParcelClassification
    @LimitDate nvarchar(30),
    @ExcludedList nvarchar(MAX),
    @ObjectIdMin int,
    @ObjectIdMax int
AS
SELECT OBJECTID, Price_Group_int, Residential, Special_Purposes_Plan, Agricultural, Commercial,
       Manufacturing, Price_Per_Single_Area_Unit, IMPROVE_Curr_Value, PARCEL_TYP,
       LAND_Curr_Value, PERIMETER, PARCEL_TYP, CENTER_X, CENTER_Y,
       CENTER_LAT, CENTER_LON, Parcel_Area, LAND_Curr_Roll_Yr,
       IMPROVE_Curr_Roll_YR, BD_LINE_1_Yr_Built, BD_LINE_1_Sq_Ft_of_Main_Improve,
       City_int, Current_improvement_base_value, cluster_location, cluster_type
FROM PARCEL_VECTORS
WHERE @ObjectIdMin <= OBJECTID AND OBJECTID < @ObjectIdMax
      AND ( LS1_Sale_Date <= @LimitDate
            OR
            LS1_Sale_Amount IN (SELECT value FROM STRING_SPLIT(@ExcludedList, ';')))
GO

-- ===============================================
-- Procedure to update table with new value
-- ===============================================
CREATE PROCEDURE dbo.UpdateEstimatedPriceLevelGroup
    @NEW_Estimated_Price_Group varchar(20),
    @ObjectID int
AS
SET NOCOUNT ON;
UPDATE PARCEL_VECTORS
  SET Price_Group_int = @NEW_Estimated_Price_Group, Row_Version_Stamp = Row_Version_Stamp + 1
  WHERE OBJECTID = @ObjectID
GO