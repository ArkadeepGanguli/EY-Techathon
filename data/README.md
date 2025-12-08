# Data Directory - Secure Storage

This directory contains sensitive customer data and generated documents. **Do not commit any files from this directory to version control.**

## Directory Structure

```
data/
├── sanction_letters/     # Generated PDF sanction letters
│   └── .gitkeep         # Keeps directory in git
├── .gitignore           # Prevents committing sensitive files
└── README.md            # This file
```

## Sanction Letters

The `sanction_letters/` folder stores all generated PDF sanction letters for approved loans.

### File Naming Convention
- Format: `sanction_<SANCTION_ID>.pdf`
- Example: `sanction_SAN2025120712ABCDEF.pdf`

### Security Measures

1. **Git Ignore**: All PDF files are excluded from version control
2. **Secure Directory**: Only the directory structure is tracked
3. **Access Control**: Ensure proper file system permissions in production
4. **API Protection**: Downloads require valid session ID

### Production Deployment

For production environments, consider:

1. **Cloud Storage**: Use AWS S3, Azure Blob Storage, or similar
2. **Encryption**: Encrypt PDFs at rest and in transit
3. **Access Logs**: Track all downloads for audit purposes
4. **Automatic Cleanup**: Delete old sanction letters after a retention period
5. **Backup**: Regular backups of generated documents

### API Endpoints

- **Generate**: `POST /api/sanction/generate/{session_id}`
- **Download**: `GET /api/sanction/download/{sanction_id}`

### Maintenance

To clean up old sanction letters:

```bash
# Delete sanction letters older than 90 days (example)
find data/sanction_letters -name "*.pdf" -type f -mtime +90 -delete
```

## Important Notes

⚠️ **Never commit PDF files to git**
⚠️ **Ensure proper permissions (e.g., 700) in production**
⚠️ **Implement retention policies for data compliance**
⚠️ **Use HTTPS for all API communications**

---

Last Updated: December 7, 2025
