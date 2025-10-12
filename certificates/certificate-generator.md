
## End to End Setup
- This whole setup requires a mandatory variables setup 
    - SLIDE_TEMPLATE_ID = 'PROVIDE_YOUR_SLIDE_TEMPLATE_ID_HERE';
    - OFFICERS_SHEET_ID = 'PROVIDE_YOUR_OFFICERS_SHEET_ID_HERE'; 
- Create a Google Form Like [this](./Generate%20Certificates%20for%20Incentives%20-%20Google%20Forms.pdf)
- Link a Sheet to newly Google Form
- Link a App Script to Sheet
- Copy [certificate-generator.js](./certificate-generator.js) script into Google Apps Script
- Give Permissions of Google Slides and Google Sheets API
- Setup a Trigger on `onFormSubmit` with Form's Output Sheet.

## Verification
- If final incentives distribution list has invalid or missing data then email will be sent to incentives coordinators for further verification and it incorrect incentives distribution list won't be sent to Active Campaign Manager.