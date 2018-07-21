-- =============================================
-- CREATE NEW TABLE FILTERED_PARCEL
-- not interested values are dropped
-- =============================================


IF (EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_NAME = 'FILTERED_PARCEL'))
BEGIN
	DROP TABLE FILTERED_PARCEL
END
     
SELECT  *
	INTO FILTERED_PARCEL FROM PARCEL
	WHERE LS1_Sale_Date > 20150000
      and LS1_Sale_Amount != 9
      and LS1_Sale_Amount != 0
      and LS1_Sale_Amount != 999999999;


DELETE FROM FILTERED_PARCEL
WHERE Zoning_Code IS NULL
GO

-- =============================================
-- Get data from Zoning_Code column
-- Adding and filling new column Simple_Zoning_Code
-- Adding and filling new column City
-- Adding new column Price_Per_Single_Area_Unit 
-- Adding new column Parcel_Area
-- =============================================

IF (NOT EXISTS (select * from information_schema.COLUMNS where TABLE_NAME = 'FILTERED_PARCEL' and COLUMN_NAME = 'Simple_Zoning_Code'))
	BEGIN
		ALTER TABLE FILTERED_PARCEL
			ADD 
				Simple_Zoning_Code NVARCHAR(15) DEFAULT NULL, 
				City NVARCHAR(5),
				Price_Per_Single_Area_Unit INT,
				Parcel_Area INT
	END
GO

UPDATE FILTERED_PARCEL
  SET City=substring(Zoning_Code,1,2)
GO

-- =============================================
-- Get data from connected to parcel area
-- data from Shape geometry column
-- =============================================


UPDATE FILTERED_PARCEL
  SET Parcel_Area=Shape.STArea()
GO

UPDATE FILTERED_PARCEL
  SET Price_Per_Single_Area_Unit=(LS1_Sale_Amount/(Parcel_Area+1))
GO


-- =============================================
-- ADD NEW COLUMNS FOR BASIC AREAS TYPES
-- ============================================= to jest dodatkowe

--IF (NOT EXISTS (select * from information_schema.COLUMNS where TABLE_NAME = 'FILTERED_PARCEL' and COLUMN_NAME =))
BEGIN
	ALTER TABLE FILTERED_PARCEL
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

UPDATE FILTERED_PARCEL
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
UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = substring(Zoning_Code, 4, 2)
    WHERE Zoning_Code like 'SCUR%'
GO


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R2'
	WHERE Zoning_Code like 'LAMR2'
GO

UPDATE FILTERED_PARCEL
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

UPDATE FILTERED_PARCEL
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
UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'C5'
    WHERE Zoning_Code like 'LAC5';


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'CM'
    WHERE Zoning_Code like 'LACM';


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'CR'
    WHERE Zoning_Code like 'LBCR*'
          or Zoning_Code like 'LBCR'
          or Zoning_Code like 'AHCR'
          or Zoning_Code like 'LRCR*';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'CPD'
    WHERE Zoning_Code like 'CPD';

UPDATE FILTERED_PARCEL
    SET Agricultural = (CASE
                       WHEN Simple_Zoning_code IN ('A1', 'A2', 'A3') THEN 1 ELSE 0 END);

UPDATE FILTERED_PARCEL
    SET Commercial = (CASE
                       WHEN Simple_Zoning_code IN ('C1', 'C2', 'C3', 'C4', 'C5', 'CM', 'CPD', 'CR') THEN 1 ELSE 0 END);

UPDATE FILTERED_PARCEL
    SET Manufacturing = (CASE
                       WHEN Simple_Zoning_code IN ('M1', 'M2', 'M3') THEN 1 ELSE 0 END);

-- =============================================
-- SPECIAL PURPOSE ZONES
-- SP: Specific Plan
-- PR - restricted parking
-- RR - resort and recreation
-- =============================================

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'SP'
    WHERE Zoning_Code like 'PDSP'
          or Zoning_Code like 'PDSP*'
          or Zoning_Code like 'LRSP'
          or Zoning_Code like 'NOSP2*'
		  or Zoning_Code like 'SCSP';

		  
UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'RR'
    WHERE substring(Zoning_Code, 3, 3) like 'RR-';    

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PR'
    WHERE substring(Zoning_Code, 3, 3) like 'PR-';


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PR'
    WHERE Zoning_Code like 'LCPR*'
          or Zoning_Code like 'POPRD*';


UPDATE FILTERED_PARCEL
    SET Special_Purposes_Plan = (CASE
                       WHEN Simple_Zoning_code IN ('SP', 'RR', 'PR') THEN 1 ELSE 0 END);


-- =============================================
-- OTHER TYPES
-- =============================================

UPDATE FILTERED_PARCEL
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

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R'
    WHERE Zoning_Code like '__R%'
           and Simple_Zoning_Code is null;





---------------polecenie które zwraca ilosc roznych kodów - Zoning_Code, których nie udalo sie odszyfrowaæ------------------
--SELECT Zoning_Code, Simple_Zoning_Code, count(*) as quantity FROM FILTERED_PARCEL
--where Simple_Zoning_Code is null
--group by Zoning_Code, Simple_Zoning_Code
--order by quantity desc







---------New table - Lands_Vectors - Lands with mapped values into integer--
select * into Lands_Vectors from Filtered_Parcel

alter table Lands_Vectors
drop column AIN, Shape
GO



alter table Lands_Vectors
drop column PHASE, PCLTYPE, MOVED, TRA, USECODE, BLOCK, UDATE, EDITORNAME, UNIT_NO, PM_REF, TOT_UNITS, Agency_Class_Number,
SA_Fraction, SA_Unit, MA_Fraction, MA_Unit, F1st_Owner_Assee_Name, F1st_Owner_Name_Overflow, Special_Name_Legend,
Special_Name_Assee_Name, F2nd_Owner_Assee_Name, HA_City_Ky, HA_Information, Partial_Interest, Document_Reason_Cde, Ownership_Cde, 
Exemption_Claim_Type, PersProp_Ky, PersProp_Value, Pers_Prop_Exempt_Value, Fixture_Value, Fixture_Exempt_Value
GO

select * from Lands_Vectors


alter table Lands_Vectors
drop column ASSRDATA_M, Real_Est_Exempt_Value, LS1_Verification_Ky, LS2_Verification_Ky, LS3_Verification_Ky, LS3_Sale_Amount, 
GO



-----------					Street and State concatenations			------------------------------------------------------------------------------------------

-----New column to Lands_Vectors to concatenate MA_Street_Name and MA_City_and_State
-----New column to Lands_Vectors to concatenate SA_Street_Name and SA_City_and_State
ALTER table Lands_Vectors
add MA_Street_and_City_and_State nvarchar(100), SA_Street_and_City_and_State nvarchar(100)
GO

UPDATE Lands_Vectors
set MA_Street_and_City_and_State = MA_Street_Name + ' '+ MA_City_and_State,
	SA_Street_and_City_and_State = SA_Street_Name + ' '+ SA_City_and_State;




-----------					TEMP TABLES	TO MAPPING			------------------------------------------------------------------------------------------
--1
---Table to map simple_zone
select DISTINCT Simple_Zoning_Code 
into Simple_Zones_Mapping from Lands_Vectors
GO


ALTER TABLE Simple_Zones_Mapping 
	ADD Simple_Zone_int INT IDENTITY(1,1) 
GO


--2
----Table to map SA_Direction and MA_Direction---
select DISTINCT SA_Direction 
	into Directions_Mapping from Lands_Vectors
GO

--changing name of column - this table will be use not only for SA_Direction, also for MA_Direction - so generaly - Direction
sp_rename 'Directions_Mapping.SA_Direction', 'Direction', 'COLUMN';

ALTER TABLE Directions_Mapping
ADD Direction_int INT IDENTITY(1,1)

--3
----Table to map SA_Street-and_City-and_State---
select DISTINCT SA_Street_and_City_and_State
into Localization_SA_Mapping from Lands_Vectors
GO

ALTER TABLE Localization_SA_Mapping
ADD SA_Street_and_City_and_State_int INT IDENTITY(1,1)


--4
----Table to map SA_Street-and_City-and_State---
SELECT DISTINCT MA_Street_and_City_and_State
into Localization_MA_Mapping from Lands_Vectors
GO

ALTER TABLE Localization_MA_Mapping
ADD MA_Street_and_City_and_State_int INT IDENTITY(1,1)


--5
----Table to map Zoning_Code---
select DISTINCT Zoning_Code
into Zoning_Codes_Mapping from Lands_Vectors
GO

ALTER TABLE Zoning_Codes_Mapping
ADD Zoning_Code_int INT IDENTITY(1,1)


--6
----Table to map BD_LINE_1_Quality---
select DISTINCT BD_LINE_1_Quality__Class___Shap
into BD_LINE_1_Quality__Class___Shap_Mapping from Lands_Vectors
GO

ALTER TABLE BD_LINE_1_Quality__Class___Shap_Mapping
ADD BD_LINE_1_Quality__Class___Shap_int INT IDENTITY(1,1)

--7
----Table to map City---
select DISTINCT City
into City_Mapping from Lands_Vectors
GO

ALTER TABLE City_Mapping
ADD City_int INT IDENTITY(1,1)

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

ALTER TABLE Lands_Vectors
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
from Lands_Vectors l
inner join Directions_Mapping d on l.SA_Direction = d.Direction
GO

update Lands_Vectors
set SA_Direction_int = 1 
where SA_Direction is null
GO

--2
update l set l.MA_Direction_int = d.Direction_int
from Lands_Vectors l
inner join Directions_Mapping d on l.MA_Direction = d.Direction
GO

update Lands_Vectors
set MA_Direction_int = 1 
where MA_Direction is null
GO


--3
update l set l.Zoning_Code_int = z.Zoning_Code_int
from Lands_Vectors l
inner join Zoning_Codes_Mapping z on l.Zoning_Code = z.Zoning_Code
GO

--4
update l set l.SA_Localization_int = lm.SA_Street_and_City_and_State_int
from Lands_Vectors l
inner join Localization_SA_Mapping lm on l.SA_Street_and_City_and_State = lm.SA_Street_and_City_and_State
GO

update Lands_Vectors
set SA_Localization_int = 0 
where SA_Localization_int is null
GO


--5
update l set l.MA_Localization_int = lm.MA_Street_and_City_and_State_int
from Lands_Vectors l
inner join Localization_MA_Mapping lm on l.MA_Street_and_City_and_State = lm.MA_Street_and_City_and_State
GO

update Lands_Vectors
set MA_Localization_int = 0 
where MA_Localization_int is null
GO


--6
update l set l.Simple_Zone_int = s.Simple_Zone_int
from Lands_Vectors l
inner join Simple_Zones_Mapping s on l.Simple_Zoning_Code = s.Simple_Zoning_Code
GO

update Lands_Vectors
set Simple_Zone_int = 1 
where Simple_Zone_int is null
GO

--7
update l set l.BD_LINE_1_Quality__Class___Shap_int = m.BD_LINE_1_Quality__Class___Shap_int
from Lands_Vectors l
inner join BD_LINE_1_Quality__Class___Shap_Mapping m on l.BD_LINE_1_Quality__Class___Shap = m.BD_LINE_1_Quality__Class___Shap
GO

update Lands_Vectors
set BD_LINE_1_Quality__Class___Shap_int = 0 
where BD_LINE_1_Quality__Class___Shap_int is null
GO

--8
update l set l.City_int = c.City_int
from Lands_Vectors l
inner join City_Mapping c on l.City = c.City
GO


------Droping columns with string values from Lands_Vectors -----
ALTER TABLE Lands_Vectors
DROP COLUMN 
SA_Direction, SA_Street_Name, SA_City_and_State, 
MA_Direction, MA_Street_Name, MA_City_and_State,
Zoning_Code, BD_LINE_1_Quality__Class___Shap,
SA_Street_and_City_and_State, MA_Street_and_City_and_State, City, Simple_Zoning_Code


select * from Lands_Vectors









------Mapping NULL values into numbers----------
--columns with null values: Use_Cde and BD_LINE_1_Design_Type

--only 4 records 21.07.2018
DELETE FROM Lands_Vectors
WHERE Use_Cde is null;

--around 11 thousand records -> update:
 UPDATE Lands_Vectors
 set BD_LINE_1_Design_Type = 0000 where BD_LINE_1_Design_Type is null
 GO
-------


--do csv ObjectID;PERIMETERLS2_Sale_Date;LS3_Sale_Date;BD_LINE_1_Subpart;BD_LINE_1_Design_Type;BD_LINE_1_Yr_Built;BD_LINE_1_No_of_Units;BD_LINE_1_No_of_Bedrooms;BD_LINE_1_No_of_Baths;BD_LINE_1_Sq_Ft_of_Main_Improve;BD_LINE_2_Yr_Built;BD_LINE_2_No_of_Units;BD_LINE_2_No_of_Bedrooms;BD_LINE_2_No_of_Baths;BD_LINE_2_Sq_Ft_of_Main_Improve;Current_Land_Base_Year;Current_Improvement_Base_Year;Current_Land_Base_Value;Current_Improvement_Base_Value;Cluster_Location;Cluster_Type;Cluster_Appraisal_Unit;Document_Transfer_Tax_Sales_Amo;BD_LINE_1_Year_Changed;BD_LINE_1_Unit_Cost_Main;BD_LINE_1_RCN_Main;BD_LINE_2_Year_Changed;BD_LINE_2_Unit_Cost_Main;BD_LINE_2_RCN_Main;Landlord_Reappraisal_Year;Landlord_Number_of_Units;Price_Per_Area;Area;SA_Localization_int;MA_Localization_int;MA_Direction_int;SA_Direction_int;Simple_Zone_int;Zoning_Code_int;BD_LINE_1_Quality__Class___Shap_int;City_int

IMPROVE_Curr_Value;SA_Zip_Cde;Recording_Date;Use_Cde;

---Move LS1_Sale_Amount column to the end, rename it

alter table Lands_Vectors
add Sale_Amount int 

update Lands_Vectors set Sale_Amount = LS1_Sale_Amount

select LS1_Sale_Amount, Sale_Amount from Lands_Vectors


alter table Lands_Vectors
drop column LS1_Sale_Amount

---

select * from Lands_Vectors 
order by Sale_Amount 

