-- ================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Magdalena Nowak
-- Create date: 2.10.2018
-- Description:	Function to get price of area (geometry type)
-- =============================================
CREATE FUNCTION ValuationArea
(
	@area geometry
)
RETURNS int
AS
BEGIN
	DECLARE @price int;

	SELECT @price = sum((v.Shape.StIntersection(@area).StArea()/v.Shape.StArea()) * v.PredictedPrice )
	FROM PARCEL_Vectors v
	WHERE p.Shape.STIntersects(@area) = 1
	group by ((v.Shape.StIntersection(@area).StArea()/v.Shape.StArea()) * v.PredictedPrice )
	
	RETURN @price

END
GO

