express = require('express');
var router = express.Router();

/* GET html. */
router.get('/', function(req, res, next) {
  res.render("./html/map.html");
});

module.exports = router;
