const functions = require('firebase-functions');
const admin = require('firebase-admin');
const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const app = express();

const serviceAccountPath = path.join(__dirname, 'serviceAccountkey.json');
const scriptPath = path.join(__dirname, 'main.py');

admin.initializeApp({
    credential: admin.credential.cert(require(serviceAccountPath)),
    storageBucket: 'pthuy-50c34.appspot.com'
});

app.get('/*', (req, res) => {
  const childPython = spawn('python3', [scriptPath]);

  let dataToSend = '';

  childPython.stdout.on('data', (data) => {
    dataToSend += data.toString();
  });

  childPython.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    res.status(500).send(data.toString());
  });

  childPython.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    res.send(dataToSend);
  });
});

exports.app = functions.https.onRequest(app);
