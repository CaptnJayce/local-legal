import { PROVIDERS, type SettingsState } from "../useSettings";

interface Props {
  settings: SettingsState;
  onChange: (field: keyof SettingsState, value: string) => void;
}

export function Settings({ settings, onChange }: Props) {
  const { provider, model, apiKey } = settings;

  return (
    <div className="settings">
      <h2 className="settings-heading">Settings</h2>

      <div className="settings-field">
        <label className="settings-label">Provider</label>
        <select
          className="settings-select"
          value={provider}
          onChange={e => onChange("provider", e.target.value)}
        >
          {PROVIDERS.map(p => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>

      <div className="settings-field">
        <label className="settings-label">Model</label>
        <input
          className="settings-input"
          type="text"
          value={model}
          onChange={e => onChange("model", e.target.value)}
        />
      </div>

      {provider !== "ollama" && (
        <div className="settings-field">
          <label className="settings-label">API Key</label>
          <input
            className="settings-input"
            type="password"
            value={apiKey}
            onChange={e => onChange("apiKey", e.target.value)}
            placeholder="sk-..."
          />
        </div>
      )}
    </div>
  );
}
