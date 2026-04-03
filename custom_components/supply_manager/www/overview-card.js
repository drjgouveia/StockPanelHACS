class SupplyOverviewCard extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._hass = null;
    this._title = config.title || "Supply Overview";
    this._showCategories = config.show_categories !== false;
    this._showLowStock = config.show_low_stock !== false;
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
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  }

  _render() {
    if (!this._hass) return;

    const supplyEntities = Object.entries(this._hass.states)
      .filter(([id]) => id.startsWith("sensor.") && id.includes("stock"))
      .map(([id, state]) => ({
        entity_id: id,
        name: state.attributes?.friendly_name?.replace(" Stock", "") || state.attributes?.supply_id || id,
        quantity: parseFloat(state.state) || 0,
        unit: state.attributes?.unit_of_measurement || "pcs",
        category: state.attributes?.category || "other",
        min_threshold: state.attributes?.min_threshold || 0,
        expiration_date: state.attributes?.expiration_date,
        location: state.attributes?.location,
        is_low_stock: state.attributes?.is_low_stock || false,
      }));

    const totalSupplies = supplyEntities.length;
    const lowStockItems = supplyEntities.filter(s => s.is_low_stock);

    const categoryCounts = {};
    supplyEntities.forEach(s => {
      categoryCounts[s.category] = (categoryCounts[s.category] || 0) + 1;
    });

    let categoriesHtml = "";
    if (this._showCategories) {
      categoriesHtml = Object.entries(categoryCounts).map(([cat, count]) => `
        <div class="category-item">
          <ha-icon icon="${this._getCategoryIcon(cat)}"></ha-icon>
          <span>${cat.charAt(0).toUpperCase() + cat.slice(1)}</span>
          <span class="count">${count}</span>
        </div>
      `).join("");
    }

    let lowStockHtml = "";
    if (this._showLowStock && lowStockItems.length > 0) {
      lowStockHtml = `
        <div class="low-stock-section">
          <h3>Low Stock Alerts</h3>
          ${lowStockItems.map(item => `
            <div class="low-item">
              <ha-icon icon="${this._getCategoryIcon(item.category)}"></ha-icon>
              <span class="name">${item.name}</span>
              <span class="qty">${item.quantity} ${item.unit}</span>
            </div>
          `).join("")}
        </div>
      `;
    }

    this.innerHTML = `
      <ha-card>
        <div class="card-header">
          <h2>${this._title}</h2>
          <div class="total-badge">${totalSupplies} items</div>
        </div>
        <div class="card-content">
          ${categoriesHtml ? `<div class="categories">${categoriesHtml}</div>` : ""}
          ${lowStockHtml}
        </div>
        <style>
          ha-card {
            border-radius: 12px;
            overflow: hidden;
          }
          .card-header {
            padding: 16px;
            border-bottom: 1px solid var(--divider-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          .card-header h2 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
          }
          .total-badge {
            background: var(--primary-color);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
          }
          .card-content {
            padding: 16px;
          }
          .categories {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 8px;
            margin-bottom: 16px;
          }
          .category-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: var(--secondary-background-color);
            border-radius: 8px;
            font-size: 14px;
          }
          .category-item ha-icon {
            color: var(--primary-color);
          }
          .category-item .count {
            margin-left: auto;
            background: var(--primary-color);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
          }
          .low-stock-section h3 {
            margin: 0 0 12px 0;
            font-size: 14px;
            color: var(--error-color, #db4437);
          }
          .low-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: rgba(219, 68, 55, 0.1);
            border-radius: 8px;
            margin-bottom: 8px;
            font-size: 14px;
          }
          .low-item ha-icon {
            color: var(--error-color, #db4437);
          }
          .low-item .name {
            flex: 1;
          }
          .low-item .qty {
            color: var(--error-color, #db4437);
            font-weight: 500;
          }
        </style>
      </ha-card>
    `;
  }

  getCardSize() {
    return 4;
  }
}

customElements.define("supply-overview-card", SupplyOverviewCard);
