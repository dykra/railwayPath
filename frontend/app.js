var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var reglue = require('reglue');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var javascriptRouter = require('./routes/javascript');

var app = express();

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.engine('tjs', reglue.build);

app.use('/', indexRouter);
app.use('/javascript', javascriptRouter);
app.use('/users', usersRouter);
app.get('/test', function(req, res){
  res.send('test');
});

module.exports = app;