const express = require("express");
var cors = require('cors')
const app = express();
const port = 1337;

app.use(cors())
const parser = require('body-parser');
const urlencodedParser = parser.urlencoded({extended : false});
// before your routes
app.use(parser .json());
app.use(urlencodedParser)

app.get("/", (req, res) => {
    res.json({
        "/": "Shows a list of all possible routes that are used.",
        "/data": "Shows a list of all possible dependent components.",
        "/data?keyword=keyword": "Shows components that contain the specific keyword.",
        "/componentinfo": "Shows information about the component being analyzed.",
        "/graph": "Shows a list of all filtered dependent components.",
        "/graph/basedir": "Shows only the root directory of all filtered dependent components.",
    });
});

app.get("/data", (req, res) => {
    const itemsfile = require("../data/final_dependencies.json");
    let result = [{"Message": "Data loading..."}];

    maxQueryParam = Object.keys(req.query).length;

    switch (maxQueryParam) {
        case 1:
            if (req.query.keyword) {
                console.log("Searching for dependency containing: "+req.query.keyword+" in the data.");

                result = itemsfile.filter(item => 
                    item.base_dir.includes(req.query.keyword));
                
            } 
            break;
    
        default:
            console.log("Fetching all data")
            result = itemsfile
            break;
    }
    res.json(result);
});

app.get("/componentinfo", (req, res) => {
    const keyfile = require("../data/key.json");
    let result = [{"Message": "Data loading..."}];

    console.log("Fetching the component's info")
    result = keyfile
    res.json(result);
});

app.get("/graph/:type?", (req, res) => {
    const itemsfile = require("../data/data.json");
    let result = [{"Message": "Data loading..."}];

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