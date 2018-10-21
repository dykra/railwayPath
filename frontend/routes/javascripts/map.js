express = require('express');
var router = express.Router();

/* GET javascript. */
router.get('/', function(req, res, next) {
  res.render("./map.tjs");
});

module.exports = router;
