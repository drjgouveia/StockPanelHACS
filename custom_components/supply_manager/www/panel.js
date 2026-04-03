import { LitElement, html, css } from "https://unpkg.com/lit-element@3.3.3/lit-element.js?module";

class SupplyManagerPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      panel: { type: Object },
      _activeTab: { type: String },
      _supplies: { type: Array },
      _consumptionLog: { type: Array },
      _storageLog: { type: Array },
      _loading: { type: Boolean },
      _showAddDialog: { type: Boolean },
      _showEditDialog: { type: Boolean },
      _editingSupply: { type: Object },
      _newSupply: { type: Object },
    };
  }

  constructor() {
    super();
    this._activeTab = "supplies";
    this._supplies = [];
    this._consumptionLog = [];
    this._storageLog = [];
    this._loading = true;
    this._showAddDialog = false;
    this._showEditDialog = false;
    this._editingSupply = null;
    this._newSupply = {
      name: "",
      category: "other",
      quantity: 0,
      unit: "pcs",
      min_threshold: 0,
      expiration_date: "",
      location: "",
      notes: "",
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        background: var(--primary-background-color);
        min-height: 100vh;
      }
      .header {
        background: var(--card-background-color);
        border-bottom: 1px solid var(--divider-color);
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 400;
      }
      .tabs {
        display: flex;
        background: var(--card-background-color);
        border-bottom: 1px solid var(--divider-color);
      }
      .tab {
        padding: 12px 24px;
        cursor: pointer;
        border: none;
        background: none;
        font-size: 14px;
        font-weight: 500;
        color: var(--secondary-text-color);
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
      }
      .tab:hover {
        color: var(--primary-text-color);
      }
      .tab.active {
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
      }
      .content {
        padding: 24px;
        max-width: 1200px;
        margin: 0 auto;
      }
      .card {
        background: var(--card-background-color);
        border-radius: 12px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
        margin-bottom: 16px;
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
      .card-content {
        padding: 16px;
      }
      .supply-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
      }
      .supply-item {
        background: var(--card-background-color);
        border-radius: 12px;
        box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
        padding: 16px;
        position: relative;
        border-left: 4px solid var(--primary-color);
      }
      .supply-item.low-stock {
        border-left-color: var(--error-color, #db4437);
      }
      .supply-item .name {
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 8px;
      }
      .supply-item .details {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
      }
      .supply-item .quantity {
        font-size: 24px;
        font-weight: 300;
      }
      .supply-item .unit {
        font-size: 14px;
        color: var(--secondary-text-color);
      }
      .supply-item .meta {
        font-size: 12px;
        color: var(--secondary-text-color);
        margin-top: 8px;
      }
      .supply-item .actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
      .category-badge {
        display: inline-block;
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
      .low-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        background: var(--error-color, #db4437);
        color: white;
      }
      .log-table {
        width: 100%;
        border-collapse: collapse;
      }
      .log-table th, .log-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid var(--divider-color);
      }
      .log-table th {
        font-weight: 500;
        color: var(--secondary-text-color);
        font-size: 12px;
        text-transform: uppercase;
      }
      .log-table td {
        font-size: 14px;
      }
      .log-table tr:hover {
        background: var(--secondary-background-color);
      }
      .action-icon {
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        transition: background 0.2s;
      }
      .action-icon:hover {
        background: var(--secondary-background-color);
      }
      .dialog-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      }
      .dialog {
        background: var(--card-background-color);
        border-radius: 12px;
        width: 90%;
        max-width: 500px;
        max-height: 90vh;
        overflow-y: auto;
      }
      .dialog-header {
        padding: 24px 24px 16px;
        border-bottom: 1px solid var(--divider-color);
      }
      .dialog-header h2 {
        margin: 0;
        font-size: 20px;
      }
      .dialog-content {
        padding: 24px;
      }
      .dialog-actions {
        padding: 16px 24px;
        border-top: 1px solid var(--divider-color);
        display: flex;
        justify-content: flex-end;
        gap: 8px;
      }
      .form-group {
        margin-bottom: 16px;
      }
      .form-group label {
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        font-weight: 500;
        color: var(--secondary-text-color);
      }
      .form-group input, .form-group select, .form-group textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        font-size: 14px;
        background: var(--input-background-color, var(--secondary-background-color));
        color: var(--primary-text-color);
        box-sizing: border-box;
      }
      .form-group textarea {
        min-height: 80px;
        resize: vertical;
      }
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
      }
      .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
      }
      .btn-primary {
        background: var(--primary-color);
        color: white;
      }
      .btn-primary:hover {
        opacity: 0.9;
      }
      .btn-secondary {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }
      .btn-danger {
        background: var(--error-color, #db4437);
        color: white;
      }
      .btn-small {
        padding: 6px 12px;
        font-size: 12px;
      }
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
      }
      .stat-card {
        background: var(--card-background-color);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: var(--ha-card-box-shadow, 0 2px 4px rgba(0,0,0,0.1));
      }
      .stat-card .value {
        font-size: 36px;
        font-weight: 300;
        margin-bottom: 8px;
      }
      .stat-card .label {
        font-size: 14px;
        color: var(--secondary-text-color);
      }
      .filter-bar {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }
      .filter-bar select, .filter-bar input {
        padding: 8px 12px;
        border: 1px solid var(--divider-color);
        border-radius: 8px;
        font-size: 14px;
        background: var(--input-background-color, var(--secondary-background-color));
        color: var(--primary-text-color);
      }
      .empty-state {
        text-align: center;
        padding: 48px;
        color: var(--secondary-text-color);
      }
      .empty-state ha-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }
      .progress-bar {
        height: 4px;
        background: var(--secondary-background-color);
        border-radius: 2px;
        margin-top: 8px;
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
    `;
  }

  firstUpdated() {
    this._loadData();
  }

  async _loadData() {
    this._loading = true;
    try {
      const supplies = await this._callService("get_supply_history", { limit: 1000 });
      const consumption = await this._callService("get_consumption_log", { limit: 1000 });

      const supplyStates = this.hass.states;
      const supplySensors = Object.entries(supplyStates)
        .filter(([entityId]) => entityId.startsWith("sensor.") && entityId.includes("stock"))
        .map(([entityId, state]) => ({
          entity_id: entityId,
          name: state.attributes?.friendly_name?.replace(" Stock", "") || entityId,
          quantity: parseFloat(state.state) || 0,
          unit: state.attributes?.unit_of_measurement || "pcs",
          category: state.attributes?.category || "other",
          min_threshold: state.attributes?.min_threshold || 0,
          expiration_date: state.attributes?.expiration_date,
          location: state.attributes?.location || "",
          notes: state.attributes?.notes || "",
          supply_id: state.attributes?.supply_id || "",
          is_low_stock: state.attributes?.is_low_stock || false,
          updated_at: state.attributes?.updated_at,
        }));

      this._supplies = supplySensors;
      this._consumptionLog = consumption?.log || [];
      this._storageLog = supplies?.log || [];
    } catch (err) {
      console.error("Failed to load data:", err);
    }
    this._loading = false;
  }

  async _callService(service, data = {}) {
    return new Promise((resolve, reject) => {
      const resultEvent = `supply_manager_${service}_result`;
      const timeout = setTimeout(() => {
        this.hass.connection.unsubscribeEvents(subscription);
        reject(new Error("Service call timeout"));
      }, 5000);

      const subscription = this.hass.connection.subscribeMessage(
        (msg) => {
          clearTimeout(timeout);
          this.hass.connection.unsubscribeEvents(subscription);
          resolve(msg);
        },
        {
          type: "call_service",
          domain: "supply_manager",
          service: service,
          service_data: data,
          return_response: true,
        }
      );

      this.hass.callService("supply_manager", service, data);
    });
  }

  async _addSupply() {
    try {
      await this.hass.callService("supply_manager", "add_supply", {
        ...this._newSupply,
        user: this.hass.user?.name || "system",
      });
      this._showAddDialog = false;
      this._newSupply = {
        name: "",
        category: "other",
        quantity: 0,
        unit: "pcs",
        min_threshold: 0,
        expiration_date: "",
        location: "",
        notes: "",
      };
      await this._loadData();
    } catch (err) {
      console.error("Failed to add supply:", err);
    }
  }

  async _updateSupply() {
    if (!this._editingSupply) return;
    try {
      await this.hass.callService("supply_manager", "update_stock", {
        supply_id: this._editingSupply.supply_id,
        quantity: this._editingSupply.quantity,
        user: this.hass.user?.name || "system",
      });
      this._showEditDialog = false;
      this._editingSupply = null;
      await this._loadData();
    } catch (err) {
      console.error("Failed to update supply:", err);
    }
  }

  async _logConsumption(supply) {
    const quantity = prompt(`How much ${supply.name} was consumed? (${supply.unit})`);
    if (!quantity || isNaN(parseFloat(quantity))) return;

    const reason = prompt("Reason for consumption (optional):") || "";

    try {
      await this.hass.callService("supply_manager", "log_consumption", {
        supply_id: supply.supply_id,
        quantity: parseFloat(quantity),
        user: this.hass.user?.name || "system",
        reason: reason,
      });
      await this._loadData();
    } catch (err) {
      console.error("Failed to log consumption:", err);
    }
  }

  async _removeSupply(supply) {
    if (!confirm(`Are you sure you want to remove "${supply.name}"?`)) return;

    try {
      await this.hass.callService("supply_manager", "remove_supply", {
        supply_id: supply.supply_id,
        user: this.hass.user?.name || "system",
      });
      await this._loadData();
    } catch (err) {
      console.error("Failed to remove supply:", err);
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

  _formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  }

  _getStockPercentage(supply) {
    if (!supply.min_threshold || supply.min_threshold === 0) return 100;
    const ratio = supply.quantity / (supply.min_threshold * 3);
    return Math.min(100, Math.max(0, ratio * 100));
  }

  render() {
    return html`
      <div class="header">
        <h1>Supply Manager</h1>
        <button class="btn btn-primary" @click="${() => this._showAddDialog = true}">
          + Add Supply
        </button>
      </div>

      <div class="tabs">
        <button class="tab ${this._activeTab === "supplies" ? "active" : ""}" @click="${() => this._activeTab = "supplies"}">
          Supplies
        </button>
        <button class="tab ${this._activeTab === "consumption" ? "active" : ""}" @click="${() => this._activeTab = "consumption"}">
          Consumption Log
        </button>
        <button class="tab ${this._activeTab === "history" ? "active" : ""}" @click="${() => this._activeTab = "history"}">
          Storage History
        </button>
      </div>

      <div class="content">
        ${this._activeTab === "supplies" ? this._renderSupplies() : ""}
        ${this._activeTab === "consumption" ? this._renderConsumption() : ""}
        ${this._activeTab === "history" ? this._renderHistory() : ""}
      </div>

      ${this._showAddDialog ? this._renderAddDialog() : ""}
      ${this._showEditDialog ? this._renderEditDialog() : ""}
    `;
  }

  _renderStats() {
    const total = this._supplies.length;
    const lowStock = this._supplies.filter(s => s.is_low_stock).length;
    const categories = [...new Set(this._supplies.map(s => s.category))].length;

    return html`
      <div class="stats-grid">
        <div class="stat-card">
          <div class="value">${total}</div>
          <div class="label">Total Supplies</div>
        </div>
        <div class="stat-card">
          <div class="value" style="color: ${lowStock > 0 ? "var(--error-color)" : "inherit"}">${lowStock}</div>
          <div class="label">Low Stock Alerts</div>
        </div>
        <div class="stat-card">
          <div class="value">${categories}</div>
          <div class="label">Categories Used</div>
        </div>
      </div>
    `;
  }

  _renderSupplies() {
    if (this._loading) {
      return html`<div class="empty-state">Loading...</div>`;
    }

    if (this._supplies.length === 0) {
      return html`
        <div class="empty-state">
          <div>No supplies tracked yet</div>
          <div style="margin-top: 8px;">Click "Add Supply" to get started</div>
        </div>
      `;
    }

    return html`
      ${this._renderStats()}

      <div class="filter-bar">
        <select @change="${(e) => this._filterCategory = e.target.value}">
          <option value="">All Categories</option>
          <option value="medicine">Medicine</option>
          <option value="food">Food</option>
          <option value="water">Water</option>
          <option value="cleaning">Cleaning</option>
          <option value="hygiene">Hygiene</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="supply-grid">
        ${this._supplies.map(supply => html`
          <div class="supply-item ${supply.is_low_stock ? "low-stock" : ""}">
            <div class="details">
              <div>
                <span class="category-badge ${supply.category}">${supply.category}</span>
                ${supply.is_low_stock ? html`<span class="low-badge">LOW STOCK</span>` : ""}
              </div>
            </div>
            <div class="name">${supply.name}</div>
            <div class="details">
              <span class="quantity">${supply.quantity}</span>
              <span class="unit">${supply.unit}</span>
            </div>
            <div class="progress-bar">
              <div class="fill ${supply.is_low_stock ? "low" : ""}" style="width: ${this._getStockPercentage(supply)}%"></div>
            </div>
            <div class="meta">
              ${supply.location ? html`<div>Location: ${supply.location}</div>` : ""}
              ${supply.expiration_date ? html`<div>Expires: ${this._formatDate(supply.expiration_date)}</div>` : ""}
              ${supply.min_threshold > 0 ? html`<div>Min threshold: ${supply.min_threshold} ${supply.unit}</div>` : ""}
            </div>
            <div class="actions">
              <button class="btn btn-primary btn-small" @click="${() => this._logConsumption(supply)}">Consume</button>
              <button class="btn btn-secondary btn-small" @click="${() => { this._editingSupply = {...supply}; this._showEditDialog = true; }}">Edit</button>
              <button class="btn btn-danger btn-small" @click="${() => this._removeSupply(supply)}">Remove</button>
            </div>
          </div>
        `)}
      </div>
    `;
  }

  _renderConsumption() {
    if (this._consumptionLog.length === 0) {
      return html`<div class="empty-state">No consumption records yet</div>`;
    }

    return html`
      <div class="card">
        <div class="card-header">
          <h2>Consumption Log (${this._consumptionLog.length} entries)</h2>
        </div>
        <div class="card-content" style="overflow-x: auto;">
          <table class="log-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Supply</th>
                <th>Category</th>
                <th>Consumed</th>
                <th>Remaining</th>
                <th>User</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              ${this._consumptionLog.slice().reverse().map(entry => html`
                <tr>
                  <td>${this._formatDate(entry.timestamp)}</td>
                  <td>${entry.supply_name}</td>
                  <td><span class="category-badge ${entry.category}">${entry.category}</span></td>
                  <td>${entry.quantity_consumed} ${entry.unit}</td>
                  <td>${entry.remaining_quantity} ${entry.unit}</td>
                  <td>${entry.user}</td>
                  <td>${entry.reason || "-"}</td>
                </tr>
              `)}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  _renderHistory() {
    if (this._storageLog.length === 0) {
      return html`<div class="empty-state">No storage history yet</div>`;
    }

    return html`
      <div class="card">
        <div class="card-header">
          <h2>Storage History (${this._storageLog.length} entries)</h2>
        </div>
        <div class="card-content" style="overflow-x: auto;">
          <table class="log-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Action</th>
                <th>Supply</th>
                <th>Details</th>
                <th>User</th>
              </tr>
            </thead>
            <tbody>
              ${this._storageLog.slice().reverse().map(entry => html`
                <tr>
                  <td>${this._formatDate(entry.timestamp)}</td>
                  <td>
                    <span class="category-badge ${entry.action === "added" ? "food" : entry.action === "updated" ? "water" : entry.action === "removed" ? "other" : "cleaning"}">
                      ${entry.action}
                    </span>
                  </td>
                  <td>${entry.supply_name}</td>
                  <td>${entry.details}</td>
                  <td>${entry.user}</td>
                </tr>
              `)}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  _renderAddDialog() {
    return html`
      <div class="dialog-overlay" @click="${(e) => { if (e.target === e.currentTarget) this._showAddDialog = false; }}">
        <div class="dialog">
          <div class="dialog-header">
            <h2>Add New Supply</h2>
          </div>
          <div class="dialog-content">
            <div class="form-group">
              <label>Name *</label>
              <input type="text" .value="${this._newSupply.name}" @input="${(e) => this._newSupply = {...this._newSupply, name: e.target.value}}" placeholder="e.g., Ibuprofen, Rice, Bottled Water" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Category</label>
                <select .value="${this._newSupply.category}" @change="${(e) => this._newSupply = {...this._newSupply, category: e.target.value}}">
                  <option value="medicine">Medicine</option>
                  <option value="food">Food</option>
                  <option value="water">Water</option>
                  <option value="cleaning">Cleaning</option>
                  <option value="hygiene">Hygiene</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label>Unit</label>
                <select .value="${this._newSupply.unit}" @change="${(e) => this._newSupply = {...this._newSupply, unit: e.target.value}}">
                  <option value="pcs">Pieces</option>
                  <option value="L">Liters</option>
                  <option value="kg">Kilograms</option>
                  <option value="g">Grams</option>
                  <option value="mL">Milliliters</option>
                  <option value="packs">Packs</option>
                  <option value="boxes">Boxes</option>
                  <option value="bottles">Bottles</option>
                  <option value="tablets">Tablets</option>
                  <option value="rolls">Rolls</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Quantity *</label>
                <input type="number" .value="${this._newSupply.quantity}" @input="${(e) => this._newSupply = {...this._newSupply, quantity: parseFloat(e.target.value) || 0}}" min="0" step="0.1" />
              </div>
              <div class="form-group">
                <label>Min Threshold</label>
                <input type="number" .value="${this._newSupply.min_threshold}" @input="${(e) => this._newSupply = {...this._newSupply, min_threshold: parseFloat(e.target.value) || 0}}" min="0" step="0.1" />
              </div>
            </div>
            <div class="form-group">
              <label>Location</label>
              <input type="text" .value="${this._newSupply.location}" @input="${(e) => this._newSupply = {...this._newSupply, location: e.target.value}}" placeholder="e.g., Kitchen Cabinet" />
            </div>
            <div class="form-group">
              <label>Expiration Date</label>
              <input type="date" .value="${this._newSupply.expiration_date}" @input="${(e) => this._newSupply = {...this._newSupply, expiration_date: e.target.value}}" />
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea .value="${this._newSupply.notes}" @input="${(e) => this._newSupply = {...this._newSupply, notes: e.target.value}" placeholder="Additional notes..."></textarea>
            </div>
          </div>
          <div class="dialog-actions">
            <button class="btn btn-secondary" @click="${() => this._showAddDialog = false}">Cancel</button>
            <button class="btn btn-primary" @click="${() => this._addSupply()}">Add Supply</button>
          </div>
        </div>
      </div>
    `;
  }

  _renderEditDialog() {
    if (!this._editingSupply) return "";

    return html`
      <div class="dialog-overlay" @click="${(e) => { if (e.target === e.currentTarget) this._showEditDialog = false; }}">
        <div class="dialog">
          <div class="dialog-header">
            <h2>Edit Supply: ${this._editingSupply.name}</h2>
          </div>
          <div class="dialog-content">
            <div class="form-group">
              <label>Quantity</label>
              <input type="number" .value="${this._editingSupply.quantity}" @input="${(e) => this._editingSupply = {...this._editingSupply, quantity: parseFloat(e.target.value) || 0}}" min="0" step="0.1" />
            </div>
            <div class="form-group">
              <label>Location</label>
              <input type="text" .value="${this._editingSupply.location}" @input="${(e) => this._editingSupply = {...this._editingSupply, location: e.target.value}}" />
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea .value="${this._editingSupply.notes}" @input="${(e) => this._editingSupply = {...this._editingSupply, notes: e.target.value}"></textarea>
            </div>
          </div>
          <div class="dialog-actions">
            <button class="btn btn-secondary" @click="${() => this._showEditDialog = false}">Cancel</button>
            <button class="btn btn-primary" @click="${() => this._updateSupply()}">Save Changes</button>
          </div>
        </div>
      </div>
    `;
  }
}

customElements.define("supply-manager-panel", SupplyManagerPanel);
