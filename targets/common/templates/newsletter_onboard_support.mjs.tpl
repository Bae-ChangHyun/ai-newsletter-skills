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

export { intro, note, outro };

export const HOME_ROOT = "__HOME_ROOT__";
export const RUNTIME_ROOT = "__RUNTIME_ROOT__";
export const CONFIG_FILE = path.join(RUNTIME_ROOT, ".data", "config.json");
const SCHEDULE_PROMPT_FILE = path.join(RUNTIME_ROOT, "prompts", "normalize_schedule.md");
const CREDENTIALS_DIR = path.join(RUNTIME_ROOT, ".data", "credentials");
const COPILOT_GITHUB_TOKEN_FILE = path.join(CREDENTIALS_DIR, "github_copilot_github_token.json");
const COPILOT_API_TOKEN_FILE = path.join(CREDENTIALS_DIR, "github_copilot_api_token.json");
const CODEX_BIN = process.env.CODEX_BIN || "__DEFAULT_CODEX_BIN__";
const CLAUDE_BIN = process.env.CLAUDE_BIN || "__DEFAULT_CLAUDE_BIN__";
const DEFAULT_WORKDIR = "__DEFAULT_WORKDIR__";
const GITHUB_COPILOT_CLIENT_ID = "Iv1.b507a08c87ecfe98";
const GITHUB_COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token";
const DEFAULT_GITHUB_COPILOT_API_BASE_URL = "https://api.individual.githubcopilot.com";
const COPILOT_IDE_USER_AGENT = "GitHubCopilotChat/0.26.7";
const COPILOT_EDITOR_VERSION = "vscode/1.96.2";
const COPILOT_REQUESTS_DOCS_URL = "https://docs.github.com/en/copilot/concepts/billing/copilot-requests";

export const DEFAULT_PLATFORMS = ["hn", "reddit", "geeknews", "tldr", "devday", "velopers"];
export const DEFAULT_SUBREDDITS = [
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
export const BACK = "__back__";
export const BACKENDS = [
  { value: "claude", label: "Claude Code" },
  { value: "codex", label: "Codex" },
  { value: "github_copilot", label: "GitHub Copilot" },
  { value: "openai", label: "OpenAI-compatible API" },
];
export const DELIVERY_OPTIONS = [
  { value: "telegram", label: "Telegram" },
  { value: "terminal", label: "Terminal only (preview / local runs)" },
];
export const PLATFORM_OPTIONS = [
  { value: "hn", label: "Hacker News" },
  { value: "reddit", label: "Reddit" },
  { value: "geeknews", label: "GeekNews" },
  { value: "tldr", label: "TLDR" },
  { value: "devday", label: "DevDay" },
  { value: "velopers", label: "Velopers" },
  { value: "threads", label: "Threads via RSSHub" },
];
const COPILOT_CUSTOM_MODEL = "__custom_model__";
const COPILOT_PREMIUM_MULTIPLIERS = {
  "claude-haiku-4.5": "0.33",
  "claude-opus-4.5": "3",
  "claude-opus-4.6": "3",
  "claude-opus-4.6-fast": "30",
  "claude-sonnet-4": "1",
  "claude-sonnet-4.5": "1",
  "claude-sonnet-4.6": "1",
  "gemini-2.5-pro": "1",
  "gemini-3-flash": "0.33",
  "gemini-3-flash-preview": "0.33",
  "gemini-3-pro": "1",
  "gemini-3.1-pro-preview": "1",
  "gpt-4.1": "0",
  "gpt-4o": "0",
  "gpt-5-mini": "0",
  "gpt-5.1": "1",
  "gpt-5.1-codex": "1",
  "gpt-5.1-codex-mini": "0.33",
  "gpt-5.1-codex-max": "1",
  "gpt-5.2": "1",
  "gpt-5.2-codex": "1",
  "gpt-5.3-codex": "1",
  "gpt-5.4": "1",
  "gpt-5.4-mini": "0.33",
  "grok-code-fast-1": "0.25",
  "oswe-vscode-prime": "0",
  "oswe-vscode-secondary": "0",
  "raptor-mini": "0",
};
const COPILOT_MODELS = [
  { value: "claude-haiku-4.5", label: "Claude Haiku 4.5" },
  { value: "claude-opus-4.5", label: "Claude Opus 4.5" },
  { value: "claude-opus-4.6", label: "Claude Opus 4.6" },
  { value: "claude-opus-4.6-fast", label: "Claude Opus 4.6 (fast mode)" },
  { value: "claude-sonnet-4", label: "Claude Sonnet 4" },
  { value: "claude-sonnet-4.5", label: "Claude Sonnet 4.5" },
  { value: "claude-sonnet-4.6", label: "Claude Sonnet 4.6" },
  { value: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
  { value: "gemini-3-flash-preview", label: "Gemini 3 Flash (Preview)" },
  { value: "gemini-3-pro", label: "Gemini 3 Pro" },
  { value: "gemini-3.1-pro-preview", label: "Gemini 3.1 Pro (Preview)" },
  { value: "gpt-4.1", label: "GPT-4.1" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "gpt-5-mini", label: "GPT-5 mini" },
  { value: "gpt-5.1", label: "GPT-5.1" },
  { value: "gpt-5.1-codex", label: "GPT-5.1-Codex" },
  { value: "gpt-5.1-codex-mini", label: "GPT-5.1-Codex-Mini" },
  { value: "gpt-5.1-codex-max", label: "GPT-5.1-Codex-Max" },
  { value: "gpt-5.2", label: "GPT-5.2" },
  { value: "gpt-5.2-codex", label: "GPT-5.2-Codex" },
  { value: "gpt-5.3-codex", label: "GPT-5.3-Codex" },
  { value: "gpt-5.4", label: "GPT-5.4" },
  { value: "gpt-5.4-mini", label: "GPT-5.4 mini" },
  { value: "grok-code-fast-1", label: "Grok Code Fast 1" },
  { value: "raptor-mini", label: "Raptor mini (Preview)" },
];

export class WizardCancelledError extends Error {
  constructor(message = "wizard cancelled") {
    super(message);
    this.name = "WizardCancelledError";
  }
}

export function loadExistingConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf-8"));
  } catch {
    return {};
  }
}

function loadSavedCopilotGitHubToken() {
  try {
    const parsed = JSON.parse(fs.readFileSync(COPILOT_GITHUB_TOKEN_FILE, "utf-8"));
    const token = String(parsed?.github_token || "").trim();
    const clientId = String(parsed?.client_id || "").trim();
    if (!token || clientId !== GITHUB_COPILOT_CLIENT_ID) {
      return "";
    }
    return token;
  } catch {
    return "";
  }
}

function saveCopilotGitHubToken(token) {
  fs.mkdirSync(CREDENTIALS_DIR, { recursive: true });
  fs.writeFileSync(
    COPILOT_GITHUB_TOKEN_FILE,
    `${JSON.stringify(
      {
        github_token: token,
        client_id: GITHUB_COPILOT_CLIENT_ID,
        updated_at: new Date().toISOString(),
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );
  fs.rmSync(COPILOT_API_TOKEN_FILE, { force: true });
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

export function uniqueList(values) {
  return [...new Set((values || []).filter(Boolean))];
}

export function subredditOptions(existing = []) {
  return uniqueList([...DEFAULT_SUBREDDITS, ...existing]).map((name) => ({
    value: name,
    label: name,
  }));
}

function guardCancel(value) {
  if (isCancel(value)) {
    cancel("Setup cancelled.");
    throw new WizardCancelledError();
  }
  return value;
}

export function ensureBinary(name, binValue, installHint) {
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

function validateRequired(label, value) {
  if (String(value || "").trim()) return undefined;
  return `${label} is required`;
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

export async function verifyTelegram(botToken, chatId) {
  try {
    await telegramApi(botToken, "getMe", {});
  } catch (error) {
    await note(error instanceof Error ? error.message : String(error), "Telegram validation failed");
    return false;
  }
  await note("Telegram bot token OK", "Telegram");
  const code = randomCode();
  const message = `Newsletter setup verification code: ${code}`;
  try {
    await telegramApi(botToken, "sendMessage", { chat_id: chatId, text: message });
  } catch (error) {
    await note(error instanceof Error ? error.message : String(error), "Telegram delivery test failed");
    return false;
  }
  const entered = await askRequiredText("Enter the verification code you received on Telegram", "");
  if (entered === BACK) return BACK;
  if (String(entered).trim() !== code) {
    await note("Verification code did not match. Try again.", "Telegram verification failed");
    return false;
  }
  await note("Telegram verification OK", "Telegram");
  return true;
}

export async function validateRedditSubreddits(subreddits) {
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

export async function validateThreadsAccounts(rsshubUrl, accounts) {
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

function parseCopilotExpiresAt(value) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value < 100_000_000_000 ? value * 1000 : value;
  }
  if (typeof value === "string" && value.trim()) {
    const parsed = Number.parseInt(value.trim(), 10);
    if (Number.isFinite(parsed)) {
      return parsed < 100_000_000_000 ? parsed * 1000 : parsed;
    }
  }
  throw new Error("Copilot token response missing expires_at");
}

function loadCachedCopilotApiToken() {
  try {
    const parsed = JSON.parse(fs.readFileSync(COPILOT_API_TOKEN_FILE, "utf-8"));
    return {
      token: String(parsed?.token || "").trim(),
      expiresAt: parseCopilotExpiresAt(parsed?.expires_at ?? parsed?.expiresAt),
    };
  } catch {
    return null;
  }
}

function isCopilotApiTokenUsable(cache, now = Date.now()) {
  return Boolean(cache?.token) && Number(cache?.expiresAt || 0) - now > 5 * 60 * 1000;
}

function resolveCopilotProxyHost(proxyEp) {
  const trimmed = String(proxyEp || "").trim();
  if (!trimmed) return null;
  const urlText = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
  try {
    const url = new URL(urlText);
    if (url.protocol !== "http:" && url.protocol !== "https:") return null;
    return url.hostname.toLowerCase();
  } catch {
    return null;
  }
}

function deriveCopilotApiBaseUrlFromToken(token) {
  const trimmed = String(token || "").trim();
  if (!trimmed) return null;
  const match = trimmed.match(/(?:^|;)\s*proxy-ep=([^;\s]+)/i);
  const proxyEp = match?.[1]?.trim();
  if (!proxyEp) return null;
  const proxyHost = resolveCopilotProxyHost(proxyEp);
  if (!proxyHost) return null;
  return `https://${proxyHost.replace(/^proxy\./i, "api.")}`;
}

function saveCopilotApiTokenCache(token, expiresAt) {
  fs.mkdirSync(CREDENTIALS_DIR, { recursive: true });
  fs.writeFileSync(
    COPILOT_API_TOKEN_FILE,
    `${JSON.stringify(
      {
        token,
        expires_at: expiresAt,
        updated_at: new Date().toISOString(),
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );
}

function resolveCopilotPremiumMultiplier(item) {
  const apiMultiplier = item?.billing?.multiplier;
  if (apiMultiplier !== undefined && apiMultiplier !== null && String(apiMultiplier).trim()) {
    return String(apiMultiplier).trim().replace(/[xX]$/, "");
  }
  const candidates = [
    String(item?.id || "").trim().toLowerCase(),
    String(item?.value || "").trim().toLowerCase(),
    String(item?.version || "").trim().toLowerCase(),
    String(item?.capabilities?.family || "").trim().toLowerCase(),
  ];
  for (const candidate of candidates) {
    if (candidate && COPILOT_PREMIUM_MULTIPLIERS[candidate]) {
      return COPILOT_PREMIUM_MULTIPLIERS[candidate];
    }
  }
  return "";
}

function formatCopilotPremiumText(item) {
  const multiplier = resolveCopilotPremiumMultiplier(item);
  if (!multiplier) return "";
  return `x${multiplier}`;
}

function buildCopilotExchangeHeaders(githubToken) {
  return {
    Accept: "application/json",
    Authorization: `Bearer ${githubToken}`,
    "User-Agent": COPILOT_IDE_USER_AGENT,
  };
}

function buildCopilotApiHeaders(apiToken, extraHeaders = {}) {
  return {
    Accept: "application/json",
    Authorization: `Bearer ${apiToken}`,
    "User-Agent": COPILOT_IDE_USER_AGENT,
    "Editor-Version": COPILOT_EDITOR_VERSION,
    ...extraHeaders,
  };
}

async function githubOAuthJson(url, body) {
  const form = new URLSearchParams();
  for (const [key, value] of Object.entries(body || {})) {
    form.set(key, String(value ?? ""));
  }
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
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
  const name = String(item?.name || item?.label || item?.id || item?.value || "").trim();
  const premium = formatCopilotPremiumText(item);
  if (!name) return premium ? `Model (${premium})` : "Model";
  return premium ? `${name} (${premium})` : name;
}

function decorateCopilotStaticOption(option) {
  const value = String(option?.value || "").trim();
  return {
    ...option,
    value,
    label: formatCopilotModelLabel({ id: value, label: String(option?.label || value).trim() || value }),
  };
}

async function fetchCopilotModels(runtimeAuth) {
  const response = await fetch(`${runtimeAuth.baseUrl.replace(/\/$/, "")}/models`, {
    method: "GET",
    headers: buildCopilotApiHeaders(runtimeAuth.token),
  });
  if (!response.ok) {
    throw new Error(`GitHub Copilot models fetch failed: HTTP ${response.status}`);
  }
  const data = await response.json();
  const items = Array.isArray(data?.data) ? data.data : [];
  const chatModels = items.filter((item) => {
    const modelType = String(item?.capabilities?.type || "").trim().toLowerCase();
    const endpoints = Array.isArray(item?.supported_endpoints) ? item.supported_endpoints : [];
    if (modelType && modelType !== "chat") return false;
    if (endpoints.length === 0) return true;
    return endpoints.some((endpoint) => String(endpoint || "").toLowerCase().includes("chat"));
  });
  const pickerModels = chatModels.filter((item) => item?.model_picker_enabled === true);
  const selectedModels = pickerModels.length > 0 ? pickerModels : chatModels;
  const seen = new Set();
  return selectedModels
    .map((item) => {
      const hints = [];
      const id = String(item?.id || "").trim();
      if (!id || seen.has(id)) return null;
      seen.add(id);
      if (id) hints.push(id);
      if (item?.vendor) hints.push(String(item.vendor));
      if (item?.preview) hints.push("preview");
      return {
        value: id,
        label: formatCopilotModelLabel(item),
        hint: hints.join(" · ") || undefined,
      };
    })
    .filter((item) => item?.value);
}

async function resolveCopilotRuntimeAuth(githubToken) {
  const cached = loadCachedCopilotApiToken();
  if (isCopilotApiTokenUsable(cached)) {
    return {
      token: cached.token,
      expiresAt: cached.expiresAt,
      baseUrl: deriveCopilotApiBaseUrlFromToken(cached.token) || DEFAULT_GITHUB_COPILOT_API_BASE_URL,
    };
  }

  const response = await fetch(GITHUB_COPILOT_TOKEN_URL, {
    method: "GET",
    headers: buildCopilotExchangeHeaders(githubToken),
  });
  if (!response.ok) {
    throw new Error(`Copilot token exchange failed: HTTP ${response.status}`);
  }
  const data = await response.json();
  const token = String(data?.token || "").trim();
  const expiresAt = parseCopilotExpiresAt(data?.expires_at);
  if (!token) {
    throw new Error("Copilot token response missing token");
  }
  saveCopilotApiTokenCache(token, expiresAt);
  return {
    token,
    expiresAt,
    baseUrl: deriveCopilotApiBaseUrlFromToken(token) || DEFAULT_GITHUB_COPILOT_API_BASE_URL,
  };
}

function readSchedulePrompt() {
  return fs.readFileSync(SCHEDULE_PROMPT_FILE, "utf-8");
}

function validateGeneratedConfig(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("Generated config must be a JSON object");
  }
  const backendType = String(config?.backend?.type || "").trim();
  if (!["claude", "codex", "github_copilot", "openai"].includes(backendType)) {
    throw new Error(`Generated config has unsupported backend: ${backendType || "(missing)"}`);
  }
  if (!Array.isArray(config.platforms) || config.platforms.length === 0) {
    throw new Error("Generated config must include at least one platform");
  }
  const invalidPlatforms = config.platforms.filter((platform) => !PLATFORM_OPTIONS.some((option) => option.value === platform));
  if (invalidPlatforms.length > 0) {
    throw new Error(`Generated config has unsupported platforms: ${invalidPlatforms.join(", ")}`);
  }
  const telegram = config.telegram || {};
  if (typeof telegram.enabled !== "boolean") {
    throw new Error("Generated config must include telegram.enabled");
  }
  if (telegram.enabled && (!String(telegram.bot_token || "").trim() || !String(telegram.chat_id || "").trim())) {
    throw new Error("Generated config must include telegram bot_token and chat_id when Telegram is enabled");
  }
  const schedule = config.schedule || {};
  const label = String(schedule.label || schedule.expression || schedule.cron || "").trim();
  if (!label) {
    throw new Error("Generated config must include a valid schedule");
  }
  return config;
}

function normalizeHour(hour, meridiem) {
  let value = Number.parseInt(hour, 10);
  if (!Number.isFinite(value)) return null;
  const suffix = String(meridiem || "").trim().toLowerCase();
  if (suffix === "pm" && value < 12) value += 12;
  if (suffix === "am" && value === 12) value = 0;
  if (value < 0 || value > 23) return null;
  return value;
}

function parseStructuredSchedule(rawValue) {
  const raw = String(rawValue || "").trim();
  if (!raw) return null;
  const intervalMatch = raw.match(/^(\d+)\s*([mhd])$/i);
  if (intervalMatch) {
    return { mode: "interval", expression: `${intervalMatch[1]}${intervalMatch[2].toLowerCase()}`, label: `${intervalMatch[1]}${intervalMatch[2].toLowerCase()}` };
  }
  if (raw.split(/\s+/).length === 5) {
    return { cron: raw, label: raw };
  }
  return null;
}

function isSupportedIntervalExpression(expression) {
  const match = String(expression || "").trim().toLowerCase().match(/^(\d+)\s*([mhd])$/);
  if (!match) return false;
  const amount = Number.parseInt(match[1], 10);
  const unit = match[2];
  if (!Number.isFinite(amount) || amount <= 0) return false;
  if (unit === "m") return 60 % amount === 0;
  if (unit === "h") return amount === 24 || (amount <= 24 && 24 % amount === 0);
  if (unit === "d") return amount === 1;
  return false;
}

function parseNaturalSchedule(rawValue) {
  const raw = String(rawValue || "").trim();
  if (!raw) return null;
  const normalized = raw.toLowerCase();

  let match = normalized.match(/(?:every|매)\s*(\d+)\s*(?:minutes?|mins?|분)(?:마다)?/i) || normalized.match(/(\d+)\s*(?:minutes?|mins?|분)마다/i);
  if (match) return { mode: "interval", expression: `${match[1]}m`, label: raw };

  match = normalized.match(/(?:every|매)\s*(\d+)\s*(?:hours?|hrs?|시간)(?:마다)?/i) || normalized.match(/(\d+)\s*(?:hours?|hrs?|시간)마다/i);
  if (match) return { mode: "interval", expression: `${match[1]}h`, label: raw };

  match = normalized.match(/(?:every|매)\s*(?:day|daily|일)(?:\s*(?:at)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?)?/i) || normalized.match(/매일\s*(\d{1,2})시(?:\s*(\d{1,2})분)?/i);
  if (match) {
    if (match[1] === undefined) return null;
    const hour = normalizeHour(match[1] ?? "9", match[3]);
    const minute = Number.parseInt(match[2] ?? "0", 10);
    if (hour !== null && Number.isFinite(minute) && minute >= 0 && minute < 60) {
      return { cron: `${minute} ${hour} * * *`, label: raw };
    }
  }
  return null;
}

function validateScheduleSpec(schedule) {
  if (!schedule || typeof schedule !== "object") {
    throw new Error("Schedule normalization failed");
  }
  if (schedule.mode === "interval") {
    const expression = String(schedule.expression || "").trim().toLowerCase();
    const parsed = parseStructuredSchedule(expression);
    if (!parsed || parsed.mode !== "interval" || !isSupportedIntervalExpression(parsed.expression)) {
      throw new Error("Normalized interval schedule is invalid");
    }
    return { mode: "interval", expression: parsed.expression, label: String(schedule.label || expression).trim() || parsed.expression };
  }
  if (schedule.cron) {
    const cron = String(schedule.cron || "").trim();
    if (cron.split(/\s+/).length !== 5) {
      throw new Error("Normalized cron schedule is invalid");
    }
    return { cron, label: String(schedule.label || cron).trim() || cron };
  }
  throw new Error("Schedule normalization produced an unsupported shape");
}

async function callCodexForJson(promptText) {
  const result = spawnSync(
    CODEX_BIN,
    ["exec", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", "-C", DEFAULT_WORKDIR, "-"],
    { input: promptText, encoding: "utf-8" },
  );
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || "Codex normalization failed").trim());
  }
  return JSON.parse(stripJsonResponse(result.stdout));
}

async function callClaudeForJson(promptText) {
  const result = spawnSync(CLAUDE_BIN, ["-p", promptText, "--dangerously-skip-permissions"], { encoding: "utf-8" });
  if (result.status !== 0) {
    throw new Error((result.stderr || result.stdout || "Claude normalization failed").trim());
  }
  return JSON.parse(stripJsonResponse(result.stdout));
}

async function callCopilotForJson(state, promptText) {
  const model = String(state.backendSettings?.model || "").trim();
  const githubToken = loadSavedCopilotGitHubToken();
  if (!model) throw new Error("GitHub Copilot model is required");
  if (!githubToken) throw new Error("GitHub Copilot login is required");
  const runtimeAuth = await resolveCopilotRuntimeAuth(githubToken);
  const url = `${runtimeAuth.baseUrl.replace(/\/$/, "")}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: buildCopilotApiHeaders(runtimeAuth.token, { "Content-Type": "application/json" }),
    body: JSON.stringify({
      model,
      temperature: 0,
      response_format: { type: "json_object" },
      messages: [{ role: "user", content: promptText }],
    }),
  });
  if (!response.ok) {
    throw new Error(`GitHub Copilot API error: ${response.status} ${await response.text()}`);
  }
  const data = await response.json();
  let content = data?.choices?.[0]?.message?.content ?? "";
  if (Array.isArray(content)) content = content.map((part) => part?.text || "").join("");
  return JSON.parse(stripJsonResponse(content));
}

async function callOpenAIForJson(state, promptText) {
  const baseUrl = state.backendSettings?.base_url;
  const model = state.backendSettings?.model;
  const apiKeyEnv = state.backendSettings?.api_key_env || "OPENAI_API_KEY";
  const apiKey = process.env[apiKeyEnv];
  if (!baseUrl || !model) throw new Error("OpenAI-compatible backend requires base_url and model");
  if (!apiKey) throw new Error(`${apiKeyEnv} is not set`);
  const url = baseUrl.endsWith("/chat/completions") ? baseUrl : `${baseUrl.replace(/\/$/, "")}/chat/completions`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({
      model,
      temperature: 0,
      response_format: { type: "json_object" },
      messages: [{ role: "user", content: promptText }],
    }),
  });
  if (!response.ok) {
    throw new Error(`OpenAI-compatible API error: ${response.status} ${await response.text()}`);
  }
  const data = await response.json();
  let content = data?.choices?.[0]?.message?.content ?? "";
  if (Array.isArray(content)) content = content.map((part) => part?.text || "").join("");
  return JSON.parse(stripJsonResponse(content));
}

async function callBackendForSchedule(state, rawInput) {
  const promptText = `${readSchedulePrompt()}\n\nInput JSON:\n${JSON.stringify({ language: state.language || "ko", raw_input: rawInput }, null, 2)}\n`;
  if (state.backend === "codex") return callCodexForJson(promptText);
  if (state.backend === "claude") return callClaudeForJson(promptText);
  if (state.backend === "github_copilot") return callCopilotForJson(state, promptText);
  if (state.backend === "openai") return callOpenAIForJson(state, promptText);
  throw new Error(`Unsupported backend: ${state.backend}`);
}

export async function resolveScheduleInput(state, rawInput) {
  const strict = parseStructuredSchedule(rawInput);
  if (strict) return validateScheduleSpec(strict);
  const natural = parseNaturalSchedule(rawInput);
  if (natural) return validateScheduleSpec(natural);
  const llmPayload = await callBackendForSchedule(state, rawInput);
  return validateScheduleSpec(llmPayload);
}

export function buildConfigFromState(state) {
  const config = {
    language: String(state.language || "ko").trim() || "ko",
    backend: {
      type: state.backend,
      settings: {},
    },
    platforms: uniqueList(state.platforms && state.platforms.length ? state.platforms : DEFAULT_PLATFORMS),
    telegram: {
      enabled: Boolean(state.telegram?.enabled),
    },
    schedule: validateScheduleSpec(state.schedule),
  };

  if (state.backend === "github_copilot") {
    config.backend.settings = {
      model: String(state.backendSettings?.model || "").trim(),
      auth_flow: "device_flow",
    };
  } else if (state.backend === "openai") {
    config.backend.settings = {
      base_url: String(state.backendSettings?.base_url || "").trim(),
      model: String(state.backendSettings?.model || "").trim(),
      api_key_env: String(state.backendSettings?.api_key_env || "OPENAI_API_KEY").trim(),
    };
  }

  if (config.platforms.includes("reddit")) {
    const subreddits = uniqueList(state.subreddits || []);
    if (subreddits.length > 0) config.subreddits = subreddits;
  }

  if (config.platforms.includes("threads")) {
    const accounts = uniqueList(state.threadsAccounts || []);
    if (accounts.length > 0 && state.rsshubUrl) {
      config.rsshub_url = String(state.rsshubUrl || "").trim();
      config.threads_accounts = accounts;
    }
  }

  if (config.telegram.enabled) {
    config.telegram.bot_token = String(state.telegram?.bot_token || "").trim();
    config.telegram.chat_id = String(state.telegram?.chat_id || "").trim();
  }

  return validateGeneratedConfig(config);
}

export function installBackendRuntime(backend) {
  const env = { ...process.env, AI_NEWSLETTER_HOME: HOME_ROOT };
  if (backend === "claude") {
    const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "install_claude_backend.py")], {
      env,
      encoding: "utf-8",
    });
    if (result.status !== 0) throw new Error((result.stderr || result.stdout || "Failed to install Claude runtime").trim());
    return;
  }
  if (backend === "codex") {
    const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "install_codex_backend.py")], {
      env,
      encoding: "utf-8",
    });
    if (result.status !== 0) throw new Error((result.stderr || result.stdout || "Failed to install Codex runtime").trim());
  }
}

export function clearExistingCron() {
  const result = spawnSync("python3", [path.join(RUNTIME_ROOT, "scripts", "manage_cron.py"), "stop"], {
    env: { ...process.env, AI_NEWSLETTER_HOME: HOME_ROOT },
    encoding: "utf-8",
  });
  return result.status === 0;
}

export async function askSelect(message, options, initialValue, includeBack = true) {
  const choices = options.map((opt) => ({ value: opt.value, label: opt.label, hint: opt.hint }));
  if (includeBack) choices.push({ value: BACK, label: "Back" });
  return guardCancel(await select({ message, options: choices, initialValue }));
}

export async function askConfirm(message, initialValue = true, includeBack = true) {
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

export async function askText(message, initialValue = "", placeholder = "", includeBack = true) {
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

export async function askRequiredText(message, initialValue = "", includeBack = true) {
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

export async function askMultiselect(message, options, initialValues) {
  return guardCancel(
    await multiselect({
      message,
      options: options.map((opt) => ({ value: opt.value, label: opt.label, hint: opt.hint })),
      initialValues,
    }),
  );
}

export async function askEditableMultiselect(message, options, initialValues, addPrompt) {
  const selected = await askMultiselect(message, options, initialValues);
  if (selected === BACK) return BACK;
  const extraRaw = await askText(addPrompt, "", "comma-separated or leave empty");
  if (extraRaw === BACK) return BACK;
  const extra = parseCsv(extraRaw);
  return uniqueList([...(selected || []), ...extra]);
}

export async function checkRsshub(baseUrl) {
  const base = baseUrl.replace(/\/$/, "");
  for (const url of [`${base}/healthz`, base]) {
    try {
      const response = await fetch(url, { method: "GET" });
      if (response.ok) return true;
    } catch {}
  }
  return false;
}

export function previousStep(steps, index, state) {
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

export async function configureBackendSettings(state, index, steps) {
  if (state.backend === "codex") {
    ensureBinary("codex", CODEX_BIN, "https://developers.openai.com/codex/cli");
    state.backendSettings = {};
    return { nextIndex: index + 1 };
  }
  if (state.backend === "claude") {
    ensureBinary("claude", CLAUDE_BIN, "Install Claude Code first.");
    state.backendSettings = {};
    return { nextIndex: index + 1 };
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
      if (reuse === BACK) return { nextIndex: previousStep(steps, index, state) };
      if (!reuse) githubToken = "";
    }
    if (!githubToken) {
      githubToken = await runCopilotDeviceLogin();
      saveCopilotGitHubToken(githubToken);
      await note("GitHub Copilot login OK", "GitHub Copilot Login");
    }
    const runtimeAuth = await resolveCopilotRuntimeAuth(githubToken);
    let modelOptions = COPILOT_MODELS.map((option) => decorateCopilotStaticOption(option));
    try {
      const fetchedModels = await fetchCopilotModels(runtimeAuth);
      if (fetchedModels.length > 0) modelOptions = fetchedModels;
    } catch (error) {
      await note(`${String(error?.message || error)}\nFalling back to the built-in model list.`, "GitHub Copilot Models");
    }
    modelOptions = [...modelOptions, { value: COPILOT_CUSTOM_MODEL, label: "Custom model ID" }];
    await note(
      [
        "Model list follows GitHub Copilot picker metadata when available.",
        "Multiplier labels prefer live Copilot metadata and fall back to GitHub's premium request docs.",
        `Reference: ${COPILOT_REQUESTS_DOCS_URL}`,
      ].join("\n"),
      "GitHub Copilot Models",
    );
    const initialModel = String(state.backendSettings.model || "").trim();
    const defaultModel = modelOptions.find((item) => item.value === "gpt-4o")?.value || modelOptions[0].value;
    const initialChoice = initialModel
      ? (modelOptions.some((item) => item.value === initialModel) ? initialModel : COPILOT_CUSTOM_MODEL)
      : defaultModel;
    let selectedModel = await askSelect("Choose a GitHub Copilot model", modelOptions, initialChoice || defaultModel);
    if (selectedModel === BACK) return { nextIndex: previousStep(steps, index, state) };
    let model = selectedModel;
    if (selectedModel === COPILOT_CUSTOM_MODEL) {
      model = await askRequiredText("GitHub Copilot custom model ID", initialChoice === COPILOT_CUSTOM_MODEL ? initialModel : "");
      if (model === BACK) return { nextIndex: previousStep(steps, index, state) };
      model = String(model || "").trim();
    }
    state.backendSettings = { model, auth_flow: "device_flow" };
    return { nextIndex: index + 1 };
  }
  if (state.backend === "openai") {
    const baseUrl = await askText("OpenAI-compatible base URL", state.backendSettings.base_url || "http://localhost:8000/v1");
    if (baseUrl === BACK) return { nextIndex: previousStep(steps, index, state) };
    const model = await askText("OpenAI-compatible model", state.backendSettings.model || "gpt-4.1-mini");
    if (model === BACK) return { nextIndex: previousStep(steps, index, state) };
    const apiKeyEnv = await askText("API key env var name", state.backendSettings.api_key_env || "OPENAI_API_KEY");
    if (apiKeyEnv === BACK) return { nextIndex: previousStep(steps, index, state) };
    state.backendSettings = { base_url: baseUrl, model, api_key_env: apiKeyEnv };
    return { nextIndex: index + 1 };
  }
  return { nextIndex: index + 1 };
}
