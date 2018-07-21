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

SELECT Zoning_Code, Simple_Zoning_Code, count(*) as quantity FROM FILTERED_PARCEL
where Simple_Zoning_Code is null
group by Zoning_Code, Simple_Zoning_Code
order by quantity desc



SELECT Zoning_Code, Simple_Zoning_Code, count(*) as quantity FROM FILTERED_PARCEL
group by Zoning_Code, Simple_Zoning_Code
order by quantity desc


select * from FILTERED_PARCEL





