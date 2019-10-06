-- =============================================
-- Object:  Index [R56_pk]
-- =============================================
ALTER TABLE PARCEL ADD  CONSTRAINT [R56_pk] PRIMARY KEY CLUSTERED 
(
	[OBJECTID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 75) ON [PRIMARY]
GO

-- =============================================
-- Object:  Constraint [[g51_ck]]
-- =============================================
ALTER TABLE PARCEL  WITH CHECK ADD  CONSTRAINT [g51_ck] CHECK  (([SHAPE].[STSrid]=(2229)))
GO

ALTER TABLE PARCEL CHECK CONSTRAINT [g51_ck]
GO

SET ARITHABORT ON
SET CONCAT_NULL_YIELDS_NULL ON
SET QUOTED_IDENTIFIER ON
SET ANSI_NULLS ON
SET ANSI_PADDING ON
SET ANSI_WARNINGS ON
SET NUMERIC_ROUNDABORT OFF
GO

-- =============================================
-- Object:  Index [S51_idx]
-- =============================================
CREATE SPATIAL INDEX [S51_idx] ON PARCEL
(
	[Shape]
)USING  GEOMETRY_AUTO_GRID 
WITH (BOUNDING_BOX =(6275487.79, 1384146.14, 6668480.77, 2122084.6), 
CELLS_PER_OBJECT = 16, PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO


