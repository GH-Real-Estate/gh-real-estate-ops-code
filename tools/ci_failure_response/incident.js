"use strict";

const crypto = require("node:crypto");

const MONITORED_WORKFLOWS = Object.freeze([
  "Accounting Authority Checks",
  "Accounting Authority Review Calendar",
  "Authority Discovery",
  "Authority Refresh Checks",
  "Authority Release Promotion",
  "Legal Release Checks",
  "Legal Source Monitor",
  "Repo Checks",
]);

const INCIDENT_CONCLUSIONS = new Set([
  "action_required",
  "failure",
  "startup_failure",
  "timed_out",
]);
const RECOVERY_CONCLUSION = "success";
const INCIDENT_LABEL = "ci-incident";
const ATTENTION_LABEL = "codex-attention";
const MARKER_VERSION = "v1";

function oneLine(value, maxLength = 160) {
  const normalized = String(value ?? "")
    .replace(/[\u0000-\u001f\u007f]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return (normalized || "unknown").slice(0, maxLength);
}

function inlineCode(value, maxLength = 160) {
  return `\`${oneLine(value, maxLength).replace(/`/g, "'")}\``;
}

function safeGithubUrl(value, repository) {
  try {
    const url = new URL(String(value));
    const expectedPrefix = `/${repository}/actions/runs/`;
    if (
      url.protocol === "https:" &&
      url.hostname === "github.com" &&
      url.pathname.startsWith(expectedPrefix)
    ) {
      return url.toString();
    }
  } catch {
    // Untrusted event URLs are rendered as unavailable rather than guessed.
  }
  return null;
}

function positiveInteger(value, fallback = 0) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isSafeInteger(parsed) && parsed >= 0 ? parsed : fallback;
}

function monitoredWorkflow(name) {
  return MONITORED_WORKFLOWS.includes(name);
}

function normalizeRun(context, inputs = {}) {
  const repository = `${context.repo.owner}/${context.repo.repo}`;

  if (context.eventName === "workflow_run") {
    const run = context.payload.workflow_run;
    if (!run || typeof run !== "object") {
      throw new Error("workflow_run payload is missing workflow_run");
    }

    const workflowName = oneLine(run.name, 120);
    if (!monitoredWorkflow(workflowName)) {
      return null;
    }

    return {
      namespace: "real",
      workflowId: oneLine(run.workflow_id, 80),
      workflowName,
      repository,
      headRepository: oneLine(run.head_repository?.full_name || repository, 160),
      branch: oneLine(run.head_branch || "unknown", 200),
      headSha: oneLine(run.head_sha || "unknown", 64),
      conclusion: oneLine(run.conclusion, 40).toLowerCase(),
      runId: positiveInteger(run.id),
      runAttempt: positiveInteger(run.run_attempt, 1),
      createdAt: oneLine(run.created_at || "", 40),
      actor: oneLine(run.actor?.login || "unknown", 80),
      url: safeGithubUrl(run.html_url, repository),
    };
  }

  if (context.eventName === "workflow_dispatch") {
    const workflowName = oneLine(inputs.workflowName, 120);
    if (!monitoredWorkflow(workflowName)) {
      throw new Error(`simulation requested an unmonitored workflow: ${workflowName}`);
    }

    return {
      namespace: "simulation",
      workflowId: `simulation:${workflowName}:${oneLine(inputs.scenarioKey, 80)}`,
      workflowName,
      repository,
      headRepository: repository,
      branch: oneLine(inputs.headBranch || "simulation/ci-failure-response", 200),
      headSha: oneLine(context.sha || "simulation", 64),
      conclusion: oneLine(inputs.conclusion, 40).toLowerCase(),
      runId: positiveInteger(context.runId),
      runAttempt: positiveInteger(context.runAttempt, 1),
      createdAt: new Date().toISOString(),
      actor: oneLine(context.actor || "manual-dispatch", 80),
      url: safeGithubUrl(
        `https://github.com/${repository}/actions/runs/${positiveInteger(context.runId)}`,
        repository,
      ),
    };
  }

  return null;
}

function incidentKey(run) {
  const material = [
    MARKER_VERSION,
    run.namespace,
    run.workflowId,
    run.headRepository,
    run.branch,
  ].join("\n");
  return crypto.createHash("sha256").update(material).digest("hex").slice(0, 32);
}

function incidentMarker(key) {
  return `<!-- ci-failure-response:${MARKER_VERSION}:key:${key} -->`;
}

function runMarker(run) {
  const state = {
    runId: run.runId,
    runAttempt: run.runAttempt,
    createdAt: run.createdAt,
    conclusion: run.conclusion,
  };
  const encoded = Buffer.from(JSON.stringify(state), "utf8").toString("base64url");
  return `<!-- ci-failure-response:${MARKER_VERSION}:state:${encoded} -->`;
}

function parseRunMarker(body) {
  const match = String(body || "").match(
    /<!-- ci-failure-response:v1:state:([A-Za-z0-9_-]+) -->/,
  );
  if (!match) return null;
  try {
    const parsed = JSON.parse(Buffer.from(match[1], "base64url").toString("utf8"));
    return {
      runId: positiveInteger(parsed.runId),
      runAttempt: positiveInteger(parsed.runAttempt, 1),
      createdAt: oneLine(parsed.createdAt || "", 40),
      conclusion: oneLine(parsed.conclusion, 40).toLowerCase(),
    };
  } catch {
    return null;
  }
}

function compareObservations(left, right) {
  const leftTime = Date.parse(left.createdAt || "");
  const rightTime = Date.parse(right.createdAt || "");
  if (Number.isFinite(leftTime) && Number.isFinite(rightTime) && leftTime !== rightTime) {
    return leftTime > rightTime ? 1 : -1;
  }
  if (left.runId !== right.runId) return left.runId > right.runId ? 1 : -1;
  if (left.runAttempt !== right.runAttempt) {
    return left.runAttempt > right.runAttempt ? 1 : -1;
  }
  return 0;
}

function sameObservation(left, right) {
  return (
    left.runId === right.runId &&
    left.runAttempt === right.runAttempt &&
    left.conclusion === right.conclusion
  );
}

function issueTitle(run) {
  const simulation = run.namespace === "simulation" ? " [SIMULATION]" : "";
  return oneLine(`CI Incident${simulation}: ${run.workflowName} on ${run.branch}`, 240);
}

function renderBody(run, key) {
  const runLink = run.url ? `[Open GitHub Actions run](${run.url})` : "Run link unavailable";
  const status = run.conclusion === RECOVERY_CONCLUSION ? "Recovered" : "Failure detected";
  return [
    incidentMarker(key),
    runMarker(run),
    `## ${status}`,
    "",
    "A monitored GitHub Actions workflow reported this state. The responder used trusted code from the default branch and did **not** check out or execute the failed revision or its artifacts.",
    "",
    `- **Workflow:** ${inlineCode(run.workflowName, 120)}`,
    `- **Conclusion:** ${inlineCode(run.conclusion, 40)}`,
    `- **Repository / branch:** ${inlineCode(`${run.headRepository}:${run.branch}`, 260)}`,
    `- **Head SHA:** ${inlineCode(run.headSha, 64)}`,
    `- **Run / attempt:** ${inlineCode(`${run.runId} / ${run.runAttempt}`, 60)}`,
    `- **Actor:** ${inlineCode(run.actor, 80)}`,
    `- **Observed:** ${inlineCode(run.createdAt, 40)}`,
    `- **Evidence:** ${runLink}`,
    "",
    "### Remediation guardrails",
    "",
    "Codex may diagnose this incident and prepare a focused draft pull request for a low-risk code defect. It must not directly push to `main`, auto-merge, weaken a check, expose secrets/PII, or autonomously change legal currentness, accounting conclusions, tax treatment, payments, leases, tenants, notices, deposits, security controls, or workflow permissions.",
    "",
    "@GHRealEstate",
  ].join("\n");
}

async function ensureLabels(github, owner, repo) {
  const definitions = [
    { name: INCIDENT_LABEL, color: "B60205", description: "Current or recovered GitHub Actions incident" },
    { name: ATTENTION_LABEL, color: "5319E7", description: "Queued for guarded Codex diagnosis" },
  ];
  for (const definition of definitions) {
    try {
      await github.rest.issues.getLabel({ owner, repo, name: definition.name });
    } catch (error) {
      if (error.status !== 404) throw error;
      await github.rest.issues.createLabel({ owner, repo, ...definition });
    }
  }
}

async function findIncident(github, owner, repo, key) {
  const issues = await github.paginate(github.rest.issues.listForRepo, {
    owner,
    repo,
    state: "all",
    labels: INCIDENT_LABEL,
    per_page: 100,
  });
  const marker = incidentMarker(key);
  return issues.find((issue) => !issue.pull_request && String(issue.body || "").includes(marker)) || null;
}

async function hasNewerSuccessfulRun(github, owner, repo, run, core) {
  if (run.namespace !== "real") return false;
  try {
    const response = await github.rest.actions.listWorkflowRuns({
      owner,
      repo,
      workflow_id: run.workflowId,
      branch: run.branch,
      per_page: 20,
    });
    return (response.data.workflow_runs || []).some((candidate) => {
      if (candidate.conclusion !== RECOVERY_CONCLUSION) return false;
      if (oneLine(candidate.head_repository?.full_name || run.repository, 160) !== run.headRepository) {
        return false;
      }
      return compareObservations(
        {
          runId: positiveInteger(candidate.id),
          runAttempt: positiveInteger(candidate.run_attempt, 1),
          createdAt: oneLine(candidate.created_at || "", 40),
        },
        run,
      ) > 0;
    });
  } catch (error) {
    // Incident publication remains available if the optional freshness query
    // is temporarily unavailable. A later success will still close the issue.
    core.warning(`Could not verify newer workflow runs: ${oneLine(error.message, 160)}`);
    return false;
  }
}

async function handleIncident({ github, context, core = console, inputs = {} }) {
  const run = normalizeRun(context, inputs);
  if (!run) {
    core.info("No monitored workflow observation to process.");
    return { action: "ignored", reason: "unmonitored-event" };
  }

  const isIncident = INCIDENT_CONCLUSIONS.has(run.conclusion);
  const isRecovery = run.conclusion === RECOVERY_CONCLUSION;
  if (!isIncident && !isRecovery) {
    core.info(`Ignoring non-incident conclusion: ${run.conclusion}`);
    return { action: "ignored", reason: "non-incident-conclusion" };
  }

  const { owner, repo } = context.repo;
  const key = incidentKey(run);
  await ensureLabels(github, owner, repo);
  const existing = await findIncident(github, owner, repo, key);
  if (isIncident && !existing && await hasNewerSuccessfulRun(github, owner, repo, run, core)) {
    core.info("Ignoring a failure superseded by a newer successful run.");
    return { action: "ignored", reason: "superseded-failure" };
  }
  const previous = existing ? parseRunMarker(existing.body) : null;
  if (previous) {
    // Delivery identity is the run, attempt, and conclusion. GitHub may
    // redeliver the same observation with non-identical timestamp text.
    if (sameObservation(run, previous)) {
      core.info("Ignoring duplicate workflow delivery.");
      return { action: "ignored", reason: "duplicate-delivery", issue: existing.number };
    }
    const order = compareObservations(run, previous);
    if (order < 0) {
      core.info("Ignoring an observation older than the incident state.");
      return { action: "ignored", reason: "stale-observation", issue: existing.number };
    }
  }

  const body = renderBody(run, key);
  const labels = [INCIDENT_LABEL, ATTENTION_LABEL];

  if (isIncident && !existing) {
    const created = await github.rest.issues.create({
      owner,
      repo,
      title: issueTitle(run),
      body,
      labels,
    });
    core.info(`Created CI incident #${created.data.number}.`);
    return { action: "created", issue: created.data.number };
  }

  if (isIncident) {
    await github.rest.issues.update({
      owner,
      repo,
      issue_number: existing.number,
      title: issueTitle(run),
      body,
      labels,
      state: "open",
    });
    await github.rest.issues.createComment({
      owner,
      repo,
      issue_number: existing.number,
      body: `A newer failure was observed for run ${inlineCode(run.runId, 30)}, attempt ${inlineCode(run.runAttempt, 10)}. ${run.url ? `[Open run](${run.url})` : "Run link unavailable."}`,
    });
    core.info(`Updated CI incident #${existing.number}.`);
    return { action: "updated", issue: existing.number };
  }

  if (!existing || existing.state !== "open") {
    core.info("Recovery has no matching open incident.");
    return { action: "ignored", reason: "no-open-incident", issue: existing?.number };
  }

  await github.rest.issues.update({
    owner,
    repo,
    issue_number: existing.number,
    title: issueTitle(run),
    body,
    labels,
    state: "closed",
    state_reason: "completed",
  });
  await github.rest.issues.createComment({
    owner,
    repo,
    issue_number: existing.number,
    body: `Recovery confirmed by run ${inlineCode(run.runId, 30)}, attempt ${inlineCode(run.runAttempt, 10)}. ${run.url ? `[Open run](${run.url})` : "Run link unavailable."}`,
  });
  core.info(`Closed recovered CI incident #${existing.number}.`);
  return { action: "closed", issue: existing.number };
}

module.exports = {
  ATTENTION_LABEL,
  INCIDENT_CONCLUSIONS,
  INCIDENT_LABEL,
  MONITORED_WORKFLOWS,
  compareObservations,
  hasNewerSuccessfulRun,
  handleIncident,
  incidentKey,
  incidentMarker,
  normalizeRun,
  oneLine,
  parseRunMarker,
  renderBody,
};

