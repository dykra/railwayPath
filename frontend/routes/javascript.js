express = require('express');
var mapRouter = require('./javascripts/map');
var indexRouter = require('./javascripts/index');
var router = express.Router();

/* GET javascript. */
router.use('/map.js', mapRouter);
router.use('/index', indexRouter);

module.exports = router;
