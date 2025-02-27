const port = 18082;
const express = require('express');
const app = express();
const cors = require('cors');

app.use(cors())
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


const blindsController = require('./controllers/blind');
const liftUpDownBlinds = require('./controllers/liftUpDownBlinds');



app.post('/registerBlinds', blindsController.registerBlinds);
app.get('/getBlinds', blindsController.getBlinds);
app.post('/liftUpDownBlinds', liftUpDownBlinds.sendLiftUpDownCommand);


app.use(express.static("otherpieces/blinds-web/out"));

// For parsing application/x-www-form-urlencoded



app.listen(port, () => {
    console.log(`server listening on port ${port}`)
})