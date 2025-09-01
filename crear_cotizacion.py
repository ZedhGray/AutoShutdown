import json
import logging
import sys
import io

# Configurar UTF-8 para Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import datetime
from database import get_db_connection, SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD

# Datos de prueba de Supabase
DATOS_SUPABASE_PRUEBA = [
    {"id": 1, "importe": "500.00", "pcompra": "", "cantidad": "1", "unitario": "500.00", "proveedor": "Garcia", "descripcion": "MANO DE OBRA"},
    {"id": 2, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Garcia", "descripcion": "RIN FIERRO"},
    {"id": 3, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Bustos", "descripcion": "ROTULA SUPERIOR"},
    {"id": 4, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Bustos", "descripcion": "AMORTIGUADOR DELANTERO"},
    {"id": 5, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Bustos", "descripcion": "BRIDAS"},
    {"id": 6, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Bustos", "descripcion": "GOMA DE REBOTE CON CUBRE POLVO"},
    {"id": 7, "importe": "1000.00", "pcompra": "", "cantidad": "1", "unitario": "1000", "proveedor": "Garcia", "descripcion": ""}

]

def get_next_folio():
    """
    Obtiene el siguiente folio disponible de la tabla Cotizaciones4.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(Folio) FROM Cotizaciones4")
        result = cursor.fetchone()
        
        if result and result[0]:
            return result[0] + 1
        else:
            return 1  # Si no hay registros, empezar en 1
            
    except Exception as e:
        logging.error(f"Error obteniendo siguiente folio: {e}")
        return None
    finally:
        conn.close()

def buscar_articulo_por_clave(clave):
    """
    Busca un artículo por clave exacta en Servicios e Inventario.
    Devuelve (clave, descripcion, precio, tabla_origen) o None si no encuentra.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        
        # Buscar en Servicios primero (campo Cve)
        cursor.execute("""
            SELECT Cve, Descripcion, Precio, 'Servicios' as Tabla
            FROM Servicios 
            WHERE Cve = ?
        """, (clave,))
        
        result = cursor.fetchone()
        if result:
            return result
        
        # Buscar en Inventario (campo Clave)
        cursor.execute("""
            SELECT Clave, Descripcion, PVenta, 'Inventario' as Tabla
            FROM [dbo].[Inventario]
            WHERE Clave = ?
        """, (clave,))
        
        result = cursor.fetchone()
        if result:
            return result
            
        return None
        
    except Exception as e:
        logging.error(f"Error buscando artículo por clave {clave}: {e}")
        return None
    finally:
        conn.close()

def buscar_articulo_por_descripcion(descripcion):
    """
    Busca un artículo en las tablas Servicios e Inventario por descripción.
    Primero busca coincidencia exacta, luego parcial con LIKE.
    Devuelve (clave, descripcion_encontrada, precio, tabla_origen) o None si no encuentra.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        descripcion_upper = descripcion.upper().strip()
        
        print(f"    Buscando en BD: '{descripcion_upper}'")
        
        # === PASO 1: BÚSQUEDA EXACTA ===
        # Buscar en Servicios - coincidencia exacta
        cursor.execute("""
            SELECT Cve, Descripcion, Precio, 'Servicios' as Tabla
            FROM Servicios 
            WHERE UPPER(LTRIM(RTRIM(Descripcion))) = ?
        """, (descripcion_upper,))
        
        result = cursor.fetchone()
        if result:
            print(f"    -> Encontrado exacto en Servicios: {result[0]} - {result[1]}")
            return result
        
        # Buscar en Inventario - coincidencia exacta
        cursor.execute("""
            SELECT Clave, Descripcion, PVenta, 'Inventario' as Tabla
            FROM [dbo].[Inventario]
            WHERE UPPER(LTRIM(RTRIM(Descripcion))) = ?
        """, (descripcion_upper,))
        
        result = cursor.fetchone()
        if result:
            print(f"    -> Encontrado exacto en Inventario: {result[0]} - {result[1]}")
            return result
        
        # === PASO 2: BÚSQUEDA PARCIAL CON LIKE ===
        # Buscar en Servicios - coincidencia parcial
        cursor.execute("""
            SELECT Cve, Descripcion, Precio, 'Servicios' as Tabla
            FROM Servicios 
            WHERE UPPER(Descripcion) LIKE ?
            ORDER BY LEN(Descripcion) ASC
        """, (f"%{descripcion_upper}%",))
        
        result = cursor.fetchone()
        if result:
            print(f"    -> Encontrado parcial en Servicios: {result[0]} - {result[1]}")
            return result
        
        # Buscar en Inventario - coincidencia parcial
        cursor.execute("""
            SELECT Clave, Descripcion, PVenta, 'Inventario' as Tabla
            FROM [dbo].[Inventario]
            WHERE UPPER(Descripcion) LIKE ?
            ORDER BY LEN(Descripcion) ASC
        """, (f"%{descripcion_upper}%",))
        
        result = cursor.fetchone()
        if result:
            print(f"    -> Encontrado parcial en Inventario: {result[0]} - {result[1]}")
            return result
            
        print(f"    -> No encontrado en BD")
        return None
        
    except Exception as e:
        logging.error(f"Error buscando artículo {descripcion}: {e}")
        return None
    finally:
        conn.close()

def aplicar_filtro_proveedor(articulo_info, proveedor):
    """
    Aplica filtro de proveedor según reglas de negocio:
    - Garcia: puede servicios + artículos limitados (aceites, rines, birlos, tuercas, válvulas)
    - Otros proveedores: solo artículos, NO servicios
    
    Retorna: (True/False, motivo_rechazo)
    """
    clave, descripcion, precio, tabla_origen = articulo_info
    proveedor_upper = proveedor.strip().upper()
    es_servicio = tabla_origen == 'Servicios'
    
    print(f"    Aplicando filtro proveedor: {proveedor_upper} | Tabla: {tabla_origen}")
    
    # ARTÍCULOS PERMITIDOS PARA GARCIA
    articulos_garcia_permitidos = [
        'ACEITE', 'RIN', 'RINES', 'LLANTA', 'LLANTAS', 'BIRLO', 'BIRLOS', 
        'TUERCA', 'TUERCAS', 'VALVULA', 'VALVULAS', 'ANTICONGELANTE',
        'LIQUIDO', 'GRASA', 'WD-40', 'AFLOJATODO'
    ]
    
    if proveedor_upper == "GARCIA":
        # Garcia puede dar servicios
        if es_servicio:
            print(f"    -> PERMITIDO: Garcia puede dar servicios")
            return True, ""
        
        # Garcia solo puede vender artículos de su lista
        if not es_servicio:
            descripcion_upper = descripcion.upper()
            articulo_permitido = any(art in descripcion_upper for art in articulos_garcia_permitidos)
            
            if articulo_permitido:
                print(f"    -> PERMITIDO: Artículo en lista de Garcia")
                return True, ""
            else:
                print(f"    -> RECHAZADO: Artículo NO permitido para Garcia")
                return False, f"Garcia no vende este tipo de artículo: {descripcion}"
    
    elif proveedor_upper != "":
        # Otros proveedores NO pueden dar servicios
        if es_servicio:
            print(f"    -> RECHAZADO: {proveedor_upper} no puede dar servicios")
            return False, f"{proveedor} no puede proporcionar servicios"
        
        # Otros proveedores SÍ pueden vender artículos
        print(f"    -> PERMITIDO: {proveedor_upper} puede vender artículos")
        return True, ""
    
    else:
        # Sin proveedor - permitir todo (compatibilidad anterior)
        print(f"    -> PERMITIDO: Sin proveedor especificado")
        return True, ""

def calcular_totales(items_supabase):
    """
    Calcula Total, Subtotal e IVA de los items.
    """
    total = sum(float(item["importe"]) for item in items_supabase)
    iva_rate = 0.16
    subtotal = total / (1 + iva_rate)
    iva = total - subtotal
    
    return total, subtotal, iva

def crear_cotizacion_header(folio, total, subtotal, iva, num_articulos):
    """
    Crea el registro principal en Cotizaciones4.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        # Fecha y hora actuales
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%I:%M:%S %p")
        
        cursor.execute("""
            INSERT INTO Cotizaciones4 
            (Folio, Fecha, Cliente, Ticket, Hora, Total, Subtotal, IVA, 
             Tipo, Usuario, Articulos, Descripcion, CveCte, Band)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            folio,
            fecha_actual,
            "PUBLICO EN GENERAL",
            "",  # Ticket vacío, lo genera el programa
            hora_actual,
            total,
            subtotal,
            iva,
            "POS",
            "MIR",
            str(num_articulos),
            "",  # Descripción vacía, la genera el programa
            "1500-0074",
            False
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        logging.error(f"Error creando header de cotización: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def crear_cotizacion_detalles(folio, items_mapeados):
    """
    Crea los detalles en Cotizaciones4Det.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        for item in items_mapeados:
            cursor.execute("""
                INSERT INTO Cotizaciones4Det 
                (Folio, Cant, Clave, Descripcion, Unitario, Importe, 
                 UnitarioSinIVA, ImporteSinIVA, Stock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                folio,
                float(item["cantidad"]),
                item["clave_local"],
                item["descripcion_local"],
                float(item["unitario"]),
                float(item["importe"]),
                float(item["unitario"]) / 1.16,  # Sin IVA
                float(item["importe"]) / 1.16,   # Sin IVA
                False  # Stock por defecto False
            ))
        
        conn.commit()
        return True
        
    except Exception as e:
        logging.error(f"Error creando detalles de cotización: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def procesar_cotizacion_supabase(datos_supabase):
    """
    Función principal simplificada - sin mapeo genérico.
    Solo busca directamente en la base de datos y aplica filtros de proveedor.
    """
    print("=== PROCESANDO COTIZACIÓN SUPABASE (SIN MAPEO GENÉRICO) ===\n")
    
    # 1. Obtener siguiente folio
    folio = get_next_folio()
    if not folio:
        print("❌ Error: No se pudo obtener el siguiente folio")
        return False
    
    print(f"✅ Folio asignado: {folio}")
    
    # 2. Procesar productos - SOLO BÚSQUEDA DIRECTA EN BD
    items_mapeados = []
    productos_no_encontrados = []
    productos_rechazados = []
    
    print(f"\n=== PROCESANDO {len(datos_supabase)} PRODUCTOS ===")
    
    for i, item in enumerate(datos_supabase, 1):
        descripcion = item["descripcion"].strip()
        proveedor = item.get("proveedor", "").strip()
        
        print(f"\n[{i}/{len(datos_supabase)}] '{descripcion}' | Proveedor: '{proveedor}'")
        
        # BÚSQUEDA DIRECTA EN BASE DE DATOS
        articulo_encontrado = buscar_articulo_por_descripcion(descripcion)
        
        if not articulo_encontrado:
            print(f"    ❌ No encontrado en BD")
            productos_no_encontrados.append({
                "descripcion": descripcion,
                "proveedor": proveedor,
                "motivo": "No existe en base de datos"
            })
            continue
        
        # APLICAR FILTRO DE PROVEEDOR
        permitido, motivo_rechazo = aplicar_filtro_proveedor(articulo_encontrado, proveedor)
        
        if not permitido:
            print(f"    ❌ Rechazado por filtro: {motivo_rechazo}")
            productos_rechazados.append({
                "descripcion": descripcion,
                "proveedor": proveedor,
                "motivo": motivo_rechazo
            })
            continue
        
        # PRODUCTO VÁLIDO - AGREGAR A LA COTIZACIÓN
        clave_local = articulo_encontrado[0]
        desc_local = articulo_encontrado[1]
        precio_local = articulo_encontrado[2]
        tabla_origen = articulo_encontrado[3]
        
        print(f"    ✅ Mapeado: [{tabla_origen}] {clave_local} - {desc_local} - ${precio_local}")
        
        items_mapeados.append({
            "clave_local": clave_local,
            "descripcion_local": desc_local,
            "cantidad": item["cantidad"],
            "unitario": item["unitario"],
            "importe": item["importe"]
        })
    
    # 3. MOSTRAR RESUMEN DE PROCESAMIENTO
    print(f"\n=== RESUMEN DE PROCESAMIENTO ===")
    print(f"✅ Productos procesados: {len(items_mapeados)}")
    print(f"❌ No encontrados en BD: {len(productos_no_encontrados)}")
    print(f"🚫 Rechazados por filtro: {len(productos_rechazados)}")
    
    # Mostrar productos no encontrados
    if productos_no_encontrados:
        print(f"\n--- PRODUCTOS NO ENCONTRADOS EN BD ---")
        for prod in productos_no_encontrados:
            print(f"  • {prod['descripcion']} ({prod['proveedor']}) - {prod['motivo']}")
    
    # Mostrar productos rechazados
    if productos_rechazados:
        print(f"\n--- PRODUCTOS RECHAZADOS POR FILTRO ---")
        for prod in productos_rechazados:
            print(f"  • {prod['descripcion']} ({prod['proveedor']}) - {prod['motivo']}")
    
    # 4. VERIFICAR SI HAY PRODUCTOS PARA PROCESAR
    if not items_mapeados:
        print(f"\n❌ No hay productos válidos para crear la cotización")
        return False
    
    # 5. CALCULAR TOTALES
    total, subtotal, iva = calcular_totales(datos_supabase)
    print(f"\n=== TOTALES ===")
    print(f"Total: ${total:.2f}")
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"IVA: ${iva:.2f}")
    
    # 6. CREAR COTIZACIÓN
    print(f"\n=== CREANDO COTIZACIÓN ===")
    
    # Header
    if not crear_cotizacion_header(folio, total, subtotal, iva, len(items_mapeados)):
        print("❌ Error creando header de cotización")
        return False
    
    print("✅ Header creado")
    
    # Detalles
    if not crear_cotizacion_detalles(folio, items_mapeados):
        print("❌ Error creando detalles de cotización")
        return False
    
    print("✅ Detalles creados")
    
    print(f"\n🎉 COTIZACIÓN {folio} CREADA EXITOSAMENTE")
    print(f"📊 Productos incluidos: {len(items_mapeados)}")
    
    if productos_no_encontrados or productos_rechazados:
        print(f"\n⚠️  NOTA: {len(productos_no_encontrados + productos_rechazados)} productos no fueron incluidos")
        print("Revisa el resumen arriba para más detalles")
    
    return True

# Ejecutar con datos de prueba
if __name__ == "__main__":
    print("=== CONVERSOR COTIZACIONES SUPABASE --> LOCAL (SIMPLIFICADO) ===")
    
    success = procesar_cotizacion_supabase(DATOS_SUPABASE_PRUEBA)
    
    if success:
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ El proceso falló")