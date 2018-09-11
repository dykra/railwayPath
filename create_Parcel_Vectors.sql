-- =============================================
-- CREATE NEW TABLE PARCEL_VECTORS
-- not interested values are dropped
-- =============================================


IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'PARCEL_VECTORS'))
BEGIN
	DROP TABLE PARCEL_VECTORS
END

SELECT  
	OBJECTID, PERIMETER, PARCEL_TYP, TRA_1, 
	LAND_Curr_Roll_Yr, LAND_Curr_Value, IMPROVE_Curr_Roll_YR, IMPROVE_Curr_Value, 
	SA_House_Number, SA_Direction, SA_Street_Name, SA_City_and_State, SA_Zip_Cde,
	MA_House_Number, MA_Direction, MA_Street_Name, MA_City_and_State, MA_Zip_Cde, 
	Recording_Date, Zoning_Code, Hmownr_Exempt_Number, Hmownr_Exempt_Value, --22
	LS1_Sale_Amount, LS1_Sale_Date,	LS2_Sale_Date,	LS3_Sale_Date,	
	BD_LINE_1_Quality__Class___Shap, BD_LINE_1_Yr_Built, BD_LINE_1_No_of_Units, 
	BD_LINE_1_No_of_Bedrooms, BD_LINE_1_No_of_Baths, BD_LINE_1_Sq_Ft_of_Main_Improve, 
	BD_LINE_2_Subpart, BD_LINE_2_Yr_Built,	BD_LINE_2_No_of_Units,	
	BD_LINE_2_No_of_Bedrooms,	BD_LINE_2_No_of_Baths, BD_LINE_2_Sq_Ft_of_Main_Improve, 
	BD_LINE_3_Subpart,	BD_LINE_3_Yr_Built,	BD_LINE_3_No_of_Units,	--19
	BD_LINE_3_No_of_Bedrooms, BD_LINE_3_No_of_Baths, BD_LINE_3_Sq_Ft_of_Main_Improve,
	Current_Land_Base_Year, Current_Improvement_Base_Year, Current_Land_Base_Value, 
	Current_Improvement_Base_Value, 
	Cluster_Location, Cluster_Type, Cluster_Appraisal_Unit, Document_Transfer_Tax_Sales_Amo, 
	BD_LINE_1_Year_Changed, BD_LINE_1_Unit_Cost_Main, BD_LINE_1_RCN_Main,
	BD_LINE_2_Year_Changed,	BD_LINE_2_Unit_Cost_Main, BD_LINE_2_RCN_Main, 
	BD_LINE_3_Year_Changed, BD_LINE_3_Unit_Cost_Main,BD_LINE_3_RCN_Main,	--20
	BD_LINE_4_Year_Changed,	Landlord_Reappraisal_Year,	Landlord_Number_of_Units,	
	Recorders_Document_Number, Shape --5
INTO PARCEL_VECTORS FROM PARCEL;


-- =============================================
-- Get data from Zoning_Code column
-- Adding and filling new column Simple_Zoning_Code
-- Adding and filling new column City
-- Adding new column Price_Per_Single_Area_Unit 
-- Adding new column Parcel_Area
-- =============================================

IF (NOT EXISTS (select * from information_schema.COLUMNS where TABLE_NAME = 'PARCEL_VECTORS' and COLUMN_NAME = 'Simple_Zoning_Code'))
	BEGIN
		ALTER TABLE PARCEL_VECTORS
			ADD 
				Simple_Zoning_Code NVARCHAR(15), 
				City NVARCHAR(5),
				Price_Per_Single_Area_Unit INT,
				Parcel_Area INT
	END
GO

UPDATE PARCEL_VECTORS
  SET City=substring(Zoning_Code,1,2)
GO

-- =============================================
-- Get data from connected to parcel area
-- data from Shape geometry column
-- =============================================


UPDATE PARCEL_VECTORS
  SET Parcel_Area=Shape.STArea()
GO

UPDATE PARCEL_VECTORS
  SET Price_Per_Single_Area_Unit=(LS1_Sale_Amount/(Parcel_Area+1))
GO

-- =============================================
-- ADD NEW COLUMNS FOR BASIC AREAS TYPES
-- ============================================= to jest dodatkowe

--IF (NOT EXISTS (select * from information_schema.COLUMNS where TABLE_NAME = 'PARCEL_VECTORS' and COLUMN_NAME =))
BEGIN
	ALTER TABLE PARCEL_VECTORS
  ADD 
	Residential SMALLINT, 
	Special_Purposes_Plan SMALLINT, 
	Agricultural SMALLINT, 
	Commercial SMALLINT,
	Manufacturing SMALLINT
END
GO


-- =============================================
-- Parse Zoning codes
-- RESIDENTIAL
-- R1 - single family residence
-- R2 - two family residence
-- R3 - limited multiple residence
-- =============================================

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code =
    CASE substring(Zoning_Code, 3, 1)
        WHEN 'R' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'R1'
                WHEN '2' THEN 'R2'
                WHEN '3' THEN 'R3'
				WHEN '4' THEN 'R4'
              END
	END
	WHERE Simple_Zoning_Code is null
GO


-- for SCUR1, SCUR2, SCUR3, SCUR4, SCUR5 
UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = substring(Zoning_Code, 4, 2)
    WHERE Zoning_Code like 'SCUR%'
GO


UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'R2'
	WHERE Zoning_Code like 'LAMR2'
GO

UPDATE PARCEL_VECTORS
    SET Residential = (CASE
                       WHEN Simple_Zoning_code IN ('R1', 'R2', 'R3', 'R4', 'R5') THEN 1 ELSE 0 END)
GO


-- =============================================
-- AGRICULTURAL
-- A1: Light Agriculture
-- A2: Heavy Agriculture, Including Hog Ranches

-- COMMERCIAL
-- C1: Restricted Business
-- C2: Neighborhood Business
-- C3: Unlimited Commercial
-- CM: Commercial Manufacturing
-- CR: Commercial Recreation
-- CPD: Commercial Planned Development

-- MANUFACTURING
-- M1: Light Manufacturing
-- M2 Aircraft Heavy Manufacturing
-- M3: Unclassified
-- =============================================

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code =
    CASE substring(Zoning_Code, 3, 1)
        WHEN 'A' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'A1'
                WHEN '2' THEN 'A2'
                WHEN '3' THEN 'A3'
              END

        WHEN 'C' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'C1'
                WHEN '2' THEN 'C2'
                WHEN '3' THEN 'C3'
                WHEN '4' THEN 'C4'
              END

        WHEN 'M' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'M1'
                WHEN '2' THEN 'M2'
                WHEN '3' THEN 'M3'
              END
    END
WHERE Simple_Zoning_Code is null;


-- TODO co to jest C5
UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'C5'
    WHERE Zoning_Code like 'LAC5';


UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'CM'
    WHERE Zoning_Code like 'LACM';


UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'CR'
    WHERE Zoning_Code like 'LBCR*'
          or Zoning_Code like 'LBCR'
          or Zoning_Code like 'AHCR'
          or Zoning_Code like 'LRCR*';

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'CPD'
    WHERE Zoning_Code like 'CPD';

UPDATE PARCEL_VECTORS
    SET Agricultural = (CASE
                       WHEN Simple_Zoning_code IN ('A1', 'A2', 'A3') THEN 1 ELSE 0 END);

UPDATE PARCEL_VECTORS
    SET Commercial = (CASE
                       WHEN Simple_Zoning_code IN ('C1', 'C2', 'C3', 'C4', 'C5', 'CM', 'CPD', 'CR') THEN 1 ELSE 0 END);

UPDATE PARCEL_VECTORS
    SET Manufacturing = (CASE
                       WHEN Simple_Zoning_code IN ('M1', 'M2', 'M3') THEN 1 ELSE 0 END);

-- =============================================
-- SPECIAL PURPOSE ZONES
-- SP: Specific Plan
-- PR - restricted parking
-- RR - resort and recreation
-- =============================================

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'SP'
    WHERE Zoning_Code like 'PDSP'
          or Zoning_Code like 'PDSP*'
          or Zoning_Code like 'LRSP'
          or Zoning_Code like 'NOSP2*'
		  or Zoning_Code like 'SCSP';

		  
UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'RR'
    WHERE substring(Zoning_Code, 3, 3) like 'RR-';    

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'PR'
    WHERE substring(Zoning_Code, 3, 3) like 'PR-';


UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'PR'
    WHERE Zoning_Code like 'LCPR*'
          or Zoning_Code like 'POPRD*';


UPDATE PARCEL_VECTORS
    SET Special_Purposes_Plan = (CASE
                       WHEN Simple_Zoning_code IN ('SP', 'RR', 'PR') THEN 1 ELSE 0 END);


-- =============================================
-- OTHER TYPES
-- =============================================

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code =
    CASE Zoning_Code
        WHEN 'GAMUO' THEN 'GAMUO' 
		WHEN 'RBPDR*' THEN 'RBPDR*' 
		WHEN 'PRSF*' THEN 'SF?' 
		WHEN 'LAWC' THEN 'W1' 
		WHEN 'LACW' THEN 'W2' 
		WHEN 'PSC-' THEN 'PSC?'  
		WHEN 'LBPD1' THEN 'PD1?' 
		WHEN 'LAMR1' THEN 'R1'     
	END
WHERE Simple_Zoning_Code is null
GO

UPDATE PARCEL_VECTORS
  SET Simple_Zoning_Code = 'R'
    WHERE Zoning_Code like '__R%'
           and Simple_Zoning_Code is null;




-----------					Street and State concatenations			------------------------------------------------------------------------------------------

-----New column to PARCEL_VECTORS to concatenate MA_Street_Name and MA_City_and_State
-----New column to PARCEL_VECTORS to concatenate SA_Street_Name and SA_City_and_State
ALTER table PARCEL_VECTORS
add MA_Street_and_City_and_State nvarchar(100), SA_Street_and_City_and_State nvarchar(100)
GO

UPDATE PARCEL_VECTORS
set MA_Street_and_City_and_State = MA_Street_Name + ' '+ MA_City_and_State,
	SA_Street_and_City_and_State = SA_Street_Name + ' '+ SA_City_and_State;



-------------------------					TEMP TABLES	TO MAPPING			-----------------------------------------------------------------

--------------------------------
--Mapping tables:
--Simple_Zones_Mapping +
--Directions_Mapping +
--Localization_SA_Mapping +
--Localization_MA_Mapping +
--Zoning_Codes_Mapping
--BD_LINE_1_Quality__Class___Shap_Mapping
--City_Mapping

-----------------------------

--1
---Table to map simple_zone


IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'Simple_Zones_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END

ELSE
BEGIN
	insert into Simple_Zones_Mapping (Simple_Zoning_Code)
	select DISTINCT P.Simple_Zoning_Code 
	from PARCEL_VECTORS P
	where P.Simple_Zoning_Code not in (
		select DISTINCT P.Simple_Zoning_Code from PARCEL_VECTORS P
		inner join Simple_Zones_Mapping L
		on L.Simple_Zoning_Code = P.Simple_Zoning_Code
	)

END


--2
----Table to map SA_Direction and MA_Direction---
--only possible values are NULL, W, E, N, S - so this table do not need updates when the data set is growing

IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'Directions_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN
	insert into Directions_Mapping (Direction)
	select DISTINCT P.SA_Direction 
	from PARCEL_VECTORS P
	where P.SA_Direction not in (
	select DISTINCT P.SA_Direction from PARCEL_VECTORS P
	inner join Directions_Mapping D
	on D.Direction = P.SA_Direction)

	insert into Directions_Mapping (Direction)
	select DISTINCT P.MA_Direction 
	from PARCEL_VECTORS P
	where P.MA_Direction not in (
	select DISTINCT P.MA_Direction from PARCEL_VECTORS P
	inner join Directions_Mapping D
	on D.Direction = P.MA_Direction
	)

END

--3
----Table to map SA_Street-and_City-and_State---
IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'Localization_SA_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN
	insert into Localization_SA_Mapping (SA_Street_and_City_and_State)
	select DISTINCT P.SA_Street_and_City_and_State 
	from Lands_Vectors P
	where P.SA_Street_and_City_and_State not in (
	select DISTINCT P.SA_Street_and_City_and_State from Lands_Vectors P
	inner join Localization_SA_Mapping L
	on L.SA_Street_and_City_and_State = P.SA_Street_and_City_and_State
	)

END


--4
----Table to map MA_Street-and_City-and_State---
IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'Localization_MA_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN
	insert into Localization_MA_Mapping (MA_Street_and_City_and_State)
	select DISTINCT P.MA_Street_and_City_and_State 
	from PARCEL_VECTORS P
	where P.MA_Street_and_City_and_State not in (
	select DISTINCT P.MA_Street_and_City_and_State from PARCEL_VECTORS P
	inner join Localization_MA_Mapping L
	on L.MA_Street_and_City_and_State = P.MA_Street_and_City_and_State
	)
END


--5
----Table to map Zoning_Code---
IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'Zoning_Codes_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN
	
	insert into Zoning_Codes_Mapping (Zoning_Code)
	select DISTINCT P.Zoning_Code 
	from PARCEL_VECTORS P
	where P.Zoning_Code not in (
	select DISTINCT P.Zoning_Code from PARCEL_VECTORS P
	inner join Zoning_Codes_Mapping L
	on L.Zoning_Code = P.Zoning_Code
	)

END


--6
----Table to map BD_LINE_1_Quality---
IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'BD_LINE_1_Quality__Class___Shap_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN

	insert into BD_LINE_1_Quality__Class___Shap_Mapping (BD_LINE_1_Quality__Class___Shap)
	select DISTINCT P.BD_LINE_1_Quality__Class___Shap 
	from PARCEL_VECTORS P
	where P.BD_LINE_1_Quality__Class___Shap not in (
	select DISTINCT P.BD_LINE_1_Quality__Class___Shap from PARCEL_VECTORS P
	inner join BD_LINE_1_Quality__Class___Shap_Mapping M
	on M.BD_LINE_1_Quality__Class___Shap = P.BD_LINE_1_Quality__Class___Shap
	)

END


--7
----Table to map City---

IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'City_Mapping'))
BEGIN
	PRINT 'FIRSTLY RUN create_mapping_tables SCRIPT'
END
ELSE
BEGIN
	insert into City_Mapping (City)
	select DISTINCT P.City 
	from PARCEL_VECTORS P
	where P.City not in (
	select DISTINCT P.City from PARCEL_VECTORS P
	inner join City_Mapping M
	on M.City = P.City
	)

END

--------------------------------------------------------------------------------------


ALTER TABLE PARCEL_VECTORS
ADD SA_Localization_int int, 
	MA_Localization_int int, 
	MA_Direction_int int, 
	SA_Direction_int int,
	Simple_Zone_int int,
	Zoning_Code_int int,
	BD_LINE_1_Quality__Class___Shap_int int,
	City_int int




---Rewriting mapping from mapping tables into Lands_Vector table----------

--1
update l set l.SA_Direction_int = d.Direction_int
from PARCEL_VECTORS l
inner join Directions_Mapping d on l.SA_Direction = d.Direction
GO

update PARCEL_VECTORS
set SA_Direction_int = 1 
where SA_Direction is null
GO

--2
update l set l.MA_Direction_int = d.Direction_int
from PARCEL_VECTORS l
inner join Directions_Mapping d on l.MA_Direction = d.Direction
GO

update PARCEL_VECTORS
set MA_Direction_int = 1 
where MA_Direction is null
GO


--3

update l set l.Zoning_Code_int = z.Zoning_Code_int
from PARCEL_VECTORS l
inner join Zoning_Codes_Mapping z on l.Zoning_Code = z.Zoning_Code
GO

--Zoning Code = NULL -> Zoning_Code_int = 0
update PARCEL_VECTORS
set Zoning_Code_int = 0 
where Zoning_Code_int is null
GO

--4
update l set l.SA_Localization_int = lm.SA_Street_and_City_and_State_int
from PARCEL_VECTORS l
inner join Localization_SA_Mapping lm on l.SA_Street_and_City_and_State = lm.SA_Street_and_City_and_State
GO

update PARCEL_VECTORS
set SA_Localization_int = 0 
where SA_Localization_int is null
GO


--5
update l set l.MA_Localization_int = lm.MA_Street_and_City_and_State_int
from PARCEL_VECTORS l
inner join Localization_MA_Mapping lm on l.MA_Street_and_City_and_State = lm.MA_Street_and_City_and_State
GO

update PARCEL_VECTORS
set MA_Localization_int = 0 
where MA_Localization_int is null
GO


--6
update l set l.Simple_Zone_int = s.Simple_Zone_int
from PARCEL_VECTORS l
inner join Simple_Zones_Mapping s on l.Simple_Zoning_Code = s.Simple_Zoning_Code
GO

update PARCEL_VECTORS
set Simple_Zone_int = 1 
where Simple_Zone_int is null
GO

--7
update l set l.BD_LINE_1_Quality__Class___Shap_int = m.BD_LINE_1_Quality__Class___Shap_int
from PARCEL_VECTORS l
inner join BD_LINE_1_Quality__Class___Shap_Mapping m on l.BD_LINE_1_Quality__Class___Shap = m.BD_LINE_1_Quality__Class___Shap
GO

update PARCEL_VECTORS
set BD_LINE_1_Quality__Class___Shap_int = 0 
where BD_LINE_1_Quality__Class___Shap_int is null
GO

--8
update l set l.City_int = c.City_int
from PARCEL_VECTORS l
inner join City_Mapping c on l.City = c.City
GO

--City = NULL -> City_int = 0
update PARCEL_VECTORS
set City_int = 0 
where City_int is null
GO


------Droping columns with string values from Lands_Vectors -----
ALTER TABLE PARCEL_VECTORS
DROP COLUMN 
SA_Direction, SA_Street_Name, SA_City_and_State, 
MA_Direction, MA_Street_Name, MA_City_and_State,
Zoning_Code, BD_LINE_1_Quality__Class___Shap,
SA_Street_and_City_and_State, MA_Street_and_City_and_State, City, Simple_Zoning_Code, Shape



------Mapping NULL values into numbers----------

exec UpdateNullValues

exec GetColumnsWithNullValues


---Move LS1_Sale_Amount column to the end and rename it

alter table PARCEL_VECTORS
add Sale_Amount int 
GO

update PARCEL_VECTORS set Sale_Amount = LS1_Sale_Amount
GO


alter table PARCEL_VECTORS
drop column LS1_Sale_Amount

---



SELECT OBJECTID, PERIMETER, PARCEL_TYP, TRA_1, LAND_Curr_Roll_Yr,LAND_Curr_Value, IMPROVE_Curr_Roll_YR, IMPROVE_Curr_Value, SA_House_Number, SA_Zip_Cde, 
MA_House_Number,	MA_Zip_Cde,	Recording_Date,
Hmownr_Exempt_Number, Hmownr_Exempt_Value, LS1_Sale_Date, LS2_Sale_Date,
LS3_Sale_Date, BD_LINE_1_Yr_Built, BD_LINE_1_No_of_Units,	--20

BD_LINE_1_No_of_Bedrooms, BD_LINE_1_No_of_Baths, BD_LINE_1_Sq_Ft_of_Main_Improve, BD_LINE_2_Subpart,
BD_LINE_2_Yr_Built, BD_LINE_2_No_of_Units,
BD_LINE_2_No_of_Bedrooms, BD_LINE_2_No_of_Baths, BD_LINE_2_Sq_Ft_of_Main_Improve,
BD_LINE_3_Subpart,
BD_LINE_3_Yr_Built, BD_LINE_3_No_of_Units,BD_LINE_3_No_of_Bedrooms, BD_LINE_3_No_of_Baths, BD_LINE_3_Sq_Ft_of_Main_Improve,
Current_Land_Base_Year, Current_Improvement_Base_Year,
Current_Land_Base_Value, Current_Improvement_Base_Value, Cluster_Location,	--20

Cluster_Type, Cluster_Appraisal_Unit, Document_Transfer_Tax_Sales_Amo, BD_LINE_1_Year_Changed,
BD_LINE_1_Unit_Cost_Main, BD_LINE_1_RCN_Main, BD_LINE_2_Year_Changed, 
BD_LINE_2_Unit_Cost_Main, BD_LINE_2_RCN_Main, BD_LINE_3_Year_Changed, 
BD_LINE_3_Unit_Cost_Main, BD_LINE_3_RCN_Main, BD_LINE_4_Year_Changed,Landlord_Reappraisal_Year,
Landlord_Number_of_Units, Recorders_Document_Number, Price_Per_Single_Area_Unit, Parcel_Area, Residential,
Special_Purposes_Plan,	--20 

Agricultural, Commercial, Manufacturing, SA_Localization_int,
MA_Localization_int, MA_Direction_int, SA_Direction_int, Simple_Zone_int,
Zoning_Code_int,
BD_LINE_1_Quality__Class___Shap_int,	--10

City_int, Sale_Amount
INTO PARCEL_DATA_SET FROM Lands_Vectors
	WHERE Sale_Amount < 10000000


 select top 10 * from PARCEL_DATA_SET



 select * from PARCEL_DATA_SET where Sale_Amount <1000000 and Sale_Amount > 500000
 order by OBJECTID 



SELECT *
 --select top 1 * 
 FROM PARCEL_VECTORS
	WHERE Sale_Amount <500000
	and LS1_Sale_Date > 20150000
      and Sale_Amount != 9
      and Sale_Amount != 0
      and Sale_Amount != 999999999 and Zoning_Code_int != 0 
	order by Price_Per_Single_Area_Unit--OBJECTID
---TU skonczone