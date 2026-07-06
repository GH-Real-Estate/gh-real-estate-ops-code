# Code Review Checklist

## Blockers

- Hardcoded secrets, credentials, tokens, or live tenant data
- Duplicate financial actions
- Missing null checks on external/Zoho responses
- Missing pagination for multi-record fetches
- Automation that can rerun and create duplicates
- Production behavior change without deployment warning

## High Priority

- Incorrect date, proration, rent, late fee, invoice, payment, or deposit logic
- Unclear Zoho module names, field names, or connection names
- Poor error handling around external APIs
- Lack of dry-run or safe failure behavior for money-related workflows

## Medium Priority

- Unclear file organization
- Missing operator notes
- Missing examples or fixtures
- Unnecessary dependencies
- Over-engineered abstractions
