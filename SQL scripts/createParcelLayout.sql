﻿
--drop table PARCEL_LAYOUTS_2
CREATE TABLE PARCEL_LAYOUTS_2
(
	OBJECTID INT NOT NULL UNIQUE,
	CENTER_LAT numeric(38,8),
	CENTER_LON numeric(38,8),
	Improve_Curr_Value int,
	LS1_Sale_Date int,
	BD_LINE_1_Sq_Ft_of_Main_Improve int,
	Price_Per_Single_Area_Unit int,
	Parcel_Area int,
	Simple_Zone_int int,
	Price_Group varchar(50),
	Sale_Amount int,
	Estimated_Amount INT,
	--ShapeString varchar(max)
)
GO

BULK INSERT PARCEL_LAYOUTS_2
    FROM 'C:\Magdalena\INZYNIERKA\Parcel_Layout.csv' --tu zmien sciezkę
    WITH
    (
    FIRSTROW = 1,
    FIELDTERMINATOR = ',',  -- CSV field delimiter
    ROWTERMINATOR = '\n',
    ERRORFILE = 'C:\Magdalena\INZYNIERKA\pl_errors.txt', -- tu zmien sciezki
    TABLOCK
    )

ALTER TABLE PARCEL_LAYOUTS_2
ADD ShapeBinary varbinary(max), Shape Geometry 

--	SELECT CAST(@NB AS Geometry)

--declare @t = STGeomFromText(0xB508000001040900000090C2F5B84F62584140E17AD4B8043E413085EBE1566258410048E1BA2C053E4120AE47E14E625841C03D0A5729053E41405F17204B625841C0D8326327053E41A09999594762584100A4703D26053E4110AE47513E6258414085EB9194043E4100295CAF4062584100713D0A8B043E413033339349625841001F856B9E043E4190C2F5B84F62584140E17AD4B8043E4101000000020000000001000000FFFFFFFF0000000003, SRID)

UPDATE PARCEL_LAYOUTS_2 SET ShapeBinary = CONVERT(VARBINARY(max), ShapeString, 1)
FROM PARCEL_LAYOUTS_2 L
GO

select * from PARCEL_LAYOUTS_2

UPDATE PARCEL_LAYOUTS_2 SET Shape = CAST(ShapeBinary AS Geometry)
FROM PARCEL_LAYOUTS_2 L
GO

select * from PARCEL_LAYOUTS_2

DECLARE @g varbinary(max)
SET @g = 0xB508000001040900000090C2F5B84F62584140E17AD4B8043E413085EBE1566258410048E1BA2C053E4120AE47E14E625841C03D0A5729053E41405F17204B625841C0D8326327053E41A09999594762584100A4703D26053E4110AE47513E6258414085EB9194043E4100295CAF4062584100713D0A8B043E413033339349625841001F856B9E043E4190C2F5B84F62584140E17AD4B8043E4101000000020000000001000000FFFFFFFF0000000003

SELECT CAST(@g AS Geometry)

SELECT @g-- .ToString(); 


select * from Simple_Zones_Mapping

select * from PARCEL_LAYOUTS_2


ALTER TABLE PArcel_Layouts_2 DROP COLUMN Shape, ShapeBinary, ShapeString

select * from PARCEL_LAYOUTS_2

select * from PARCEL_LAYOUTS_2