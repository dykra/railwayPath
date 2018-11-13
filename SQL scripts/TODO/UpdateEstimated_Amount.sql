

CREATE TABLE ESTIMATED_PRICES
(
	ID INT,
	Estimated_Amount INT
)
GO


BULK INSERT ESTIMATED_PRICES
    FROM 'C:\Magdalena\INZYNIERKA\estimated_prices.csv'
    WITH
    (
    FIRSTROW = 1,
    FIELDTERMINATOR = ',',  -- CSV field delimiter
    ROWTERMINATOR = '\n',
    ERRORFILE = 'C:\Magdalena\INZYNIERKA\estimated_prices_errors.txt',
    TABLOCK
    )

	UPDATE PARCEL_VECTORS SET PARCEL_VECTORS.Estimated_Amount = E.Estimated_Amount, Row_Version_Stamp = Row_Version_Stamp + 1
	FROM PARCEL_VECTORS P
	INNER JOIN ESTIMATED_PRICES E
	ON P.OBJECTID = E.ID;
	GO

	UPDATE PARCEL_VECTORS SET Estimated_Amount = P.Sale_Amount, Row_Version_Stamp = Row_Version_Stamp + 1
	FROM PARCEL_VECTORS P
	WHERE Estimated_Amount is null
	GO

SELECT 
	P.OBJECTID, CENTER_LAT, CENTER_LON, V.Improve_Curr_Value, V.LS1_Sale_Date, V.BD_LINE_1_Sq_Ft_of_Main_Improve, 
	Price_Per_Single_Area_Unit, Parcel_Area, Simple_Zone_int, 
	Price_Group, Sale_Amount, Estimated_Amount, P.Shape
INTO Parcel_Layout
	FROM PARCEL_VECTORS V
	INNER JOIN PARCEL P
	ON P.OBJECTID = V.OBJECTID

CREATE CLUSTERED INDEX center_lat_index ON dbo.Parcel_Layout(CENTER_LAT)
CREATE NONCLUSTERED INDEX center_lon_index ON dbo.Parcel_Layout(CENTER_LON)