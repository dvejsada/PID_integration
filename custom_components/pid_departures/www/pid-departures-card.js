/**
 * PID Departures card for Home Assistant.
 *
 * Bundled with the pid_departures integration, which serves this file and
 * registers it with the frontend, so no Lovelace resource has to be added.
 *
 * The card is configured with departure board devices rather than entity IDs:
 * entity IDs are generated from translated names and differ per language.
 */

const DOMAIN = "pid_departures";
const CARD_TYPE = "pid-departures-card";
const EDITOR_TYPE = "pid-departures-card-editor";

// The integration polls the API once a minute; the countdown is recomputed
// locally in between so it does not freeze for up to a minute.
const TICK_MS = 15 * 1000;
// Keep a departure that just left visible briefly, the data may be a minute old.
const DEPARTED_GRACE_MS = 30 * 1000;
// Three missed polls in a row mean the shown data can no longer be trusted.
const STALE_AFTER_MS = 3 * 60 * 1000;

const DEFAULTS = {
  time_format: "both",
  show_header: true,
  show_infotext: true,
  show_delay: true,
  hide_departed: true,
  compact: false,
};

const TRANSLATIONS = {
  en: {
    min: "min",
    now: "now",
    at_stop: "at stop",
    canceled: "Canceled",
    no_departures: "No upcoming departures",
    no_board: "Select a departure board in the card configuration.",
    board_not_found: "Departure board not found. Check the card configuration.",
    stale: "Not updated since {time}",
    delay: "Delay",
    no_realtime: "Timetable (no real-time data)",
    platform: "Platform",
    wheelchair: "Wheelchair accessible vehicle",
    air_conditioned: "Air conditioned",
    night: "Night line",
    substitute: "Substitute service",
    route_type: {
      tram: "Tram", metro: "Metro", train: "Train", bus: "Bus",
      ferry: "Ferry", funicular: "Funicular", trolleybus: "Trolleybus",
    },
    editor: {
      devices: "Departure boards",
      title: "Title (default: stop name)",
      max_departures: "Maximum departures",
      time_format: "Departure time",
      time_format_both: "Countdown and time",
      time_format_relative: "Countdown only",
      time_format_absolute: "Time only",
      show_header: "Show header",
      show_infotext: "Show service alerts",
      show_delay: "Show delay",
      show_platform: "Show platform",
      hide_departed: "Hide departed",
      compact: "Compact layout",
    },
  },
  cs: {
    min: "min",
    now: "teď",
    at_stop: "v zastávce",
    canceled: "Zrušeno",
    no_departures: "Žádné nadcházející odjezdy",
    no_board: "V nastavení karty vyberte odjezdovou tabuli.",
    board_not_found: "Odjezdová tabule nebyla nalezena. Zkontrolujte nastavení karty.",
    stale: "Neaktualizováno od {time}",
    delay: "Zpoždění",
    no_realtime: "Dle jízdního řádu (bez online dat)",
    platform: "Nástupiště",
    wheelchair: "Bezbariérové vozidlo",
    air_conditioned: "Klimatizace",
    night: "Noční linka",
    substitute: "Náhradní doprava",
    route_type: {
      tram: "Tramvaj", metro: "Metro", train: "Vlak", bus: "Autobus",
      ferry: "Přívoz", funicular: "Lanovka", trolleybus: "Trolejbus",
    },
    editor: {
      devices: "Odjezdové tabule",
      title: "Nadpis (výchozí: název zastávky)",
      max_departures: "Maximální počet odjezdů",
      time_format: "Čas odjezdu",
      time_format_both: "Odpočet a čas",
      time_format_relative: "Pouze odpočet",
      time_format_absolute: "Pouze čas",
      show_header: "Zobrazit záhlaví",
      show_infotext: "Zobrazit mimořádnosti",
      show_delay: "Zobrazit zpoždění",
      show_platform: "Zobrazit nástupiště",
      hide_departed: "Skrýt odjeté spoje",
      compact: "Kompaktní rozložení",
    },
  },
  sk: {
    min: "min",
    now: "teraz",
    at_stop: "na zastávke",
    canceled: "Zrušené",
    no_departures: "Žiadne nadchádzajúce odchody",
    no_board: "V nastavení karty vyberte odchodovú tabuľu.",
    board_not_found: "Odchodová tabuľa nebola nájdená. Skontrolujte nastavenie karty.",
    stale: "Neaktualizované od {time}",
    delay: "Meškanie",
    no_realtime: "Podľa cestovného poriadku (bez online údajov)",
    platform: "Nástupište",
    wheelchair: "Bezbariérové vozidlo",
    air_conditioned: "Klimatizácia",
    night: "Nočná linka",
    substitute: "Náhradná doprava",
    route_type: {
      tram: "Električka", metro: "Metro", train: "Vlak", bus: "Autobus",
      ferry: "Prievoz", funicular: "Lanovka", trolleybus: "Trolejbus",
    },
    editor: {
      devices: "Odchodové tabule",
      title: "Nadpis (predvolený: názov zastávky)",
      max_departures: "Maximálny počet odchodov",
      time_format: "Čas odchodu",
      time_format_both: "Odpočet a čas",
      time_format_relative: "Iba odpočet",
      time_format_absolute: "Iba čas",
      show_header: "Zobraziť hlavičku",
      show_infotext: "Zobraziť mimoriadnosti",
      show_delay: "Zobraziť meškanie",
      show_platform: "Zobraziť nástupište",
      hide_departed: "Skryť odídené spoje",
      compact: "Kompaktné rozloženie",
    },
  },
  de: {
    min: "Min.",
    now: "jetzt",
    at_stop: "am Steig",
    canceled: "Fällt aus",
    no_departures: "Keine anstehenden Abfahrten",
    no_board: "Wähle in der Kartenkonfiguration eine Abfahrtstafel aus.",
    board_not_found: "Abfahrtstafel nicht gefunden. Prüfe die Kartenkonfiguration.",
    stale: "Nicht aktualisiert seit {time}",
    delay: "Verspätung",
    no_realtime: "Fahrplan (keine Echtzeitdaten)",
    platform: "Steig",
    wheelchair: "Barrierefreies Fahrzeug",
    air_conditioned: "Klimatisiert",
    night: "Nachtlinie",
    substitute: "Ersatzverkehr",
    route_type: {
      tram: "Straßenbahn", metro: "Metro", train: "Zug", bus: "Bus",
      ferry: "Fähre", funicular: "Standseilbahn", trolleybus: "Oberleitungsbus",
    },
    editor: {
      devices: "Abfahrtstafeln",
      title: "Titel (Standard: Haltestellenname)",
      max_departures: "Maximale Anzahl Abfahrten",
      time_format: "Abfahrtszeit",
      time_format_both: "Countdown und Uhrzeit",
      time_format_relative: "Nur Countdown",
      time_format_absolute: "Nur Uhrzeit",
      show_header: "Kopfzeile anzeigen",
      show_infotext: "Störungsmeldungen anzeigen",
      show_delay: "Verspätung anzeigen",
      show_platform: "Steig anzeigen",
      hide_departed: "Abgefahrene ausblenden",
      compact: "Kompaktes Layout",
    },
  },
};

function translations(hass) {
  const lang = (hass?.locale?.language || hass?.language || "en").split("-")[0];
  return TRANSLATIONS[lang] || TRANSLATIONS.en;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Formats a time respecting the user's HA profile (12/24 h, server/local time zone). */
function timeFormatter(hass) {
  const locale = hass?.locale || {};
  const options = { hour: "2-digit", minute: "2-digit" };
  if (locale.time_format === "12") options.hour12 = true;
  if (locale.time_format === "24") options.hour12 = false;
  if (locale.time_zone === "server" && hass?.config?.time_zone) {
    options.timeZone = hass.config.time_zone;
  }
  const language = locale.time_format === "system" ? undefined : locale.language || hass?.language;
  try {
    return new Intl.DateTimeFormat(language, options);
  } catch (_err) {
    return new Intl.DateTimeFormat(undefined, options);
  }
}

function normalizeConfig(config) {
  if (!config || typeof config !== "object") {
    throw new Error("Invalid configuration");
  }
  const raw = config.devices ?? config.device ?? [];
  const devices = [...new Set(Array.isArray(raw) ? raw : [raw])].filter(Boolean);
  return { ...DEFAULTS, ...config, devices };
}

/**
 * Finds the entities belonging to the configured departure boards.
 *
 * Uses the entity registry display entries in `hass.entities`, which carry the
 * device and translation key, so the lookup works whatever the entity IDs are.
 */
function resolveBoards(hass, deviceIds) {
  const byDevice = new Map(deviceIds.map((id) => [id, []]));
  for (const entry of Object.values(hass.entities || {})) {
    if (entry.platform === DOMAIN && byDevice.has(entry.device_id)) {
      byDevice.get(entry.device_id).push(entry);
    }
  }

  return deviceIds.map((deviceId) => {
    const entries = byDevice.get(deviceId);
    const device = hass.devices?.[deviceId];
    const find = (domain, key) => entries.find(
      (e) => e.translation_key === key && e.entity_id.startsWith(`${domain}.`),
    )?.entity_id;

    return {
      deviceId,
      found: entries.length > 0,
      name: device?.name_by_user || device?.name || "",
      routeEntities: entries
        .filter((e) => e.translation_key === "route_name" && e.entity_id.startsWith("sensor."))
        .map((e) => e.entity_id),
      infotextEntity: find("binary_sensor", "infotext"),
      updatedEntity: find("sensor", "updated"),
    };
  });
}

/** Common leading words of the board names, e.g. "Palmovka" for "Palmovka A" and "Palmovka B". */
function commonTitle(names) {
  const unique = [...new Set(names.filter(Boolean))];
  if (unique.length <= 1) return unique[0] || "";
  const split = unique.map((n) => n.split(" "));
  const prefix = [];
  for (let i = 0; split.every((words) => i < words.length && words[i] === split[0][i]); i++) {
    prefix.push(split[0][i]);
  }
  return prefix.length ? prefix.join(" ") : unique.join(" · ");
}

function lineClass(attrs) {
  const type = attrs.route_type;
  if (type === "metro") {
    const line = String(attrs.route_name || "").toLowerCase();
    return ["a", "b", "c"].includes(line) ? `metro-${line}` : "metro";
  }
  if (attrs.is_night) return "night";
  return ["tram", "train", "bus", "ferry", "funicular", "trolleybus"].includes(type) ? type : "bus";
}

class PidDeparturesCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._boards = [];
    this._entitiesRef = undefined;
    this._devicesRef = undefined;
    this._watched = [];
    this._infoExpanded = false;
  }

  static getConfigElement() {
    return document.createElement(EDITOR_TYPE);
  }

  static getStubConfig(hass) {
    const entry = Object.values(hass.entities || {}).find(
      (e) => e.platform === DOMAIN && e.device_id && e.translation_key === "route_name",
    );
    return { devices: entry ? [entry.device_id] : [] };
  }

  setConfig(config) {
    this._config = normalizeConfig(config);
    this._entitiesRef = undefined;
    this._render();
  }

  set hass(hass) {
    const previous = this._hass;
    this._hass = hass;
    if (!this._config) return;

    // hass.entities and hass.devices only change on registry updates.
    if (hass.entities !== this._entitiesRef || hass.devices !== this._devicesRef) {
      this._entitiesRef = hass.entities;
      this._devicesRef = hass.devices;
      this._boards = resolveBoards(hass, this._config.devices);
      this._watched = this._boards.flatMap((b) => [
        ...b.routeEntities, b.infotextEntity, b.updatedEntity,
      ]).filter(Boolean);
      this._render();
      return;
    }

    // hass is replaced on every state change in the whole system, so only
    // re-render when one of the card's own entities or the locale changed.
    if (
      !previous
      || previous.locale !== hass.locale
      || this._watched.some((id) => previous.states[id] !== hass.states[id])
    ) {
      this._render();
    }
  }

  connectedCallback() {
    this._timer = window.setInterval(() => {
      if (document.visibilityState !== "hidden") this._render();
    }, TICK_MS);
    this._onVisible = () => {
      if (document.visibilityState === "visible") this._render();
    };
    document.addEventListener("visibilitychange", this._onVisible);
    this._render();
  }

  disconnectedCallback() {
    window.clearInterval(this._timer);
    document.removeEventListener("visibilitychange", this._onVisible);
  }

  getCardSize() {
    const rows = this._config?.max_departures || this._boards.reduce((n, b) => n + b.routeEntities.length, 0) || 3;
    return (this._config?.show_header === false ? 0 : 1) + Math.ceil(rows * (this._config?.compact ? 0.8 : 1.2));
  }

  // Sections view (2024.11+).
  getGridOptions() {
    return { columns: 12, min_columns: 6 };
  }

  // Sections view (2024.8 - 2024.10).
  getLayoutOptions() {
    return { grid_columns: 4, grid_min_columns: 2 };
  }

  _departures(now) {
    const departures = [];
    for (const board of this._boards) {
      for (const entityId of board.routeEntities) {
        const stateObj = this._hass.states[entityId];
        if (!stateObj || ["unavailable", "unknown"].includes(stateObj.state)) continue;
        const a = stateObj.attributes;
        const scheduled = parseDate(a.departure_time_sched) || parseDate(a.arrival_time_sched);
        const estimated = parseDate(a.departure_time_est) || parseDate(a.arrival_time_est) || scheduled;
        if (!estimated) continue;
        departures.push({ entityId, attrs: a, scheduled: scheduled || estimated, estimated });
      }
    }

    departures.sort((x, y) => x.estimated - y.estimated);

    const visible = this._config.hide_departed
      ? departures.filter((d) => d.attrs.is_at_stop || d.estimated - now > -DEPARTED_GRACE_MS)
      : departures;
    return this._config.max_departures ? visible.slice(0, this._config.max_departures) : visible;
  }

  _render() {
    if (!this._config || !this._hass || !this.isConnected) return;
    const t = translations(this._hass);
    const fmt = timeFormatter(this._hass);
    const now = Date.now();
    const config = this._config;

    const columns = this._columns();
    let body;
    if (!config.devices.length) {
      body = `<div class="message">${escapeHtml(t.no_board)}</div>`;
    } else if (!this._boards.some((b) => b.found)) {
      body = `<div class="message warning">${escapeHtml(t.board_not_found)}</div>`;
    } else {
      const departures = this._departures(now);
      body = departures.length
        ? departures.map((d) => this._renderRow(d, now, t, fmt, columns)).join("")
        : `<div class="message">${escapeHtml(t.no_departures)}</div>`;
    }

    if (!this._card) {
      const style = document.createElement("style");
      style.textContent = STYLES;
      this._card = document.createElement("ha-card");
      this.shadowRoot.append(style, this._card);
    }

    this._card.classList.toggle("compact", config.compact);

    // Re-rendering replaces the rows, keep keyboard focus on the same departure.
    const focused = this.shadowRoot.activeElement?.dataset?.entity;

    // Every row is a subgrid of this grid, so a column has the same width in all
    // rows: a delay badge or a long label never shifts the neighbouring rows.
    const departuresClass = columns.includes("count")
      ? (columns.includes("time") ? "stackable" : "")
      : "no-count";
    const template = columns
      .map((c) => `[${c}] ${c === "main" ? "minmax(0, 1fr)" : "max-content"}`)
      .join(" ");
    this._card.innerHTML = `
      ${config.show_header ? this._renderHeader(now, t, fmt) : ""}
      ${config.show_infotext ? this._renderInfotext() : ""}
      <div class="content">
        <div class="departures ${departuresClass}"
             style="grid-template-columns: ${template} [end]">${body}</div>
      </div>
    `;

    if (focused) {
      this._card.querySelector(`.row[data-entity="${CSS.escape(focused)}"]`)?.focus();
    }

    this._card.querySelectorAll(".row").forEach((row) => {
      row.addEventListener("click", () => this._moreInfo(row.dataset.entity));
      row.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          this._moreInfo(row.dataset.entity);
        }
      });
    });
    this._card.querySelector(".infotext")?.addEventListener("click", () => {
      this._infoExpanded = !this._infoExpanded;
      this._render();
    });
  }

  /** Grid columns of the departure list, in display order. */
  _columns() {
    const config = this._config;
    const columns = ["line", "main"];
    if (config.show_platform ?? this._boards.length > 1) columns.push("platform");
    if (config.time_format !== "relative") columns.push("time");
    if (config.show_delay) columns.push("delay");
    if (config.time_format !== "absolute") columns.push("count");
    return columns;
  }

  _renderHeader(now, t, fmt) {
    const title = this._config.title || commonTitle(this._boards.map((b) => b.name));

    // The "updated" sensor keeps its old timestamp when polling fails.
    let status = "";
    const updated = this._boards
      .map((b) => b.updatedEntity && parseDate(this._hass.states[b.updatedEntity]?.state))
      .filter(Boolean)
      .sort((x, y) => x - y)[0];
    if (updated && now - updated > STALE_AFTER_MS) {
      status = `
        <div class="stale" title="${escapeHtml(t.stale.replace("{time}", fmt.format(updated)))}">
          <ha-icon icon="mdi:cloud-alert"></ha-icon>
          <span>${escapeHtml(fmt.format(updated))}</span>
        </div>`;
    }

    if (!title && !status) return "";
    return `
      <div class="header">
        <div class="title">${escapeHtml(title)}</div>
        ${status}
      </div>`;
  }

  _renderInfotext() {
    const language = (this._hass.locale?.language || this._hass.language || "en").split("-")[0];
    const texts = new Set();
    for (const board of this._boards) {
      const stateObj = board.infotextEntity && this._hass.states[board.infotextEntity];
      if (stateObj?.state !== "on") continue;
      const a = stateObj.attributes;
      const text = language !== "cs" && language !== "sk" && a.text_en ? a.text_en : a.text;
      if (text) texts.add(text);
    }
    if (!texts.size) return "";
    return `
      <div class="infotext ${this._infoExpanded ? "expanded" : ""}" role="button" tabindex="0">
        <ha-icon icon="mdi:alert-outline"></ha-icon>
        <div class="infotext-text">${[...texts].map(escapeHtml).join("<br>")}</div>
      </div>`;
  }

  _renderRow(d, now, t, fmt, columns) {
    const a = d.attrs;
    const diffMs = d.estimated - now;
    const minutes = Math.floor(diffMs / 60000);
    const realtime = a.is_delay_avail === true;
    const delayMin = realtime ? Math.floor((a.delay_sec ?? 0) / 60) : 0;
    const time = fmt.format(d.scheduled);
    const typeLabel = t.route_type[a.route_type] || "";

    // Countdown, rounded down so the user is never told they have more time than they do.
    let countdown;
    if (a.is_canceled) countdown = t.canceled;
    else if (a.is_at_stop) countdown = t.at_stop;
    else if (diffMs <= 0) countdown = t.now;
    else if (minutes < 1) countdown = `<1 ${t.min}`;
    else if (minutes < 60) countdown = `${minutes} ${t.min}`;
    // A countdown in hours is harder to read than the time itself; the time
    // column already shows it, otherwise show when it actually leaves.
    else countdown = columns.includes("time") ? "" : fmt.format(d.estimated);

    // Scheduled time plus delay, the convention used on PID departure boards.
    let delay = "";
    if (a.is_canceled) {
      delay = "";
    } else if (!realtime) {
      delay = `<ha-icon icon="mdi:calendar-clock" title="${escapeHtml(t.no_realtime)}"></ha-icon>`;
    } else if (delayMin !== 0) {
      const severity = delayMin >= 5 ? "severe" : delayMin > 0 ? "late" : "early";
      delay = `<span class="badge ${severity}" title="${escapeHtml(t.delay)}">${delayMin > 0 ? "+" : "−"}${Math.abs(delayMin)}</span>`;
    }

    const features = [
      a.route_type === "train" && a.train_number ? `<span>${escapeHtml(a.train_number)}</span>` : "",
      a.is_wheelchair_accessible ? `<ha-icon icon="mdi:wheelchair-accessibility" title="${escapeHtml(t.wheelchair)}"></ha-icon>` : "",
      a.is_air_conditioned ? `<ha-icon icon="mdi:snowflake" title="${escapeHtml(t.air_conditioned)}"></ha-icon>` : "",
      a.is_night ? `<ha-icon icon="mdi:weather-night" title="${escapeHtml(t.night)}"></ha-icon>` : "",
      a.is_substitute ? `<ha-icon icon="mdi:swap-horizontal-bold" title="${escapeHtml(t.substitute)}"></ha-icon>` : "",
    ].filter(Boolean).join("");

    const cells = {
      line: `<span class="line line--${lineClass(a)}" title="${escapeHtml(typeLabel)}">${escapeHtml(a.route_name || "?")}</span>`,
      main: `
        <div class="headsign">${escapeHtml(a.trip_headsign)}</div>
        ${features ? `<div class="features">${features}</div>` : ""}`,
      platform: a.stop_platform
        ? `<span class="platform" title="${escapeHtml(t.platform)}">${escapeHtml(a.stop_platform)}</span>` : "",
      time: escapeHtml(time),
      delay,
      count: escapeHtml(countdown),
    };

    const soon = !a.is_canceled && (a.is_at_stop || diffMs < 2 * 60000);
    const label = [typeLabel, a.route_name, a.trip_headsign, a.stop_platform && `${t.platform} ${a.stop_platform}`,
      time, countdown].filter(Boolean).join(", ");

    return `
      <div class="row ${a.is_canceled ? "canceled" : ""} ${soon ? "soon" : ""}"
           data-entity="${escapeHtml(d.entityId)}" role="button" tabindex="0" aria-label="${escapeHtml(label)}">
        ${columns.map((c) => `<div class="cell ${c}-cell">${cells[c]}</div>`).join("")}
      </div>`;
  }

  _moreInfo(entityId) {
    this.dispatchEvent(new CustomEvent("hass-more-info", {
      detail: { entityId }, bubbles: true, composed: true,
    }));
  }
}

const STYLES = `
  ha-card { overflow: hidden; }
  .header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px 16px 8px;
  }
  .title {
    flex: 1;
    min-width: 0;
    font-size: var(--ha-card-header-font-size, 24px);
    line-height: 1.2;
    color: var(--ha-card-header-color, var(--primary-text-color));
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .stale {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--warning-color);
    font-size: 12px;
    --mdc-icon-size: 18px;
  }
  .infotext {
    display: flex;
    gap: 8px;
    margin: 0 16px 8px;
    padding: 8px 12px;
    border-radius: 8px;
    color: var(--primary-text-color);
    background: rgba(var(--rgb-warning-color, 255, 166, 0), 0.15);
    font-size: 13px;
    line-height: 1.4;
    cursor: pointer;
    --mdc-icon-size: 20px;
  }
  .infotext ha-icon { color: var(--warning-color); flex: none; }
  .infotext-text {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .infotext.expanded .infotext-text { display: block; }
  .content {
    /* Lets the rows adapt to the width of the card, not of the window. */
    container-type: inline-size;
    padding: 0 8px 8px;
  }
  ha-card > .content:first-child { padding-top: 8px; }
  .departures {
    display: grid;
    column-gap: 10px;
    font-variant-numeric: tabular-nums;
  }
  .row {
    grid-column: 1 / -1;
    display: grid;
    /* Fallback for browsers without subgrid: same layout, columns sized per row. */
    grid-template-columns: inherit;
    grid-template-columns: subgrid;
    column-gap: inherit;
    align-items: center;
    min-height: 52px;
    padding: 6px 8px;
    box-sizing: border-box;
    border-radius: 8px;
    cursor: pointer;
    outline: none;
  }
  .row:hover, .row:focus-visible { background: var(--secondary-background-color); }
  .row + .row { border-top: 1px solid var(--divider-color); }
  .cell { min-width: 0; }
  .line-cell { grid-column: line; display: flex; }
  .main-cell { grid-column: main; }
  .platform-cell { grid-column: platform; text-align: center; }
  .time-cell { grid-column: time; text-align: end; }
  .delay-cell { grid-column: delay; display: flex; justify-content: center; }
  .count-cell { grid-column: count; text-align: end; }

  /* Reserved widths, so a column does not jump when its widest value changes
     between updates (e.g. the first delay appears or "9 min" becomes "12 min"). */
  .platform-cell { min-width: 2em; }
  .delay-cell { min-width: 2.25em; }
  .count-cell { min-width: 3.75em; }

  .line {
    flex: 1;
    box-sizing: border-box;
    min-width: 2.75em;
    max-width: 5em;
    padding: 4px 6px;
    border-radius: 6px;
    text-align: center;
    font-weight: 700;
    font-size: 15px;
    line-height: 1.2;
    color: #fff;
    background: var(--pid-line-bg);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  /* Approximation of the PID line colours, a theme can override them. */
  .line--tram { --pid-line-bg: var(--pid-color-tram, #7a0603); }
  .line--bus { --pid-line-bg: var(--pid-color-bus, #007da8); }
  .line--trolleybus { --pid-line-bg: var(--pid-color-trolleybus, #80166f); }
  .line--train { --pid-line-bg: var(--pid-color-train, #283583); }
  .line--ferry { --pid-line-bg: var(--pid-color-ferry, #00a3c7); }
  .line--funicular { --pid-line-bg: var(--pid-color-funicular, #8b6d4c); }
  .line--metro { --pid-line-bg: var(--pid-color-metro, #555555); }
  .line--metro-a { --pid-line-bg: var(--pid-color-metro-a, #00a562); }
  .line--metro-b { --pid-line-bg: var(--pid-color-metro-b, #f8b322); color: #1d1d1b; }
  .line--metro-c { --pid-line-bg: var(--pid-color-metro-c, #cf003d); }
  .line--night {
    --pid-line-bg: var(--pid-color-night, #1d1d1b);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
  }
  .headsign {
    font-size: 15px;
    font-weight: 500;
    color: var(--primary-text-color);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .features {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 2px;
    color: var(--secondary-text-color);
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    --mdc-icon-size: 16px;
  }
  .platform {
    display: inline-block;
    min-width: 1.2em;
    padding: 0 4px;
    border: 1px solid var(--divider-color);
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    color: var(--secondary-text-color);
  }
  .time-cell {
    font-size: 13px;
    color: var(--secondary-text-color);
    white-space: nowrap;
  }
  .count-cell {
    font-size: 16px;
    font-weight: 600;
    color: var(--primary-text-color);
    white-space: nowrap;
  }
  /* Without a countdown the time is the main information. */
  .no-count .time-cell {
    font-size: 16px;
    font-weight: 600;
    color: var(--primary-text-color);
  }
  .soon .count-cell { color: var(--primary-color); }
  .delay-cell { color: var(--secondary-text-color); --mdc-icon-size: 16px; }
  .badge {
    box-sizing: border-box;
    min-width: 2em;
    padding: 1px 4px;
    border-radius: 4px;
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    line-height: 1.3;
  }
  .badge.early { background: var(--info-color, #039be5); color: #fff; }
  .badge.late { background: var(--warning-color, #ffa600); color: #1d1d1b; }
  .badge.severe { background: var(--error-color, #db4437); color: #fff; }
  .canceled .headsign, .canceled .time-cell { text-decoration: line-through; }
  .canceled .line-cell, .canceled .main-cell, .canceled .platform-cell { opacity: 0.5; }
  .canceled .count-cell { color: var(--error-color); }
  .message {
    grid-column: 1 / -1;
    padding: 16px 8px;
    color: var(--secondary-text-color);
    text-align: center;
  }
  .message.warning { color: var(--warning-color); }

  @supports not (grid-template-columns: subgrid) {
    /* Without subgrid each row sizes its own columns, fix the widest ones instead. */
    .line-cell { width: 3.25em; }
    .time-cell { min-width: 3.25em; }
  }

  /* Medium cards: the time and delay move under the countdown, in their columns. */
  @container (max-width: 419px) {
    .stackable .row { grid-template-rows: auto auto; row-gap: 2px; }
    .stackable .line-cell, .stackable .main-cell, .stackable .platform-cell { grid-row: 1 / span 2; }
    .stackable .count-cell { grid-row: 1; grid-column: time / end; }
    .stackable .time-cell, .stackable .delay-cell { grid-row: 2; }
    .stackable .time-cell { font-size: 12px; }
  }

  /* Narrow cards: the destination gets the whole first line, the values the second. */
  @container (max-width: 339px) {
    .departures { column-gap: 8px; }
    .departures .row { grid-template-rows: auto auto; row-gap: 2px; }
    .departures .line-cell { grid-row: 1 / span 2; }
    .departures .main-cell { grid-row: 1; grid-column: main / end; }
    .departures .features { display: none; }
    .departures .platform-cell, .departures .time-cell,
    .departures .delay-cell, .departures .count-cell { grid-row: 2; }
    .departures .count-cell { grid-column: count; }
  }

  /* Compact: one line per departure, for wall panels and small tiles. */
  .compact .row { min-height: 36px; padding: 2px 8px; grid-template-rows: auto; row-gap: 0; }
  .compact .features { display: none; }
  .compact .line { min-width: 2.5em; padding: 2px 4px; font-size: 14px; }
  .compact .cell { grid-row: 1; }
  .compact .main-cell { grid-column: main; }
  .compact .time-cell { grid-column: time; font-size: 13px; }
  .compact .count-cell { grid-column: count; }
  .compact .header { padding: 12px 16px 4px; }
  .compact .title { font-size: 18px; }
  @container (max-width: 339px) {
    /* One line has no room for both, the countdown matters more. */
    .compact .stackable .time-cell { display: none; }
  }
`;

class PidDeparturesCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = normalizeConfig(config);
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._form) this._form.hass = hass;
    else this._render();
  }

  async _render() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      await loadHaForm();
      if (this._form) return;
      this._form = document.createElement("ha-form");
      this._form.addEventListener("value-changed", (ev) => this._valueChanged(ev.detail.value));
      this.appendChild(this._form);
    }
    const t = translations(this._hass).editor;
    this._form.hass = this._hass;
    this._form.schema = editorSchema(t);
    this._form.computeLabel = (schema) => t[schema.name] || schema.name;
    this._form.data = {
      ...this._config,
      show_platform: this._config.show_platform ?? this._config.devices.length > 1,
    };
  }

  _valueChanged(value) {
    // Keep the YAML short: drop options that are left at their defaults.
    const config = { ...value, type: `custom:${CARD_TYPE}` };
    delete config.device;
    for (const [key, defaultValue] of Object.entries(DEFAULTS)) {
      if (config[key] === defaultValue) delete config[key];
    }
    if (config.show_platform === (config.devices || []).length > 1) delete config.show_platform;
    if (!config.title) delete config.title;
    if (!config.max_departures) delete config.max_departures;
    this._config = normalizeConfig(config);
    this.dispatchEvent(new CustomEvent("config-changed", {
      detail: { config }, bubbles: true, composed: true,
    }));
  }
}

function editorSchema(t) {
  return [
    {
      name: "devices",
      required: true,
      selector: { device: { multiple: true, filter: { integration: DOMAIN } } },
    },
    { name: "title", selector: { text: {} } },
    {
      type: "grid",
      name: "",
      schema: [
        { name: "max_departures", selector: { number: { min: 1, max: 50, mode: "box" } } },
        {
          name: "time_format",
          selector: {
            select: {
              mode: "dropdown",
              options: ["both", "relative", "absolute"].map((value) => ({
                value, label: t[`time_format_${value}`],
              })),
            },
          },
        },
      ],
    },
    {
      type: "grid",
      name: "",
      schema: [
        "show_header", "show_infotext", "show_delay", "show_platform", "hide_departed", "compact",
      ].map((name) => ({ name, selector: { boolean: {} } })),
    },
  ];
}

/** ha-form is lazy loaded by the frontend; loading a built-in card editor pulls it in. */
async function loadHaForm() {
  if (customElements.get("ha-form")) return;
  try {
    const helpers = await window.loadCardHelpers();
    const card = await helpers.createCardElement({ type: "entities", entities: [] });
    await card.constructor.getConfigElement();
  } catch (_err) {
    // Fall through and wait, the editor dialog loads ha-form itself too.
  }
  await customElements.whenDefined("ha-form");
}

if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, PidDeparturesCard);
  customElements.define(EDITOR_TYPE, PidDeparturesCardEditor);
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: CARD_TYPE,
    name: "PID Departures",
    description: "Departure board for Prague Integrated Transport stops.",
    preview: true,
    documentationURL: "https://github.com/dvejsada/PID_integration#dashboard",
  });
}
