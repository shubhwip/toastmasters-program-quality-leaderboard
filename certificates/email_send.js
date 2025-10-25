/**
 * HTML Email Template with formatting
 */
/**
 * Professional HTML Email Template with enhanced formatting
 */
const EMAIL_HTML_TEMPLATE = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { 
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.7; 
      color: #2c3e50;
      background-color: #f8f9fa;
      margin: 0;
      padding: 20px;
    }
    .email-wrapper {
      max-width: 650px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
      padding: 40px 30px;
      text-align: center;
      color: white;
    }
    .header h1 {
      margin: 0;
      font-size: 28px;
      font-weight: 600;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header .trophy {
      font-size: 48px;
      margin-bottom: 10px;
    }
    .container { 
      padding: 40px 35px;
    }
    h2 { 
      color: #1a73e8;
      font-size: 24px;
      margin-top: 0;
      margin-bottom: 20px;
    }
    h3 { 
      color: #1a73e8;
      font-size: 19px;
      margin-top: 30px;
      margin-bottom: 15px;
      border-bottom: 2px solid #e3f2fd;
      padding-bottom: 8px;
    }
    p {
      margin: 15px 0;
      font-size: 15px;
    }
    .highlight-box { 
      background: linear-gradient(135deg, #e3f2fd 0%, #f0f7ff 100%);
      border-left: 5px solid #1a73e8;
      border-radius: 8px;
      padding: 25px;
      margin: 25px 0;
      box-shadow: 0 2px 4px rgba(26, 115, 232, 0.1);
    }
    .highlight-box h3 {
      margin-top: 0;
      color: #0d47a1;
      border-bottom: none;
      font-size: 20px;
    }
    .highlight-box ul {
      margin: 10px 0;
      padding-left: 20px;
    }
    .highlight-box li {
      margin: 12px 0;
    }
    .button { 
      display: inline-block;
      padding: 14px 32px;
      background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
      color: white !important;
      text-decoration: none;
      border-radius: 6px;
      margin: 15px 0;
      font-weight: 600;
      font-size: 15px;
      box-shadow: 0 4px 6px rgba(26, 115, 232, 0.3);
    }
    ul, ol { 
      line-height: 1.9;
      font-size: 15px;
    }
    ol {
      padding-left: 25px;
    }
    ol li {
      margin: 18px 0;
      padding-left: 8px;
    }
    ul li {
      margin: 12px 0;
    }
    .tip-box { 
      background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
      border: 2px solid #ffc107;
      border-radius: 8px;
      padding: 18px 22px;
      margin-top: 30px;
      box-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
    }
    .tip-box strong {
      color: #f57c00;
      font-size: 16px;
    }
    strong { 
      color: #1a73e8;
      font-weight: 600;
    }
    a {
      color: #1a73e8;
      text-decoration: none;
      font-weight: 500;
    }
    .signature {
      margin-top: 35px;
      padding-top: 25px;
      border-top: 2px solid #e3f2fd;
    }
    .signature p {
      margin: 5px 0;
      font-size: 15px;
    }
    .signature .name {
      font-weight: 600;
      color: #1a73e8;
      font-size: 16px;
    }
    .signature .title {
      color: #546e7a;
      font-style: italic;
    }
    .footer {
      background-color: #f8f9fa;
      padding: 25px;
      text-align: center;
      border-top: 3px solid #1a73e8;
    }
    .footer p {
      margin: 5px 0;
      font-size: 13px;
      color: #78909c;
    }
    .footer .logo {
      font-size: 14px;
      font-weight: 600;
      color: #1a73e8;
      margin-bottom: 8px;
    }
    .divider {
      height: 2px;
      background: linear-gradient(to right, transparent, #1a73e8, transparent);
      margin: 30px 0;
    }
  </style>
</head>
<body>
  <div class="email-wrapper">
    <div class="header">
      <div class="trophy">🏆</div>
      <h1>Congratulations on Your Achievement!</h1>
    </div>
    
    <div class="container">
      <h2>Hello {{Club Names}},</h2>
      
      <p><strong>Congratulations to {{Club Names}}!</strong> Your hard work and dedication have earned a <strong>{{Award Name}} Award</strong>—what a fantastic achievement!</p>
      
      <p>To help you make the most of this success, District 91 is delighted to offer an exclusive incentive for your club:</p>

      <div class="highlight-box">
        <h3>💰 Your Incentive Package</h3>
        <ul>
          <li><strong>£{{Award Amount}} voucher</strong> to shop at the Toastmasters International Store and Clubs can use the voucher towards room hire or zoom licence</li>
          <li>Explore exciting options—such as sets of 10 ribbons (Evaluator, Speaker, Topics) for just $5 each, or a Chat Box of 156 Favourite Things to spark inspiration and energy ($8 each, three to choose from)!</li>
        </ul>
      </div>

      <h3>📋 How to Claim Your Incentive ?</h3>
      <ol>
        <li><strong>Download your voucher:</strong> <a href="{{Certificate}}" class="button">Click Here to Download</a></li>
        <li><strong>Shop at the store:</strong> Make your purchase from the <a href="https://shop.toastmasters.org/shop">Toastmasters International Store</a> using your voucher</li>
        <li><strong>Submit your claim:</strong> Upload your purchase receipt along with the voucher in Concur
          <ul>
            <li>⏰ Claims must be submitted on or before <strong>{{Expiry Date}}</strong></li>
          </ul>
        </li>
      </ol>

      <div class="divider"></div>

      <h3>📚 Need Step-by-Step Guidance?</h3>
      <p>Find comprehensive instructions in the <a href="https://d91toastmasters.org.uk/wp-content/uploads/D91-Finance-Guide-2024-25-v1.159.pdf" target="_blank"><strong>2024-25 Finance Guide</strong></a>:</p>
      <ul>
        <li><strong>Pages 18-20:</strong> Complete process overview (don't miss slide 20!)</li>
        <li><strong>Pages 21-25:</strong> Concur user setup and registration guide</li>
        <li><strong>Page 61:</strong> Required Report Name for your claim</li>
        <li><strong>Pages 57-73:</strong> Detailed step-by-step claim instructions for Concur users</li>
      </ul>

      <h3>✅ Next Steps</h3>
      <p>Please let us know:</p>
      <ul>
        <li>If your nominated individual <strong>already has Concur access</strong>, OR</li>
        <li>If a <strong>new user needs to be set up</strong> (see Page 25 for setup details)</li>
      </ul>

      <p>For any questions or assistance with the claims, payment process or CONCUR, don't hesitate to reach out to our D91 Finance Director Guler Cortis at <a href="mailto:guler.cortis@gmail.com">guler.cortis@gmail.com</a>.</p>

      <p>For any questions or assistance with incentives, don't hesitate to reach out to me, or to our D91 Incentives Team 2025-26, Shubham Jain and Elangoraj Thiruppandiaraj at <a href="mailto:d91incentives@gmail.com">d91incentives@gmail.com</a>.</p>

      <p>We're thrilled to celebrate your success—keep inspiring and leading! 🌟</p>

      <div class="signature">
        <p class="name">{{Incentives Director First Name}}</p>
        <p class="name">{{Incentives Director Name}}</p>
        <p><a href="mailto:{{Incentives Director Email}}">{{Incentives Director Email}}</a></p>
      </div>

      <div class="tip-box">
        <strong>💡 Helpful Tip:</strong> If you've already claimed your incentive, please disregard this email.
      </div>
    </div>

    <div class="footer">
      <p class="logo">🎤 District 91 Toastmasters</p>
      <p>Incentives Program {{CURRENT_YEAR}}</p>
      <p>Building Leaders Through Communication & Leadership Excellence</p>
    </div>
  </div>
</body>
</html>
`;


/**
 * Test function to preview email content WITHOUT sending
 * This shows you what the email would look like
 */
function testEmailPreview() {
  try {
    // CONFIGURE THESE VALUES
    const TEST_SHEET_NAME = 'Sheet1';
    const TEST_ROW_NUMBER = 2; // Which row to preview (2 = first data row)
    
    console.log('=== Email Preview Test ===');
    
    // Open spreadsheet
    const testSpreadsheet = SpreadsheetApp.openById(TEST_SPREADSHEET_ID);
    const testSheet = testSpreadsheet.getSheetByName(TEST_SHEET_NAME);
    
    // Get data
    const data = testSheet.getDataRange().getValues();
    const headers = data[0];
    const rowData = data[TEST_ROW_NUMBER - 1]; // Convert to 0-based
    
    // Get template
    const templateDoc = DocumentApp.openById(EMAIL_TEMPLATE_DOC_ID_1);
    const templateBody = templateDoc.getBody().getText();
    
    console.log('\n--- ORIGINAL TEMPLATE ---');
    console.log(templateBody);
    
    // Prepare email (same logic as sendIndividualCertificateEmail)
    let emailBody = templateBody;
    
    headers.forEach((header, index) => {
      let value = rowData[index];
      
      if (header.includes('Date') && value instanceof Date) {
        value = dayWithDateFromDateObject(value);
      } else if (value === null || value === undefined) {
        value = '';
      } else {
        value = value.toString();
      }
      
      const placeholder = `{{${header}}}`;
      emailBody = emailBody.replace(new RegExp(placeholder, 'g'), value);
    });
    
    emailBody = emailBody
      .replace(/{{CURRENT_DATE}}/g, new Date().toLocaleDateString())
      .replace(/{{CURRENT_YEAR}}/g, new Date().getFullYear().toString());
    
    console.log('\n--- PROCESSED EMAIL BODY ---');
    console.log(emailBody);
    
    // Show recipients
    const getColumnValue = (columnName) => {
      const idx = headers.indexOf(columnName);
      return idx !== -1 ? (rowData[idx] || '') : '';
    };
    
    const presidentEmail = getColumnValue('President Email Address');
    const treasurerEmail = getColumnValue('Treasurer Email Address');
    const incentiveType = getColumnValue('Incentive Type');
    const vpEmail = incentiveType === 'CGD' 
      ? getColumnValue('VPM Email Address')
      : getColumnValue('VPE Email Address');
    
    console.log('\n--- RECIPIENTS ---');
    console.log('TO:', [presidentEmail, treasurerEmail, vpEmail].filter(e => e).join(', '));
    console.log('CC:', [
      getColumnValue('Division Director Email'),
      getColumnValue('Area Director Email'),
      getColumnValue('Finance Director Email'),
      getColumnValue('Incentives Director Email')
    ].filter(e => e).join(', '));
    console.log('BCC:', getColumnValue('D91incentives Email'));
    
    console.log('\n--- SUBJECT ---');
    console.log(`Congratulations ${getColumnValue('Club Names')} 🎉 Claim Your ${getColumnValue('Award Name')} Incentive – Celebrate Your Success!`);
    
    console.log('\n=== Preview Complete (NO EMAIL SENT) ===');
    
  } catch (error) {
    console.error('Error in preview:', error);
  }
}

/**
 * Test function for certificate email distribution
 * Run this manually from the Apps Script editor to test
 */
function testCertificateEmails() {
  try {
    // CONFIGURE THESE VALUES FOR TESTING
    const TEST_SHEET_NAME = 'Sheet1'; // Replace with actual sheet name if different
    
    console.log('=== Testing Certificate Email Function ===');
    
    // Open the test spreadsheet
    const testSpreadsheet = SpreadsheetApp.openById(TEST_SPREADSHEET_ID);
    const testSheet = testSpreadsheet.getSheetByName(TEST_SHEET_NAME);
    
    if (!testSheet) {
      console.error('Sheet not found! Check TEST_SHEET_NAME');
      return;
    }
    
    console.log(`Using spreadsheet: ${testSpreadsheet.getName()}`);
    console.log(`Using sheet: ${testSheet.getName()}`);
    
    // Get all data
    const data = testSheet.getDataRange().getValues();
    const headers = data[0];
    const dataRows = data.slice(1);
    
    console.log(`Found ${dataRows.length} data rows`);
    console.log(`Headers: ${headers.join(', ')}`);
    
    // Create processedRows array (simulate what would be created during normal processing)
    const processedRows = dataRows.map((row, index) => ({
      rowIndex: index + 2, // +2 because row 1 is header, array index is 0-based
      data: row
    }));
    
    // // TEST OPTION 1: Send emails to ALL rows
    // console.log('\n--- Sending emails to ALL rows ---');
    // sendCertificateEmails(testSheet, processedRows);
    
    // TEST OPTION 2: Send email to ONLY FIRST row (uncomment to use)
    console.log('\n--- Sending email to FIRST row only ---');
    sendCertificateEmails(testSheet, [processedRows[0]]);
    
    // TEST OPTION 3: Send email to SPECIFIC row (uncomment and change index to use)
    // console.log('\n--- Sending email to SPECIFIC row ---');
    // const specificRow = processedRows[2]; // Index 2 = 3rd data row (row 4 in sheet)
    // sendCertificateEmails(testSheet, [specificRow]);
    
    console.log('\n=== Test Complete ===');
    console.log('Check your email and logs above for results');
    
  } catch (error) {
    console.error('Error in test function:', error);
    console.error('Stack trace:', error.stack);
  }
}


/**
 * Sends personalized certificate emails to club officers for each row
 * @param {Sheet} submissionSheet - Submission sheet
 * @param {Array} processedRows - Array of processed row data
 */
function sendCertificateEmails(submissionSheet, processedRows) {
  console.log('=== Starting Certificate Email Distribution ===');
  
  try {
    // Get email template
    const templateDoc = DocumentApp.openById(EMAIL_TEMPLATE_DOC_ID);
    const templateBody = templateDoc.getBody().getText();
    
    const data = submissionSheet.getDataRange().getValues();
    const headers = data[0];
    
    // Process each row (club)
    processedRows.forEach(rowInfo => {
      try {
        const rowData = data[rowInfo.rowIndex - 1]; // Convert to 0-based index
        sendIndividualCertificateEmail(headers, rowData, templateBody);
      } catch (error) {
        console.error(`Error sending email for row ${rowInfo.rowIndex}:`, error);
      }
    });
    
    console.log('Certificate emails sent successfully');
    
  } catch (error) {
    console.error('Error in sendCertificateEmails:', error);
  }
}

/**
 * Sends individual certificate email for a specific club/row
 * @param {Array} headers - Column headers
 * @param {Array} rowData - Row data
 * @param {string} templateHtml - Email template HTML body (not used when using constant)
 */
function sendIndividualCertificateEmail(headers, rowData, templateHtml) {
  // Get column value helper
  const getColumnValue = (columnName) => {
    const idx = headers.indexOf(columnName);
    return idx !== -1 ? (rowData[idx] || '') : '';
  };
  
  // Extract recipient emails
  const presidentEmail = getColumnValue('President Email Address');
  const treasurerEmail = getColumnValue('Treasurer Email Address');
  const incentiveType = getColumnValue('Incentive Type');
  
  let vpEmail = '';
  if (incentiveType === 'CGD') {
    vpEmail = getColumnValue('VPM Email Address');
  } else if (incentiveType === 'PQD') {
    vpEmail = getColumnValue('VPE Email Address');
  }
  
  // CC recipients
  const divisionDirectorEmail = getColumnValue('Division Director Email');
  const areaDirectorEmail = getColumnValue('Area Director Email');
  const financeDirectorEmail = getColumnValue('Finance Director Email');
  const incentivesDirectorEmail = getColumnValue('Incentives Director Email');
  
  // BCC recipient
  const d91incentivesEmail = getColumnValue('D91incentives Email');
  
  // Validate recipients
  const toRecipients = [presidentEmail, treasurerEmail, vpEmail].filter(email => email.trim() !== '');
  if (toRecipients.length === 0) {
    console.warn(`No valid TO recipients for club: ${getColumnValue('Club Names')}`);
    return;
  }
  
  const ccRecipients = [
    divisionDirectorEmail,
    areaDirectorEmail,
    financeDirectorEmail,
    incentivesDirectorEmail
  ].filter(email => email.trim() !== '');
  
  // USE THE HTML CONSTANT INSTEAD OF TEMPLATE
  let emailHtml = EMAIL_HTML_TEMPLATE;
  
  // Replace placeholders
  headers.forEach((header, index) => {
    let value = rowData[index];
    
    if (header.includes('Date') && value instanceof Date) {
      value = dayWithDateFromDateObject(value);
    } else if (value === null || value === undefined) {
      value = '';
    } else {
      value = value.toString();
    }
    
    // Escape HTML in values
    value = value.replace(/&/g, '&amp;')
                 .replace(/</g, '&lt;')
                 .replace(/>/g, '&gt;');
    
    const placeholder = `{{${header}}}`;
    emailHtml = emailHtml.replace(new RegExp(placeholder, 'g'), value);
  });
  
  // Additional replacements
  emailHtml = emailHtml
    .replace(/{{CURRENT_DATE}}/g, new Date().toLocaleDateString())
    .replace(/{{CURRENT_YEAR}}/g, new Date().getFullYear().toString());
  
  // Subject
  const clubName = getColumnValue('Club Names');
  const awardName = getColumnValue('Award Name');
  const subject = `Congratulations ${clubName} 🎉 Claim Your ${awardName} Incentive – Celebrate Your Success!`
  
  // Replace Incentives Director Name based on type
  const incentivesDirectorName = incentiveType === 'CGD' 
    ? 'Lynne Gayer<br>Club Growth Director'
    : 'Seema Menon<br>Program Quality Director';

  // Extract first name more reliably (handles HTML tags)
  const incentivesDirectorFirstName = incentivesDirectorName.split('<br>')[0].split(/\s+/)[0];
  emailHtml = emailHtml.replace(/{{Incentives Director Name}}/g, incentivesDirectorName);
  emailHtml = emailHtml.replace(/{{Incentives Director First Name}}/g, incentivesDirectorFirstName);

  // Send email
  try {
    const emailOptions = {
      to: toRecipients.join(','),
      subject: subject,
      htmlBody: emailHtml,
      name: 'District 91 Incentives Team'
    };
    
    if (ccRecipients.length > 0) {
      emailOptions.cc = ccRecipients.join(',');
    }
    
    if (d91incentivesEmail.trim() !== '') {
      emailOptions.bcc = d91incentivesEmail;
    }
    
    MailApp.sendEmail(emailOptions);
    
    console.log(`✓ Email sent for ${clubName}`);
    
  } catch (error) {
    console.error(`Error sending email for ${clubName}:`, error);
  }
}
