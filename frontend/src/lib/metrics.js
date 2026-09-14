export function parsePrometheusText(text) {
  const values = {};
  for (const line of text.split('\n')) {
    if (!line || line.startsWith('#')) continue;
    const match = line.match(/^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+([0-9.eE+-]+)/);
    if (!match) continue;
    const [, name, , rawValue] = match;
    if (!(name in values)) {
      values[name] = Number(rawValue);
    }
  }
  return values;
}

export function pickStat(values, name, fallback = 0) {
  return values[name] ?? fallback;
}