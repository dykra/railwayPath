-- =============================================
-- CREATE NEW TABLE FILTERED_PARCEL
-- not interested values are dropped
-- =============================================

BEGIN TRAN

SELECT  *
INTO FILTERED_PARCEL FROM PARCEL
WHERE LS1_Sale_Date > 20150000
      and LS1_Sale_Amount != 9
      and LS1_Sale_Amount != 0
      and LS1_Sale_Amount != 999999999


DELETE FROM FILTERED_PARCEL
WHERE Zoning_Code IS NULL

COMMIT TRAN;


-- =============================================
-- Get data from Zoning_Code column
-- Adding and filling new column Simple_Zoning_Code
-- Adding and filling new column City
-- =============================================

ALTER TABLE FILTERED_PARCEL
  ADD Simple_Zoning_Code NVARCHAR(15)
    DEFAULT NULL
GO

ALTER TABLE FILTERED_PARCEL
  ADD City NVARCHAR(5)
GO

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code=substring(Zoning_Code,3,1)

UPDATE FILTERED_PARCEL
  SET City=substring(Zoning_Code,1,2)


-- =============================================
-- Get data from connected to parcel area
-- data from Shape geometry column
-- =============================================


ALTER TABLE FILTERED_PARCEL
  ADD Price_Per_Single_Area_Unit INT
GO

ALTER TABLE FILTERED_PARCEL
  ADD Parcel_Area INT
GO

UPDATE FILTERED_PARCEL
  SET Parcel_Area=Shape.STArea()

UPDATE FILTERED_PARCEL
  SET Price_Per_Single_Area_Unit=(LS1_Sale_Amount/(Parcel_Area+1))


-- =============================================
-- ADD NEW COLUMNS FOR BASIC AREAS TYPES
-- ============================================= to jest dodatkowe

ALTER TABLE FILTERED_PARCEL
  ADD Residential SMALLINT
GO

ALTER TABLE FILTERED_PARCEL
    ADD Special_Purposes_Plan SMALLINT
GO

ALTER TABLE FILTERED_PARCEL
  ADD Agricultural SMALLINT
GO

ALTER TABLE FILTERED_PARCEL
  ADD Commercial SMALLINT
GO

ALTER TABLE FILTERED_PARCEL
  ADD Manufacturing SMALLINT
GO


-- =============================================
-- Parse Zoning codes
-- RESIDENTIAL
-- R1 - single family residence
-- R2 - two family residence
-- R3 - limited multiple residence
-- =============================================

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R1'
    WHERE substring(Zoning_Code, 3, 2) like 'R1'

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code =
    CASE substring(Zoning_Code, 3, 1)
        WHEN 'R' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'R1'
                WHEN '2' THEN 'R2'
                WHEN '3' THEN 'R3'
              END



-- for SCUR1, SCUR2, SCUR3, SCUR4, SCUR5 
UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = substring(Zoning_Code, 4, 2)
    WHERE Zoning_Code like 'SCUR%'


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R2'
    WHERE substring(Zoning_Code, 3, 2) like 'R2'


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R2'
    WHERE Zoning_Code like 'LAMR2';

--

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R3'
    WHERE substring(Zoning_Code, 3, 2) like 'R3';
   

--
--TODO opisac R4 i R5 czym sa

--
UPDATE FILTERED_PARCEL
    SET Residential = (CASE
                       WHEN Simple_Zoning_code IN ('R1', 'R2', 'R3', 'R4', 'R5') THEN 1 ELSE 0 END);

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
                WHEN '3' THEN 'A3' -- TODO A3 co to jest?
              END

        WHEN 'C' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'C1'
                WHEN '2' THEN 'C2'
                WHEN '3' THEN 'C3'
                WHEN '4' THEN 'C4' --TODO C4 co to jest?
              END

        WHEN 'M' THEN
             CASE substring(Zoning_Code, 4, 1)
                WHEN '1' THEN 'M1'
                WHEN '2' THEN 'M2'
                WHEN '3' THEN 'M3'
              END
    END

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
          or Zoning_Code like 'LRCR*'


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


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'SP'
    WHERE Zoning_Code like 'SCSP';


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'RR'
    WHERE substring(Zoning_Code, 3, 3) like 'RR-'    

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PR'
    WHERE substring(Zoning_Code, 3, 3) like 'PR-'


UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PR'
    WHERE Zoning_Code like 'LCPR*'
          or Zoning_Code like 'POPRD*'


UPDATE FILTERED_PARCEL
    SET Special_Purposes_Plan = (CASE
                       WHEN Simple_Zoning_code IN ('SP', 'RR', 'PR') THEN 1 ELSE 0 END);



-- =============================================
-- OTHER TYPES
-- =============================================

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'GAMUO'
    WHERE Zoning_Code like 'GAMUO';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'RBPDR*'
    WHERE Zoning_Code like 'RBPDR*';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'SF?'
    WHERE Zoning_Code like 'PRSF*';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'W1'
    WHERE Zoning_Code like 'LAWC'

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'W2'
    WHERE Zoning_Code like 'LACW'

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PSC?'
    WHERE Zoning_Code like 'PSC-';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'PD1?'
    WHERE Zoning_Code like 'LBPD1';

UPDATE FILTERED_PARCEL
  SET Simple_Zoning_Code = 'R1'
    WHERE Zoning_Code like 'LAMR1'

---------------polecenie które zwraca ilosc roznych kodów - Zoning_Code, których nie udalo sie odszyfrowaæ------------------
SELECT Zoning_Code, simple_zone, count(*) as q from Lands where simple_zone != 'R1' and simple_zone != 'R2' and simple_zone != 'R3' and simple_zone != 'R4' 
and simple_zone != 'R5' and simple_zone != 'R' and simple_zone != 'A1' and simple_zone != 'A2' and simple_zone != 'A3' and simple_zone != 'A4'
and simple_zone != 'C1' and simple_zone != 'C2' and simple_zone != 'C3' and simple_zone != 'RR' and simple_zone != 'M1' and simple_zone != 'C4'
and simple_zone != 'PR' and simple_zone != 'M2' and simple_zone != 'M3' and simple_zone != 'GAMUO' and simple_zone != 'RBPDR*'
and simple_zone !='C5' and simple_zone != 'CM' and simple_zone !='SP' and simple_zone !='SF?' 
and simple_zone !='SP'and simple_zone != 'PSC?'and simple_zone != 'PD1?'and simple_zone != 'W' 
and simple_zone != 'CR' and simple_zone != 'SP' and simple_zone != 'CPD' and simple_zone != 'CR' and simple_zone != 'PR' 
and simple_zone !='LAMR1' and simple_zone !='LACW'
group by Zoning_Code, simple_zone 
order by q desc 
