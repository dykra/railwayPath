
ALTER PROCEDURE dbo.getTrainingDataPriceEstimation
    @LimitDate nvarchar(30),
    @BucketType nvarchar(30),
    @ExcludedList nvarchar(MAX)
AS
SELECT Price_Group
FROM FILTERED_PARCEL
WHERE LS1_Sale_Date > @LimitDate
      AND Price_Group LIKE @BucketType AND
      LS1_Sale_Amount not in (SELECT value FROM STRING_SPLIT(@ExcludedList, ';'))
GO


-- EXEC dbo.getTrainingDataPriceEstimation @LimitDate = '20150000', @BucketType="cheap", @list='0;9'
