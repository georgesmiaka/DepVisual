const express = require("express");
const cors = require('cors');
const app = express();
const http = require('http');
const { spawn } = require('child_process');
const WebSocket = require('ws');
const parser = require('body-parser');

const port = 1337;

// WebSocket server setup
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middlewares
app.use(cors());
app.use(parser.json());
app.use(parser.urlencoded({ extended: false }));

// Tracking analysis progress
let analysisProgress = 0;

// Serve the routes as usual
app.get("/", (req, res) => {
    res.json({
        "/": "Shows a list of all possible routes that are used.",
        "/data": "Shows a list of all possible components", 
        "/data?keyword=keyword": "Shows components that contain the specific keyword.",
        "/analyze": "Endpoint that receives the list of components being analyzed.",
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
    analysisProgress = 0;
    // Run the Python analysis script
    const process = spawn('python3', ['../client/dep_analyze.py', JSON.stringify(selectedDocs)]);

    process.stdout.on('data', (data) => {
        analysisProgress += 1;  // Adjust as needed based on actual progress updates
        broadcastProgress(analysisProgress);  // Send updates to all WebSocket clients
        console.log(`Progress: ${data}`);
        console.log(`progress_status: ${analysisProgress}`)
    });

    process.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });

    process.on('close', (code) => {
        analysisProgress = 100;  // Mark completion
        broadcastProgress(analysisProgress);  // Final update
        console.log(`Script completed with code ${code}`);
        res.json({ message: "Analysis complete" });
    });
});

// Broadcast progress to all WebSocket clients
const broadcastProgress = (progress) => {
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({ progress }));
        }
    });
};

// Additional route handlers as needed
app.get("/dependency", (req, res) => {
    // Clear the require cache so that the server reloads new content every time
    // the client calls this api.
    delete require.cache[require.resolve("../data/component_dependencies_filtered.json")];

    // Re-require the file to get the updated content
    const itemsfile = require("../data/component_dependencies_filtered.json");

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

app.get("/graph/:type?", (req, res) => { /* ...route handling code... */ });

// Start the server and WebSocket server
server.listen(port, () => {
    console.log('The server is now listening on port:', port);
});
