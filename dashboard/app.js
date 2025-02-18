/*
  * This is a simple Express server that proxies requests to the ETF API.
  * It also serves a static HTML file and any other static files in the
  * current directory.
  */

const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require('path');

const app = express();

const etfProxy = createProxyMiddleware({
  target: "http://fundgz.1234567.com.cn",
  changeOrigin: true, // Required for CORS to work
  pathRewrite: {
    "/([^/]+)": "/js/$1.js", // /etf/[fundcode] -> /js/[fundcode].js
  },
  on: {
    proxyReq: (proxyReq, req) => {
      //console.log("Proxying request to:", proxyReq.path); // Log the outgoing path
    },
  },
});

app.use("/etf", etfProxy); // All requests to /etf will be proxied

// Serve your HTML file (important!)
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'myindex.html')); // Adjust path if needed
});

// Serve static files (if you have any CSS, images, etc.)
app.use(express.static(path.join(__dirname, '.'))); // Serve files from the current directory

app.listen(8300, () => {
  console.log("ETF Query proxy server listening on port 8300");
});
