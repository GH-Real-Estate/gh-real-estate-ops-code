"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const candidates = [
  path.resolve(__dirname, "../../../.github/workflows/ci-failure-response.yml"),
  path.resolve(__dirname, "ci-failure-response.yml"),
];
const workflowPath = candidates.find((candidate) => fs.existsSync(candidate));

test("workflow supports only manual simulation and preserves security controls", () => {
  assert.ok(workflowPath, "ci-failure-response.yml was not found");
  const content = fs.readFileSync(workflowPath, "utf8");
  for (const name of [
    "Accounting Authority Checks",
    "Accounting Authority Review Calendar",
    "Authority Discovery",
    "Authority Refresh Checks",
    "Authority Release Promotion",
    "Legal Release Checks",
    "Legal Source Monitor",
    "Repo Checks",
  ]) {
    assert.match(content, new RegExp(name));
  }
  for (const line of content.split("\n").filter((entry) => entry.trim().startsWith("uses:"))) {
    assert.match(line, /@[0-9a-f]{40}(?:\s+#.*)?$/);
  }
  assert.match(content, /^  workflow_dispatch:/m);
  assert.match(content, /^  pull_request:/m);
  assert.match(content, /^  push:/m);
  assert.doesNotMatch(content, /^  workflow_run:/m);
  assert.match(
    content,
    /github\.event_name == 'workflow_dispatch' &&\s*github\.ref == format\('refs\/heads\/\{0\}', github\.event\.repository\.default_branch\)/,
  );
  assert.match(content, /ref: \$\{\{ github\.sha \}\}/);
  assert.match(content, /git ls-remote --exit-code origin/);
  assert.match(content, /persist-credentials: false/);
  assert.match(content, /actions:\s*read/);
  assert.match(content, /issues:\s*write/);
  assert.match(content, /queue:\s*max/);
  assert.doesNotMatch(content, /group:.*workflow_run/);
  assert.doesNotMatch(content, /workflow_run\.head_sha/);
  assert.doesNotMatch(content, /download-artifact/);
  assert.doesNotMatch(content, /pull_request_target/);
  assert.doesNotMatch(content, /contents:\s*write/);
});
