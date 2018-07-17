
-- NEW COLUMNS
ALTER TABLE dbo.filtered_parcel
ADD pieceNumber int

ALTER TABLE dbo.filtered_parcel
ADD neighbours_str


--------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------
-- FUNCTIONS


USE [LosAngelesCounty]
GO

/****** Object:  UserDefinedFunction [dbo].[getPartNumber]    Script Date: 2018-07-17 11:52:02 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


-- =============================================
-- Author:		<Dawid Tomasiewicz>
-- Create date: <17.07.2018>
-- Description:	<Returns number of part of our map model>
-- =============================================
CREATE FUNCTION [dbo].[getPartNumber]
(
	-- Add the parameters for the function here
	@centerLat float,
	@centerLon float,
	@latCoefficient float,
	@lonCoefficient float,
	@lonWestBase float,
	@latSouthBase float,
	@numberOfPieces int


)
RETURNS int
AS
BEGIN
	-- Declare the return variable here
	DECLARE @result int
	DECLARE @x int
	DECLARE @y int

	-- Add the T-SQL statements to compute the return value here
	SELECT @x = FLOOR((@centerLon - @lonWestBase)/@lonCoefficient)
	SELECT @y = FLOOR((@centerLat - @latSouthBase)/@latCoefficient)
	SELECT @result = @numberOfPieces * @y + @x

	-- Return the result of the function
	RETURN @result

END
GO


USE [LosAngelesCounty]
GO

/****** Object:  UserDefinedFunction [dbo].[getPartNeighbours]    Script Date: 2018-07-17 11:52:56 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date, ,>
-- Description:	<Description, ,>
-- =============================================
CREATE FUNCTION [dbo].[getPartNeighbours]
(
	-- Add the parameters for the function here
	@partNumber int,
	@numberOfPieces int

)
RETURNS varchar(255)
AS
BEGIN
	-- Declare the return variable here
	DECLARE @result varchar(255)
	DECLARE @mode varchar(255) = 'center'

	if (@partNumber % @numberOfPieces = 0)
	BEGIN
		SELECT @mode = 'left'
	END

	if (@partNumber < @numberOfPieces)
	BEGIN
		SELECT @mode='bottom'
	END

	if ((@partNumber + 1) % @numberOfPieces = 0)
	BEGIN
		SELECT @mode = 'right'
	END

	if (@partNumber >= @numberOfPieces * (@numberOfPieces - 1))
	BEGIN
		SELECT @mode='top'
	END
	SELECT @result = ''
	if (@mode = 'center')
	BEGIN
		SELECT @result += CAST(@partNumber - @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces + 1 as varchar(10))
	END

	if (@mode = 'top')
	BEGIN
		SELECT @result += CAST(@partNumber - @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + 1 as varchar(10))
	END

	if (@mode = 'bottom')
	BEGIN
		SELECT @result += CAST(@partNumber - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces + 1 as varchar(10))
	END

	if (@mode = 'left')
	BEGIN
		SELECT @result += CAST(@partNumber - @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces + 1 as varchar(10))
	END

	if (@mode = 'right')
	BEGIN
		SELECT @result += CAST(@partNumber - @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - @numberOfPieces as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces - 1 as varchar(10))
		SELECT @result += ','
		SELECT @result += CAST(@partNumber + @numberOfPieces as varchar(10))
	END


	-- Add the T-SQL statements to compute the return value here


	-- Return the result of the function
	RETURN @result

END
GO

--------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------
-- actual script
declare @count int, @density int, @northwestLat float, @northwestLon float, @southeastLat float, @southeastLon float;
declare @parcelsInPart int = 80
declare @lonCoefficient float, @latCoefficient float, @numberOfPieces float
declare @partNumber int;

SELECT @count = count(*), @density = count(*)/@parcelsInPart
FROM dbo.FILTERED_PARCEL

select top 1 @northwestLon = center_lon
from dbo.FILTERED_PARCEL
where CENTER_X != 0 and CENTER_Y != 0
order by CENTER_LON --desc

select top 1 @southeastLon = center_lon
from dbo.FILTERED_PARCEL
where CENTER_X != 0 and CENTER_Y != 0
order by CENTER_LON desc

select top 1 @southeastLat = center_lat
from dbo.FILTERED_PARCEL
where CENTER_X != 0 and CENTER_Y != 0
order by center_lat

select top 1 @northwestLat = center_lat
from dbo.FILTERED_PARCEL
where CENTER_X != 0 and CENTER_Y != 0
order by center_lat desc

select @numberOfPieces = CEILING(SQRT(@density))

select @lonCoefficient = (@southeastLon - @northwestLon)/@numberOfPieces
select @latCoefficient = (@northwestLat - @southeastLat)/@numberOfPieces

SELECT @partNumber = dbo.getPartNumber(33.86513816, -118.06924695, @latCoefficient,
						@lonCoefficient, @northwestLon, @southeastLat, @numberOfPieces)

update dbo.FILTERED_PARCEL
set pieceNumber = dbo.getPartNumber(center_lat, center_lon, @latCoefficient,
						@lonCoefficient, @northwestLon, @southeastLat, @numberOfPieces)
where CENTER_X != 0 and CENTER_Y != 0

update dbo.FILTERED_PARCEL
set neighbours_str = dbo.getPartNeighbours(pieceNumber, @numberOfPieces)
where CENTER_X != 0 and CENTER_Y != 0