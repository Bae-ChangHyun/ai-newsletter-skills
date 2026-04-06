#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import {
  BACK,
  BACKENDS,
  CONFIG_FILE,
  DEFAULT_PLATFORMS,
  DEFAULT_SUBREDDITS,
  DELIVERY_OPTIONS,
  PLATFORM_OPTIONS,
  WizardCancelledError,
  askEditableMultiselect,
  askMultiselect,
  askRequiredText,
  askSelect,
  askText,
  buildConfigFromState,
  checkRsshub,
  clearExistingCron,
  configureBackendSettings,
  installBackendRuntime,
  intro,
  loadExistingConfig,
  note,
  outro,
  previousStep,
  resolveScheduleInput,
  subredditOptions,
  uniqueList,
  validateRedditSubreddits,
  validateThreadsAccounts,
  verifyTelegram,
} from "./newsletter_onboard_support.mjs";

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
  await note("Unified onboarding for Claude Code, Codex, GitHub Copilot, and OpenAI-compatible backends.", "Welcome");
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
    schedule: existingConfig.schedule || { mode: "interval", expression: "1h", label: "1h" },
  };

  if (Object.keys(existingConfig).length) {
    await note("Existing config detected. Starting from your saved values.", "Existing config");
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

    if ((step === "telegram_bot_token" || step === "telegram_chat_id") && !state.telegram.enabled) {
      index += 1;
      continue;
    }
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
      try {
        const outcome = await configureBackendSettings(state, index, steps);
        index = outcome.nextIndex;
      } catch (error) {
        await note(String(error?.message || error), "Backend setup failed");
        index = previousStep(steps, index, state);
      }
      continue;
    }

    if (step === "platforms") {
      const selected = await askMultiselect("Select source platforms", PLATFORM_OPTIONS, state.platforms);
      state.platforms = selected.length ? selected : [...DEFAULT_PLATFORMS];
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
          await note(`Invalid subreddits: ${checked.invalid.join(", ")}\nPlease correct them and try again.`, "Reddit validation failed");
          continue;
        }
        state.subreddits = checked.valid;
      }
      index += 1;
      continue;
    }

    if (step === "delivery_platform") {
      const value = await askSelect("Choose delivery platform", DELIVERY_OPTIONS, state.telegram.enabled ? "telegram" : "terminal");
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.telegram.enabled = value === "telegram";
      index += 1;
      continue;
    }

    if (step === "telegram_bot_token") {
      const value = await askRequiredText("Telegram bot token (use BotFather)", state.telegram.bot_token || "");
      if (value === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      state.telegram.bot_token = value;
      index += 1;
      continue;
    }

    if (step === "telegram_chat_id") {
      const value = await askRequiredText("Telegram chat id (use get_id bot)", state.telegram.chat_id || "");
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
      if (!verified) continue;
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
        if (choice === "retry") continue;
        await note("Threads disabled. Continuing without Threads.", "RSSHub");
        state.platforms = state.platforms.filter((item) => item !== "threads");
        state.rsshubUrl = null;
        state.threadsAccounts = [];
      }
      index += 1;
      continue;
    }

    if (step === "threads_accounts") {
      const value = await askRequiredText("Threads handles without @ (comma-separated)", state.threadsAccounts.join(","));
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
        await note(`Invalid Threads handles: ${checked.invalid.join(", ")}\nPlease correct them and try again.`, "Threads validation failed");
        continue;
      }
      state.threadsAccounts = checked.valid;
      index += 1;
      continue;
    }

    if (step === "schedule") {
      const rawSchedule = await askText(
        "How often should we deliver the newsletter? You can type 1h, 30m, a 5-field cron, or natural text like 1시간마다.",
        state.schedule.label || state.schedule.expression || state.schedule.cron || "1h",
      );
      if (rawSchedule === BACK) {
        index = previousStep(steps, index, state);
        continue;
      }
      try {
        state.schedule = await resolveScheduleInput(state, rawSchedule);
        const normalized = state.schedule.label || state.schedule.expression || state.schedule.cron;
        if (String(rawSchedule).trim() !== normalized) {
          await note(`Normalized schedule: ${normalized}`, "Schedule");
        }
        index += 1;
      } catch (error) {
        await note(
          `${String(error?.message || error)}\nTry examples like 30m, 1h, 0 9 * * *, or a natural phrase such as 1시간마다.`,
          "Schedule normalization failed",
        );
      }
      continue;
    }

    if (step === "generate") {
      const previousBackend = existingConfig.backend?.type || null;
      const config = buildConfigFromState(state);
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
          `- newsletter-doctor`,
          `- newsletter-history`,
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
