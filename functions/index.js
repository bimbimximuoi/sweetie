const functions = require('firebase-functions');
const { createProxyMiddleware } = require('http-proxy-middleware');
const express = require('express');

const app = express();
const apiProxy = createProxyMiddleware({
  target: 'http://127.0.0.1:4000',
  changeOrigin: true
});

app.use('/', apiProxy);


exports.app = functions.runWith({
    timeoutSeconds: 300,
    memory: '1GB'
  }).https.onRequest(app);