const SLIDE_TEMPLATE_ID = 'PROVIDE_YOUR_SLIDE_TEMPLATE_ID_HERE';
const OFFICERS_SHEET_ID = 'PROVIDE_YOUR_OFFICERS_SHEET_ID_HERE'; 
const OFFICERS_SHEET_NAME = 'Club Officer';
const FINAL_SHEET_LINK = 'Final Certificates';

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
  
  // Ensure required columns exist
  ensureColumn(sheet, FINAL_SHEET_LINK);
  
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
  
  if (incentiveType === 'CGD') {
    newHeaders.push('VPM Email Address', 'Treasurer Email Address', 'President Email Address');
  } else if (incentiveType === 'PQD') {
    newHeaders.push('VPE Email Address', 'Treasurer Email Address', 'President Email Address');
  }
  
  newHeaders.push('Certificate Link', 'Claimed Status');
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
  // Write certificate link
  const certColIdx = headers.indexOf('Certificate Link');
  if (certColIdx !== -1) {
    sheet.getRange(rowIdx, certColIdx + 1).setValue(imgUrl);
    console.log(`Certificate URL written to column ${certColIdx + 1}`);
  }
  
  // Set claimed status
  const claimedColIdx = headers.indexOf('Claimed Status');
  if (claimedColIdx !== -1) {
    sheet.getRange(rowIdx, claimedColIdx + 1).setValue('Unclaimed');
    console.log(`Claimed status set to 'Unclaimed'`);
  }
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
 * Gets required officer types for incentive type
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
 * Formats a Date object as a day and date string
 * @param {Date} dateObj - Date object to format
 * @returns {string} Formatted date string
 */
function dayWithDateFromDateObject(dateObj) {
  if (!(dateObj instanceof Date)) {
    return dateObj;
  }
  
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const dayStr = days[dateObj.getDay()];
  const dd = String(dateObj.getDate()).padStart(2, '0');
  const mm = String(dateObj.getMonth() + 1).padStart(2, '0'); // Months are 0-based
  const yyyy = dateObj.getFullYear();
  
  return `${dayStr}, ${dd}-${mm}-${yyyy}`;
}