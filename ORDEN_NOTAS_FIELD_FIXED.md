# Orden Model Field Name Fix - notas → observaciones

## Problem Description
The error "AttributeError: 'Orden' object has no attribute 'notas'" was occurring in the mesero orders view because the code was trying to access `orden.notas` but the Orden model field is actually named `observaciones`.

## Root Cause
This is a field name mismatch between:
1. The view code expecting a `notas` field
2. The actual Orden model which has an `observaciones` field

## Solution Implemented

### 1. Fixed mesero/views.py
**File**: `mesero/views.py` line 168
```python
# BEFORE (causing error):
'notas': orden.notas or '',

# AFTER (fixed):
'notas': orden.observaciones or '',
```

### 2. Fixed dashboard/views/cajero_views.py
**File**: `dashboard/views/cajero_views.py`

**Fix 1** - JSON response (line ~683):
```python
# BEFORE:
'notas': orden.notas,

# AFTER:
'notas': orden.observaciones,
```

**Fix 2** - Order cancellation (line ~772):
```python
# BEFORE:
orden.notas = (orden.notas or '') + f"\n[CANCELADA] {motivo}"

# AFTER:
orden.observaciones = (orden.observaciones or '') + f"\n[CANCELADA] {motivo}"
```

### 3. Additional Mesa Model Fixes
Also fixed remaining references to `mesa.activo` which should be `mesa.activa`:

**Files fixed**:
- `dashboard/views/sucursales_views.py` (3 occurrences)
- `dashboard/views/croquis_views.py` (1 occurrence)

## Error Details
- **Error Location**: mesero/views.py, line 168, in orders function
- **Request URL**: http://127.0.0.1:8000/mesero/orders/
- **Error Type**: AttributeError
- **Error Message**: 'Orden' object has no attribute 'notas'

## Model Field Mapping
| Frontend/View Variable | Model Field |
|----------------------|-------------|
| `notas` | `observaciones` |
| `activo` (Mesa) | `activa` |

## Files Modified

1. **mesero/views.py**
   - Fixed reference to `orden.notas` → `orden.observaciones` in orders view

2. **dashboard/views/cajero_views.py**
   - Fixed JSON response field reference
   - Fixed order cancellation notes handling

3. **dashboard/views/sucursales_views.py**
   - Fixed mesa field references `mesa.activo` → `mesa.activa`

4. **dashboard/views/croquis_views.py**
   - Fixed mesa field reference `mesa.activo` → `mesa.activa`

## What This Fixes

- ✅ Resolves AttributeError when accessing /mesero/orders/
- ✅ Fixes order notes display in mesero interface
- ✅ Fixes order notes in cajero JSON responses
- ✅ Fixes order cancellation notes handling
- ✅ Ensures consistent mesa field name usage across all views

## Testing

After applying these fixes, the following should work:
1. Navigate to `/mesero/orders/` without AttributeError
2. Order notes should display correctly in mesero interface
3. Order cancellation should properly update observaciones field
4. Mesa active status should work correctly in all views

## Related Model Fields

**Orden model** (correct field names):
- `observaciones` - for order notes/observations
- `notas_cocina` - for kitchen notes

**Mesa model** (correct field names):
- `activa` - for active status (Boolean)
- `notas` - for mesa notes/observations

This fix ensures that all view code uses the correct model field names as defined in the Django models.
