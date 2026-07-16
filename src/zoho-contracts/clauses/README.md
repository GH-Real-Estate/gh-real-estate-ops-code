# Governed Clause Records

Store every repository-managed Zoho Contracts clause definition in this directory or a domain subdirectory with the suffix `.clause.json`. The authoring validator recursively scans that exact pattern; a clause stored elsewhere is not governed and must not be treated as production-ready.

Start from `../templates/clause-definition.template.json` and follow `../schemas/clause-definition.schema.json`.

Each record must:

- use one exact Clause Type from the 16-item master list;
- include a stable Clause Name and a neutral library Question ending in `?`;
- contain exactly one standard language variant and only approved alternatives;
- keep each variant's Clause Title and `Heading 2` rendering instruction separate from its substantive Language blocks;
- label Language blocks as Heading 3, Heading 4, Heading 5, or Normal without skipping heading depth;
- declare every Sign recipient role when its Language contains text tags; and
- keep unverified Zoho API names null and fail closed.

Do not store tenant names, addresses, emails, signatures, signed contracts, accommodation evidence, payment data, private documents, or attorney-client material here. Clause validation confirms structure and approved syntax; it does not substitute for legal review.

Run:

```powershell
python src/zoho-contracts/scripts/validate_contract_authoring_standard.py
python -m unittest discover -s src/zoho-contracts/tests -p 'test_*.py' -v
```
