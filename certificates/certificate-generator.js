const SLIDE_TEMPLATE_ID = 'PROVIDE_YOUR_VALUE';
const OFFICERS_SHEET_ID = 'PROVIDE_YOUR_VALUE'; 
const OFFICERS_SHEET_NAME = 'Club Officer';
const FINAL_SHEET_LINK = 'Final Certificates';
const DIV_AREA_LEADER_SHEET_ID = 'PROVIDE_YOUR_VALUE'; 
const DISTRICT_LEADERS_SHEET_ID = 'PROVIDE_YOUR_VALUE'; // Sheet with Name, Div Dir/AD, Division, Area, Email
const DISTRICT_LEADERS_SHEET_NAME = 'Sheet1'; 
const ACTIVE_CAMPAIGN_MANAGER_EMAIL = 'PROVIDE_YOUR_VALUE';
const EMAIL_TEMPLATE_DOC_ID = 'PROVIDE_YOUR_VALUE';

// Add these constants with your other constants at the top
const VERIFICATION_EMAIL_RECIPIENTS = [
  'PROVIDE_YOUR_VALUE',
  'PROVIDE_YOUR_VALUE', 
  'PROVIDE_YOUR_VALUE'
];

/**
 * Club Incentive Certificate Generation Script
 * Processes form submissions and generates certificates for multiple clubs
 */

// === MAIN EVENT HANDLERS ===

/**
 * Handles form submission events
 * @param {Object} e - Form submission event object
 */
function onFormSubmit(e) {
  try {
    const sheet = e.range.getSheet();
    const rowIdx = e.range.getRow();
    
    processSubmission(sheet, rowIdx);
  } catch (error) {
    console.error('Error in onFormSubmit:', error);
  }
}

/**
 * Debug function to test the script manually
 * Uses the last row of data for testing
 */
function debug() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Form Responses 1');
    const rowIdx = sheet.getLastRow();
    
    processSubmission(sheet, rowIdx);
  } catch (error) {
    console.error('Error in debug function:', error);
  }
}

// === CORE PROCESSING FUNCTIONS ===

/**
 * Main processing function for form submissions
 * @param {Sheet} sheet - The source sheet containing form data
 * @param {number} rowIdx - Row index of the submission to process
 */
function processSubmission(sheet, rowIdx) {
  console.log(`=== Processing submission for row ${rowIdx} ===`);
  
  // Get form data
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const formRow = data[rowIdx - 1];
  
  // Extract submission details
  const submissionDetails = extractSubmissionDetails(headers, formRow);
  console.log(`Processing clubs: ${submissionDetails.clubs.join(', ')}`);
  
  // Create new spreadsheet for this submission
  const submissionWorkbook = createSubmissionSpreadsheet(rowIdx, headers, submissionDetails.incentiveType);
  
  // Process each club
  const processedRows = processClubs(submissionWorkbook.sheet, headers, formRow, submissionDetails);
  
  // Write submission sheet link back to original form
  writeSubmissionLink(sheet, rowIdx, submissionWorkbook.url);
  
  // Generate certificates for each processed row
  generateCertificates(submissionWorkbook.sheet, processedRows);

  // Verify submission data and certificate generation
  const verificationPassed = verifySubmissionData(
    submissionWorkbook.sheet, 
    submissionDetails.clubs.length, 
    submissionWorkbook.url, 
    submissionDetails
  );
  
  // Send email notification only if verification passed
  if (verificationPassed) {
    sendSubmissionNotification(submissionWorkbook.url, submissionDetails.incentiveType, submissionDetails.clubs);
  } else {
    console.warn('Skipping success notification email due to verification errors');
  }
  
  console.log(`=== Completed processing submission ${rowIdx} ===`);
}

/**
 * Extracts submission details from form data
 * @param {Array} headers - Column headers
 * @param {Array} formRow - Form submission data
 * @returns {Object} Submission details
 */
function extractSubmissionDetails(headers, formRow) {
  const clubCellIdx = headers.indexOf('Club Names');
  const typeCellIdx = headers.indexOf('Incentive Type');
  const rawClubCell = formRow[clubCellIdx];
  const incentiveType = formRow[typeCellIdx];
  
  const clubs = typeof rawClubCell === 'string'
    ? rawClubCell.split(',').map(club => club.trim()).filter(club => club.length > 0)
    : [rawClubCell];
  
  return {
    clubs,
    incentiveType,
    clubCellIdx
  };
}

/**
 * Creates a new spreadsheet for the submission
 * @param {number} rowIdx - Submission row index
 * @param {Array} headers - Original headers
 * @param {string} incentiveType - Type of incentive (CGD/PQD)
 * @returns {Object} Object containing sheet and URL
 */
function createSubmissionSpreadsheet(rowIdx, headers, incentiveType) {
  console.log('Creating new submission spreadsheet...');
  
  // Create new spreadsheet
  const submissionSpreadsheet = SpreadsheetApp.create(`Club Incentive - Submission ${rowIdx}`);
  const submissionSheet = submissionSpreadsheet.getActiveSheet(); // Get the actual Sheet object
  const submissionSheetUrl = submissionSpreadsheet.getUrl();
  
  // Set up enhanced headers
  const enhancedHeaders = createEnhancedHeaders(headers, incentiveType);
  submissionSheet.appendRow(enhancedHeaders);
  
  // Set up Claimed Status column with dropdown validation
  setupClaimedStatusDropdown(submissionSheet, enhancedHeaders);
  
  // Style the spreadsheet to look beautiful
  styleSubmissionSheet(submissionSheet, enhancedHeaders);
  
  // Set sharing permissions
  setSpreadsheetPermissions(submissionSpreadsheet.getId());
  
  return {
    spreadsheet: submissionSpreadsheet,
    sheet: submissionSheet,
    url: submissionSheetUrl,
    headers: enhancedHeaders
  };
}

/**
 * Creates enhanced headers with officer email columns
 * @param {Array} originalHeaders - Original form headers
 * @param {string} incentiveType - Type of incentive
 * @returns {Array} Enhanced headers array
 */
function createEnhancedHeaders(originalHeaders, incentiveType) {
  const newHeaders = [...originalHeaders]; // Use spread operator for cleaner array copying
  newHeaders.push('Claimed Status');  
  if (incentiveType === 'CGD') {
    newHeaders.push('VPM Email Address', 'Treasurer Email Address', 'President Email Address');
  } else if (incentiveType === 'PQD') {
    newHeaders.push('VPE Email Address', 'Treasurer Email Address', 'President Email Address');
  }
  
  newHeaders.push(
    'Division Director Email',
    'Area Director Email', 
    'Finance Director Email',
    'Incentives Director Email',
    'D91incentives Email',
  );
  newHeaders.pop('Final Certificates');  
  return newHeaders;
}

/**
 * Sets sharing permissions for the submission spreadsheet
 * @param {string} spreadsheetId - ID of the spreadsheet
 */
function setSpreadsheetPermissions(spreadsheetId) {
  try {
    const submissionFile = DriveApp.getFileById(spreadsheetId);
    submissionFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.EDIT);
    console.log('Spreadsheet permissions set successfully');
  } catch (error) {
    console.warn('Could not set spreadsheet permissions:', error);
  }
}

/**
 * Processes each club and creates individual rows
 * @param {Sheet} submissionSheet - Target sheet for club data
 * @param {Array} headers - Original headers
 * @param {Array} formRow - Original form data
 * @param {Object} submissionDetails - Submission details
 * @returns {Array} Array of processed row data
 */
function processClubs(submissionSheet, headers, formRow, submissionDetails) {
  const officersSheet = SpreadsheetApp.openById(OFFICERS_SHEET_ID).getSheetByName(OFFICERS_SHEET_NAME);
  const processedRows = [];
  
  submissionDetails.clubs.forEach((club, index) => {
    console.log(`Processing club: ${club}`);
    
    // Create club-specific row data
    const clubRowData = [...formRow];
    clubRowData[submissionDetails.clubCellIdx] = club;
    
    // Look up officer emails
    const officerEmails = lookupOfficerEmails(officersSheet, club, submissionDetails.incentiveType);
    const finalRow = clubRowData.concat(officerEmails);
    
    // Add to submission sheet
    submissionSheet.appendRow(finalRow);
    
    // Track for certificate generation (row index is 2-based: header + clubs processed)
    processedRows.push({
      rowIndex: index + 2,
      data: finalRow
    });
  });
  
  return processedRows;
}

/**
 * Writes the submission spreadsheet link back to the original form
 * @param {Sheet} originalSheet - Original form sheet
 * @param {number} rowIdx - Row index in original sheet
 * @param {string} submissionUrl - URL of the submission spreadsheet
 */
function writeSubmissionLink(originalSheet, rowIdx, submissionUrl) {
  try {
    const linkCol = getColumn(originalSheet, FINAL_SHEET_LINK);
    originalSheet.getRange(rowIdx, linkCol).setValue(submissionUrl);
    console.log(`Submission link written to row ${rowIdx}`);
  } catch (error) {
    console.error('Error writing submission link:', error);
  }
}

/**
 * Generates certificates for all processed rows
 * @param {Sheet} submissionSheet - Submission sheet containing club data
 * @param {Array} processedRows - Array of processed row data
 */
function generateCertificates(submissionSheet, processedRows) {
  console.log('Starting certificate generation...');
  
  // Get current data from submission sheet
  const submissionData = submissionSheet.getDataRange().getValues();
  const submissionHeaders = submissionData[0];
  
  // Generate certificate for each club row
  processedRows.forEach(rowInfo => {
    console.log(`Generating certificate for row ${rowInfo.rowIndex}`);
    
    try {
      const rowData = submissionData[rowInfo.rowIndex - 1]; // Convert to 0-based index
      processCertificateRow(submissionSheet, rowInfo.rowIndex, rowData, submissionHeaders);
    } catch (error) {
      console.error(`Error generating certificate for row ${rowInfo.rowIndex}:`, error);
    }
  });
}

// === CERTIFICATE GENERATION ===

/**
 * Processes a single row to generate and link a certificate
 * @param {Sheet} sheet - Target sheet
 * @param {number} rowIdx - Row index (1-based)
 * @param {Array} row - Row data
 * @param {Array} headers - Headers array
 */
function processCertificateRow(sheet, rowIdx, row, headers) {
  console.log(`=== Generating certificate for row ${rowIdx} ===`);
  
  try {
    // Validate inputs
    if (!validateCertificateInputs(sheet, rowIdx, row, headers)) {
      return;
    }
    
    const clubName = row[headers.indexOf('Club Names')];
    console.log(`Processing certificate for: ${clubName}`);
    
    // Create award folder
    const certFolder = createAwardFolder(row, headers);
    
    // Generate certificate slide
    const certificateData = generateCertificateSlide(row, headers, clubName, certFolder);
    
    // Export and save certificate image
    const imgUrl = saveCertificateImage(certificateData.slideCopyId, clubName, certFolder);
    
    // Write certificate data back to sheet
    writeCertificateData(sheet, rowIdx, headers, imgUrl);
    // Populate district leader emails
    populateDistrictLeaderEmails(sheet, rowIdx, row, headers);
    // Clean up temporary slide
    DriveApp.getFileById(certificateData.slideCopyId).setTrashed(true);
    
    console.log(`Certificate generation completed for ${clubName}`);
    
  } catch (error) {
    console.error(`Error in processCertificateRow for row ${rowIdx}:`, error);
  }
}



/**
 * Validates inputs for certificate processing
 * @param {Sheet} sheet - Target sheet
 * @param {number} rowIdx - Row index
 * @param {Array} row - Row data
 * @param {Array} headers - Headers array
 * @returns {boolean} True if inputs are valid
 */
function validateCertificateInputs(sheet, rowIdx, row, headers) {
  if (typeof sheet.getRange !== 'function') {
    console.error('Invalid sheet object provided');
    return false;
  }
  
  if (typeof rowIdx !== 'number' || rowIdx < 1) {
    console.error('Invalid row index:', rowIdx);
    return false;
  }
  
  if (!Array.isArray(row) || !Array.isArray(headers)) {
    console.error('Invalid row data or headers');
    return false;
  }
  
  return true;
}

/**
 * Creates or finds the award folder for certificates
 * @param {Array} row - Row data
 * @param {Array} headers - Headers array
 * @returns {Folder} Google Drive folder for certificates
 */
function createAwardFolder(row, headers) {
  const awardName = row[headers.indexOf('Award Name')];
  const awardDate = dayWithDateFromDateObject(row[headers.indexOf('Award Date')]);
  const folderName = `${awardName} - ${awardDate}`;
  
  const awardFolders = DriveApp.getFoldersByName(folderName);
  
  if (awardFolders.hasNext()) {
    console.log(`Using existing folder: ${folderName}`);
    return awardFolders.next();
  } else {
    console.log(`Creating new folder: ${folderName}`);
    return DriveApp.createFolder(folderName);
  }
}

/**
 * Generates certificate slide from template
 * @param {Array} row - Row data
 * @param {Array} headers - Headers array
 * @param {string} clubName - Name of the club
 * @param {Folder} certFolder - Folder to store certificate
 * @returns {Object} Certificate data including slide copy ID
 */
function generateCertificateSlide(row, headers, clubName, certFolder) {
  // Create copy of slide template
  const slideCopy = DriveApp.getFileById(SLIDE_TEMPLATE_ID).makeCopy(`${clubName} Certificate`, certFolder);
  const slideCopyId = slideCopy.getId();
  
  // Open and modify the slide
  const slides = SlidesApp.openById(slideCopyId);
  const slide = slides.getSlides()[0];
  
  // Replace template placeholders with actual data
  for (let j = 0; j < headers.length; j++) {
    let value = row[j];
    
    // Format value based on type
    if (headers[j].includes('Date') && value instanceof Date) {
      value = dayWithDateFromDateObject(value);
    } else if (value === undefined || value === null) {
      value = '';
    } else {
      value = value.toString();
    }
    
    slide.replaceAllText(`<<${headers[j]}>>`, value);
  }
  
  slides.saveAndClose();
  
  return { slideCopyId };
}

/**
 * Exports slide as PNG and saves to Drive
 * @param {string} slideCopyId - ID of the slide copy
 * @param {string} clubName - Name of the club
 * @param {Folder} certFolder - Folder to store certificate
 * @returns {string} URL of the saved image
 */
function saveCertificateImage(slideCopyId, clubName, certFolder) {
  // Export slide as PNG
  const imageBlob = exportSlideAsPNG(clubName, slideCopyId);
  
  // Save to Drive and set sharing
  const imgFile = certFolder.createFile(imageBlob);
  imgFile.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  
  return imgFile.getUrl();
}

/**
 * Writes certificate data back to the submission sheet
 * @param {Sheet} sheet - Target sheet
 * @param {number} rowIdx - Row index
 * @param {Array} headers - Headers array
 * @param {string} imgUrl - URL of the certificate image
 */
function writeCertificateData(sheet, rowIdx, headers, imgUrl) {
  // Write certificate image link
  const certColIdx = headers.indexOf('Certificate');
  if (certColIdx !== -1) {
    sheet.getRange(rowIdx, certColIdx + 1).setValue(imgUrl);
    console.log(`Certificate image URL written to column ${certColIdx + 1}`);
  }
  
  // Set claimed status with default value
  const claimedColIdx = headers.indexOf('Claimed Status');
  if (claimedColIdx !== -1) {
    sheet.getRange(rowIdx, claimedColIdx + 1).setValue('Unclaimed');
    console.log(`Claimed status set to 'Unclaimed'`);
  }
}

/**
 * Populates district leader email columns
 * @param {Sheet} sheet - Target sheet
 * @param {number} rowIdx - Row index
 * @param {Array} row - Row data
 * @param {Array} headers - Headers array
 */
function populateDistrictLeaderEmails(sheet, rowIdx, row, headers) {
  try {
    const clubName = row[headers.indexOf('Club Names')];
    const incentiveType = row[headers.indexOf('Incentive Type')];
    
    // Get club's division and area from officers sheet
    const clubInfo = getClubDivisionAndArea(clubName);
    
    // Get district leaders sheet
    const districtLeadersSheet = SpreadsheetApp.openById(DISTRICT_LEADERS_SHEET_ID)
      .getSheetByName(DISTRICT_LEADERS_SHEET_NAME);
    
    // Lookup all district leader emails
    const leaderEmails = lookupDistrictLeaderEmails(
      districtLeadersSheet, 
      clubInfo.division, 
      clubInfo.area, 
      incentiveType
    );
    
    // Write emails to sheet
    writeDistrictLeaderEmails(sheet, rowIdx, headers, leaderEmails);
    
    console.log(`District leader emails populated for ${clubName}`);
    
  } catch (error) {
    console.error('Error populating district leader emails:', error);
  }
}

/**
 * Gets club's division and area from officers sheet
 * @param {string} clubName - Name of the club
 * @returns {Object} Object with division and area
 */
function getClubDivisionAndArea(clubName) {
  const officersSheet = SpreadsheetApp.openById(OFFICERS_SHEET_ID)
    .getSheetByName(OFFICERS_SHEET_NAME);
  const data = officersSheet.getDataRange().getValues();
  const headers = data[0];
  
  const clubCol = headers.indexOf('Club Name');
  const divisionCol = headers.indexOf('Division');
  const areaCol = headers.indexOf('Area');
  
  const clubRow = data.find(row => 
    row[clubCol] && row[clubCol].toString().trim() === clubName
  );
  
  return {
    division: clubRow ? clubRow[divisionCol] : '',
    area: clubRow ? clubRow[areaCol] : ''
  };
}

/**
 * Looks up district leader emails from the district leaders sheet
 * @param {Sheet} districtLeadersSheet - District leaders sheet
 * @param {string} division - Club's division
 * @param {string} area - Club's area
 * @param {string} incentiveType - Type of incentive (CGD/PQD)
 * @returns {Object} Object with all leader emails
 */
function lookupDistrictLeaderEmails(districtLeadersSheet, division, area, incentiveType) {
  const data = districtLeadersSheet.getDataRange().getValues();
  const headers = data[0];
  
  const nameCol = headers.indexOf('Name');
  const roleCol = headers.indexOf('Div Dir/AD');
  const divisionCol = headers.indexOf('Division');
  const areaCol = headers.indexOf('Area');
  const emailCol = headers.indexOf('Email');
  
  let divisionDirectorEmail = '';
  let areaDirectorEmail = '';
  let financeDirectorEmail = '';
  
  // Find Division Director (Div Dir/AD = "Div" AND Area is empty AND Division matches)
  const divDirector = data.find(row =>
    row[roleCol] && row[roleCol].toString().trim() === 'Div' &&
    (!row[areaCol] || row[areaCol].toString().trim() === '') &&
    row[divisionCol] && row[divisionCol].toString().trim() === division
  );
  if (divDirector) {
    divisionDirectorEmail = divDirector[emailCol];
  }
  
  // Find Area Director (Div Dir/AD = "AD" AND Area is not empty AND Division and Area match)
  const areaDirector = data.find(row =>
    row[roleCol] && row[roleCol].toString().trim() === 'AD' &&
    row[divisionCol] && row[divisionCol].toString().trim() === division &&
    row[areaCol] && row[areaCol].toString().trim() === area.toString()
  );
  if (areaDirector) {
    areaDirectorEmail = areaDirector[emailCol];
  }
  
  // Find Finance Director (Div Dir/AD = "Finance Dir")
  const financeDirector = data.find(row =>
    row[roleCol] && row[roleCol].toString().trim() === 'Finance Dir'
  );
  if (financeDirector) {
    financeDirectorEmail = financeDirector[emailCol];
  }
  
  // Incentives Director Email based on type
  const incentivesDirectorEmail = incentiveType === 'CGD' 
    ? 'lynnecantorgayer@gmail.com' 
    : 'seematoastmaster@gmail.com';
  
  // D91 Incentives Email (constant)
  const d91incentivesEmail = 'd91incentives@gmail.com';
  
  return {
    divisionDirectorEmail,
    areaDirectorEmail,
    financeDirectorEmail,
    incentivesDirectorEmail,
    d91incentivesEmail
  };
}

/**
 * Writes district leader emails to the sheet
 * @param {Sheet} sheet - Target sheet
 * @param {number} rowIdx - Row index
 * @param {Array} headers - Headers array
 * @param {Object} leaderEmails - Object containing all leader emails
 */
function writeDistrictLeaderEmails(sheet, rowIdx, headers, leaderEmails) {
  const emailMappings = [
    { header: 'Division Director Email', value: leaderEmails.divisionDirectorEmail },
    { header: 'Area Director Email', value: leaderEmails.areaDirectorEmail },
    { header: 'Finance Director Email', value: leaderEmails.financeDirectorEmail },
    { header: 'Incentives Director Email', value: leaderEmails.incentivesDirectorEmail },
    { header: 'D91incentives Email', value: leaderEmails.d91incentivesEmail }
  ];
  
  emailMappings.forEach(mapping => {
    const colIdx = headers.indexOf(mapping.header);
    if (colIdx !== -1) {
      sheet.getRange(rowIdx, colIdx + 1).setValue(mapping.value);
    }
  });
}

// === UTILITY FUNCTIONS ===

/**
 * Looks up officer emails for a specific club and incentive type
 * @param {Sheet} officersSheet - Officers master sheet
 * @param {string} clubName - Name of the club
 * @param {string} incentiveType - Type of incentive (CGD/PQD)
 * @returns {Array} Array of officer email addresses
 */
function lookupOfficerEmails(officersSheet, clubName, incentiveType) {
  const officesNeeded = getRequiredOffices(incentiveType);
  
  // Get all officer data once
  const data = officersSheet.getDataRange().getValues();
  const headers = data[0];
  const clubCol = headers.indexOf('Club Name');
  const officeCol = headers.indexOf('Office');
  const emailCol = headers.indexOf('Email Address');
  
  // Find email for each required office
  const emails = officesNeeded.map(officeType => {
    const match = data.find(row =>
      row[clubCol] && row[clubCol].toString().trim() === clubName &&
      row[officeCol] && row[officeCol].toString().trim() === officeType
    );
    return match ? match[emailCol] : '';
  });
  
  console.log(`Officer emails for ${clubName}:`, emails);
  return emails;
}

/**
 * Sets up dropdown validation for Claimed Status column
 * @param {Sheet} sheet - Target sheet
 * @param {Array} headers - Headers array
 */
function setupClaimedStatusDropdown(sheet, headers) {
  const claimedColIdx = headers.indexOf('Claimed Status');
  if (claimedColIdx !== -1) {
    const claimedCol = claimedColIdx + 1; // Convert to 1-based
    
    // Create dropdown validation rule
    const rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(['Unclaimed', 'Claimed'])
      .setAllowInvalid(false)
      .build();
    
    // Apply to the entire column (starting from row 2 to avoid header)
    const range = sheet.getRange(2, claimedCol, sheet.getMaxRows() - 1, 1);
    range.setDataValidation(rule);
    
    console.log('Claimed Status dropdown validation set up');
  }
}

/**
 * Styles the submission sheet to look beautiful like Google Forms linked sheets
 * @param {Sheet} sheet - Target sheet to style
 * @param {Array} headers - Headers array
 */
function styleSubmissionSheet(sheet, headers) {
  try {
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    
    // Set header styling similar to Google Forms
    headerRange
      .setBackground('#4285f4')  // Google blue color
      .setFontColor('#ffffff')   // White text
      .setFontWeight('bold')     // Bold text
      .setFontSize(11)           // Standard font size
      .setVerticalAlignment('middle')
      .setHorizontalAlignment('center');
    
    // Auto-resize columns to fit content
    for (let i = 1; i <= headers.length; i++) {
      sheet.autoResizeColumn(i);
    }
    
    // Freeze the header row
    sheet.setFrozenRows(1);
    
    // Add alternating row colors for better readability
    const dataRange = sheet.getRange(2, 1, sheet.getMaxRows() - 1, headers.length);
    dataRange.applyRowBanding(SpreadsheetApp.BandingTheme.LIGHT_GREY, false, true);
    
    // Set border around header
    headerRange.setBorder(true, true, true, true, true, true, '#000000', SpreadsheetApp.BorderStyle.SOLID);
    
    console.log('Sheet styling applied successfully');
    
  } catch (error) {
    console.warn('Could not apply sheet styling:', error);
  }
}
/*
 * @param {string} incentiveType - Type of incentive
 * @returns {Array} Array of required office types
 */
function getRequiredOffices(incentiveType) {
  const officeMap = {
    'CGD': ['Club VP Membership', 'Club Treasurer', 'Club President'],
    'PQD': ['Club VP Education', 'Club Treasurer', 'Club President']
  };
  
  return officeMap[incentiveType] || [];
}

/**
 * Ensures a column exists in the sheet, creates it if missing
 * @param {Sheet} sheet - Target sheet
 * @param {string} colName - Column name to ensure
 */
function ensureColumn(sheet, colName) {
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  if (headers.indexOf(colName) === -1) {
    sheet.getRange(1, headers.length + 1).setValue(colName);
    console.log(`Added column: ${colName}`);
  }
}

/**
 * Gets column index for a given column name, creates column if missing
 * @param {Sheet} sheet - Target sheet
 * @param {string} colName - Column name to find
 * @returns {number} 1-based column index
 */
function getColumn(sheet, colName) {
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  let colIdx = headers.indexOf(colName);
  
  if (colIdx === -1) {
    // Create the column
    sheet.getRange(1, headers.length + 1).setValue(colName);
    return headers.length + 1;
  }
  
  return colIdx + 1; // Convert to 1-based index
}

/**
 * Exports a slide as PNG image blob
 * @param {string} clubName - Name of the club (for filename)
 * @param {string} presentationId - ID of the presentation
 * @returns {Blob} PNG image blob
 */
function exportSlideAsPNG(clubName, presentationId) {
  try {
    const slides = Slides.Presentations.get(presentationId).slides;
    const slideId = slides[0].objectId;
    
    const thumbnailUrl = `https://slides.googleapis.com/v1/presentations/${presentationId}/pages/${slideId}/thumbnail?thumbnailProperties.mimeType=PNG`;
    const token = ScriptApp.getOAuthToken();
    
    // Get thumbnail URL
    const response = UrlFetchApp.fetch(thumbnailUrl, {
      headers: { Authorization: 'Bearer ' + token }
    });
    
    const thumbnailData = JSON.parse(response.getContentText());
    
    // Fetch actual image
    const imageResponse = UrlFetchApp.fetch(thumbnailData.contentUrl);
    return imageResponse.getBlob().setName(`${clubName}.png`);
    
  } catch (error) {
    console.error('Error exporting slide as PNG:', error);
    throw error;
  }
}


/**
 * Sends email notification about the submission
 * @param {string} submissionSheetUrl - URL of the submission sheet
 * @param {string} incentiveType - Type of incentive
 * @param {Array} clubs - Array of club names
 */
function sendSubmissionNotification(submissionSheetUrl, incentiveType, clubs) {
  try {
    // Get email template
    const templateDoc = DocumentApp.openById(EMAIL_TEMPLATE_DOC_ID);
    let emailBody = templateDoc.getBody().getText();
    
    // Replace placeholders in template
    emailBody = emailBody
      .replace('{{SUBMISSION_SHEET_LINK}}', submissionSheetUrl)
      .replace('{{INCENTIVE_TYPE}}', incentiveType)
      .replace('{{CLUBS}}', clubs.join(', '))
      .replace('{{DATE}}', new Date().toLocaleDateString());
    
    // Get finance director email
    const districtLeadersSheet = SpreadsheetApp.openById(DISTRICT_LEADERS_SHEET_ID)
      .getSheetByName(DISTRICT_LEADERS_SHEET_NAME);
    const data = districtLeadersSheet.getDataRange().getValues();
    const headers = data[0];
    
    const roleCol = headers.indexOf('Div Dir/AD');
    const emailCol = headers.indexOf('Email');
    
    const financeDirector = data.find(row =>
      row[roleCol] && row[roleCol].toString().trim() === 'Finance Dir'
    );
    const financeDirectorEmail = financeDirector ? financeDirector[emailCol] : '';
    
    // Send email
    const recipients = [ACTIVE_CAMPAIGN_MANAGER_EMAIL];
    if (financeDirectorEmail) {
      recipients.push(financeDirectorEmail);
    }
    
    MailApp.sendEmail({
      to: recipients.join(','),
      subject: `New ${incentiveType} Incentive Submission - ${clubs.join(', ')}`,
      body: emailBody,
      htmlBody: emailBody.replace(/\n/g, '<br>')
    });
    
    console.log('Email notification sent successfully');
    
  } catch (error) {
    console.error('Error sending email notification:', error);
  }
}


/**
 * Verifies submission data completeness and certificate generation
 * @param {Sheet} submissionSheet - Submission sheet to verify
 * @param {number} expectedClubCount - Expected number of clubs
 * @param {string} submissionSheetUrl - URL of submission sheet
 * @param {Object} submissionDetails - Original submission details
 * @returns {boolean} True if verification passed
 */
function verifySubmissionData(submissionSheet, expectedClubCount, submissionSheetUrl, submissionDetails) {
  console.log('=== Starting Verification ===');
  
  const data = submissionSheet.getDataRange().getValues();
  const headers = data[0];
  const dataRows = data.slice(1); // Skip header
  
  const errors = [];
  
  // Verify number of rows matches number of clubs
  if (dataRows.length !== expectedClubCount) {
    errors.push(`Expected ${expectedClubCount} clubs, but found ${dataRows.length} rows in submission sheet`);
  }
  
  // Required columns to check
  const requiredColumns = [
    'Incentive Type',
    'Club Names',
    'Award Date',
    'Expiry Date',
    'Award Name',
    'Award Amount',
    'Voucher Code',
    'President Email Address',
    'Treasurer Email Address',
    'Certificate',
    'Claimed Status',
    'Division Director Email',
    'Area Director Email',
    'Finance Director Email',
    'Incentives Director Email',
    'D91incentives Email'
  ];
  
  // Check if all required columns exist
  const missingColumns = requiredColumns.filter(col => headers.indexOf(col) === -1);
  if (missingColumns.length > 0) {
    errors.push(`Missing columns: ${missingColumns.join(', ')}`);
  }
  
  // Check each row for empty required values
  dataRows.forEach((row, index) => {
    const rowNum = index + 2; // +2 because index is 0-based and row 1 is header
    const rowErrors = [];
    
    requiredColumns.forEach(colName => {
      const colIdx = headers.indexOf(colName);
      if (colIdx !== -1) {
        const value = row[colIdx];
        if (value === null || value === undefined || value.toString().trim() === '') {
          rowErrors.push(colName);
        }
      }
    });
    
    if (rowErrors.length > 0) {
      errors.push(`Row ${rowNum} (${row[headers.indexOf('Club Names')] || 'Unknown Club'}): Missing values in ${rowErrors.join(', ')}`);
    }
  });
  
  // Count certificates generated
  const certColIdx = headers.indexOf('Certificate');
  let certificatesGenerated = 0;
  if (certColIdx !== -1) {
    certificatesGenerated = dataRows.filter(row => 
      row[certColIdx] && row[certColIdx].toString().trim() !== ''
    ).length;
  }
  
  if (certificatesGenerated !== expectedClubCount) {
    errors.push(`Expected ${expectedClubCount} certificates, but only ${certificatesGenerated} were generated`);
  }
  
  // If there are errors, send notification email
  if (errors.length > 0) {
    console.error('Verification failed with errors:', errors);
    sendVerificationErrorEmail(errors, submissionSheetUrl, submissionDetails);
    return false;
  }
  
  console.log('✓ Verification passed successfully');
  return true;
}

/**
 * Sends verification error email to administrators
 * @param {Array} errors - Array of error messages
 * @param {string} submissionSheetUrl - URL of submission sheet
 * @param {Object} submissionDetails - Submission details
 */
function sendVerificationErrorEmail(errors, submissionSheetUrl, submissionDetails) {
  try {
    const subject = `⚠️ Incentive Submission Verification Failed - ${submissionDetails.incentiveType}`;
    
    const emailBody = `
<h2>Submission Verification Failed</h2>

<p><strong>Incentive Type:</strong> ${submissionDetails.incentiveType}</p>
<p><strong>Clubs:</strong> ${submissionDetails.clubs.join(', ')}</p>
<p><strong>Expected Club Count:</strong> ${submissionDetails.clubs.length}</p>
<p><strong>Submission Time:</strong> ${new Date().toLocaleString()}</p>

<h3>Errors Found:</h3>
<ul>
${errors.map(error => `<li>${error}</li>`).join('\n')}
</ul>

<p><strong>Submission Sheet:</strong> <a href="${submissionSheetUrl}">${submissionSheetUrl}</a></p>

<p>Please review and correct the issues in the submission sheet.</p>

<hr>
<p><em>This is an automated message from the Club Incentive Certificate Generation System.</em></p>
    `;
    
    MailApp.sendEmail({
      to: VERIFICATION_EMAIL_RECIPIENTS.join(','),
      subject: subject,
      htmlBody: emailBody
    });
    
    console.log('Verification error email sent to:', VERIFICATION_EMAIL_RECIPIENTS.join(', '));
    
  } catch (error) {
    console.error('Error sending verification email:', error);
  }
}

/**
 * Formats a Date object as a day and date string
 * @param {Date} dateObj - Date object to format
 * @returns {string} Formatted date string
 */
function dayWithDateFromDateObject(dateObj) {
  if (!(dateObj instanceof Date)) {
    return dateObj;
  }
  
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  const dayStr = days[dateObj.getDay()];
  const dd = dateObj.getDate();
  const mmm = months[dateObj.getMonth()]; // Months are 0-based
  const yyyy = dateObj.getFullYear();
  
  return `${dayStr}, ${dd} ${mmm} ${yyyy}`;
}