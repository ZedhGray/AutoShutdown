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
    {"id": 1, "importe": "600.00", "pcompra": "400", "cantidad": "1", "unitario": "600.00", "proveedor": "Rios", "descripcion": "BALERO DOBLE"},
    {"id": 2, "importe": "500.00", "pcompra": "", "cantidad": "1", "unitario": "500", "proveedor": "Rios", "descripcion": "RIN FIERRO"},
    {"id": 3, "importe": "300.00", "pcompra": "", "cantidad": "2", "unitario": "150", "proveedor": "Rios", "descripcion": "BIRLO AUTOMOTRIZ"},
    {"id": 4, "importe": "50.00", "pcompra": "", "cantidad": "1", "unitario": "50", "proveedor": "Rios", "descripcion": "TUERCA"},
    {"id": 5, "importe": "450.00", "pcompra": "", "cantidad": "1", "unitario": "450", "proveedor": "Garcia", "descripcion": "MANO DE OBRA"}
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
    Devuelve (clave, descripcion_encontrada, precio, tabla_origen) o None si no encuentra.
    """
    conn = get_db_connection(SQL_SERVER_GARCIA, DATABASE, USERNAME, PASSWORD)
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        
        # Buscar en Servicios primero
        cursor.execute("""
            SELECT Cve, Descripcion, Precio, 'Servicios' as Tabla
            FROM Servicios 
            WHERE UPPER(Descripcion) LIKE UPPER(?)
        """, (f"%{descripcion}%",))
        
        result = cursor.fetchone()
        if result:
            return result
        
        # Buscar en Inventario
        cursor.execute("""
            SELECT Clave, Descripcion, PVenta, 'Inventario' as Tabla
            FROM [dbo].[Inventario]
            WHERE UPPER(Descripcion) LIKE UPPER(?)
        """, (f"%{descripcion}%",))
        
        result = cursor.fetchone()
        if result:
            return result
            
        return None
        
    except Exception as e:
        logging.error(f"Error buscando artículo {descripcion}: {e}")
        return None
    finally:
        conn.close()

def extraer_palabra_principal(descripcion):
    """
    Extrae la palabra principal de una descripción usando reglas de prioridad.
    """
    # Palabras clave que indican productos principales (no servicios)
    palabras_producto = {
        'ROTULA', 'BALERO', 'FILTRO', 'ACEITE', 'BUJIA', 'AMORTIGUADOR', 
        'TERMINAL', 'BOMBA', 'CILINDRO', 'DISCO', 'BALATA', 'ZAPATA',
        'BARRA', 'SOPORTE', 'GOMA', 'BUJE', 'HORQUILLA', 'FLECHA',
        'CRUCETA', 'TUERCA', 'BIRLO', 'TORNILLO', 'PERNO', 'CLAVO',
        'BANDA', 'POLEA', 'CLUTCH', 'BATERIA', 'ALTERNADOR', 'BOBINA',
        'SENSOR', 'FOCO', 'RIN', 'LLANTA', 'VALVULA', 'RESORTE',
        'SILENCIADOR', 'RADIADOR', 'BOMBA', 'MANGUERA', 'ABRAZADERA'
    }
    
    # Palabras de servicio/ubicación (menor prioridad como palabra principal)
    palabras_servicio = {
        'SERVICIO', 'CAMBIO', 'REPARACION', 'INSTALACION', 'MANTENIMIENTO',
        'REVISION', 'AJUSTE', 'LIMPIEZA', 'RECTIFICACION', 'MANO', 'OBRA'
    }
    
    # Palabras de ubicación/especificación (complementarias)
    palabras_ubicacion = {
        'DELANTERO', 'TRASERO', 'SUPERIOR', 'INFERIOR', 'DERECHO', 'IZQUIERDO',
        'EXTERIOR', 'INTERIOR', 'CENTRAL', 'LATERAL', 'DOBLE', 'SIMPLE'
    }
    
    palabras = descripcion.upper().split()
    
    # 1. Buscar palabra producto principal
    for palabra in palabras:
        if palabra in palabras_producto:
            return palabra
    
    # 2. Si no hay palabra producto, buscar la primera palabra significativa
    # (que no sea artículo, preposición o palabra muy común)
    palabras_ignorar = {'DE', 'DEL', 'LA', 'EL', 'LAS', 'LOS', 'Y', 'O', 'EN', 'CON', 'PARA', 'POR'}
    
    for palabra in palabras:
        if len(palabra) > 2 and palabra not in palabras_ignorar:
            return palabra
    
    return palabras[0] if palabras else ""

def crear_resultado_coincidencia(es_coincidencia, puntuacion, tipo, palabras_coincidentes):
    """Función auxiliar para crear el resultado de coincidencia."""
    return {
        "es_coincidencia": es_coincidencia,
        "puntuacion": puntuacion,
        "tipo": tipo,
        "palabras_coincidentes": palabras_coincidentes
    }

def verificar_orden_palabras(descripcion, concepto):
    """Verifica si las palabras aparecen en orden similar."""
    palabras_concepto = concepto.split()
    posiciones = []
    
    for palabra in palabras_concepto:
        pos = descripcion.find(palabra)
        if pos != -1:
            posiciones.append(pos)
        else:
            return False
    
    return posiciones == sorted(posiciones)

def analizar_coincidencia_mejorada(descripcion, concepto, proveedor_supabase=""):
    """
    Sistema mejorado que considera la palabra principal, proveedor y penaliza servicios innecesarios.
    """
    # Extraer palabra principal de la descripción
    palabra_principal = extraer_palabra_principal(descripcion)
    
    palabras_descripcion = set(descripcion.split())
    palabras_concepto = concepto.split()
    palabras_concepto_set = set(palabras_concepto)
    
    print(f"    Palabra principal: '{palabra_principal}' | Proveedor: '{proveedor_supabase}'")
    print(f"    Analizando concepto: '{concepto}'")
    
    # === SISTEMA DE PUNTUACIÓN MEJORADO ===
    
    # 1. Coincidencia exacta
    if descripcion == concepto:
        return crear_resultado_coincidencia(True, 1000, "EXACTA", palabras_concepto_set)
    
    # 2. Verificar si la palabra principal está en el concepto
    palabra_principal_en_concepto = palabra_principal in palabras_concepto_set
    
    if not palabra_principal_en_concepto:
        print(f"    ❌ Palabra principal '{palabra_principal}' NO está en concepto")
        return crear_resultado_coincidencia(False, 0, "SIN_PALABRA_PRINCIPAL", set())
    
    print(f"    ✅ Palabra principal '{palabra_principal}' SÍ está en concepto")
    
    # 3. Calcular coincidencias básicas
    palabras_coincidentes = palabras_concepto_set.intersection(palabras_descripcion)
    porcentaje_coincidencia = len(palabras_coincidentes) / len(palabras_concepto_set)
    
    # 4. FILTRO POR PROVEEDOR - REGLA DE NEGOCIO INTELIGENTE
    proveedor_limpio = proveedor_supabase.strip().upper()
    
    # ARTICULOS QUE GARCIA SÍ VENDE (el 10% de excepción)
    articulos_garcia_permitidos = {
        'RIN', 'RINES', 'LLANTA', 'LLANTAS', 'BIRLO', 'BIRLOS', 
        'TUERCA', 'TUERCAS', 'ACEITE', 'ACEITES', 'VALVULA', 'VALVULAS'
    }
    
    # Verificar si la descripción contiene artículos que Garcia sí vende
    descripcion_tiene_articulo_garcia = any(
        articulo in descripcion.upper() for articulo in articulos_garcia_permitidos
    )
    
    # Verificar si el concepto es un servicio
    es_servicio_concepto = any(palabra in concepto.upper() for palabra in 
                              ['SERVICIO', 'CAMBIO', 'REPARACION', 'INSTALACION', 'MANO DE OBRA', 'RECTIFICACION', 'ALINEACION', 'BALANCEO'])
    
    es_articulo_concepto = not es_servicio_concepto
    
    # LÓGICA INTELIGENTE PARA GARCIA
    if proveedor_limpio == "GARCIA":
        # Si Garcia y es un artículo que NO está en la lista permitida → RECHAZAR
        if es_articulo_concepto and not any(articulo in concepto.upper() for articulo in articulos_garcia_permitidos):
            print(f"    🚫 FILTRO GARCIA: Artículo '{concepto}' NO está en lista permitida para Garcia")
            return crear_resultado_coincidencia(False, 0, "ARTICULO_NO_PERMITIDO_GARCIA", set())
        
        # Si Garcia y es servicio → SIEMPRE PERMITIR
        if es_servicio_concepto:
            print(f"    ✅ GARCIA: Servicio permitido")
        
        # Si Garcia y es artículo permitido → PERMITIR
        elif es_articulo_concepto and any(articulo in concepto.upper() for articulo in articulos_garcia_permitidos):
            print(f"    ✅ GARCIA: Artículo en lista permitida")
    
    # LÓGICA PARA OTROS PROVEEDORES (solo artículos)
    elif proveedor_limpio != "" and proveedor_limpio != "GARCIA":
        if es_servicio_concepto:
            print(f"    🚫 FILTRO PROVEEDOR: '{proveedor_limpio}' NO vende servicios")
            return crear_resultado_coincidencia(False, 0, "SERVICIO_NO_PERMITIDO_PROVEEDOR", set())
        print(f"    ✅ PROVEEDOR: Artículo permitido para '{proveedor_limpio}'")
    
    # Sin proveedor - usar lógica anterior
    else:
        descripcion_es_producto = not any(palabra in descripcion.upper() for palabra in 
                                        ['SERVICIO', 'CAMBIO', 'REPARACION', 'INSTALACION'])
        
        if descripcion_es_producto and es_servicio_concepto:
            print(f"    ⚠️  PENALIZACION: Descripción es producto pero concepto es servicio")
            return crear_resultado_coincidencia(False, 0, "SERVICIO_INNECESARIO", set())
    
    # BONUS por coincidencia correcta de tipo
    bonus_tipo = 0
    if proveedor_limpio == "GARCIA":
        if es_servicio_concepto:
            bonus_tipo = 50  # Garcia + Servicio = bonus alto
            print(f"    🎯 BONUS GARCIA: Servicio = +{bonus_tipo}")
        elif es_articulo_concepto:
            bonus_tipo = 25  # Garcia + Artículo permitido = bonus moderado
            print(f"    🎯 BONUS GARCIA: Artículo permitido = +{bonus_tipo}")
    elif proveedor_limpio != "":
        bonus_tipo = 30  # Otros proveedores + Artículo = bonus normal
        print(f"    ✅ BONUS PROVEEDOR: Artículo = +{bonus_tipo}")
    
    # 5. Calcular puntuación base
    if len(palabras_coincidentes) == len(palabras_concepto_set):
        # Coincidencia completa
        puntuacion_base = 100 * len(palabras_concepto)
        tipo_coincidencia = "COMPLETA"
        
        # BONUS: Palabra principal en primera posición del concepto
        if palabras_concepto[0] == palabra_principal:
            puntuacion_base += 100
            print(f"    🎯 BONUS: Palabra principal en primera posición")
        
        # BONUS: Concepto corto y específico (menos ruido)
        if len(palabras_concepto) <= 3:
            puntuacion_base += 50
            print(f"    📏 BONUS: Concepto corto y específico")
        
        # PENALTY: Concepto muy largo (posible ruido)
        if len(palabras_concepto) > 5:
            penalty = (len(palabras_concepto) - 5) * 10
            puntuacion_base -= penalty
            print(f"    ❌ PENALTY: Concepto muy largo (-{penalty})")
        
        # BONUS: Orden correcto de palabras
        if verificar_orden_palabras(descripcion, concepto):
            puntuacion_base += 30
            print(f"    🔄 BONUS: Orden correcto de palabras")
        
        # Agregar bonus por tipo de proveedor
        puntuacion_base += bonus_tipo
            
    elif porcentaje_coincidencia >= 0.5:
        # Coincidencia parcial
        puntuacion_base = 50 * len(palabras_coincidentes)
        tipo_coincidencia = "PARCIAL"
        
        # Penalty más fuerte por palabras no coincidentes
        palabras_no_coincidentes = len(palabras_concepto_set) - len(palabras_coincidentes)
        penalty = 15 * palabras_no_coincidentes
        puntuacion_base -= penalty
        
        # Agregar bonus por tipo (reducido para parciales)
        puntuacion_base += bonus_tipo // 2
        
    else:
        return crear_resultado_coincidencia(False, 0, "INSUFICIENTE", set())
    
    # 6. BONUS adicional: Palabra principal es la primera palabra coincidente
    primera_coincidencia = None
    for palabra in palabras_concepto:
        if palabra in palabras_descripcion:
            primera_coincidencia = palabra
            break
    
    if primera_coincidencia == palabra_principal:
        puntuacion_base += 75
        print(f"    ⭐ BONUS: Palabra principal es la primera coincidencia")
    
    puntuacion_final = max(1, puntuacion_base)
    print(f"    📊 Puntuación final: {puntuacion_final}")
    
    return crear_resultado_coincidencia(
        True, puntuacion_final, tipo_coincidencia, palabras_coincidentes
    )

def mapear_producto_generico(descripcion, proveedor=""):
    """
    Mapea productos detallados a conceptos genéricos usando claves REALES de la base de datos.
    LÓGICA MEJORADA con filtro de proveedor:
    - Proveedor "Garcia" = servicios
    - Otros proveedores = artículos
    """
    
    # ======================================================================
    # MAPEOS ORGANIZADOS POR CATEGORÍAS - AQUÍ VAN TUS MAPEOS COMPLETOS
    # ======================================================================
    mapeos_genericos = {
        
        # ==================== ACEITES Y LUBRICANTES ====================
        # Aceites específicos por viscosidad
        "ACEITE MOBIL 15W40": "30614",
        "ACEITE 0W20 SINTETIC0": "6755",
        "ACEITE 0W40": "30748", 
        "ACEITE 15W30": "6411",
        "ACEITE 20W50 QUAKER GARRAFA": "6658",
        "ACEITE 20W50 NISSAN ORIGINAL": "6037",
        "ACEITE 90 MONOGRADO": "5675",
        "ACEITE BARDAL 80W90": "5920",
        "ACEITE MINERAL": "5776",
        "ACEITE MONOGRADO W40": "6056",
        "ACEITE VOLKSWAGEN ORIGINAL": "4867",
        "ACEITE VERMAR TOOL OIL": "AVT3/4",
        # Aceites por tipo/aplicación
        "ACEITE PARA TRANSMISION AUTOMATICA": "5191",
        "ACEITE P/TRANSMISION MERCON": "STL5",
        "ACEITE PARA DIRECC. HIDRAULICA": "5553",
        "ACEITE DE DIRECCION": "4723",
        "ACEITE PARA DIFERENCIAL": "5960",
        # Aceites genéricos
        "LITRO DE ACEITE 5W 30 SINTETICO": "4554",
        "LITRO DE ACEITE SAE90": "5187",
        "ACEITE": "4723",  # Genérico - usa aceite de dirección como base
        
        # ==================== ANTICONGELANTES Y FLUIDOS ====================
        "ANTICONGELANTE MOBIL ROSA GALON": "7501116201662",
        "ANTICONGELANTE MOBIL ROSA": "7501116201679",
        "ANTICONGELANTE MOBIL VERDE GALON": "7501116201617", 
        "ANTICONGELANTE MOBIL VERDE": "7501116201600",
        "ANTICONGELANTE": "7501116201600",  # Genérico
        "LIQUIDO DE FRENOS 1LT GONHER": "768994080865",
        "LIQUIDO DE FRENOS 250ML GONHER": "768994080858",
        "LIQUIDO DE FRENOS": "30968",
        "GRASA BAT 3": "5208",
        "GRASA": "31080",
        "WD-40 AEROSOL": "079567520221",
        "WD-40": "079567520221",
        "AFLOJATODO": "31000",
        
        # ==================== FRENOS - ESPECÍFICO A GENERAL ====================
        "BALATAS DELANTERAS": "30953",
        "BALATAS TRASERAS": "30708", 
        "BALATAS": "31021",  # Genérico
        "RECTIFICACION DE DISCO C/UNO": "4502",
        "DISCOS DELANTEROS": "6311",
        "DISCOS TRACEROS": "6608",
        "DISCO": "31053",
        "TAMBOR": "30755",
        "ZAPATAS PARA FRENOS": "4598",
        "ZAPATA": "4598",
        "BOMBA DE FRENOS O CILINDRO MAESTRO": "6313",
        "BOMBA DE FRENOS": "6313",
        "CILINDRO DE FRENOS": "4746",
        "CALIPER": "30648",
        "MANGUERA": "6854",
        "TUBO DE FRENO": "30711",
        "TUBO FRENO": "5079",
        
        # ==================== BALEROS - ESPECÍFICO A GENERAL ====================
        "BALERO DE TRASMISION": "31219",
        "BALERO DELANTERO": "30884",
        "BALERO EXTERIOR": "31204",
        "BALERO INFERIOR": "31205",
        "BALERO DOBLE": "30873",
        "BALERO HOMOCINETICO": "75926",
        "BALERO HOOMOCINETICO": "30811",
        "BALERO ESPIGA": "30658",
        "BALERO MASA": "30574",
        "BALERO TIPOIDE": "30732",
        "BALERO": "30572",  # Genérico
        
        # ==================== FILTROS - ESPECÍFICO A GENERAL ====================
        "FILTRO DE COMBUSTIBLE DIESEL": "6746",
        "FILTRO DE GASOLINA": "30679",
        "FILTRO DE ACEITE": "31191",
        "FILTO DE ACEITE NISSAN VERSA": "4555",
        "FILTRO DE AIRE": "30557",
        "FILTRO": "31107",  # Genérico
        
        # ==================== ACEITES MOBIL ESPECÍFICOS ====================
        "MOBIL DELVAC 15W40 1300 CUBETA": "MBVAC15WCB",
        "MOBIL DELVAC 15W40 GALON": "7501116200955",
        "MOBIL DELVAC LEGEND 25W50 CUBETA": "MBLG25WCB",
        "MOBIL ATF D/M CUBETA": "MBDMCB",
        "MOBIL MULTIGRADO 15W40 CUBETA": "1540MG",
        "MOBIL SUPER TRC-PRO 15W40 GALON": "7501116200146",
        "MOBIL SUPER TRC-PRO 20W50 GALON": "7501116200153",
        "MOBIL 15W40 1LT SUPER TRC-PRO": "7501116200061",
        "MOBIL 20W50 1LT SUPER TRC-PRO": "7501116200078",
        "MOBIL 5W20 1LT SUPER ANTIFRICTION": "7501116200115",
        "MOBIL 5W30 1LT SYNTETIC": "7501116200474",
        "MOBIL 5W30 1LT ANTIFRICTION": "7501116200108",
        "MOBIL EXTENGINE 5W30 1LT": "7501116200122",
        "MOBIL 15W50 1LT SINTETICO": "5W50ACMB",
        
        # ==================== BANDAS Y TRANSMISIÓN ====================
        "KIT DE BANDA DE DISTRIBUCION": "5202",
        "BANDA DE DISTRIBUCION": "5202",
        "BANDA DE ACCESORIOS": "5466",
        "BANDA AUTOMOTRIZ": "31223",
        "POLEA": "5467",
        "CLUTCH": "6909",
        "KIT DE ENBRAGUE NP 300": "6699",
        "CILINDRO CLUCH": "5707",
        "CARTER DE TRANSMISION": "5314",
        
        # ==================== BATERÍA Y ELÉCTRICOS ====================
        "BATERIA": "6850",
        "ALTERNADOR": "4831",
        "BOBINA": "30931",
        "RELEVADOR": "5942",
        "SENSOR ABS": "6805",
        "SENSOR TPMS CON VALVULA DE ALUMINIO": "6695",
        "SENSOR TPMS CON VALVULA DE HULE": "6694",
        "FOCO DE FARO DELANTERO": "5261",
        "FOCO": "5261",
        "BOTON INTERMITENTE": "5943",
        "TABLERO LED": "4968",
        
        # ==================== SOPORTES - ESPECÍFICO A GENERAL ====================
        "SOPORTE DE TRANSMISION": "6852",
        "SOPORTE DE MOTOR": "6911",
        "SOPORTE DE ESCAPE": "5558",
        "SOPORTE DE TORSION O HUESO": "4487",
        "SOPORTE DE CAJA DE CABINA": "5557",
        "SOPORTE TIPO HUESO": "6189",
        "SOPORTE CENTRAL": "5254",
        "SOPORTE HUESO": "6189",
        "SOPORTE GENERAL": "6663",
        "SOPORTE": "6663",  # Genérico
        "MUELAS DE SOPORTE": "31213",
        
        # ==================== GOMAS Y CAUCHOS - ESPECÍFICO A GENERAL ====================
        "GOMAS DE BARRA ESTABILIZADORA": "5463",
        "GOMA BUJE BARRA ESTABILIZADORA": "30702",
        "GOMA DE REBOTE CON CUBRE POLVO": "30855",
        "GOMA DE REBOTE": "30579",
        "GOMA DE DIRECCION": "31055",
        "GOMA DE TIRANTE": "30542",
        "GOMAS AMORTIGUADOR": "30839",
        "GOMAS DE ESTABILIZADORA": "5442",
        "GOMAS DE TORNILLO ESTABILIZADOR": "6778",
        "GOMAS": "31007",  # Genérico
        
        # ==================== DIRECCION - ESPECÍFICO A GENERAL ====================
        "TERMINAL DE DIRECCION": "30843",
        "BOMBA DE DIRECCION HIDRAULICA": "6910",
        "BARRA CENTRAL DE DIRRECION": "4995",
        "VARILLA DE DIRECCION": "30876",
        "CAJA DE DIRECCION": "31051",
        "CREMALLERA DE DIRECCION": "4975",
        "CRUCETA DE DIRECCION": "4720",
        "TERMINAL SUPERIOR": "6782",
        "TERMINAL INFERIOR": "6783",
        "TERMINA DERECHA": "31157",
        "TERMINAL": "31169",  # Genérico
        
        # ==================== AMORTIGUADORES Y SUSPENSIÓN ====================
        "BRIDAS DE AMORTIGUADOR": "30571",
        "BASE DE AMORTIGUADOR": "31166",
        "CUBRE POLVO DE AMORTIGUADOR": "30897",
        "KIT SOPORTE AMORTIGUADOR": "31087",
        "KIT RESORTE AMORTIGUADOR": "30580",
        "AMORTIGUADORES": "31047",
        "AMORTIGUADOR": "31160",
        "COMPLEMENTO DE SUSPENSION": "4989",
        "SUSPENSION SUPERIOR": "30905",
        
        # ==================== BARRA ESTABILIZADORA ====================
        "BUJE DE BARRA ESTABILIZADORA": "31200",
        "TORNILLO ESTABILIZADOR": "4654",
        "BARRA ESTABILIZADORA": "30802",
        
        # ==================== BUJES Y HORQUILLAS ====================
        "BUJES DE HORQUILLA": "30972",
        "HORQUILLA C/BUJES": "31071",
        "HORQUILLA COMPLETA": "6312",
        "HORQUILLA": "6312",
        "BARRA HORQUILLA SUPERIOR": "30882",
        "BUJE": "30514",
        
        # ==================== ROTULAS - ESPECÍFICO A GENERAL ====================
        "ROTULA DELANTERA": "5487",
        "ROTULA SUPERIOR": "5490",
        "ROTULA INFERIOR": "5735",
        "ROTULA DERECHA": "30578",
        "ROTULA IZQUIERDA": "5564",
        "ROTULAS": "30724",
        "ROTULA": "31048",  # Genérico
        
        # ==================== BUJIAS ====================
        "CAPUCHON PARA BUJIA": "6036",
        "BUJIAS": "30615",
        "BUJIA": "31194",
        "AUMENTADOR DE BUGIA": "31130",
        
        # ==================== CACAHUATES ====================
        "CACAHUATES": "31104",
        "CACAHUATE": "30809",
        
        # ==================== RESORTES ====================
        "BASE RESORTE": "6889",
        "MUELA RESORTE": "6404",
        "RESORTE": "31086",
        
        # ==================== ESCAPE Y SILENCIADORES ====================
        "TRAMO DE TUBO DE ESCAPE": "6925",
        "CURVA DE ESCAPE": "6738",
        "SILENCIADOR Y SOPORTE": "5306",
        "SILENCIADOR": "5306",
        "PRESILENCIADOR": "4967",
        
        # ==================== VÁLVULAS ====================
        "VALVULA P/RIN CON SENSOR TPMS": "VSENSOR",
        "VALVULA P/RIN DE CAMION DOBLADA DE ALUMINIO": "545DVL",
        "VALVULA P/RIN DE CAMION DOBLADA DE BRONZE": "6703",
        "VALVULA P/RIN DE CAMION NORMAL": "573438VL",
        "VALVULA P/RIN DE MOTO CROMADA RECTA": "4700",
        "VALVULA P/RIN DE MOTO DOBLADA CROMADA": "VDPS",
        "VALVULA P/RIN DE MOTO HULE DOBLADA": "6444",
        "VALVULA P/RIN DE RETRO": "3204VL",
        "VALVULA DE HULE GRUESA": "4558",
        "VALVULA DE HULE": "4450",
        "VALVULA P/RIN": "4450",  # Genérico
        "VALVULA": "4450",  # Genérico
        "AUMENTO PARA VALVULA": "6443",
        
        # ==================== KITS - ESPECÍFICO A GENERAL ====================
        "KIT BIRLOS DE SEGURIDAD 12X1.25": "KITBS-12X1.25",
        "KIT BIRLOS DE SEGURIDAD 12X1.5": "KITBS-12X1.5",
        "KIT BIRLOS DE SEGURIDAD 14X1.25": "KITBS-14X1.25",
        "KIT BIRLOS DE SEGURIDAD 14X1.5": "KITBS-14X1.5",
        "KIT TUERCAS DE SEGURIDAD 1/2-20": "KITTS-1-2-20",
        "KIT TUERCAS DE SEGURIDAD 12X1.25": "KITTS-12X1.25",
        "KIT TUERCAS DE SEGURIDAD 12X1.5": "KITTS-12X1.5",
        "KIT TUERCAS DE SEGURIDAD 12X1.75": "KITTS-12X1.75",
        "KIT TUERCAS DE SEGURIDAD 14X1.5": "KITTS-14X1.5",
        "KIT TUERCAS DE SEGURIDAD 14X2": "KITTS-14X2",
        "KIT TUERCAS DE SEGURIDAD 9/16": "KITTS-9-16",
        "KIT DE BALERO": "30976",
        "KIT DE FRENOS": "31066",
        "KIT FRENOS": "31023",
        "KIT DE HERRAJE": "30774",
        "KIT LIGAS": "30587",
        "KIT DE HERRAMIENTA PARA CAMBIO DE LLANTA": "6927",
        
        # ==================== TUERCAS - ESPECÍFICO A GENERAL ====================
        "TUERCA CAMPANA FLOTANTE M12X1.75": "TCAMPANAF12175H19MM",
        "TUERCA CAMPANA M14X1.5": "TCAMPANA1415H19MM",
        "TUERCA CODIGO K FORJADA LARGA 14X2": "TCODIGOKFL142",
        "TUERCA CODIGO K FORJADA LARGA 14X1.5": "TCODIGOKFL1415",
        "TUERCA CODIGO K FORJADA LARGA 12X1.5": "TUERCACOKFL215",
        "TUERCA CODIGO K FORJADA 14X1.5": "TUERCA1412KF",
        "TUERCA CODIGO K FORJADA 12X1.50": "TUERCACOKF1215",
        "TUERCA CODIGO K FORJADA 12X1.25": "TCODIGOKF1225",
        "TUERCA CODIGO K FORJADA 7/16X20": "TCODIGO716KF",
        "TUERCA CODIGO K FORJADA 1/2X20": "TCODIGOKF1220",
        "TUERCA CODIGO K ABIERTA 14X2": "TCK142",
        "TUERCA CODIGO K ABIERTA 12X1.75": "TUERCA12175",
        "TUERCA TROPICALIZADA CON CAMPANA FLOTANTE": "6711",
        "TUERCA TIPO BOTELLA 12X1.5": "TCONICA1215H13819MM",
        "TUERCA DE LUJO 14X1.5 HEX 22MM": "TLUJO1415H22MM",
        "TUERCA DE LUJO 14X1.25": "TLUJO1415H21MMA405",
        "TUERCA DE LUJO 12X1.75": "TLUJO1215H21MM",
        "TUERCA DE LUJO 12X1.5": "TLUJO1215H19MM",
        "TUERCA DE LUJO 12X1.25": "TA30-312RC",
        "TUERCA DE LUJO 9/16X18": "TLUJO91618H78",
        "TUERCA DE LUJO 7/16X20": "6438",
        "TUERCA DE LUJO 1/2X20": "TLUJO1220H34",
        "TUERCA CONICA M14X1.5": "TCONICA1415H22MM",
        "TUERCA CONICA M12X1.5": "TCONICA1215H19MM",
        "TUERCA CONICA M12X1.25": "TCONICA12125H1316",
        "TUERCA CONICA ABIERTA 12X1.25": "TCONICAA12125",
        "TUERCA CONICA 1/2-20": "TCONICA1220H34",
        "TUERCA CON CUELLO 14X2": "TCONICA142H21MM",
        "TUERCA TUNNER 12X1.5": "TT1215LLAVEH",
        "TUERCA TUNNER 12X1.25": "TT12125LLAVEH",
        "TUERCA TUNNER 1/2X20": "TT1220LLAVEH",
        "TUERCA 14X1.5 CON CUELLO Y RONDANA": "TUERCA1721047P",
        "TUERCA 12X1.25 BOLITA": "4371",
        "TUERCA 12X1.25 ACERO CERRADA": "T12125ABH1316",
        "TUERCA DE LUJO": "TA30-312RC",  # Genérico
        "TUERCA CONICA": "TCONICA12125H1316",  # Genérico
        "TUERCA TUNNER": "TT12125LLAVEH",  # Genérico
        "TUERCA": "4927",  # Genérico
        
        # ==================== BIRLOS - ESPECÍFICO A GENERAL ====================
        "BIRLO TUNNER 7 PUNTAS 14X1.25": "6710",
        "BIRLO TUNNER 7 PUNTAS 12X1.5": "BTH1215L",
        "BIRLO TUNNER 7 PUNTAS 12X1.25 LARGO": "BT12125LLAVEL7P",
        "BIRLO TUNNER 7 PUNTAS 12X1.25 CORTO": "BT12125LLAVEH",
        "BIRLO TUNNER 14X1.5 LARGO": "BT1415LLLAVEH",
        "BIRLO TUNNER 14X1.5": "BT1415LLAVEH",
        "BIRLO TUNNER 14X1.25": "BTN1425HEX",
        "BIRLO TUNNER 12X1.5 LARGO": "BT1215LLAVEHLARGO",
        "BIRLO TUNNER 12X1.5 CORTO": "BT1215CLLAVEH",
        "BIRLO NORMAL 12X1.25 HEX 3/4": "6721",
        "BIRLO NORMAL 12X1.25 HEX 11/16": "6722",
        "BIRLO AUTOMOTRIZ": "31041",
        "BIRLO AUTOMOTRIS": "30611",
        "BIRLO AUTOMOTRIZ": "30904",
        "BIRLO TUNNER": "BT12125LLAVEH",  # Genérico
        "BIRLO NORMAL": "6721",  # Genérico
        "BIRLO": "31059",  # Genérico
        
        # ==================== OTROS CONCEPTOS IMPORTANTES ====================
        "ABRAZADERAS": "30760",
        "ABRAZADERA": "30667",
        "ARO DENTADO": "31217",
        "BRIDA": "31109",
        "BIELETA": "31002",
        "MAZA": "31091",
        "MASA COMPLETA": "31132",
        "DISCO": "31053",
        "RETEN": "30530",
        "CUBRE POLVO DE FLECHA": "4894",
        "CUBRE POLVO DE VIELETA": "4574",
        "CUBRE POLVO TRASERO": "5379",
        "CUBRE POLVO": "31165",
        "TRIPOIDE": "30784",
        "FLECHA COMPLETA": "5921",
        "FLECHA": "5921",
        "CRUCETA": "30765",
        "TORNILLO Y RONDANA": "6080",
        "TORNILLO ESCALA": "5556",
        "TORNILLO": "30898",
        "PIJA": "5992",
        "PERNOS": "30525",
        "GRAPA": "30966",
        "GRAPAS": "30966",
        "RADIADOR/ENFRIADOR": "4954",
        "RADIADOR": "4954",
        "ENFRIADOR": "4954",
        "TAPON DE RADIADOR": "30467",
        "TAPON ACEITE": "31044",
        "TAPON": "31075",
        "BOMBA DE AGUA": "4988",
        "BOMBA DE GASOLINA": "4822",
        "BARRA CENTRAL": "30877",
        "RIN ALUMINIO": "6920",
        "RIN FIERRO": "6919",
        "LIMPIADOR DE CUERPO DE ACELERACION": "30937",
        "LIMPIADOR CUERPO DE ACELERACION": "123",
        "LIMPIEZA CUERPO DE ACELERACION": "4999",
        "SILICON O SELLADOR": "4745",
        "SILICON": "30682",
        "SELLADOR PARA JUNTA DE CABEZA": "5853",
        "SELLADOR": "30581",
        "CILINDROS": "30735",
        "CILINDRO": "30523",
        "GUARNICION": "30586",
        "GUARNICIONES DE SKU": "4725",
        "HERRAJE DELANTERO": "30599",
        "HERRAJE TRASERO": "30598",
        "JUEGO DE HERRAJES TRACEROS": "30938",
        "JUEGO DE JUNTAS": "30993",
        "JUEGO DE LIGAS CALIPER": "30728",
        "JUEGO DE REPUESTO": "30743",
        "REPESTO DE HERRAJE": "30562",
        "REPUESTOS PARA EMBULOS": "30775",
        "LIGAS": "31058",
        "TIRANTE": "5587",
        "TOMA DE AGUA": "5404",
        "VENTILADOR DE MOTOR": "5692",
        "VIELETA DELANTERA": "5534",
        "VIELETAS": "31090",
        "VIELETA": "31148",
        "RONDANA PLANA AUTOMOTRIZ": "5207",
        "RONDANA": "30899",
        "INSERTO": "30923",
        "COLUMPIO": "5515",
        "BRAZO AUXILIAR": "30981",
        "CINTURON DE SEGURIDAD": "6926",
        "CINTA DE AISLAR": "30971",
        "CINCHOS": "31081",
        "CLAVO": "30722",
        "COPLE": "30895",
        "ESTOPA": "30753",
        "EXTRACTOR": "6823",
        "MACHETA": "31070",
        "MACHUELA": "31233",
        "MANGO TRASERO": "5282",
        "MANGO": "30859",
        "NUDOS PARA CABLE": "30685",
        "PIEZA GALLETA": "6757",
        "REGULADOR DE PRESION": "6535",
        "SEGUROS": "STL2",
        "SIN FIN VOYAGUER": "6233",
        "SOLDADURA": "6081",
        "ESTRUCTURA METALICA": "5777",
        "EXTRACCION DE CAPUCHON": "5958",
        "DEPOSITO DE ANTICONGELANTE": "30997",
        "TAPA DE DEPOSITO": "6367",
        "TAPA DE PUNTERIA COMPLETA": "6088",
        "TAPAS DE RINES": "4779",
        "EMPAQUE DE PUNTERIA DE MOTOR": "5124",
        "CARBUKLIN": "30646",
        "ADITIVO BARDAHL 2 450ML": "5547",
        "LIMPIADOR DE INYECTORES WURTHA": "4045989294404",
        "HYDRAULICO OIL AW68 CUBETA": "HYDRAAW68",
        "ROSHFRAN ACEITE 20W50 ALTO KILOMETRAJE": "5265",
        
        # ==================== MANO DE OBRA ====================
        "MANO DE OBRA A DOMICILIO": "4518",
        "MANO DE OBRA": "1999",  # Genérico
        
        # ==================== ALINEACIÓN ====================
        "ALINEACION CAMIONETA": "4440",
        "ALINEACION AUTO": "6267",
        
        # ==================== BALANCEO ====================
        "BALANCEO RIN ALUMINIO": "4435",
        "BALANCEO RIN FIERRO": "6259",
    }
    
    
    # ======================================================================
    # APLICAR LA LÓGICA DE ANÁLISIS MEJORADA
    # ======================================================================
    
    # Limpiar y normalizar la descripción de entrada
    descripcion_limpia = descripcion.strip().upper()
    proveedor_limpio = proveedor.strip()
    
    # Lista para almacenar coincidencias con su puntuación
    coincidencias = []
    
    print(f"\n  >> Analizando: '{descripcion_limpia}' | Proveedor: '{proveedor_limpio}'")
    
    for concepto, clave_generica in mapeos_genericos.items():
        coincidencia_info = analizar_coincidencia_mejorada(descripcion_limpia, concepto, proveedor_limpio)
        
        if coincidencia_info["es_coincidencia"]:
            coincidencias.append({
                "concepto": concepto,
                "clave": clave_generica,
                "puntuacion": coincidencia_info["puntuacion"],
                "tipo_coincidencia": coincidencia_info["tipo"],
                "palabras_coincidentes": coincidencia_info["palabras_coincidentes"]
            })
    
    if not coincidencias:
        print("  >> No se encontraron coincidencias válidas")
        return None, None, None
    
    # Ordenar por puntuación (mayor a menor)
    coincidencias.sort(key=lambda x: x["puntuacion"], reverse=True)
    
    # Mostrar análisis de coincidencias
    print(f"  >> Coincidencias encontradas:")
    for i, c in enumerate(coincidencias[:3]):  # Mostrar top 3
        print(f"     {i+1}. {c['concepto']} - Puntuación: {c['puntuacion']} ({c['tipo_coincidencia']})")
    
    # Tomar la mejor coincidencia
    mejor_coincidencia = coincidencias[0]
    concepto_elegido = mejor_coincidencia["concepto"]
    clave_generica = mejor_coincidencia["clave"]
    
    print(f"  >> ELEGIDO: {concepto_elegido} (Puntuación: {mejor_coincidencia['puntuacion']})")
    
    # Buscar el artículo completo por clave
    articulo = buscar_articulo_por_clave(clave_generica)
    if articulo:
        return articulo[0], articulo[1], articulo[2]  # clave, descripcion, precio
    else:
        print(f"  ! Mapeo encontrado pero clave '{clave_generica}' no existe en BD")
        return None, None, None

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
    Función principal que procesa una cotización de Supabase y la convierte a formato local.
    """
    print("=== PROCESANDO COTIZACIÓN SUPABASE ===\n")
    
    # 1. Obtener siguiente folio
    folio = get_next_folio()
    if not folio:
        print("X Error: No se pudo obtener el siguiente folio")
        return False
    
    print(f"+ Folio asignado: {folio}")
    
    # 2. Mapear productos
    items_mapeados = []
    productos_no_encontrados = []
    
    print("\n=== MAPEANDO PRODUCTOS ===")
    
    for item in datos_supabase:
        descripcion = item["descripcion"].strip()
        proveedor = item.get("proveedor", "").strip()  # NUEVO: Obtener proveedor
        
        print(f"\nProcesando: {descripcion} | Proveedor: {proveedor}")
        
        # PRIMERO: Buscar mapeo genérico (más común) CON PROVEEDOR
        clave_local, desc_local, precio_local = mapear_producto_generico(descripcion, proveedor)
        
        if clave_local:
            print(f"  + Mapeado generico: {clave_local} - {desc_local} - ${precio_local}")
        else:
            # SEGUNDO: Buscar exacto en base de datos (menos común)
            articulo_encontrado = buscar_articulo_por_descripcion(descripcion)
            
            if articulo_encontrado:
                clave_local = articulo_encontrado[0]
                desc_local = articulo_encontrado[1]
                precio_local = articulo_encontrado[2]
                tabla_origen = articulo_encontrado[3]
                print(f"  + Encontrado exacto en {tabla_origen}: {clave_local} - {desc_local} - ${precio_local}")
            else:
                print(f"  X No encontrado: {descripcion}")
                productos_no_encontrados.append(descripcion)
                continue
        
        # Agregar item mapeado
        items_mapeados.append({
            "clave_local": clave_local,
            "descripcion_local": desc_local,
            "cantidad": item["cantidad"],
            "unitario": item["unitario"],
            "importe": item["importe"]
        })
    
    # 3. Mostrar productos no encontrados (sin detener el proceso)
    if productos_no_encontrados:
        print(f"\n! PRODUCTOS NO ENCONTRADOS ({len(productos_no_encontrados)}):")
        print("Estos productos deben agregarse manualmente:")
        for prod in productos_no_encontrados:
            print(f"  - {prod}")
        print(f"\nContinuando con {len(items_mapeados)} productos encontrados...")
    
    # 4. Calcular totales
    total, subtotal, iva = calcular_totales(datos_supabase)
    print(f"\n=== TOTALES ===")
    print(f"Total: ${total:.2f}")
    print(f"Subtotal: ${subtotal:.2f}")
    print(f"IVA: ${iva:.2f}")
    
    # 5. Crear cotización
    print(f"\n=== CREANDO COTIZACIÓN ===")
    
    # Header
    if not crear_cotizacion_header(folio, total, subtotal, iva, len(items_mapeados)):
        print("X Error creando header de cotizacion")
        return False
    
    print("+ Header creado")
    
    # Detalles
    if not crear_cotizacion_detalles(folio, items_mapeados):
        print("X Error creando detalles de cotizacion")
        return False
    
    print("+ Detalles creados")
    
    print(f"\n*** COTIZACION {folio} CREADA EXITOSAMENTE ***")
    print(f"Productos procesados: {len(items_mapeados)}")
    
    return True

# Ejecutar con datos de prueba
if __name__ == "__main__":
    print("=== CONVERSOR COTIZACIONES SUPABASE --> LOCAL (MEJORADO) ===")
    
    # Casos de prueba específicos para Garcia
    print("\n=== CASOS DE PRUEBA PARA GARCIA ===")
    casos_garcia = [
        # ARTICULOS PERMITIDOS para Garcia (10%)
        ("RIN FIERRO 15 PULGADAS", "Garcia"),           # ✅ Permitido
        ("LLANTA MICHELIN 195/65", "Garcia"),           # ✅ Permitido  
        ("BIRLO AUTOMOTRIZ 12X1.25", "Garcia"),         # ✅ Permitido
        ("TUERCA CONICA 14X1.5", "Garcia"),             # ✅ Permitido
        ("ACEITE MOBIL 15W40", "Garcia"),               # ✅ Permitido
        ("VALVULA P/RIN DE HULE", "Garcia"),            # ✅ Permitido
        
        # SERVICIOS para Garcia (90%)
        ("MANO DE OBRA ESPECIALIZADA", "Garcia"),       # ✅ Permitido
        ("CAMBIO DE ACEITE COMPLETO", "Garcia"),        # ✅ Permitido
        ("ALINEACION Y BALANCEO", "Garcia"),            # ✅ Permitido
        
        # ARTICULOS NO PERMITIDOS para Garcia
        ("ROTULA SUPERIOR PREMIUM", "Garcia"),          # ❌ Garcia no vende rótulas
        ("FILTRO DE ACEITE FRAM", "Garcia"),            # ❌ Garcia no vende filtros
        ("AMORTIGUADOR DELANTERO", "Garcia"),           # ❌ Garcia no vende amortiguadores
        
        # OTROS PROVEEDORES (solo artículos)
        ("ROTULA SUPERIOR PREMIUM", "Rios"),            # ✅ Permitido
        ("MANO DE OBRA", "Rios"),                       # ❌ Rios no da servicios
        ("ACEITE MOBIL 15W40", "Mobil"),               # ✅ Permitido
    ]
    
    print("Probando lógica de Garcia...")
    for desc, prov in casos_garcia:
        print(f"\n{'─'*50}")
        print(f"📝 Caso: '{desc}' | Proveedor: '{prov}'")
        resultado = mapear_producto_generico(desc, prov)
        if resultado[0]:
            print(f"✅ Mapeado: {resultado[1]} ({resultado[0]})")
        else:
            print(f"❌ No mapeado")
    
    print(f"\n{'='*60}")
    print("=== PROCESAMIENTO NORMAL ===")
    
    success = procesar_cotizacion_supabase(DATOS_SUPABASE_PRUEBA)
    
    if success:
        print("\n+ Proceso completado exitosamente")
    else:
        print("\nX El proceso fallo")