# Upload Or Rename Existing Repo

## Best path from the current screenshot

Your screenshot appears to show the repo already exists under the organization:

```text
GH-Real-Estate/gh-real-estate
```

So do this:

1. Open the repo.
2. Go to `Settings`.
3. Under `Repository name`, rename it to:

```text
gh-real-estate-ops-code
```

4. Save.
5. Confirm the final URL is:

```text
https://github.com/GH-Real-Estate/gh-real-estate-ops-code
```

## If the repo is still under your personal account

If the repo URL starts with:

```text
https://github.com/GHRealEstate/...
```

then it is personal-owned. Transfer it into the org instead of deleting it if it has useful commits/files.

## If you have both repos

If both exist:

```text
GHRealEstate/gh-real-estate-ops-code
GH-Real-Estate/gh-real-estate-ops-code
```

Keep the org-owned one. Delete or archive the personal one only after confirming no useful files are missing.

## Uploading this starter package using the GitHub website

1. Download and unzip this starter package.
2. Open the org repo in GitHub.
3. Click `Add file` → `Upload files`.
4. Drag the contents of the unzipped folder into GitHub.
5. Commit directly to `main` only for this first starter upload.
6. After this first upload, use branches and pull requests for material changes.

## Uploading with Git

From inside the unzipped starter folder:

```bash
git init
git branch -M main
git add .
git commit -m "Initial GH Real Estate ops code structure"
git remote add origin https://github.com/GH-Real-Estate/gh-real-estate-ops-code.git
git push -u origin main
```

If the repo already has one starter commit, use:

```bash
git clone https://github.com/GH-Real-Estate/gh-real-estate-ops-code.git
cd gh-real-estate-ops-code
# copy the starter files into this folder, then:
git add .
git commit -m "Add revised GH Real Estate ops code structure"
git push
```
