"""Constants for Supply Manager integration."""

DOMAIN = "supply_manager"
STORAGE_KEY = "supply_manager"
STORAGE_VERSION = 1

SUPPLY_CATEGORIES = ["medicine", "food", "water", "cleaning", "hygiene", "other"]

UNIT_PIECES = "pcs"
UNIT_LITERS = "L"
UNIT_KILOGRAMS = "kg"
UNIT_GRAMS = "g"
UNIT_MILLILITERS = "mL"
UNIT_PACKS = "packs"
UNIT_BOXES = "boxes"
UNIT_BOTTLES = "bottles"
UNIT_TABLETS = "tablets"
UNIT_ROLLS = "rolls"

UNITS = [
    UNIT_PIECES,
    UNIT_LITERS,
    UNIT_KILOGRAMS,
    UNIT_GRAMS,
    UNIT_MILLILITERS,
    UNIT_PACKS,
    UNIT_BOXES,
    UNIT_BOTTLES,
    UNIT_TABLETS,
    UNIT_ROLLS,
]

SERVICE_ADD_SUPPLY = "add_supply"
SERVICE_UPDATE_STOCK = "update_stock"
SERVICE_LOG_CONSUMPTION = "log_consumption"
SERVICE_REMOVE_SUPPLY = "remove_supply"
SERVICE_GET_LOW_STOCK = "get_low_stock"
SERVICE_GET_SUPPLY_HISTORY = "get_supply_history"
SERVICE_GET_CONSUMPTION_LOG = "get_consumption_log"

ATTR_SUPPLY_ID = "supply_id"
ATTR_NAME = "name"
ATTR_CATEGORY = "category"
ATTR_QUANTITY = "quantity"
ATTR_UNIT = "unit"
ATTR_MIN_THRESHOLD = "min_threshold"
ATTR_EXPIRATION_DATE = "expiration_date"
ATTR_LOCATION = "location"
ATTR_NOTES = "notes"
ATTR_USER = "user"
ATTR_REASON = "reason"
ATTR_START_DATE = "start_date"
ATTR_END_DATE = "end_date"

EVENT_SUPPLY_ADDED = "supply_manager_supply_added"
EVENT_SUPPLY_UPDATED = "supply_manager_supply_updated"
EVENT_SUPPLY_REMOVED = "supply_manager_supply_removed"
EVENT_CONSUMPTION_LOGGED = "supply_manager_consumption_logged"
EVENT_LOW_STOCK_ALERT = "supply_manager_low_stock_alert"
