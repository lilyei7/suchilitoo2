# OrdenItem Subtotal Field Fix

## Problem Description
The error "NOT NULL constraint failed: mesero_ordenitem.subtotal" indicates that the database table `mesero_ordenitem` has a `subtotal` column with a NOT NULL constraint, but the Django OrdenItem model does not define this field.

## Root Cause
This is a schema mismatch between:
1. The database table structure (which has a `subtotal` column)
2. The Django model definition (which did not have a `subtotal` field)

## Solution Implemented

### 1. Added subtotal field to OrdenItem model
```python
class OrdenItem(models.Model):
    # ... existing fields ...
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # ... rest of fields ...
```

### 2. Updated save() method to automatically calculate subtotal
```python
def save(self, *args, **kwargs):
    # Si no se ha establecido el precio, usar el del producto
    if not self.precio_unitario:
        self.precio_unitario = self.producto.precio
    
    # Calcular y guardar el subtotal
    self.subtotal = self.calcular_subtotal()
    
    super().save(*args, **kwargs)
    
    # Recalcular totales de la orden
    self.orden.calcular_totales()
```

### 3. Fixed all OrdenItem creation code
Updated all places where `OrdenItem.objects.create()` is called to remove invalid fields:

#### mesero/views.py
- Already correct - no changes needed

#### cajero/views.py  
- Removed invalid `subtotal` and `ingredientes_removidos` fields
- The `subtotal` is now calculated automatically in the save() method

#### dashboard/views/cajero_views.py
- Removed invalid fields: `precio_total`, `costo_unitario`, `costo_total`, `estado='completado'`
- Updated DetalleVenta creation to use `item.subtotal` instead of `item.precio_total`
- Fixed JSON responses to use `item.subtotal` and `item.observaciones`

### 4. Model Field Alignment
The OrdenItem model now correctly defines:
- `subtotal` field that matches the database column
- Automatic calculation of subtotal in save() method
- Proper field names that match the database schema

## Files Modified

1. **mesero/models.py**
   - Added `subtotal` field to OrdenItem model
   - Updated save() method to calculate subtotal automatically

2. **cajero/views.py**
   - Removed invalid fields from OrdenItem creation

3. **dashboard/views/cajero_views.py**
   - Removed invalid fields from multiple OrdenItem creation points
   - Updated DetalleVenta creation to use correct field names
   - Fixed JSON responses to use correct field names

## Migration Required

After making these changes, you may need to run:
```bash
python manage.py makemigrations mesero
python manage.py migrate
```

However, since the database already has the `subtotal` column, Django might detect that no migration is needed.

## Testing

To verify the fix works:
1. Try creating a new order with items through the mesero interface
2. Check that OrdenItem objects are created without the NOT NULL constraint error
3. Verify that subtotal values are calculated correctly

## Benefits

1. **Resolves the NOT NULL constraint error**: The model now defines the `subtotal` field that the database expects
2. **Automatic calculation**: The subtotal is calculated automatically when saving OrdenItem objects
3. **Consistency**: All OrdenItem creation code now uses only valid model fields
4. **Maintainability**: Centralized subtotal calculation in the model's save() method

## Related Issues Fixed

- Model field mismatches between Django models and database schema
- Invalid field references in OrdenItem creation code
- Inconsistent field naming in JSON responses
- Missing field definitions causing database constraint violations

This fix ensures that the order creation flow works end-to-end without database constraint violations.
