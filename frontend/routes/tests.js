express = require('express');
var mapRouter = require('./javascripts/map');
var indexRouter = require('./javascripts/index');
var router = express.Router();

/* GET javascript. */
router.get('/', function(req, res, next) {
  res.render("./html/test.html");
});
router.get('/test.js', function(req, res, next) {
  res.render("./test.tjs");
});

module.exports = router;
