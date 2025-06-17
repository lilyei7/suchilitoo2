@login_required
@require_POST
def duplicar_receta(request, receta_id):
    """Duplicar receta usando Django ORM para evitar problemas de cursor"""
    logger.info(f"Duplicando receta ID: {receta_id}")
    
    from django.db import transaction
    import time
    import random
    
    try:
        # Verificar que la receta original existe
        try:
            receta_original = Receta.objects.get(id=receta_id)
            producto_original = receta_original.producto
        except Receta.DoesNotExist:
            logger.error(f"Receta no encontrada: {receta_id}")
            return JsonResponse({
                'success': False,
                'message': 'Receta no encontrada'
            })
        
        # Crear código único para el nuevo producto
        timestamp = int(time.time())
        random_suffix = random.randint(100, 999)
        codigo_unico = f"REC{timestamp}{random_suffix}"
        
        # Verificar que el código no exista ya (aunque es muy improbable)
        contador_intentos = 0
        while ProductoVenta.objects.filter(codigo=codigo_unico).exists() and contador_intentos < 10:
            random_suffix = random.randint(100, 999)
            codigo_unico = f"REC{timestamp}{random_suffix}"
            contador_intentos += 1
        
        logger.info(f"Duplicando receta con nuevo código único: {codigo_unico}")
        
        # Crear copia del producto
        nombre_nuevo = f"Copia de {producto_original.nombre}"
        
        # Usar transacción para asegurar consistencia
        with transaction.atomic():
            try:
                # Crear nuevo producto usando Django ORM para evitar problemas de cursor
                # Convertir valores decimales a float para evitar problemas
                precio_seguro = float(producto_original.precio) if producto_original.precio else 0.0
                costo_seguro = float(producto_original.costo) if producto_original.costo else 0.0
                margen_seguro = float(producto_original.margen) if producto_original.margen else 0.0
                
                producto_nuevo = ProductoVenta.objects.create(
                    codigo=codigo_unico,
                    nombre=nombre_nuevo,
                    descripcion=producto_original.descripcion or '',
                    precio=Decimal(str(precio_seguro)),
                    costo=Decimal(str(costo_seguro)),
                    margen=Decimal(str(margen_seguro)),
                    tipo=producto_original.tipo or 'plato',
                    disponible=True,
                    es_promocion=producto_original.es_promocion or False,
                    destacado=producto_original.destacado or False,
                    categoria=producto_original.categoria
                )
                
                logger.info(f"Producto duplicado creado: {producto_nuevo.id}")
                
                # Crear nueva receta
                receta_nueva = Receta.objects.create(
                    producto=producto_nuevo,
                    tiempo_preparacion=receta_original.tiempo_preparacion or 0,
                    porciones=receta_original.porciones or 1,
                    instrucciones=receta_original.instrucciones or '',
                    activo=True
                )
                
                logger.info(f"Receta duplicada creada: {receta_nueva.id}")
                
                # Copiar ingredientes
                ingredientes_originales = RecetaInsumo.objects.filter(receta=receta_original)
                for ingrediente in ingredientes_originales:
                    try:
                        # Asegurar que la cantidad se maneja correctamente
                        cantidad = float(ingrediente.cantidad) if ingrediente.cantidad is not None else 0.0
                        
                        RecetaInsumo.objects.create(
                            receta=receta_nueva,
                            insumo=ingrediente.insumo,
                            cantidad=Decimal(str(cantidad)),
                            opcional=ingrediente.opcional or False,
                            notas=ingrediente.notas or '',
                            orden=ingrediente.orden or 0
                        )
                    except Exception as ing_error:
                        logger.error(f"Error copiando ingrediente {ingrediente.id}: {ing_error}")
                        # Continuar con el siguiente ingrediente
                
                logger.info(f"Receta {receta_id} duplicada como {receta_nueva.id} con éxito")
                
                return JsonResponse({
                    'success': True,
                    'receta': {
                        'id': receta_nueva.id,
                        'nombre': nombre_nuevo
                    },
                    'message': 'Receta duplicada correctamente'
                })
                
            except Exception as e:
                logger.error(f"Error en la transacción de duplicación: {e}")
                # Django manejará automáticamente el rollback
                return JsonResponse({
                    'success': False,
                    'message': f'Error al duplicar receta: {str(e)}'
                })
            
    except Exception as e:
        logger.error(f"Error al duplicar receta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al duplicar receta: {str(e)}'
        })
