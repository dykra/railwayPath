

CREATE TABLE PARCEL_LAYOUT
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
	Estimated_Amount INT
)
GO

BULK INSERT PARCEL_LAYOUT
    FROM 'C:\Magdalena\INZYNIERKA\Parcel_Layout_withoutShape.csv' --tu zmien sciezkę
    WITH
    (
    FIRSTROW = 1,
    FIELDTERMINATOR = ',',  -- CSV field delimiter
    ROWTERMINATOR = '\n',
    ERRORFILE = 'C:\Magdalena\INZYNIERKA\plS_errors.txt', -- tu zmien sciezki
    TABLOCK
    )

CREATE CLUSTERED INDEX center_lat_index ON dbo.Parcel_Layout(CENTER_LAT)
CREATE NONCLUSTERED INDEX center_lon_index ON dbo.Parcel_Layout(CENTER_LON)