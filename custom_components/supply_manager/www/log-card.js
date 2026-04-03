class SupplyLogCard extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._hass = null;
    this._title = config.title || "Consumption Log";
    this._maxEntries = config.max_entries || 10;
    this._filterUser = config.filter_user;
    this._filterSupply = config.filter_supply;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
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

  _formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return dateStr;
    }
  }

  _render() {
    if (!this._hass) return;

    const totalSensor = this._hass.states["sensor.supply_manager_total"];
    const totalSupplies = totalSensor ? parseInt(totalSensor.state) : 0;

    let entries = [];
    if (totalSupplies > 0) {
      const supplyIds = Object.entries(this._hass.states)
        .filter(([id]) => id.startsWith("sensor.") && id.includes("stock"))
        .map(([id, state]) => state.attributes?.supply_id)
        .filter(Boolean);

      entries = supplyIds.map(id => {
        const sensor = Object.values(this._hass.states).find(
          s => s.attributes?.supply_id === id
        );
        return sensor ? {
          supply_id: id,
          supply_name: sensor.attributes?.friendly_name?.replace(" Stock", "") || id,
          category: sensor.attributes?.category || "other",
          quantity: parseFloat(sensor.state) || 0,
          unit: sensor.attributes?.unit_of_measurement || "pcs",
          is_low_stock: sensor.attributes?.is_low_stock || false,
          updated_at: sensor.attributes?.updated_at,
        } : null;
      }).filter(Boolean);

      if (this._filterSupply) {
        entries = entries.filter(e => e.supply_name.toLowerCase().includes(this._filterSupply.toLowerCase()));
      }

      entries.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
      entries = entries.slice(0, this._maxEntries);
    }

    let entriesHtml = "";
    if (entries.length === 0) {
      entriesHtml = `<div class="empty">No supplies tracked yet</div>`;
    } else {
      entriesHtml = entries.map(entry => `
        <div class="log-entry ${entry.is_low_stock ? 'low' : ''}">
          <div class="icon">
            <ha-icon icon="${this._getCategoryIcon(entry.category)}"></ha-icon>
          </div>
          <div class="info">
            <div class="name">${entry.supply_name}</div>
            <div class="time">${this._formatDate(entry.updated_at)}</div>
          </div>
          <div class="quantity ${entry.is_low_stock ? 'low' : ''}">
            ${entry.quantity} ${entry.unit}
          </div>
          ${entry.is_low_stock ? '<div class="low-badge">LOW</div>' : ''}
        </div>
      `).join("");
    }

    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <h2>${this._title}</h2>
        </div>
        <div class="card-content">
          ${entriesHtml}
        </div>
        <style>
          ha-card {
            border-radius: 12px;
            overflow: hidden;
          }
          .card-header {
            padding: 16px;
            border-bottom: 1px solid var(--divider-color);
          }
          .card-header h2 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
          }
          .card-content {
            padding: 8px;
          }
          .empty {
            padding: 24px;
            text-align: center;
            color: var(--secondary-text-color);
          }
          .log-entry {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 4px;
          }
          .log-entry:hover {
            background: var(--secondary-background-color);
          }
          .log-entry.low {
            background: rgba(219, 68, 55, 0.05);
          }
          .icon ha-icon {
            color: var(--primary-color);
          }
          .info {
            flex: 1;
          }
          .info .name {
            font-size: 14px;
            font-weight: 500;
          }
          .info .time {
            font-size: 12px;
            color: var(--secondary-text-color);
          }
          .quantity {
            font-size: 16px;
            font-weight: 500;
          }
          .quantity.low {
            color: var(--error-color, #db4437);
          }
          .low-badge {
            background: var(--error-color, #db4437);
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 600;
          }
        </style>
      </ha-card>
    `;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("supply-log-card", SupplyLogCard);
