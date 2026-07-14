# Reviewed discovery releases

The protected promotion workflow writes immutable, reviewed discovery evidence here.
These releases establish what the discovery monitor has reviewed; they do not replace
official source text or independently certify legal or GAAP compliance.

These evidence releases and their snapshots are not production authority inputs.
Production projects should pin a separately approved legal/accounting release commit or
tag and check the domain `CURRENT_STATUS.json` before making a currentness claim.

Every later release names the SHA-256 of the prior reviewed snapshot in its candidate's
`approved_baseline`. Releases must form one chain per domain with one bootstrap root,
one tip, and nondecreasing approval dates; forks, backdated children, and unarchived
predecessors fail required offline validation.
