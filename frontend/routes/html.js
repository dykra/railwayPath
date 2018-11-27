express = require('express');
var mapRouter = require('./htmls/map');
var router = express.Router();

/* GET html. */
router.use('/map', mapRouter);

module.exports = router;
