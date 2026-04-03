class SupplyCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity && !config.supply_id) {
      throw new Error("Please define an entity or supply_id");
    }
    this._config = config;
    this._hass = null;
    this._state = null;
    this._attributes = null;
  }

  set hass(hass) {
    this._hass = hass;

    let entityId = this._config.entity;
    if (!entityId && this._config.supply_id) {
      const allEntities = Object.entries(hass.states);
      const match = allEntities.find(([id]) =>
        id.startsWith("sensor.") && id.includes(this._config.supply_id)
      );
      if (match) entityId = match[0];
    }

    if (entityId && hass.states[entityId]) {
      const state = hass.states[entityId];
      this._state = state.state;
      this._attributes = state.attributes;
      this._render();
    }
  }

  _getCategoryIcon(category) {
    const icons = {
      medicine: "mdi:pill",
      food: "mdi:food-apple",
      water: "mdi:water",
      cleaning: "mdi:broom",
      hygiene: "mdi:soap",
      other: "mdi:package-variant",
    };
    return icons[category] || "mdi:package-variant";
  }

  _getStockPercentage() {
    const minThreshold = this._attributes?.min_threshold || 0;
    if (!minThreshold) return 100;
    const ratio = parseFloat(this._state) / (minThreshold * 3);
    return Math.min(100, Math.max(0, ratio * 100));
  }

  _formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  }

  _render() {
    if (!this._state && this._state !== 0) return;

    const isLowStock = this._attributes?.is_low_stock || false;
    const category = this._attributes?.category || "other";
    const unit = this._attributes?.unit_of_measurement || "";
    const name = this._config.name || this._attributes?.friendly_name || "Unknown";
    const location = this._attributes?.location;
    const expiration = this._attributes?.expiration_date;
    const notes = this._attributes?.notes;

    this.innerHTML = `
      <ha-card>
        <div class="card-content">
          <div class="header">
            <div class="title">
              <ha-icon icon="${this._getCategoryIcon(category)}"></ha-icon>
              <span>${name}</span>
            </div>
            <span class="category-badge ${category}">${category}</span>
          </div>
          <div class="stock-display ${isLowStock ? 'low' : ''}">
            <span class="quantity">${this._state}</span>
            <span class="unit">${unit}</span>
          </div>
          ${isLowStock ? '<div class="low-stock-alert">⚠ Low Stock</div>' : ''}
          <div class="progress-bar">
            <div class="fill ${isLowStock ? 'low' : ''}" style="width: ${this._getStockPercentage()}%"></div>
          </div>
          <div class="meta">
            ${location ? `<div class="meta-item"><ha-icon icon="mdi:map-marker"></ha-icon> ${location}</div>` : ''}
            ${expiration ? `<div class="meta-item"><ha-icon icon="mdi:calendar-clock"></ha-icon> Expires: ${this._formatDate(expiration)}</div>` : ''}
            ${this._attributes?.min_threshold > 0 ? `<div class="meta-item"><ha-icon icon="mdi:alert-circle"></ha-icon> Min: ${this._attributes.min_threshold} ${unit}</div>` : ''}
            ${notes ? `<div class="meta-item"><ha-icon icon="mdi:note-text"></ha-icon> ${notes}</div>` : ''}
          </div>
        </div>
        <style>
          ha-card {
            border-radius: 12px;
            overflow: hidden;
          }
          .card-content {
            padding: 16px;
          }
          .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
          }
          .title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            font-weight: 500;
          }
          .title ha-icon {
            color: var(--primary-color);
          }
          .category-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            background: var(--primary-color);
            color: white;
          }
          .category-badge.medicine { background: #e91e63; }
          .category-badge.food { background: #4caf50; }
          .category-badge.water { background: #2196f3; }
          .category-badge.cleaning { background: #ff9800; }
          .category-badge.hygiene { background: #9c27b0; }
          .category-badge.other { background: #607d8b; }
          .stock-display {
            display: flex;
            align-items: baseline;
            gap: 4px;
            margin-bottom: 8px;
          }
          .stock-display.low {
            color: var(--error-color, #db4437);
          }
          .quantity {
            font-size: 36px;
            font-weight: 300;
          }
          .unit {
            font-size: 16px;
            color: var(--secondary-text-color);
          }
          .low-stock-alert {
            background: var(--error-color, #db4437);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
            margin-bottom: 8px;
          }
          .progress-bar {
            height: 4px;
            background: var(--secondary-background-color);
            border-radius: 2px;
            margin-bottom: 12px;
            overflow: hidden;
          }
          .progress-bar .fill {
            height: 100%;
            background: var(--primary-color);
            border-radius: 2px;
            transition: width 0.3s;
          }
          .progress-bar .fill.low {
            background: var(--error-color, #db4437);
          }
          .meta {
            display: flex;
            flex-direction: column;
            gap: 4px;
          }
          .meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--secondary-text-color);
          }
          .meta-item ha-icon {
            width: 16px;
          }
        </style>
      </ha-card>
    `;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("supply-card", SupplyCard);
