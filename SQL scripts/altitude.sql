

-- table dbo.conf contains configuration of the altitudes net, that is calculated once, required to make altitudes calculating O(1)
CREATE TABLE dbo.conf
   (netsize int NOT NULL, south float NOT NULL, north float NOT NULL, east float NOT NULL, west float NOT NULL,
    xcoordsstep float NOT NULL, ycoordsstep float NOT NULL, xsidelength int NOT NULL, ysidelength int NOT NULL)

-- table dbo.altitudesNet contains net of altitudes (numbers start from lower left corner and go right, end on upper right corner
CREATE TABLE dbo.altitudesNet
   (number int NOT NULL, altitude float NOT NULL)

-- type required to pass information about net cell to functions
CREATE TYPE [dbo].[PointsToGetAltitude] AS TABLE(
	[number] [int] NULL,
	[altitude] [float] NULL,
	[longitude] [float] NULL,
	[latitude] [float] NULL
)

GO

--
-- INPUT
--    @plon - longitude of point checked
--    @plat - latitude of point checked
-- OUTPUT
--    @points - table containing 4 points
--              each point that is in the part of the world covered by net has it's square
--              table points contains four corners of such square
--
-- function calculates number of square in which the point is based on dbo.conf table,
--   then returns proper points from net - 4 corners of such square
CREATE FUNCTION [dbo].[getSquaresFromPoints]
(
	@plon float,
	@plat float
)
RETURNS @points TABLE
(
	-- Add the column definitions for the TABLE variable here
	number int,
	altitude float,
	longitude float,
	latitude float
)
AS
BEGIN
	-- Fill the table variable with the rows for your result set
	-- Declare the return variable here
	declare @x int, @y int,@xf float, @yf float,  @west float, @south float, @xcc float, @ycc float,
		@xSideLen int, @ySideLen int, @number int, @altitude float

	-- Add the T-SQL statements to compute the return value here
	select @west = west, @south = south, @xcc = xCoordsStep, @ycc = yCoordsStep, @xSideLen = xSideLength, @ySideLen = ySideLength
	from dbo.conf
	select @xf = (@plon - @west)/@xcc, @yf = (@plat - @south)/@ycc
	select @x = FLOOR(@xf), @y = FLOOR(@yf)
	select @number = @xSideLen * @y + @x

	INSERT @points
	select number, altitude , @west + @xcc * (number % @xSideLen) as 'longitude', @south + @ycc * (number/@xSideLen) as 'latitude'
	from dbo.altitudesNet
	where number = @number or number = @number + 1 or number = @number + @xSideLen or number = @number + @xSideLen + 1

	RETURN
END

GO

--
-- INPUT
--    @points - four corners of net square
--    @plon - longitude of point checked
--    @plat - latitude of point checked
-- OUTPUT
--     altitude of point (@plat, @plon)
--
-- function uses bilinear interpolation to estimate altitude of point (@plat, @plon) based on
--    four corners of square in which this point is
CREATE FUNCTION interpolateAltitude(@Points PointsToGetAltitude READONLY, @plat float, @plon float)
RETURNS float
AS
BEGIN
	declare @x1 float, @y1 float, @x2 float, @y2 float, @fx1y1 float, @fx1y2 float, @fx2y1 float, @fx2y2 float
	declare @xdif float, @xinvdif float, @ydif float, @yinvdif float

-- get first point from @Points table
	select top 1 @fx1y1 = altitude, @x1 = longitude, @y1 = latitude
	from (
		select top 1 *
		from (
			select top 1 number, altitude, longitude, latitude
			from @Points
		) p
		order by p.number desc
	) t
-- get second point from @Points table
	select top 1 @fx2y1 = altitude--, @x2 = longitude, @y1 = latitude
	from (
		select top 1 *
		from (
			select top 2 number, altitude, longitude, latitude
			from @Points
		) p
		order by p.number desc
	) t
-- get third point from @Points table
	select top 1 @fx1y2 = altitude--, @x1 = longitude, @y2 = latitude
	from (
		select top 1 *
		from (
			select top 3 number, altitude, longitude, latitude
			from @Points
		) p
		order by p.number desc
	) t

-- get fourth point from @Points table
	select top 1 @fx2y2 = altitude, @x2 = longitude, @y2 = latitude
	from (
		select top 1 *
		from (
			select top 4 number, altitude, longitude, latitude
			from @Points
		) p
		order by p.number desc
	) t

-- Lines below do look terrible, but are readable. They could be even written inline, but it's not a gooe idea
	select @xdif = @x1 - @x2, @xinvdif = @x2 - @x1, @ydif = @y1 - @y2, @yinvdif = @y2 - @y1

	declare @a0 float, @a1 float, @a2 float, @a3 float
	declare @a01 float, @a02 float, @a03 float, @a04 float
	declare @a11 float, @a12 float, @a13 float, @a14 float
	declare @a21 float, @a22 float, @a23 float, @a24 float
	declare @a31 float, @a32 float, @a33 float, @a34 float

	select @a01 = (@fx1y1 * @x2 * @y2)/(@xdif * @ydif) , @a02 = (@fx1y2 * @x2 * @y1)/(@xdif * @yinvdif)
	select @a03 = (@fx2y1 * @x1 * @y2)/(@xdif * @yinvdif) , @a04 = (@fx2y2 * @x1 * @y1)/(@xdif * @ydif)
	select @a11 = (@fx1y1 * @y2)/(@xdif * @yinvdif) , @a12 = (@fx1y2 * @y1)/(@xdif * @ydif)
	select @a13 = (@fx2y1 * @y2)/(@xdif * @ydif) , @a14 = (@fx2y2 * @y1)/(@xdif * @yinvdif)
	select @a21 = (@fx1y1 * @x2)/(@xdif * @yinvdif) , @a22 = (@fx1y2 * @x2)/(@xdif * @ydif)
	select @a23 = (@fx2y1 * @x1)/(@xdif * @ydif) , @a24 = (@fx2y2 * @x1 )/(@xdif * @yinvdif)
	select @a31 = (@fx1y1)/(@xdif * @ydif) , @a32 = (@fx1y2)/(@xdif * @yinvdif)
	select @a33 = (@fx2y1)/(@xdif * @yinvdif) , @a34 = (@fx2y2)/(@xdif * @ydif)

	select @a0 = @a01 + @a02 + @a03 + @a04
	select @a1 = @a11 + @a12 + @a13 + @a14
	select @a2 = @a21 + @a22 + @a23 + @a24
	select @a3 = @a31 + @a32 + @a33 + @a34
	declare @resultAltitude float
	select @resultAltitude = @a0 + @a1 * @plon + @a2 * @plat + @a3 * @plon * @plat

	RETURN @resultAltitude
END

GO

-- INPUT
--    @plon - longitude of point checked
--    @plat - latitude of point checked
-- OUTPUT
--     altitude of point (@plat, @plon)
--
-- function returning altitude, it's called by backend server, it calls other SQL functions
--    (something like "endpoint" here)
CREATE FUNCTION dbo.getAltitudeFromCoordinates
(
	@lat float,
	@lon float
)
RETURNS float
AS
BEGIN
	declare @points dbo.PointsToGetAltitude

	INSERT INTO @points (number, altitude, longitude, latitude)
	select number, altitude, longitude, latitude
	from dbo.getSquaresFromPoints(@lon, @lat)

	RETURN dbo.interpolateAltitude(@points, @lat, @lon)

END
GO


-- parses points from string to table
-- input format: <altitude><comma><longitude><comma><latitude><semicolon> for each point
-- In this version of SQL I haven't found anything better
CREATE FUNCTION [dbo].[getTableFromAltitudesString]
(
	@data varchar(max)
)
RETURNS @points TABLE
(
	-- Add the column definitions for the TABLE variable here
	altitude float,
	longitude float,
	latitude float
)
AS
BEGIN

  DECLARE @singlePoint VARCHAR(500);
  DECLARE @singleValueInside VARCHAR(500);
  DECLARE @charSpliter CHAR;
  DECLARE @charSpliterInside CHAR;
  DECLARE @altitude FLOAT;
  DECLARE @latitude float;
  DECLARE @longitude float;


-- I beg you don't make me comment the code below. It works. If you need to understand this just read it 1000 times and will be fine.
  SET @charSpliter = ';'
  SET @charSpliterInside = ','
  WHILE CHARINDEX(@charSpliter, @data) > 0
  BEGIN
    SET @singlePoint = SUBSTRING(@data, 0, CHARINDEX(@charSpliter, @data))
    SET @data = SUBSTRING(@data, CHARINDEX(@charSpliter, @data) + 1, LEN(@data))

    SET @altitude = 0
    SET @latitude = 0
    SET @longitude = 0
    WHILE CHARINDEX(@charSpliterInside, @singlePoint) > 0
    BEGIN
      SET @singleValueInside = SUBSTRING(@singlePoint, 0, CHARINDEX(@charSpliterInside, @singlePoint))
      SET @singlePoint = SUBSTRING(@singlePoint, CHARINDEX(@charSpliterInside, @singlePoint) + 1, LEN(@singlePoint))

      if (@altitude = 0)
      BEGIN
        set @altitude = convert(FLOAT, @singleValueInside)
      END
      ELSE
      BEGIN
        IF (@latitude = 0)
        BEGIN
          set @latitude = convert(FLOAT, @singleValueInside)
        END
        ELSE
        BEGIN
          set @longitude = convert(FLOAT, @singleValueInside)
        END
      END
      --PRINT @singleValueInside

    END
    if (@longitude != 0)
      BEGIN
        INSERT @points(altitude, latitude, longitude)
        select @altitude, @latitude, @longitude
      END


  END
  RETURN
END


-- calls dbo.getAltitudeFromCoordinates for each point in list passed via @pointsString
--    and parsed in dbo.getTableFromAltitudesString
CREATE FUNCTION dbo.getAltitudesFromCoordinateList
(
	@pointsString varchar(max)
)
RETURNS varchar(max)
AS
BEGIN
  declare @points dbo.PointsToGetAltitude
  declare @otherPoints dbo.PointsToGetAltitude

  insert @points(altitude, latitude, longitude)
  select *
  from [dbo].[getTableFromAltitudesString](@pointsString)

  insert @otherPoints(altitude, latitude, longitude)
  select dbo.getAltitudeFromCoordinates(latitude, longitude) as altitude, latitude, longitude
  from @points


  DECLARE @tmpAltitude float,@tmpLongitude float, @tmpLatitude float
  DECLARE @finalString varchar(max)
  set @finalString = ''

  DECLARE MY_CURSOR CURSOR
    LOCAL STATIC READ_ONLY FORWARD_ONLY
  FOR
  SELECT altitude, longitude, latitude
  FROM @otherPoints

  OPEN MY_CURSOR
  FETCH NEXT FROM MY_CURSOR INTO @tmpAltitude, @tmpLongitude, @tmpLatitude

  WHILE @@FETCH_STATUS = 0
  BEGIN
--       select @tmpAltitude, @tmpLongitude, @tmpLatitude
      set @finalString += 'latitude:' + CONVERT (VARCHAR(50), @tmpLatitude,3) + ','
      set @finalString += 'longitude:' + CONVERT (VARCHAR(50), @tmpLongitude,3) + ','
      set @finalString += 'altitude:' + CONVERT (VARCHAR(50), @tmpAltitude,3) + ';'
      FETCH NEXT FROM MY_CURSOR INTO @tmpAltitude, @tmpLongitude, @tmpLatitude
  END
  CLOSE MY_CURSOR
  DEALLOCATE MY_CURSOR

  RETURN @finalString
END
