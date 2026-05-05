import { useState } from "react";

export const PROVIDERS = ["ollama", "openrouter", "anthropic"] as const;
export type Provider = typeof PROVIDERS[number];

export interface SettingsState {
  provider: string;
  model: string;
  apiKey: string;
}

const DEFAULT_MODELS: Record<Provider, string> = {
  ollama: "llama3.1",
  openrouter: "openai/gpt-4o-mini",
  anthropic: "claude-3-5-haiku-20241022",
};

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw !== null ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function persist(key: string, value: string) {
  localStorage.setItem(key, JSON.stringify(value));
}

export function useSettings() {
  const [provider, setProviderState] = useState(() => load("ll_provider", "ollama"));
  const [model, setModelState] = useState(() => load("ll_model", DEFAULT_MODELS.ollama));
  const [apiKey, setApiKeyState] = useState(() => load("ll_apiKey", ""));

  const setProvider = (p: string) => {
    const defaultModel = DEFAULT_MODELS[p as Provider] ?? "";
    setProviderState(p);
    setModelState(defaultModel);
    persist("ll_provider", p);
    persist("ll_model", defaultModel);
  };

  const setModel = (m: string) => {
    setModelState(m);
    persist("ll_model", m);
  };

  const setApiKey = (k: string) => {
    setApiKeyState(k);
    persist("ll_apiKey", k);
  };

  const update = (field: keyof SettingsState, value: string) => {
    if (field === "provider") setProvider(value);
    else if (field === "model") setModel(value);
    else setApiKey(value);
  };

  return { provider, model, apiKey, update };
}
