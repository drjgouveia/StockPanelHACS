# Supply Manager - Home Assistant Integration

A comprehensive Home Assistant integration for managing supplies, tracking stock levels, and logging consumption.

## Features

- **Supply Management**: Add, update, and remove supplies across categories (medicine, food, water, cleaning, hygiene, other)
- **Stock Tracking**: Real-time stock level monitoring with individual sensors per supply
- **Consumption Logging**: Track who consumed what, when, and why
- **Storage Operation Logging**: Full audit trail of all supply operations (add, update, remove, consume)
- **Low Stock Alerts**: Automatic alerts when supplies fall below configurable thresholds
- **Multiple Units**: Support for various units (pcs, L, kg, g, mL, packs, boxes, bottles, tablets, rolls)
- **Persistent Storage**: All data persists across Home Assistant restarts
- **Event System**: Fire events for automations (supply added, updated, removed, consumed, low stock)
- **Service API**: Full service-based API for automations and scripts

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Custom repositories"
3. Add the repository URL and select "Integration"
4. Search for "Supply Manager" and install
5. Restart Home Assistant
6. Add the integration via Settings > Devices & Services

### Manual

1. Copy the `custom_components/supply_manager` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration via Settings > Devices & Services

## Usage

### Adding Supplies

Use the `supply_manager.add_supply` service:

```yaml
service: supply_manager.add_supply
data:
  name: "Ibuprofen"
  category: "medicine"
  quantity: 50
  unit: "tablets"
  min_threshold: 10
  expiration_date: "2025-12-31"
  location: "Bathroom Cabinet"
  user: "John"
```

### Updating Stock

```yaml
service: supply_manager.update_stock
data:
  supply_id: "abc12345"
  quantity: 75
  user: "Jane"
```

### Logging Consumption

```yaml
service: supply_manager.log_consumption
data:
  supply_id: "abc12345"
  quantity: 2
  user: "John"
  reason: "Headache treatment"
```

### Removing Supplies

```yaml
service: supply_manager.remove_supply
data:
  supply_id: "abc12345"
  user: "Jane"
```

### Querying Data

```yaml
# Get low stock items
service: supply_manager.get_low_stock

# Get consumption log
service: supply_manager.get_consumption_log
data:
  user: "John"
  limit: 50

# Get supply history
service: supply_manager.get_supply_history
data:
  supply_id: "abc12345"
  start_date: "2025-01-01"
  end_date: "2025-12-31"
```

## Frontend

### Custom Panel

The integration adds a **Supply Manager** tab to the Home Assistant sidebar with a full management interface:

- **Supplies Tab**: View all supplies in a card grid, add/edit/remove items, log consumption
- **Consumption Log Tab**: Complete history of who consumed what and when
- **Storage History Tab**: Full audit trail of all operations (add, update, remove, consume)

Click "Supply Manager" in the sidebar to access it.

### Lovelace Cards

Three custom cards are available for your dashboards. Add them via the Lovelace editor:

#### Supply Card (Single Item)

Shows detailed info for one supply with progress bar and low stock indicator:

```yaml
type: custom:supply-card
entity: sensor.ibuprofen_stock
# or use supply_id instead:
# supply_id: abc12345
name: Ibuprofen
```

#### Supply Overview Card

Shows category breakdown and low stock alerts:

```yaml
type: custom:supply-overview-card
title: Supply Overview
show_categories: true
show_low_stock: true
```

#### Supply Log Card

Shows recent stock status for all supplies:

```yaml
type: custom:supply-log-card
title: Recent Stock Status
max_entries: 10
# Optional filters:
# filter_user: "John"
# filter_supply: "Ibuprofen"
```

### Example Dashboard

```yaml
title: Supply Dashboard
views:
  - title: Overview
    cards:
      - type: custom:supply-overview-card
        title: Supply Overview
        show_categories: true
        show_low_stock: true

      - type: custom:supply-log-card
        title: Recent Stock Status
        max_entries: 15

  - title: Medicine
    cards:
      - type: custom:supply-card
        entity: sensor.ibuprofen_stock
      - type: custom:supply-card
        entity: sensor.aspirin_stock

  - title: Food & Water
    cards:
      - type: custom:supply-card
        entity: sensor.rice_stock
      - type: custom:supply-card
        entity: sensor.bottled_water_stock
```

## Sensors

The integration creates the following sensors:

- **Total Supplies**: Count of all tracked supplies
- **Low Stock Alerts**: Count of supplies below their threshold
- **Individual Stock Sensors**: One sensor per supply item showing current stock level

## Events

The integration fires these events for automation triggers:

- `supply_manager_supply_added`
- `supply_manager_supply_updated`
- `supply_manager_supply_removed`
- `supply_manager_consumption_logged`
- `supply_manager_low_stock_alert`

### Example Automation: Notify on Low Stock

```yaml
automation:
  - alias: "Low Stock Notification"
    trigger:
      - platform: event
        event_type: supply_manager_low_stock_alert
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Low Stock Alert"
          message: >
            {{ trigger.event.data.name }} is running low!
            Only {{ trigger.event.data.remaining }} {{ trigger.event.data.unit }} remaining.
```

### Example Automation: Log All Consumption

```yaml
automation:
  - alias: "Log Consumption to Spreadsheet"
    trigger:
      - platform: event
        event_type: supply_manager_consumption_logged
    action:
      - service: notify.persistent_notification
        data:
          message: >
            {{ trigger.event.data.user }} consumed {{ trigger.event.data.quantity_consumed }} {{ trigger.event.data.unit }} of {{ trigger.event.data.name }}.
            Reason: {{ trigger.event.data.reason }}
            Remaining: {{ trigger.event.data.remaining }} {{ trigger.event.data.unit }}
```

## Categories

- `medicine`: Medications, supplements, first aid supplies
- `food`: Food items, pantry stock
- `water`: Water bottles, water reserves
- `cleaning`: Cleaning supplies, detergents
- `hygiene`: Personal hygiene products
- `other`: Anything else

## Units

- `pcs`: Pieces
- `L`: Liters
- `kg`: Kilograms
- `g`: Grams
- `mL`: Milliliters
- `packs`: Packs
- `boxes`: Boxes
- `bottles`: Bottles
- `tablets`: Tablets
- `rolls`: Rolls

## Data Storage

All data is stored in Home Assistant's `.storage/supply_manager` file and persists across restarts. The storage includes:

- **Supplies**: All tracked supply items with their current state
- **Consumption Log**: Complete history of all consumption events
- **Storage Log**: Complete audit trail of all operations

## Service Reference

| Service | Description | Required Fields |
|---------|-------------|-----------------|
| `add_supply` | Add a new supply | `name`, `quantity` |
| `update_stock` | Update stock quantity | `supply_id`, `quantity` |
| `log_consumption` | Log consumption | `supply_id`, `quantity` |
| `remove_supply` | Remove a supply | `supply_id` |
| `get_low_stock` | Get low stock items | None |
| `get_supply_history` | Get storage history | None |
| `get_consumption_log` | Get consumption log | None |

## License

MIT License
