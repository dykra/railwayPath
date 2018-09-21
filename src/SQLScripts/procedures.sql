-- ===============================================
-- Procedure to get training data
-- ===============================================

ALTER PROCEDURE dbo.getTrainingDataPriceEstimation
    @LimitDate nvarchar(30),
    @BucketType nvarchar(30),
    @ExcludedList nvarchar(MAX)
AS
SELECT  OBJECTID, PERIMETER, LOT, UNIT, SUBDTYPE, TRACT, PARCEL_TYP, GlobalID, CENTER_X, CENTER_Y, CENTER_LAT,
        CENTER_LON, TRA_1, LAND_Curr_Roll_Yr,
        LAND_Curr_Value	IMPROVE_Curr_Roll_YR, IMPROVE_Curr_Value, SA_House_Number, SA_Zip_Cde, MA_House_Number,
        MA_Zip_Cde,	Recording_Date,	z
        Use_Cde, Hmownr_Exempt_Number, Hmownr_Exempt_Value, LS1_Sale_Date, LS2_Sale_Amount, LS2_Sale_Date,
        LS3_Sale_Date, BD_LINE_1_Subpart, BD_LINE_1_Design_Type, BD_LINE_1_Yr_Built, BD_LINE_1_No_of_Units,
        BD_LINE_1_No_of_Bedrooms, BD_LINE_1_No_of_Baths, BD_LINE_1_Sq_Ft_of_Main_Improve, BD_LINE_2_Subpart,
        BD_LINE_2_Design_Type, BD_LINE_2_Quality__Class___Shap, BD_LINE_2_Yr_Built, BD_LINE_2_No_of_Units,
        BD_LINE_2_No_of_Bedrooms, BD_LINE_2_No_of_Baths, BD_LINE_2_Sq_Ft_of_Main_Improve, BD_LINE_3_Subpart,
        BD_LINE_3_Design_Type, BD_LINE_3_Quality__Class___Shap, BD_LINE_3_Yr_Built, BD_LINE_3_No_of_Units,
        BD_LINE_3_No_of_Bedrooms, BD_LINE_3_No_of_Baths, BD_LINE_3_Sq_Ft_of_Main_Improve,
        Legal_Description_Line1, Current_Land_Base_Year, Current_Improvement_Base_Year,
        Current_Land_Base_Value, Current_Improvement_Base_Value, Cluster_Location, Cluster_Type,
        Cluster_Appraisal_Unit,	Land_Reason_Key, Document_Transfer_Tax_Sales_Amo, BD_LINE_1_Year_Changed,
        BD_LINE_1_Unit_Cost_Main, BD_LINE_1_RCN_Main, BD_LINE_2_Year_Changed, BD_LINE_2_Unit_Cost_Main,
        BD_LINE_2_RCN_Main, BD_LINE_3_Year_Changed, BD_LINE_3_Unit_Cost_Main, BD_LINE_3_RCN_Main,
        BD_LINE_4_Year_Changed,	Landlord_Reappraisal_Year,	Landlord_Number_of_Units,
        Recorders_Document_Number,	Price_Per_Single_Area_Unit,	Parcel_Area, Residential,
        Special_Purposes_Plan, Agricultural, Commercial, Manufacturing, SA_Localization_int,
        MA_Localization_int, MA_Direction_int, SA_Direction_int, Simple_Zone_int,
        Zoning_Code_int, BD_LINE_1_Quality__Class___Shap_int, City_int,	Sale_Amount
FROM PARCEL_VECTORS
WHERE LS1_Sale_Date > @LimitDate
      AND Price_Group LIKE @BucketType AND
      LS1_Sale_Amount not in (SELECT value FROM STRING_SPLIT(@ExcludedList, ';'))
GO


-- EXEC dbo.getTrainingDataPriceEstimation @LimitDate = '20150000', @BucketType="cheap", @list='0;9'


-- ===============================================
-- Procedure to get data to calculate
-- ===============================================

ALTER PROCEDURE dbo.getDataForPriceCalculation
    @LimitDate nvarchar(30),
    @BucketType nvarchar(30),
    @ExcludedList nvarchar(MAX)
AS
SELECT  OBJECTID, PERIMETER, LOT, UNIT, SUBDTYPE, TRACT, PARCEL_TYP, GlobalID, CENTER_X, CENTER_Y, CENTER_LAT,
        CENTER_LON, TRA_1, LAND_Curr_Roll_Yr,
        LAND_Curr_Value	IMPROVE_Curr_Roll_YR, IMPROVE_Curr_Value, SA_House_Number, SA_Zip_Cde, MA_House_Number,
        MA_Zip_Cde,	Recording_Date,	z
        Use_Cde, Hmownr_Exempt_Number, Hmownr_Exempt_Value, LS1_Sale_Date, LS2_Sale_Amount, LS2_Sale_Date,
        LS3_Sale_Date, BD_LINE_1_Subpart, BD_LINE_1_Design_Type, BD_LINE_1_Yr_Built, BD_LINE_1_No_of_Units,
        BD_LINE_1_No_of_Bedrooms, BD_LINE_1_No_of_Baths, BD_LINE_1_Sq_Ft_of_Main_Improve, BD_LINE_2_Subpart,
        BD_LINE_2_Design_Type, BD_LINE_2_Quality__Class___Shap, BD_LINE_2_Yr_Built, BD_LINE_2_No_of_Units,
        BD_LINE_2_No_of_Bedrooms, BD_LINE_2_No_of_Baths, BD_LINE_2_Sq_Ft_of_Main_Improve, BD_LINE_3_Subpart,
        BD_LINE_3_Design_Type, BD_LINE_3_Quality__Class___Shap, BD_LINE_3_Yr_Built, BD_LINE_3_No_of_Units,
        BD_LINE_3_No_of_Bedrooms, BD_LINE_3_No_of_Baths, BD_LINE_3_Sq_Ft_of_Main_Improve,
        Legal_Description_Line1, Current_Land_Base_Year, Current_Improvement_Base_Year,
        Current_Land_Base_Value, Current_Improvement_Base_Value, Cluster_Location, Cluster_Type,
        Cluster_Appraisal_Unit,	Land_Reason_Key, Document_Transfer_Tax_Sales_Amo, BD_LINE_1_Year_Changed,
        BD_LINE_1_Unit_Cost_Main, BD_LINE_1_RCN_Main, BD_LINE_2_Year_Changed, BD_LINE_2_Unit_Cost_Main,
        BD_LINE_2_RCN_Main, BD_LINE_3_Year_Changed, BD_LINE_3_Unit_Cost_Main, BD_LINE_3_RCN_Main,
        BD_LINE_4_Year_Changed,	Landlord_Reappraisal_Year,	Landlord_Number_of_Units,
        Recorders_Document_Number,	Price_Per_Single_Area_Unit,	Parcel_Area, Residential,
        Special_Purposes_Plan, Agricultural, Commercial, Manufacturing, SA_Localization_int,
        MA_Localization_int, MA_Direction_int, SA_Direction_int, Simple_Zone_int,
        Zoning_Code_int, BD_LINE_1_Quality__Class___Shap_int, City_int,	Sale_Amount
FROM PARCEL_VECTORS
WHERE ( LS1_Sale_Date <= @LimitDate OR
      ( LS1_Sale_Amount IN (SELECT value FROM STRING_SPLIT(@ExcludedList, ';'))) )
      AND Price_Group LIKE @BucketType
GO