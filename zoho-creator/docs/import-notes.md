# Zoho Creator Import Notes

Store only sanitized `.ds` exports in:

```text
zoho-creator/exports/
```

Do not store:

- Live tenant data.
- Real portal users.
- Real payment records.
- Signed documents.
- Production photos.
- Maintenance records with tenant PII.

When adding a `.ds` export, document:

- Export date.
- Whether it contains structure only.
- Known import errors.
- Smoke test result.
- Whether it was imported successfully.
