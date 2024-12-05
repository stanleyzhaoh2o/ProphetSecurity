const express = require('express');
const app = express();
const PORT = 3000;

// Sample titles for investigations
const investigationTitles = [
    "Suspicious Login Attempts",
    "Malicious Process Execution",
    "Unusual Network Behavior",
    "Unauthorized Access Detected",
    "Potential Data Exfiltration",
    "Anomalous User Activity",
    "Security Policy Violation",
    "Irregular Application Traffic",
    "Ransomware Attack Indicators",
    "Elevated Risk of Phishing"
];

// Sample first and last names for analysts
const firstNames = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Robin", "Drew", "Cameron"];
const lastNames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"];

// Function to generate a random analyst name
function generateAnalystName() {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    return `${firstName} ${lastName}`;
}

// Function to generate a random date within the last two weeks
function randomDateWithinLastTwoWeeks() {
    const now = new Date();
    const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
    return new Date(twoWeeksAgo.getTime() + Math.random() * (now.getTime() - twoWeeksAgo.getTime()));
}

function generateInvestigation(id) {
    const alertFiredTimestamp = randomDateWithinLastTwoWeeks();
    const lastUpdatedTimestamp = new Date(alertFiredTimestamp.getTime() + Math.random() * (7 * 24 * 60 * 60 * 1000)); // Up to 7 days after alert

    const determination = ['True positive', 'False positive', 'In progress', 'Closed'][Math.floor(Math.random() * 4)];
    let severity;
    switch (determination) {
        case 'False positive':
            // False positives are generally not critical
            severity = 'Low'
            break;
        case 'True positive':
            // True positives can be of any severity
            severity = ['Low', 'Medium', 'High', 'Critical'][Math.floor(Math.random() * 4)];
            break;
        default:
            // For other cases, choose any severity
            severity = ['Low', 'Medium', 'High', 'Critical'][Math.floor(Math.random() * 4)];
            break;
    }

    return {
        id: id,
        title: investigationTitles[Math.floor(Math.random() * investigationTitles.length)],
        source: ['AWS', 'Azure', 'Crowdstrike', 'SentinelOne', 'Okta'][Math.floor(Math.random() * 5)],
        alertFiredTimestamp: alertFiredTimestamp.toISOString(),
        lastUpdatedTimestamp: lastUpdatedTimestamp.toISOString(),
        severity,
        analystAssigned: generateAnalystName(),
        determination,
        readyForReview: ['Yes', 'No'][Math.floor(Math.random() * 2)]
    };
}

// Function to generate random investigations with realistic logic
function generateInvestigations() {
    const investigations = [];
    for (let i = 0; i < 1000; i++) {
        let investigation = generateInvestigation(i)
        investigations.push(investigation)
    }
    return investigations;
}

let investigations = generateInvestigations();

// Schedule new investigations to be added every few minutes
const newInvestigationInterval = 10 * 1000; // ~10 seconds, for example
setInterval(function () {
    let investigation = generateInvestigation(Math.floor(Math.random() * 5000) + 1000)
    investigations.push(investigation)
    console.log(`Adding new investigation: ${investigation.id}`)
}, newInvestigationInterval);


// GET /investigations route
app.get('/investigations', (req, res) => {
    // Introduce a 1% chance to fail with a 500 error
    if (Math.random() < 0.01) {
        res.status(500).send('Internal Server Error');
        return;
    }

    const { source, severity, determination, page = 1 } = req.query;
    const id = parseInt(req.query.id);
    const pageSize = 10;
    console.log(id)
    console.log(source)

    let results = investigations.filter(inv => {
        return (!source || inv.source === source) &&
            (!severity || inv.severity === severity) &&
            (!id || inv.id === id) &&
            (!determination || inv.determination === determination);
    });

    // Pagination
    const paginatedResults = results.slice((page - 1) * pageSize, page * pageSize);

    res.json(paginatedResults);
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
