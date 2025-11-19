# Club Incentive Certificate Generation System - Architecture & Flow

## System Overview

This automation system processes club incentive form submissions and automatically generates personalized certificates for Toastmasters clubs. The system integrates multiple Google Workspace services to create a complete end-to-end workflow.

## Architecture Components

### Core Google Workspace Services
- **Google Forms**: Initial data collection
- **Google Sheets**: Data storage and processing
- **Google Slides**: Certificate template and generation
- **Google Drive**: File storage and organization
- **Gmail**: Email notifications and distribution
- **Google Apps Script**: Automation engine

### Data Sources
1. **Form Responses Sheet**: Primary input data
2. **Officers Sheet**: Club officer email lookup
3. **District Leaders Sheet**: Division/Area director emails
4. **Email Template Document**: Email communication templates
5. **Certificate Slide Template**: Certificate design template

## System Flow Diagram

```
┌─────────────────┐
│   Form Submit   │ ──► Trigger: onFormSubmit()
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Extract Details │ ──► Parse clubs, incentive type
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Create New      │ ──► Generate submission spreadsheet
│ Spreadsheet     │     with enhanced headers
└─────────────────┘
          │
          ▼
┌─────────────────┐
│ Process Each    │ ──► For each club:
│ Club            │     • Lookup officer emails
└─────────────────┘     • Create individual row
          │
          ▼
┌─────────────────┐
│ Generate        │ ──► For each club:
│ Certificates    │     • Copy slide template
└─────────────────┘     • Replace placeholders
          │              • Export as PNG
          ▼              • Save to Drive folder
┌─────────────────┐
│ Populate        │ ──► Lookup and add:
│ District        │     • Division Director email
│ Leader Emails   │     • Area Director email
└─────────────────┘     • Finance Director email
          │              • Incentives Director email
          ▼
┌─────────────────┐
│ Verification    │ ──► Validate:
│ Process         │     • Data completeness
└─────────────────┘     • Certificate generation
          │              • Email population
          ▼
┌─────────────────┐
│ Email           │ ──► Send notifications:
│ Notifications   │     • Success emails
└─────────────────┘     • Error alerts
```

## Detailed Process Flow

### 1. Form Submission Processing
```
onFormSubmit(e) → processSubmission(sheet, rowIdx)
│
├── Extract submission details
├── Identify clubs (comma-separated parsing)
├── Determine incentive type (CGD/PQD)
└── Validate input data
```

### 2. Submission Spreadsheet Creation
```
createSubmissionSpreadsheet()
│
├── Create new Google Spreadsheet
├── Generate enhanced headers
│   ├── Original form columns
│   ├── Claimed Status dropdown
│   ├── Officer email columns (VPM/VPE, Treasurer, President)
│   └── District leader email columns
├── Apply styling and formatting
├── Set sharing permissions
└── Return spreadsheet object
```

### 3. Club Processing Loop
```
For each club in submission:
│
├── processClubs()
│   ├── Create individual row for club
│   ├── lookupOfficerEmails()
│   │   ├── Query Officers Sheet
│   │   ├── Filter by club name
│   │   ├── Map office types to emails
│   │   └── Return email mappings
│   └── Append row to submission sheet
│
└── Track processed rows for certificate generation
```

### 4. Certificate Generation Pipeline
```
generateCertificates()
│
For each processed club row:
├── processCertificateRow()
│   ├── createAwardFolder()
│   │   ├── Generate folder name (Award Name + Date)
│   │   └── Create/find Drive folder
│   │
│   ├── generateCertificateSlide()
│   │   ├── Copy slide template
│   │   ├── Replace all placeholders <<COLUMN_NAME>>
│   │   └── Save modified slide
│   │
│   ├── saveCertificateImage()
│   │   ├── Export slide as PNG
│   │   ├── Save to award folder
│   │   ├── Set sharing permissions
│   │   └── Return image URL
│   │
│   ├── writeCertificateData()
│   │   ├── Write certificate URL to sheet
│   │   └── Set claimed status to 'Unclaimed'
│   │
│   └── populateDistrictLeaderEmails()
│       ├── Get club division/area
│       ├── Query District Leaders Sheet
│       ├── Match by division/area
│       └── Write leader emails to sheet
│
└── Clean up temporary files
```

### 5. District Leader Email Population
```
populateDistrictLeaderEmails()
│
├── getClubDivisionAndArea()
│   ├── Query Officers Sheet
│   ├── Find club record
│   └── Extract division/area
│
├── lookupDistrictLeaderEmails()
│   ├── Query District Leaders Sheet
│   ├── Find Division Director (Div Dir/AD = "Div")
│   ├── Find Area Director (Div Dir/AD = "AD")
│   ├── Find Finance Director (Div Dir/AD = "Finance Dir")
│   ├── Determine Incentives Director by type
│   └── Add D91 Incentives email
│
└── writeDistrictLeaderEmails()
    └── Write all emails to respective columns
```

### 6. Verification & Quality Control
```
verifySubmissionData()
│
├── Check row count matches club count
├── Validate required columns exist
├── Check for empty required values
├── Verify certificate generation count
│
├── If verification passes:
│   └── Allow email notifications
│
└── If verification fails:
    ├── Log errors
    ├── sendVerificationErrorEmail()
    └── Skip success notifications
```

### 7. Email Notification System
```
Email Notifications:
│
├── sendSubmissionNotification()
│   ├── Load email template
│   ├── Replace placeholders
│   ├── Send to campaign manager
│   └── CC finance director
│
├── sendCertificateEmails() [Currently disabled]
│   ├── For each club row:
│   ├── sendIndividualCertificateEmail()
│   │   ├── Extract recipient emails
│   │   ├── Prepare personalized content
│   │   ├── TO: President, Treasurer, VPM/VPE
│   │   ├── CC: District leaders
│   │   └── BCC: D91incentives
│   └── Log email results
│
└── sendVerificationErrorEmail()
    ├── Format error details
    ├── Include submission link
    └── Send to administrators
```

## Data Flow Architecture

### Input Data Sources
```
Google Form Submission
├── Timestamp
├── Club Names (comma-separated)
├── Incentive Type (CGD/PQD)
├── Award Name
├── Award Date
├── Expiry Date
├── Award Amount
├── Voucher Code
└── Additional metadata
```

### Lookup Tables
```
Officers Sheet (OFFICERS_SHEET_ID)
├── Club Name
├── Office (President, Treasurer, VPM, VPE)
├── Email Address
├── Division
└── Area

District Leaders Sheet (DISTRICT_LEADERS_SHEET_ID)
├── Name
├── Div Dir/AD (role identifier)
├── Division
├── Area
└── Email
```

### Output Generated
```
Submission Spreadsheet
├── Enhanced form data
├── Individual club rows
├── Officer email mappings
├── District leader emails
├── Certificate URLs
├── Claimed status tracking
└── Complete audit trail

Drive Folder Structure
├── Award Folders (by name and date)
│   ├── Certificate slides
│   └── Certificate PNG images
└── Submission spreadsheets

Email Communications
├── Success notifications
├── Error alerts
└── Certificate distribution emails
```

## Key Features & Capabilities

### 1. **Multi-Club Processing**
- Handles comma-separated club lists
- Creates individual records for each club
- Maintains data integrity across clubs

### 2. **Dynamic Officer Lookup**
- Supports different officer types by incentive
- CGD: President, Treasurer, VPM
- PQD: President, Treasurer, VPE

### 3. **Automated Certificate Generation**
- Template-based slide creation
- Dynamic placeholder replacement
- PNG export and Drive storage
- Folder organization by award

### 4. **Hierarchical Email Distribution**
- Club officers (TO)
- District leaders (CC)
- System administrators (BCC)

### 5. **Quality Assurance**
- Data validation and verification
- Error reporting and alerts
- Audit trail maintenance

### 6. **User Experience Enhancements**
- Styled spreadsheets
- Dropdown validations
- Auto-sizing and formatting
- Share link management

## Error Handling & Recovery

### Validation Points
1. **Input Validation**: Form data completeness
2. **Lookup Validation**: Officer/leader email availability
3. **Generation Validation**: Certificate creation success
4. **Output Validation**: Final data verification

### Error Recovery
- Graceful failure handling
- Detailed error logging
- Administrator notifications
- Partial success completion

## Security & Permissions

### Access Control
- Spreadsheet sharing: "Anyone with link" (Edit)
- Certificate images: "Anyone with link" (View)
- Email template: Restricted access

### Data Privacy
- Officer email protection
- Audit trail maintenance
- Temporary file cleanup

## Performance Considerations

### Optimization Strategies
- Batch processing for multiple clubs
- Single sheet reads for lookups
- Efficient template copying
- Cleanup of temporary resources

### Scalability Factors
- Form submission volume
- Club count per submission
- Certificate generation time
- Email delivery limits

## Configuration Management

### Constants & Settings
```javascript
// Core Service IDs
SLIDE_TEMPLATE_ID
OFFICERS_SHEET_ID
DIV_AREA_LEADER_SHEET_ID
EMAIL_TEMPLATE_DOC_ID

// Email Configuration
ACTIVE_CAMPAIGN_MANAGER_EMAIL
VERIFICATION_EMAIL_RECIPIENTS

// Sheet Names
OFFICERS_SHEET_NAME
DISTRICT_LEADERS_SHEET_NAME
```

### Customizable Elements
- Email templates
- Certificate slide designs
- Officer role mappings
- District leader hierarchies
- Notification recipients

This architecture provides a robust, scalable solution for automated club incentive certificate generation with comprehensive error handling, verification, and communication capabilities.