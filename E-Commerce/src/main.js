import express from 'express'; // for ESM (EcmaScript Module)
// const express = require('express'); // for CJS (Common JS Modle)
// as your package type by default it is CJS

const app = express();
const port = 3000;

app.use(express.urlencoded({extended:true}));
app.use(express.json());

app.get('/', (req, res) => {
    res.send("Hello world !")
})
app.listen(port, () => {
    console.log(`Server is running at: http://localhost:${port}`);
});