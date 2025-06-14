import sqlite3
import os

# Conectar a la base de datos SQLite
db_path = os.path.join(os.getcwd(), 'db.sqlite3')
if not os.path.exists(db_path):
    print(f"❌ Base de datos no encontrada en: {db_path}")
    exit(1)

print(f"📊 Conectando a base de datos: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar estructura de la tabla
print("\n=== ESTRUCTURA DE LA TABLA restaurant_insumo ===")
cursor.execute("PRAGMA table_info(restaurant_insumo)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Verificar todos los insumos
print("\n=== TODOS LOS INSUMOS ===")
cursor.execute("SELECT id, codigo, nombre, tipo, activo FROM restaurant_insumo ORDER BY id")
insumos = cursor.fetchall()
print(f"Total de insumos: {len(insumos)}")

for insumo in insumos:
    print(f"ID {insumo[0]}: {insumo[1]} - {insumo[2]} (tipo: {insumo[3]}, activo: {insumo[4]})")

# Verificar específicamente el ID 47
print("\n=== VERIFICACIÓN DEL ID 47 ===")
cursor.execute("SELECT * FROM restaurant_insumo WHERE id = 47")
insumo_47 = cursor.fetchone()

if insumo_47:
    print(f"✅ Insumo ID 47 EXISTE:")
    print(f"   - Código: {insumo_47[1]}")
    print(f"   - Nombre: {insumo_47[2]}")
    print(f"   - Tipo: {insumo_47[4]}")
    print(f"   - Activo: {insumo_47[12]}")
    print(f"   - Precio: {insumo_47[8]}")
else:
    print("❌ Insumo ID 47 NO EXISTE")

# Ver los últimos IDs creados
print("\n=== ÚLTIMOS INSUMOS CREADOS ===")
cursor.execute("SELECT id, codigo, nombre, tipo, activo FROM restaurant_insumo ORDER BY id DESC LIMIT 10")
ultimos = cursor.fetchall()
for insumo in ultimos:
    print(f"ID {insumo[0]}: {insumo[1]} - {insumo[2]} (tipo: {insumo[3]}, activo: {insumo[4]})")

# Verificar insumos por tipo
print("\n=== INSUMOS POR TIPO ===")
for tipo in ['basico', 'compuesto', 'elaborado']:
    cursor.execute("SELECT COUNT(*) FROM restaurant_insumo WHERE tipo = ? AND activo = 1", (tipo,))
    count = cursor.fetchone()[0]
    print(f"Insumos {tipo} activos: {count}")

conn.close()
print("\n✅ Verificación completada")
