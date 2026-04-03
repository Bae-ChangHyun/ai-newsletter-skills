#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import {
  cancel,
  intro,
  isCancel,
  multiselect,
  note,
  outro,
  select,
  text,
} from "@clack/prompts";

const HOME_ROOT = "__HOME_ROOT__";
const RUNTIME_ROOT = "__RUNTIME_ROOT__";
const CONFIG_FILE = path.join(RUNTIME_ROOT, ".data", "config.json");
const PROMPT_FILE = path.join(RUNTIME_ROOT, "prompts", "generate_config.md");
const CREDENTIALS_DIR = path.join(RUNTIME_ROOT, ".data", "credentials");
const COPILOT_GITHUB_TOKEN_FILE = path.join(CREDENTIALS_DIR, "github_copilot_github_token.json");
const CODEX_BIN = process.env.CODEX_BIN || "__DEFAULT_CODEX_BIN__";
const CLAUDE_BIN = process.env.CLAUDE_BIN || "__DEFAULT_CLAUDE_BIN__";
const DEFAULT_WORKDIR = "__DEFAULT_WORKDIR__";
const GITHUB_COPILOT_CLIENT_ID = "Ov23liZ3oXuG0kCKmuyF";
const GITHUB_COPILOT_API_BASE_URL = "https://api.githubcopilot.com";
const GITHUB_COPILOT_USER_AGENT = "ai-newsletter-skills/1.0";
const DEFAULT_PLATFORMS = ["hn", "reddit", "geeknews", "tldr"];
const DEFAULT_SUBREDDITS = [
  "Anthropic",
  "ArtificialInteligence",
  "ClaudeAI",
  "GithubCopilot",
  "LocalLLaMA",
  "ollama",
  "OpenAI",
  "openclaw",
  "opensource",
  "Qwen_AI",
  "Vllm",
];
const BACK = "__back__";

const BACKENDS = [
  { value: "claude", label: "Claude Code" },
  { value: "codex", label: "Codex" },
  { value: "github_copilot", label: "GitHub Copilot" },
  { value: "openai", label: "OpenAI-compatible API" },
];

const PLATFORM_OPTIONS = [
  { value: "hn", label: "Hacker News" },
  { value: "reddit", label: "Reddit" },
  { value: "geeknews", label: "GeekNews" },
  { value: "tldr", label: "TLDR" },
  { value: "threads", label: "Threads via RSSHub" },
];

const COPILOT_MODELS = [
  { value: "claude-haiku-4.5", label: "Claude Haiku 4.5 (paid 0.33x)" },
  { value: "claude-opus-4.1", label: "Claude Opus 4.1 (paid 10x)" },
  { value: "claude-opus-4.5", label: "Claude Opus 4.5" },
  { value: "claude-opus-4.6", label: "Claude Opus 4.6" },
  { value: "claude-opus-4.6-fast", label: "Claude Opus 4.6 Fast (preview)" },
  { value: "claude-sonnet-3.5", label: "Claude Sonnet 3.5 (paid 1x)" },
  { value: "claude-sonnet-4", label: "Claude Sonnet 4 (paid 1x)" },
  { value: "claude-sonnet-4.5", label: "Claude Sonnet 4.5 (paid 1x)" },
  { value: "claude-sonnet-4.6", label: "Claude Sonnet 4.6" },
  { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro (paid 1x)" },
  { value: "gemini-3-flash", label: "Gemini 3 Flash" },
  { value: "gemini-3-pro", label: "Gemini 3 Pro" },
  { value: "gemini-3.1-pro", label: "Gemini 3.1 Pro" },
  { value: "gpt-4.1", label: "GPT-4.1 (paid 0x)" },
  { value: "gpt-4o", label: "GPT-4o (paid 0x)" },
  { value: "gpt-5", label: "GPT-5 (paid 1x)" },
  { value: "gpt-5-mini", label: "GPT-5 mini (paid 0x)" },
  { value: "gpt-5-codex", label: "GPT-5-Codex (paid 1x)" },
  { value: "gpt-5.1", label: "GPT-5.1" },
  { value: "gpt-5.1-codex", label: "GPT-5.1-Codex" },
  { value: "gpt-5.1-codex-mini", label: "GPT-5.1-Codex-Mini" },
  { value: "gpt-5.1-codex-max", label: "GPT-5.1-Codex-Max" },
  { value: "gpt-5.2", label: "GPT-5.2 (paid 1x)" },
  { value: "gpt-5.2-codex", label: "GPT-5.2-Codex" },
  { value: "gpt-5.3-codex", label: "GPT-5.3-Codex" },
  { value: "gpt-5.4", label: "GPT-5.4 (paid 1x)" },
  { value: "gpt-5.4-mini", label: "GPT-5.4 mini" },
  { value: "grok-code-fast-1", label: "Grok Code Fast 1 (paid 0.25x)" },
  { value: "raptor-mini", label: "Raptor mini" },
  { value: "goldeneye", label: "Goldeneye" },
];

function loadExistingConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
  } catch {
    return {};
  }
}

function loadSavedCopilotGitHubToken() {
  try {
    const parsed = JSON.parse(fs.readFileSync(COPILOT_GITHUB_TOKEN_FILE, "utf-8"));
    return String(parsed?.github_token || "").trim();
  } catch {
    return "";
  }
}

function saveCopilotGitHubToken(token) {
  fs.mkdirSync(CREDENTIALS_DIR, { recursive: true });
  fs.writeFileSync(
    COPILOT_GITHUB_TOKEN_FILE,
    `${JSON.stringify({ github_token: token, updated_at: new Date().toISOString() }, null, 2)}\n`,
    "utf-8",
  );
}

function tryOpenBrowser(url) {
  const commands = [
    ["xdg-open", [url]],
    ["open", [url]],
  ];
  for (const [command, args] of commands) {
    const result = spawnSync(command, args, { stdio: "ignore" });
    if (result.status === 0) return true;
  }
  return false;
}

function uniqueList(values) {
  return [...new Set((values || []).filter(Boolean))];
}

function uniqueOptions(options = []) {
  const seen = new Set();
  const result = [];
  for (const option of options) {
    const value = String(option?.value || "").trim();
    if (!value || seen.has(value)) continue;
    seen.add(value);
    result.push({
      value,
      label: String(option?.label || value).trim() || value,
      hint: option?.hint,
    });
  }
  return result;
}

function subredditOptions(existing = []) {
  return uniqueList([...DEFAULT_SUBREDDITS, ...existing]).map((name) => ({
    value: name,
    label: name,
  }));
}

class WizardCancelledError extends Error {
  constructor(message = "wizard cancelled") {
    super(message);
    this.name = "WizardCancelledError";
  }
}

function guardCancel(value) {
  if (isCancel(value)) {
    cancel("Setup cancelled.");
    throw new WizardCancelledError();
  }
  return value;
}

function ensureBinary(name, binValue, installHint) {
  const which = spawnSync("bash", ["-lc", `command -v ${JSON.stringify(binValue)}`], {
    stdio: "ignore",
  });
  if (which.status === 0 || fs.existsSync(binValue)) {
    return;
  }
  throw new Error(`${name} not found. Install it first.\n${installHint}`);
}

function stripJsonResponse(textValue) {
  const stripped = String(textValue || "").trim();
  if (!stripped.startsWith("```")) return stripped;
  const lines = stripped.split("\n");
  if (lines[0]?.startsWith("```")) lines.shift();
  if (lines.at(-1)?.startsWith("```")) lines.pop();
  return lines.join("\n").trim();
}

function readGenerationPrompt() {
  return fs.readFileSync(PROMPT_FILE, "utf-8");
}

function buildGenerationPrompt(answers) {
  return `${readGenerationPrompt()}\n\nCollected onboarding answers:\n${JSON.stringify(answers, null, 2)}\n`;
}

function buildAnswers(state) {
  return {
    language: state.language,
    backend: state.backend,
    backend_settings: state.backendSettings,
    platforms: state.platforms,
    subreddits: state.subreddits,
    telegram: { ...state.telegram, enabled: true },
    schedule: state.schedule,
    rsshub_url: state.rsshubUrl ?? undefined,
    threads_accounts: state.threadsAccounts ?? [],
    rules: {
      config_path: CONFIG_FILE,
      allowed_backends: ["claude", "codex", "github_copilot", "openai"],
      shared_state_dir: path.join(RUNTIME_ROOT, ".data"),
    },
  };
}

function validateRequired(label, value) {
  if (String(value || "").trim()) return undefined;
  return `${label} is required`;
}

function validateSchedule(value) {
  const trimmed = String(value || "").trim();
  if (!trimmed) return "Schedule is required";
  if (/^\d+\s*[mhd]$/.test(trimmed)) return undefined;
  if (trimmed.split(/\s+/).length === 5) return undefined;
  return "Use an interval like 1h, 30m, 1d or a 5-field cron";
}

function parseCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function randomCode() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

async function telegramApi(token, method, payload) {
  const script = `
import json
import sys
import urllib.request
import urllib.error

token = sys.argv[1]
method = sys.argv[2]
payload = json.loads(sys.stdin.read() or "{}")
url = f"https://api.telegram.org/bot{token}/{method}"
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        parsed = json.loads(body)
        if not parsed.get("ok"):
            raise SystemExit(json.dumps({"error": f"Telegram API error: {parsed.get('description', 'unknown error')}"}))
        print(json.dumps({"result": parsed.get("result")}))
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(body)
        msg = parsed.get("description", str(e))
    except Exception:
        msg = body or str(e)
    raise SystemExit(json.dumps({"error": f"Telegram API error: {msg}"}))
except Exception as e:
    raise SystemExit(json.dumps({"error": f"Telegram request failed: {e}"}))
`;
  const result = spawnSync("python3", ["-c", script, token, method], {
    input: JSON.stringify(payload ?? {}),
    encoding: "utf-8",
  });
  let parsed = {};
  try {
    parsed = JSON.parse(result.stdout || result.stderr || "{}");
  } catch {
    parsed = {};
  }
  if (result.status !== 0 || parsed.error) {
    throw new Error(parsed.error || "Telegram request failed");
  }
  return parsed.result;
}

async function verifyTelegram(botToken, chatId) {
  try {
    await telegramApi(botToken, "getMe", {});
  } catch (error) {
    await note(
      error instanceof Error ? error.message : String(error),
      "Telegram validation failed",
    );
    return false;
  }
  await note("Telegram bot token OK", "Telegram");
  const code = randomCode();
  const message = `Newsletter setup verification code: ${code}`;
  try {
    await telegramApi(botToken, "sendMessage", { chat_id: chatId, text: message });
  } catch (error) {
    await note(
      error instanceof Error ? error.message : String(error),
      "Telegram delivery test failed",
    );
    return false;
  }
  const entered = await askRequiredText(
    "Enter the verification code you received on Telegram",
    "",
  );
  if (entered === BACK) return BACK;
  if (String(entered).trim() !== code) {
    await note("Verification code did not match. Try again.", "Telegram verification failed");
    return false;
  }
  await note("Telegram verification OK", "Telegram");
  return true;
}

async function validateRedditSubreddits(subreddits) {
  const script = `
import json
import sys
import urllib.request

subs = json.loads(sys.stdin.read())
valid = []
invalid = []

for sub in subs:
    url = f"https://www.reddit.com/r/{sub}/about.json?raw_json=1"
    req = urllib.request.Request(url, headers={"User-Agent": "ai-newsletter-onboard/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            name = data.get("data", {}).get("display_name")
            if name:
                valid.append(name)
            else:
                invalid.append(sub)
    except Exception:
        invalid.append(sub)

print(json.dumps({"valid": list(dict.fromkeys(valid)), "invalid": invalid}))
`;
  const result = spawnSync("python3", ["-c", script], {
    input: JSON.stringify(subreddits),
    encoding: "utf-8",
  });
  if (result.status !== 0) {
    return { valid: [], invalid: [...subreddits] };
  }
  try {
    return JSON.parse(result.stdout);
  } catch {
    return { valid: [], invalid: [...subreddits] };
  }
}

async function validateThreadsAccounts(rsshubUrl, accounts) {
  const valid = [];
  const invalid = [];
  const base = rsshubUrl.replace(/\/$/, "");
  for (const account of accounts) {
    try {
      const response = await fetch(`${base}/threads/${encodeURIComponent(account)}`, {
        headers: { "User-Agent": "ai-newsletter-onboard/1.0" },
      });
      const body = await response.text();
      if (!response.ok || !body.includes("<rss")) {
        invalid.push(account);
        continue;
      }
      if (/route not found|not found|error/i.test(body) && !body.includes(`<link>https://www.threads.net/@${account}`)) {
        invalid.push(account);
        continue;
      }
      valid.push(account);
    } catch {
      invalid.push(account);
    }
  }
  return { valid, invalid };
}

async function githubOAuthJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      "User-Agent": GITHUB_COPILOT_USER_AGENT,
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`GitHub OAuth failed: HTTP ${response.status}`);
  }
  return response.json();
}

async function requestCopilotDeviceCode() {
  const data = await githubOAuthJson("https://github.com/login/device/code", {
    client_id: GITHUB_COPILOT_CLIENT_ID,
    scope: "read:user",
  });
  if (!data?.device_code || !data?.user_code || !data?.verification_uri) {
    throw new Error("GitHub device code response missing fields");
  }
  return data;
}

async function pollCopilotAccessToken(deviceCode, intervalSeconds, expiresInSeconds) {
  const expiresAt = Date.now() + Number(expiresInSeconds || 900) * 1000;
  let waitMs = Math.max(1000, Number(intervalSeconds || 5) * 1000);
  while (Date.now() < expiresAt) {
    const data = await githubOAuthJson("https://github.com/login/oauth/access_token", {
      client_id: GITHUB_COPILOT_CLIENT_ID,
      device_code: deviceCode,
      grant_type: "urn:ietf:params:oauth:grant-type:device_code",
    });
    if (typeof data?.access_token === "string" && data.access_token.trim()) {
      return data.access_token.trim();
    }
    const error = String(data?.error || "unknown_error");
    if (error === "authorization_pending") {
      await new Promise((resolve) => setTimeout(resolve, waitMs));
      continue;
    }
    if (error === "slow_down") {
      waitMs += 2000;
      await new Promise((resolve) => setTimeout(resolve, waitMs));
      continue;
    }
    if (error === "expired_token") {
      throw new Error("GitHub device code expired. Run the login again.");
    }
    if (error === "access_denied") {
      throw new Error("GitHub login was cancelled.");
    }
    throw new Error(`GitHub device flow error: ${error}`);
  }
  throw new Error("GitHub device code expired. Run the login again.");
}

async function runCopilotDeviceLogin() {
  const device = await requestCopilotDeviceCode();
  const opened = tryOpenBrowser(device.verification_uri);
  await note(
    [
      `Open: ${device.verification_uri}`,
      `Code: ${device.user_code}`,
      "",
      opened ? "A browser open was attempted for you." : "Open the URL above in your browser.",
      "",
      "Authorize this app with a GitHub account that has an active GitHub Copilot subscription.",
    ].join("\n"),
    "GitHub Copilot Login",
  );
  const approved = await askConfirm("After authorizing in the browser, continue?", true, false);
  if (!approved) {
    throw new Error("GitHub Copilot login cancelled.");
  }
  return pollCopilotAccessToken(device.device_code, device.interval, device.expires_in);
}

function formatCopilotModelLabel(item) {
  const name = String(item?.name || item?.id || "").trim();
  const id = String(item?.id || "").trim();
  if (!name) return id;
  if (!id || name === id) return name;
  return `${name} (${id})`;
}

async function fetchCopilotModels(githubToken) {
  const response = await fetch(`${GITHUB_COPILOT_API_BASE_URL}/models`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${githubToken}`,
      "User-Agent": GITHUB_COPILOT_USER_AGENT,
    },
  });
  if (!response.ok) {
    throw new Error(`GitHub Copilot models fetch failed: HTTP ${response.status}`);
  }
  const data = await response.json();
  const items = Array.isArray(data?.data) ? data.data : [];
  return items
    .filter((item) => {
      const endpoints = Array.isArray(item?.supported_endpoints) ? item.supported_endpoints : [];
      return endpoints.length === 0 || endpoints.includes("chat");
    })
    .map((item) => ({
      value: String(item?.id || "").trim(),
      label: formatCopilotModelLabel(item),
      hint: item?.model_picker_enabled ? "available on this account" : "reported by Copilot API",
    }))
    .filter((item) => item.value);
}

function callCodexForConfig(answers) {
  const result = spawnSync(
    CODEX_BIN,
    [
      "exec",
      "--skip-git-repo-check",
      "--dangerously-bypass-approvals-and-sandbox",
      "-C",
      DEFAULT_WORKDIR,
      "-",
    ],
    {
      input: buildGenerationPrompt(answers),
      encoding: "utf-8",
    },
  );
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || "Codex config generation failed").trim());
  }
  return JSON.parse(stripJsonResponse(result.stdout));
}

function callClaudeForConfig(answers) {
  const result = spawnSync(
    CLAUDE_BIN,
    ["-p", buildGenerationPrompt(answers), "--dangerously-skip-permissions"],
    { encoding: "utf-8" },
  );
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || "Claude config generation failed").trim());
  }
  return JSON.parse(stripJsonResponse(result.stdout));
}

async function callCopilotForConfig(answers, settings) {
  const model = String(settings?.model || "").trim();
  const githubToken = loadSavedCopilotGitHubToken();
  if (!model) throw new Error("GitHub Copilot model is required");
  if (!githubToken) throw new Error("GitHub Copilot login is required");

  const url = `${GITHUB_COPILOT_API_BASE_URL}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${githubToken}`,
      "User-Agent": GITHUB_COPILOT_USER_AGENT,
      "Openai-Intent": "conversation-edits",
      "x-initiator": "user",
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: readGenerationPrompt() },
        { role: "user", content: JSON.stringify(answers, null, 2) },
      ],
    }),
  });
  if (!response.ok) {
    throw new Error(`GitHub Copilot API error: ${response.status} ${await response.text()}`);
  }
  const data = await response.json();
  let content = data?.choices?.[0]?.message?.content ?? "";
  if (Array.isArray(content)) {
    content = content.map((part) => part?.text || "").join("");
  }
  return JSON.parse(stripJsonResponse(content));
}

async function callOpenAIForConfig(answers, settings) {
  const baseUrl = settings.base_url;
  const model = settings.model;
  const apiKeyEnv = settings.api_key_env || "OPENAI_API_KEY";
  const apiKey = process.env[apiKeyEnv];
  if (!baseUrl || !model) throw new Error("OpenAI-compatible backend requires base_url and model");
  if (!apiKey) throw new Error(`${apiKeyEnv} is not set`);

  const url = baseUrl.endsWith("/chat/completions")
    ? baseUrl
    : `${baseUrl.replace(/\/$/, "")}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model,
      temperature: 0.2,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: readGenerationPrompt() },
        { role: "user", content: JSON.stringify(answers, null, 2) },
      ],
    }),
  });
  if (!response.ok) {
    throw new Error(`OpenAI-compatible API error: ${response.status} ${await response.text()}`);
  }
  const data = await response.json();
  let content = data?.choices?.[0]?.message?.content ?? "";
  if (Array.isArray(content)) {
    content = content.map((part) => part?.text || "").join("");
  }
  return JSON.parse(stripJsonResponse(content));
}

async function generateConfig(state) {
  const answers = buildAnswers(state);
  if (state.backend === "codex") return callCodexForConfig(answers);
  if (state.backend === "claude") return callClaudeForConfig(answers);
  if (state.backend === "github_copilot") return callCopilotForConfig(answers, state.backendSettings);
  if (state.backend === "openai") return callOpenAIForConfig(answers, state.backendSettings);
  throw new Error(`Unsupported backend: ${state.backend}`);
}

function installBackendRuntime(backend) {
  const env = { ...process.env, AI_NEWSLETTER_HOME: HOME_ROOT };
  if (backend === "claude") {
    const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "install_claude_backend.py")], {
      env,
      encoding: "utf-8",
    });
    if (result.status !== 0) {
      throw new Error((result.stderr || result.stdout || "Failed to install Claude runtime").trim());
    }
    return;
  }
  if (backend === "codex") {
    const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "install_codex_backend.py")], {
      env,
      encoding: "utf-8",
    });
    if (result.status !== 0) {
      throw new Error((result.stderr || result.stdout || "Failed to install Codex runtime").trim());
    }
  }
}

function clearExistingCron() {
  const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "manage_cron.py"), "stop"], {
    env: { ...process.env, AI_NEWSLETTER_HOME: HOME_ROOT },
    encoding: "utf-8",
  });
  return result.status === 0;
}

async function askSelect(message, options, initialValue, includeBack = true) {
  const choices = options.map((opt) => ({ value: opt.value, label: opt.label, hint: opt.hint }));
  if (includeBack) choices.push({ value: BACK, label: "Back" });
  return guardCancel(
    await select({
      message,
      options: choices,
      initialValue,
    }),
  );
}

async function askConfirm(message, initialValue = true, includeBack = true) {
  const result = await askSelect(
    message,
    [
      { value: "yes", label: "Yes" },
      { value: "no", label: "No" },
    ],
    initialValue ? "yes" : "no",
    includeBack,
  );
  if (result === BACK) return BACK;
  return result === "yes";
}

async function askText(message, initialValue = "", placeholder = "", includeBack = true) {
  const result = guardCancel(
    await text({
      message,
      initialValue,
      placeholder: includeBack ? (placeholder || "Type :back to return") : placeholder,
      validate(value) {
        if (includeBack && value === ":back") return undefined;
        return undefined;
      },
    }),
  );
  if (includeBack && result === ":back") return BACK;
  return result;
}

async function askRequiredText(message, initialValue = "", includeBack = true) {
  const result = guardCancel(
    await text({
      message,
      initialValue,
      placeholder: includeBack ? "Type :back to return" : "",
      validate(value) {
        if (includeBack && value === ":back") return undefined;
        return validateRequired(message, value);
      },
    }),
  );
  if (includeBack && result === ":back") return BACK;
  return result;
}

async function askValidatedText(message, initialValue, validate, includeBack = true) {
  const result = guardCancel(
    await text({
      message,
      initialValue,
      placeholder: includeBack ? "Type :back to return" : "",
      validate(value) {
        if (includeBack && value === ":back") return undefined;
        return validate(String(value || ""));
      },
    }),
  );
  if (includeBack && result === ":back") return BACK;
  return result;
}

async function askHintedRequiredText(message, hint, initialValue = "", includeBack = true) {
  const label = hint ? `${message} (${hint})` : message;
  return askRequiredText(label, initialValue, includeBack);
}

async function askMultiselect(message, options, initialValues) {
  return guardCancel(
    await multiselect({
      message,
      options: options.map((opt) => ({ value: opt.value, label: opt.label, hint: opt.hint })),
      initialValues,
    }),
  );
}

async function askEditableMultiselect(message, options, initialValues, addPrompt) {
  const selected = await askMultiselect(message, options, initialValues);
  if (selected === BACK) return BACK;
  const extraRaw = await askText(addPrompt, "", "comma-separated or leave empty");
  if (extraRaw === BACK) return BACK;
  const extra = parseCsv(extraRaw);
  return uniqueList([...(selected || []), ...extra]);
}

async function checkRsshub(baseUrl) {
  const base = baseUrl.replace(/\/$/, "");
  for (const url of [`${base}/healthz`, base]) {
    try {
      const response = await fetch(url, { method: "GET" });
      if (response.ok) return true;
    } catch {}
  }
  return false;
}

function previousStep(steps, index, state) {
  let i = index - 1;
  while (i >= 0) {
    const step = steps[i];
    if ((step === "telegram_bot_token" || step === "telegram_chat_id") && !state.telegram?.enabled) {
      i -= 1;
      continue;
    }
    if ((step === "rsshub_url" || step === "threads_accounts") && !state.platforms?.includes("threads")) {
      i -= 1;
      continue;
    }
    return i;
  }
  return 0;
}

async function runWizard() {
  intro(
    [
      " _   _                      _      _   _            ",
      "| \\ | | _____      _____  | | ___| |_| |_ ___ _ __ ",
      "|  \\| |/ _ \\ \\ /\\ / / __| | |/ _ \\ __| __/ _ \\ '__|",
      "| |\\  |  __/\\ V  V /\\__ \\ | |  __/ |_| ||  __/ |   ",
      "|_| \\_|\\___| \\_/\\_/ |___/ |_|\\___|\\__|\\__\\___|_|   ",
      "",
      "Newsletter",
    ].join("\n"),
  );
  await note(
    "Unified onboarding for Claude Code, Codex, GitHub Copilot, and OpenAI-compatible backends.",
    "Welcome",
  );
  await note(
    "Use arrow keys to move. Use space to toggle multi-select items. Choose Back to revisit a previous step. In text inputs, type :back to return.",
    "Navigation",
  );
  const existingConfig = loadExistingConfig();
  const state = {
    language: existingConfig.language || "ko",
    backend: existingConfig.backend?.type || null,
    backendSettings: existingConfig.backend?.settings || {},
    platforms: [...(existingConfig.platforms?.length ? existingConfig.platforms : DEFAULT_PLATFORMS)],
    subreddits: [...(existingConfig.subreddits?.length ? existingConfig.subreddits : DEFAULT_SUBREDDITS)],
    telegram: {
      enabled: existingConfig.telegram?.enabled ?? true,
      bot_token: existingConfig.telegram?.bot_token || "",
      chat_id: existingConfig.telegram?.chat_id || "",
    },
    rsshubUrl: existingConfig.rsshub_url || null,
    threadsAccounts: [...(existingConfig.threads_accounts || [])],
    schedule:
      existingConfig.schedule ||
      { mode: "interval", expression: "1h", label: "1h" },
  };

  if (Object.keys(existingConfig).length) {
    await note(
      "Existing config detected. Starting from your saved values.",
      "Existing config",
    );
  }

  const steps = [
    "language",
    "backend",
    "backend_settings",
    "platforms",
    "subreddits",
    "delivery_platform",
    "telegram_bot_token",
    "telegram_chat_id",
    "rsshub_url",
    "threads_accounts",
    "schedule",
    "generate",
  ];

  let index = 0;
  while (index < steps.length) {
    const step = steps[index];

    if ((step === "rsshub_url" || step === "threads_accounts") && !state.platforms.includes("threads")) {
      index += 1;
      continue;
    }

    if (step === "language") {
      const value = await askText("Language code", state.language, "ko", false);
      state.language = String(value || "ko").trim() || "ko";
      index += 1;
      continue;
    }

    if (step === "backend") {
      const value = await askSelect("Choose AI backend", BACKENDS, state.backend || "claude", false);
      state.backend = value;
      index += 1;
      continue;
    }

    if (step === "backend_settings") {
      if (state.backend === "codex") {
        try {
          ensureBinary("codex", CODEX_BIN, "https://developers.openai.com/codex/cli");
        } catch (error) {
          await note(String(error?.message || error), "Backend not available");
          index = previousStep(steps, index, state);
          continue;
        }
        state.backendSettings = {};
        index += 1;
        continue;
      }
      if (state.backend === "claude") {
        try {
          ensureBinary("claude", CLAUDE_BIN, "Install Claude Code first.");
        } catch (error) {
          await note(String(error?.message || error), "Backend not available");
          index = previousStep(steps, index, state);
          continue;
        }
        state.backendSettings = {};
        index += 1;
        continue;
      }
      if (state.backend === "github_copilot") {
        const savedGitHubToken = loadSavedCopilotGitHubToken();
        await note(
          "GitHub Copilot uses the official GitHub device-login flow. You will open github.com/login/device and enter a one-time code.",
          "GitHub Copilot Login",
        );
        let githubToken = savedGitHubToken;
        if (savedGitHubToken) {
          const reuse = await askConfirm("Use the saved GitHub Copilot login?", true);
          if (reuse === BACK) {
            index = previousStep(steps, index, state);
            continue;
          }
          if (!reuse) {
            githubToken = "";
          }
        }
        if (!githubToken) {
          try {
            githubToken = await runCopilotDeviceLogin();
            saveCopilotGitHubToken(githubToken);
            await note("GitHub Copilot login OK", "GitHub Copilot Login");
          } catch (error) {
            await note(String(error?.message || error), "GitHub Copilot Login");
            index = previousStep(steps, index, state);
            continue;
          }
        }
        let copilotModels = [...COPILOT_MODELS];
        try {
          const fetchedModels = await fetchCopilotModels(githubToken);
          if (fetchedModels.length > 0) {
            copilotModels = uniqueOptions([...fetchedModels, ...COPILOT_MODELS]);
          }
        } catch (error) {
          await note(
            `${String(error?.message || error)}\nFalling back to the built-in model list.`,
            "GitHub Copilot Models",
          );
        }
        const model = await askSelect(
          "Choose a GitHub Copilot model",
          copilotModels,
          state.backendSettings.model || copilotModels[0].value,
        );
        if (model === BACK) {
          index = previousStep(steps, index, state);
          continue;
        }
        state.backendSettings = { model, auth_flow: "device_flow" };
        index += 1;
        continue;
      }
      if (state.backend === "openai") {
        const baseUrl = await askText(
          "OpenAI-compatible base URL",
          state.backendSettings.base_url || "http://localhost:8000/v1",
        );
        if (baseUrl === BACK) {
          index = previousStep(steps, index, state);
          continue;
        }
        const model = await askText(
          "OpenAI-compatible model",
          state.backendSettings.model || "gpt-4.1-mini",
        );
        if (model === BACK) {
          index = previousStep(steps, index, state);
          continue;
        }
        const apiKeyEnv = await askText(
          "API key env var name",
          state.backendSettings.api_key_env || "OPENAI_API_KEY",
        );
        if (apiKeyEnv === BACK) {
          index = previousStep(steps, index, state);
          continue;
        }
        state.backendSettings = {
          base_url: baseUrl,
          model,
          api_key_env: apiKeyEnv,
        };
        index += 1;
        continue;
      }
    }

    if (step === "platforms") {
      const value = await askMultiselect("Select source platforms", PLATFORM_OPTIONS, state.platforms);
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.platforms = value.length ? value : [...DEFAULT_PLATFORMS];
      index += 1;
      continue;
    }

    if (step === "subreddits") {
      const value = await askEditableMultiselect(
        "Select Reddit subreddits",
        subredditOptions(state.subreddits),
        state.subreddits,
        "Add extra subreddits (comma-separated, optional)",
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.subreddits = uniqueList(value);
      if (state.platforms.includes("reddit") && state.subreddits.length === 0) {
        await note("At least one subreddit is required when Reddit is enabled.", "Validation");
        continue;
      }
      if (state.platforms.includes("reddit")) {
        const checked = await validateRedditSubreddits(state.subreddits);
        if (checked.invalid.length) {
          await note(
            `Invalid subreddits: ${checked.invalid.join(", ")}\nPlease correct them and try again.`,
            "Reddit validation failed",
          );
          continue;
        }
        state.subreddits = checked.valid;
      }
      index += 1;
      continue;
    }

    if (step === "delivery_platform") {
      const value = await askSelect(
        "Choose delivery platform",
        [{ value: "telegram", label: "Telegram" }],
        "telegram",
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.telegram.enabled = true;
      index += 1;
      continue;
    }

    if (step === "telegram_bot_token") {
      const value = await askHintedRequiredText(
        "Telegram bot token",
        "use BotFather",
        state.telegram.bot_token || "",
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.telegram.bot_token = value;
      index += 1;
      continue;
    }

    if (step === "telegram_chat_id") {
      const value = await askHintedRequiredText(
        "Telegram chat id",
        "use get_id bot",
        state.telegram.chat_id || "",
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.telegram.chat_id = value;
      const verified = await verifyTelegram(state.telegram.bot_token, state.telegram.chat_id);
      if (verified === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      if (!verified) {
        continue;
      }
      index += 1;
      continue;
    }

    if (step === "rsshub_url") {
      const value = await askText("RSSHub URL", state.rsshubUrl || "http://localhost:1200");
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.rsshubUrl = value;
      if (!(await checkRsshub(value))) {
        await note(
          "RSSHub is not reachable. Check that your self-hosted RSSHub is running and accessible, then retry or disable Threads.",
          "RSSHub validation failed",
        );
        const choice = await askSelect(
          "RSSHub is not reachable. What do you want to do?",
          [
            { value: "retry", label: "Retry RSSHub URL" },
            { value: "disable", label: "Disable Threads and continue" },
          ],
          "retry",
          true,
        );
        if (choice === BACK) {
          index = previousStep(steps, index, state);
          continue;
        }
        if (choice === "retry") {
          continue;
        }
        await note("Threads disabled. Continuing without Threads.", "RSSHub");
        state.platforms = state.platforms.filter((item) => item !== "threads");
        state.rsshubUrl = null;
        state.threadsAccounts = [];
        index += 1;
        continue;
      }
      await note("RSSHub OK", "RSSHub");
      index += 1;
      continue;
    }

    if (step === "threads_accounts") {
      const value = await askRequiredText(
        "Threads handles without @ (comma-separated)",
        state.threadsAccounts.join(","),
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.threadsAccounts = String(value || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      if (state.threadsAccounts.length === 0) {
        await note("At least one Threads handle is required when Threads is enabled.", "Validation");
        continue;
      }
      const checked = await validateThreadsAccounts(state.rsshubUrl, state.threadsAccounts);
      if (checked.invalid.length) {
        await note(
          `Invalid Threads handles: ${checked.invalid.join(", ")}\nPlease correct them and try again.`,
          "Threads validation failed",
        );
        continue;
      }
      state.threadsAccounts = checked.valid;
      index += 1;
      continue;
    }

    if (step === "schedule") {
      const value = await askValidatedText(
        "How often should we deliver the newsletter?",
        state.schedule.label || state.schedule.expression || state.schedule.cron || "1h",
        validateSchedule,
      );
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      const raw = String(value || "1h").trim() || "1h";
      state.schedule =
        raw.split(/\s+/).length === 5
          ? { cron: raw, label: raw }
          : { mode: "interval", expression: raw, label: raw };
      index += 1;
      continue;
    }

    if (step === "generate") {
      await note(`Generating config with backend: ${state.backend}`, "Config Generation");
      const previousBackend = existingConfig.backend?.type || null;
      const config = await generateConfig(state);
      fs.mkdirSync(path.dirname(CONFIG_FILE), { recursive: true });
      fs.writeFileSync(CONFIG_FILE, `${JSON.stringify(config, null, 2)}\n`, "utf-8");
      if (state.backend === "claude" || state.backend === "codex") {
        installBackendRuntime(state.backend);
      }
      if (previousBackend && previousBackend !== state.backend) {
        clearExistingCron();
        await note(
          "An existing newsletter cron entry was removed because the backend changed.\nRun `newsletter-start` again to register the new backend.",
          "Cron reset",
        );
      }
      await note(
        [
          `Saved config: ${CONFIG_FILE}`,
          "",
          "Next:",
          `- newsletter-status`,
          `- newsletter-now`,
          `- newsletter-start`,
        ].join("\n"),
        "Setup Complete",
      );
      outro("Newsletter onboarding complete.");
      return;
    }
  }
}

try {
  await runWizard();
} catch (error) {
  if (error instanceof WizardCancelledError) {
    process.exit(1);
  }
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
