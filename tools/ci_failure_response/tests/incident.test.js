"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

const responder = require("../incident.js");

function createFakeGithub() {
  const state = {
    labels: new Set(),
    issues: [],
    comments: [],
    workflowRuns: [],
    nextIssue: 1,
  };

  const issuesApi = {
    async getLabel({ name }) {
      if (!state.labels.has(name)) {
        const error = new Error("not found");
        error.status = 404;
        throw error;
      }
      return { data: { name } };
    },
    async createLabel({ name }) {
      state.labels.add(name);
      return { data: { name } };
    },
    async listForRepo() {
      return { data: state.issues };
    },
    async create({ title, body, labels }) {
      const issue = {
        number: state.nextIssue++,
        title,
        body,
        labels: labels.map((name) => ({ name })),
        state: "open",
      };
      state.issues.push(issue);
      return { data: issue };
    },
    async update({ issue_number: number, ...changes }) {
      const issue = state.issues.find((candidate) => candidate.number === number);
      if (!issue) throw new Error(`missing issue ${number}`);
      Object.assign(issue, changes);
      if (changes.labels) {
        issue.labels = changes.labels.map((name) => ({ name }));
      }
      return { data: issue };
    },
    async createComment({ issue_number, body }) {
      state.comments.push({ issue_number, body });
      return { data: { id: state.comments.length, body } };
    },
  };

  return {
    state,
    github: {
      rest: {
        issues: issuesApi,
        actions: {
          async listWorkflowRuns() {
            return { data: { workflow_runs: state.workflowRuns } };
          },
        },
      },
      async paginate(_method, _args) {
        return state.issues;
      },
    },
  };
}

function workflowContext(overrides = {}) {
  const run = {
    id: 100,
    run_attempt: 1,
    workflow_id: 50,
    name: "Repo Checks",
    head_repository: { full_name: "GH-Real-Estate/gh-real-estate-ops-code" },
    head_branch: "main",
    head_sha: "a".repeat(40),
    conclusion: "failure",
    created_at: "2026-07-14T10:00:00Z",
    html_url: "https://github.com/GH-Real-Estate/gh-real-estate-ops-code/actions/runs/100",
    actor: { login: "GHRealEstate" },
    ...overrides,
  };
  return {
    eventName: "workflow_run",
    repo: { owner: "GH-Real-Estate", repo: "gh-real-estate-ops-code" },
    payload: { workflow_run: run },
  };
}

function simulationContext(runId, conclusion) {
  return {
    context: {
      eventName: "workflow_dispatch",
      repo: { owner: "GH-Real-Estate", repo: "gh-real-estate-ops-code" },
      payload: {},
      runId,
      runAttempt: 1,
      sha: "b".repeat(40),
      actor: "GHRealEstate",
    },
    inputs: {
      workflowName: "Repo Checks",
      headBranch: "simulation/ci-failure-response",
      scenarioKey: "smoke-test",
      conclusion,
    },
  };
}

test("failure creates one labeled incident", async () => {
  const { github, state } = createFakeGithub();
  const result = await responder.handleIncident({ github, context: workflowContext() });

  assert.equal(result.action, "created");
  assert.equal(state.issues.length, 1);
  assert.deepEqual([...state.labels].sort(), ["ci-incident", "codex-attention"]);
  assert.match(state.issues[0].body, /did \*\*not\*\* check out or execute/);
});

test("duplicate delivery creates no issue or comment", async () => {
  const { github, state } = createFakeGithub();
  const context = workflowContext();
  await responder.handleIncident({ github, context });
  const result = await responder.handleIncident({ github, context });

  assert.equal(result.reason, "duplicate-delivery");
  assert.equal(state.issues.length, 1);
  assert.equal(state.comments.length, 0);
});

test("newer failure updates and comments on the same incident", async () => {
  const { github, state } = createFakeGithub();
  await responder.handleIncident({ github, context: workflowContext() });
  const newer = workflowContext({ id: 101, created_at: "2026-07-14T10:05:00Z" });
  const result = await responder.handleIncident({ github, context: newer });

  assert.equal(result.action, "updated");
  assert.equal(state.issues.length, 1);
  assert.equal(state.comments.length, 1);
  assert.equal(responder.parseRunMarker(state.issues[0].body).runId, 101);
});

test("successful newer run closes an open incident", async () => {
  const { github, state } = createFakeGithub();
  await responder.handleIncident({ github, context: workflowContext() });
  const recovery = workflowContext({
    id: 102,
    conclusion: "success",
    created_at: "2026-07-14T10:10:00Z",
  });
  const result = await responder.handleIncident({ github, context: recovery });

  assert.equal(result.action, "closed");
  assert.equal(state.issues[0].state, "closed");
  assert.equal(state.issues[0].state_reason, "completed");
  assert.equal(state.comments.length, 1);
});

test("older success cannot close a newer failure", async () => {
  const { github, state } = createFakeGithub();
  await responder.handleIncident({
    github,
    context: workflowContext({ id: 200, created_at: "2026-07-14T11:00:00Z" }),
  });
  const staleRecovery = workflowContext({
    id: 199,
    conclusion: "success",
    created_at: "2026-07-14T10:59:00Z",
  });
  const result = await responder.handleIncident({ github, context: staleRecovery });

  assert.equal(result.reason, "stale-observation");
  assert.equal(state.issues[0].state, "open");
});

test("failure is ignored when the API already reports a newer success", async () => {
  const { github, state } = createFakeGithub();
  state.workflowRuns.push({
    id: 101,
    run_attempt: 1,
    conclusion: "success",
    created_at: "2026-07-14T10:05:00Z",
    head_repository: { full_name: "GH-Real-Estate/gh-real-estate-ops-code" },
  });
  const result = await responder.handleIncident({ github, context: workflowContext() });

  assert.equal(result.reason, "superseded-failure");
  assert.equal(state.issues.length, 0);
});

test("higher attempt for the same run is newer", async () => {
  const { github, state } = createFakeGithub();
  const first = workflowContext({ id: 300, run_attempt: 1 });
  const retry = workflowContext({ id: 300, run_attempt: 2 });
  await responder.handleIncident({ github, context: first });
  const result = await responder.handleIncident({ github, context: retry });

  assert.equal(result.action, "updated");
  assert.equal(responder.parseRunMarker(state.issues[0].body).runAttempt, 2);
});

test("simulation failure and recovery share an isolated key", async () => {
  const { github, state } = createFakeGithub();
  const failure = simulationContext(400, "failure");
  const recovery = simulationContext(401, "success");
  await responder.handleIncident({ github, ...failure });
  const result = await responder.handleIncident({ github, ...recovery });

  assert.equal(result.action, "closed");
  assert.equal(state.issues.length, 1);
  assert.match(state.issues[0].title, /\[SIMULATION\]/);
});

test("simulation cannot close a real incident", async () => {
  const { github, state } = createFakeGithub();
  await responder.handleIncident({ github, context: workflowContext() });
  const recovery = simulationContext(500, "success");
  const result = await responder.handleIncident({ github, ...recovery });

  assert.equal(result.reason, "no-open-incident");
  assert.equal(state.issues[0].state, "open");
});

test("unmonitored workflow and cancelled run are ignored", async () => {
  const { github, state } = createFakeGithub();
  const unmonitored = await responder.handleIncident({
    github,
    context: workflowContext({ name: "Unknown Workflow" }),
  });
  const cancelled = await responder.handleIncident({
    github,
    context: workflowContext({ conclusion: "cancelled" }),
  });

  assert.equal(unmonitored.reason, "unmonitored-event");
  assert.equal(cancelled.reason, "non-incident-conclusion");
  assert.equal(state.issues.length, 0);
});

test("untrusted event text is bounded and inert", () => {
  const context = workflowContext({
    head_branch: "`bad`\n<script>alert(1)</script>" + "x".repeat(500),
    html_url: "https://example.com/not-github",
  });
  const run = responder.normalizeRun(context);
  const body = responder.renderBody(run, responder.incidentKey(run));

  assert.ok(run.branch.length <= 200);
  assert.doesNotMatch(body, /https:\/\/example\.com/);
  assert.doesNotMatch(body, /`bad`/);
  assert.match(body, /Run link unavailable/);
});

