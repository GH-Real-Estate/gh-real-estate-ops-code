# Approved discovery baselines

The promotion workflow writes the most recently reviewed discovery snapshot for each
domain here. Scheduled scans compare official indexes against these snapshots.

Do not edit a snapshot manually. Promote a fully resolved candidate through a separate
review pull request.

Each snapshot must equal the unique tip of its domain's immutable release chain. The
offline authority validator rejects a manually edited tip, a missing predecessor, or a
forked chain.
