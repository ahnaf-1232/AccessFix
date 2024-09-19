
            // @ts-check
            const { test, expect } = require('@playwright/test');
            const AxeBuilder = require('@axe-core/playwright').default;
            const fileReader = require('fs');

            function escapeCSV(value) {
                if (typeof value === 'string') {
                    value = value.replace(/"/g, '""');
                    if (value.includes(',') || value.includes('\n') || value.includes('\r') || value.includes('"')) {
                        return `"${value}"`;
                    }
                }
                return value;
            }

            function violationsToCSV(violations) {
                const headers = ['id', 'impact', 'tags', 'description', 'help', 'helpUrl', 'nodeImpact', 'nodeHtml', 'nodeTarget', 'nodeType', 'message', 'numViolation'];
                let csvContent = headers.join(',') + '\n';               
                const totalViolations = violations.length; 

                violations.forEach(violation => {
                    violation.nodes.forEach(node => {
                        const nodeImpacts = ['any', 'all', 'none'];
                        nodeImpacts.forEach(impactType => {
                            if (node[impactType] && node[impactType].length > 0) {
                                node[impactType].forEach(check => {
                                    const row = [
                                        escapeCSV(violation.id),
                                        escapeCSV(violation.impact),
                                        escapeCSV(violation.tags.join('|')),
                                        escapeCSV(violation.description),
                                        escapeCSV(violation.help),
                                        escapeCSV(violation.helpUrl),
                                        escapeCSV(check.impact || ''),
                                        escapeCSV(node.html),
                                        escapeCSV(node.target.join('|')),
                                        escapeCSV(impactType),
                                        escapeCSV(check.message),
                                        escapeCSV(totalViolations)
                                    ];
                                    csvContent += row.join(',') + '\n';
                                });
                            }
                        });
                    });
                });
                
                return csvContent;
            }

            test('accessibility issues', async ({ page }) => {
                await page.goto("https://calendar.google.com/");
                const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
                const violations = accessibilityScanResults.violations;

                // Write CSV data to file
                fileReader.writeFileSync("violationsWithFixedContent.csv", violationsToCSV(violations));
                // Write the number of violations to a file
                fileReader.writeFileSync("num_violations.txt", String(violations.length));
            });
        