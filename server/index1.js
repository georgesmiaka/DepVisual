const express = require("express");
var cors = require('cors')
const app = express();
const port = 1337;
const { spawn } = require('child_process');

app.use(cors())
const parser = require('body-parser');
const urlencodedParser = parser.urlencoded({ extended: false });
// before your routes
app.use(parser.json());
app.use(urlencodedParser)

// progress tracking variable
let analysisProgress = 0;

app.get("/", (req, res) => {
    res.json({
        "/": "Shows a list of all possible routes that are used.",
        "/data": "Shows a list of all possible components", 
        "/data?keyword=keyword": "Shows components that contain the specific keyword.",
        "/analyze": "Endpoint that receives the list of components being analyzed.",
        "/progress": "Send the analysis progress of the components being examined.",
        "/dependency": "Shows a list of the components being analyzed together with their dependencies.",
    });
});

app.get("/data", (req, res) => {
    const itemsfile = require("../data/component.json");
    let result = [{ "Message": "Data loading..." }];

    maxQueryParam = Object.keys(req.query).length;

    switch (maxQueryParam) {
        case 1:
            if (req.query.keyword) {
                console.log("Searching for dependency containing '" + req.query.keyword + "' in the data.");

                result = itemsfile.filter(item =>
                    item.base_dir.includes(req.query.keyword));

            }
            break;

        default:
            console.log("Fetching the list of all components")
            result = itemsfile
            break;
    }
    res.json(result);
});

app.put('/analyze', async (req, res) => {
    const selectedDocs = req.body;

    if (!selectedDocs || selectedDocs.length === 0) {
        return res.status(400).send("No documents selected for analysis.");
    }

    // Run Python script and track output
    const process = spawn('python3', ['../client/dep_analyze.py', JSON.stringify(selectedDocs)]);

    process.stdout.on('data', (data) => {
        analysisProgress += 10;  // Update as needed based on output from the script
        // Send progress to the client, e.g., via WebSocket, or save to a file/DB the client can poll
        console.log(`Progress: ${data}`);
    });

    process.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });

    process.on('close', (code) => {
        analysisProgress = 100;  // Complete progress on script close
        console.log(`Script completed with code ${code}`);
        res.json({ message: "Analysis complete" });
    });
});

// Add progress endpoint
app.get('/progress', (req, res) => {
    res.json({ progress: analysisProgress });
    console.log(analysisProgress)
});

app.get("/dependency", (req, res) => {
    const itemsfile = require("../data/component_dependencies.json");
    let result = [{ "Message": "Data loading..." }];

    maxQueryParam = Object.keys(req.query).length;

    switch (maxQueryParam) {
        case 1:
            if (req.query.keyword) {
                console.log("Searching for dependency containing: " + req.query.keyword + " in the data.");

                result = itemsfile.filter(item =>
                    item.base_dir.includes(req.query.keyword));

            }
            break;

        default:
            console.log("Fetching list containing the components and their dependencies")
            result = itemsfile
            break;
    }
    res.json(result);
});


app.get("/graph/:type?", (req, res) => {
    const itemsfile = require("../data/data.json");
    let result = [{ "Message": "Data loading..." }];

    // Check if type is 'basedir' or undefined
    if (req.params.type === "basedir") {
        console.log("Fetching the filtered dependencies.");

        result = itemsfile.map((item, index) => {
            // Split the base_dir and take the last two parts
            const baseDirParts = item.base_dir.split("/");
            const shortBaseDir = baseDirParts.slice(-2).join("/");

            // Return the short base_dir as "1", "2", etc.
            return {
                dependency: shortBaseDir,
                used: item.maven_analyse_used
            };
        });
    } else {
        console.log("Fetching all data.");
        result = itemsfile;
    }

    res.json(result);
});


app.listen(port);
console.log('The server is now listening on: ' + port);