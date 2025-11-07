# 🚀 PROPUESTA: Sistema Optimizado de Pagos AUTONEW

## 📋 **ANÁLISIS DEL SISTEMA ACTUAL**

### **Fortalezas Identificadas:**
✅ **Estructura de modelos bien definida** para diferentes tipos de usuarios  
✅ **Sistema de descuentos flexible** (individuales y empresariales)  
✅ **Soporte para múltiples tipos de suscripción**  
✅ **Cálculos automáticos de precios** con descuentos aplicados  

### **Oportunidades de Mejora:**
🔄 **Falta un modelo unificado para comisiones a empresas**  
🔄 **No hay trazabilidad de liquidaciones empresariales**  
🔄 **Sistema de pagos fragmentado** (múltiples modelos sin cohesión)  
🔄 **Ausencia de wallet/créditos empresariales**  

---

## 💡 **SOLUCIÓN PROPUESTA: SISTEMA INTEGRAL DE PAGOS**

### **🏗️ ARQUITECTURA RECOMENDADA**

#### **1. 💳 PAGOS DE USUARIOS → AUTONEW**

**Estrategia Multi-Método:**
```python
# Nuevo modelo para unificar todos los pagos
class TransaccionPago(models.Model):
    TIPOS_TRANSACCION = [
        ('reserva_individual', 'Reserva Individual'),
        ('suscripcion_individual', 'Suscripción Individual'), 
        ('suscripcion_empresarial', 'Suscripción Empresarial'),
        ('credito_empresarial', 'Recarga Créditos Empresa'),
    ]
    
    METODOS_PAGO = [
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('transferencia_bancaria', 'Transferencia Bancaria'),
        ('pse', 'PSE'),
        ('efectivo', 'Efectivo'),
        ('wallet_empresarial', 'Wallet Empresarial'),
    ]
    
    ESTADOS_TRANSACCION = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('reembolsado', 'Reembolsado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_transaccion = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tipo_transaccion = models.CharField(max_length=30, choices=TIPOS_TRANSACCION)
    
    # Referencias polimórficas
    usuario = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.CASCADE)
    
    # Detalles financieros
    monto_original = models.DecimalField(max_digits=12, decimal_places=2)
    monto_descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Información de pago
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO)
    estado = models.CharField(max_length=20, choices=ESTADOS_TRANSACCION, default='pendiente')
    
    # Trazabilidad
    referencia_externa = models.CharField(max_length=255, null=True, blank=True)  # ID de pasarela
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    ip_origen = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    notas_internas = models.TextField(blank=True)
```

**🔧 Métodos de Pago Recomendados:**

1. **💳 Tarjetas (Principal)**
   - Integración con **Stripe** (comisión ~3.4% + $900 COP)
   - **Wompi** (comisión ~3.49% + IVA)
   - **PayU** (comisión ~3.49% + $900 COP)

2. **🏦 Transferencias Bancarias**  
   - **PSE** (comisión ~$3.500 COP fija)
   - Transferencias directas (sin comisión para empresa)

3. **💰 Efectivo**
   - Pago contra-entrega
   - Punto de recaudo

#### **2. 💼 SISTEMA DE COMISIONES Y LIQUIDACIONES A EMPRESAS**

**Nueva Arquitectura Empresarial:**
```python
class WalletEmpresarial(models.Model):
    """Sistema de billetera/créditos para empresas"""
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE, related_name='wallet')
    saldo_disponible = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Por liquidar
    saldo_retenido = models.DecimalField(max_digits=12, decimal_places=2, default=0)   # Garantías
    
    # Configuración de pagos
    comision_autonew = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)  # %
    dias_liquidacion = models.IntegerField(default=7)  # Días para liberar fondos
    
    # Datos bancarios para liquidaciones
    banco = models.CharField(max_length=100, blank=True)
    numero_cuenta = models.CharField(max_length=50, blank=True)
    tipo_cuenta = models.CharField(max_length=20, choices=[
        ('ahorros', 'Ahorros'), 
        ('corriente', 'Corriente')
    ], blank=True)
    titular_cuenta = models.CharField(max_length=255, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

class MovimientoWallet(models.Model):
    """Registro de todos los movimientos en wallet empresarial"""
    TIPOS_MOVIMIENTO = [
        ('ingreso_reserva', 'Ingreso por Reserva'),
        ('descuento_comision', 'Descuento Comisión AUTONEW'),
        ('liquidacion', 'Liquidación Bancaria'),
        ('retencion', 'Retención Garantía'),
        ('liberacion_retencion', 'Liberación Retención'),
        ('ajuste_manual', 'Ajuste Manual'),
        ('recarga_creditos', 'Recarga de Créditos'),
    ]
    
    wallet = models.ForeignKey(WalletEmpresarial, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=30, choices=TIPOS_MOVIMIENTO)
    
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Referencias
    reserva = models.ForeignKey('Reserva', null=True, blank=True, on_delete=models.SET_NULL)
    liquidacion = models.ForeignKey('LiquidacionEmpresarial', null=True, blank=True, on_delete=models.SET_NULL)
    transaccion_pago = models.ForeignKey(TransaccionPago, null=True, blank=True, on_delete=models.SET_NULL)
    
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    procesado_por = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL)

class LiquidacionEmpresarial(models.Model):
    """Liquidaciones periódicas a empresas"""
    ESTADOS_LIQUIDACION = [
        ('generada', 'Generada'),
        ('aprobada', 'Aprobada'),
        ('procesada', 'Procesada'),
        ('completada', 'Completada'),
        ('rechazada', 'Rechazada'),
    ]
    
    id_liquidacion = models.UUIDField(primary_key=True, default=uuid.uuid4)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='liquidaciones')
    
    # Período de liquidación
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    
    # Cálculos financieros
    total_bruto = models.DecimalField(max_digits=12, decimal_places=2)  # Total servicios
    total_comision_autonew = models.DecimalField(max_digits=12, decimal_places=2)
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=12, decimal_places=2)  # A liquidar
    
    # Información de pago
    metodo_liquidacion = models.CharField(max_length=30, choices=[
        ('transferencia', 'Transferencia Bancaria'),
        ('cheque', 'Cheque'),
        ('wallet', 'Wallet Empresarial'),
    ])
    
    estado = models.CharField(max_length=20, choices=ESTADOS_LIQUIDACION, default='generada')
    referencia_bancaria = models.CharField(max_length=255, blank=True)
    
    # Metadatos
    reservas_incluidas = models.ManyToManyField('Reserva', related_name='liquidaciones')
    notas = models.TextField(blank=True)
    procesado_por = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL)
```

---

## ⚙️ **FLUJOS DE TRABAJO OPTIMIZADOS**

### **🔄 FLUJO 1: Pago de Usuario Individual**

```
1. Usuario selecciona servicios
2. Sistema calcula descuentos (si tiene plan activo)
3. Se genera TransaccionPago con monto_original y monto_final
4. Usuario elige método de pago
5. Se procesa el pago (tarjeta/PSE/efectivo)
6. Al confirmar: se crea la reserva y se notifica a la empresa
```

### **🔄 FLUJO 2: Reserva Empresarial con Wallet**

```
1. Cliente hace reserva en empresa
2. Sistema calcula precio con descuentos empresariales
3. Se descuenta del WalletEmpresarial si tiene saldo
4. Si no hay saldo: se genera cobro pendiente
5. Empresa recibe notificación de servicio a realizar
6. Al completar servicio: fondos se transfieren al wallet
```

### **🔄 FLUJO 3: Liquidación Empresarial Automática**

```
SEMANAL (cada lunes):
1. Sistema genera LiquidacionEmpresarial por período
2. Calcula: total_bruto - comision_autonew = total_neto
3. Empresa recibe notificación de liquidación generada
4. Admin revisa y aprueba liquidación
5. Se procesa transferencia bancaria
6. Se actualiza estado a 'completada'
```

---

## 🎯 **CONFIGURACIÓN DE COMISIONES RECOMENDADA**

### **💰 Estructura de Comisiones por Segmento:**

| Tipo de Empresa | Comisión AUTONEW | Tiempo Liquidación | Beneficios |
|----------------|------------------|-------------------|------------|
| **Básica** (1-10 servicios/mes) | 20% | 14 días | Wallet básico |
| **Premium** (11-50 servicios/mes) | 15% | 7 días | Wallet + reportes |
| **Corporativa** (50+ servicios/mes) | 12% | 3 días | Wallet + manager dedicado |
| **Aliado Estratégico** | 10% | 1 día | Todas las ventajas |

### **🔧 Configuración de Descuentos Inteligente:**

```python
def calcular_precio_con_descuentos(reserva):
    """
    Lógica unificada para calcular precios con todos los descuentos
    """
    precio_total = 0
    detalle_servicios = []
    
    for servicio in reserva.servicios.all():
        precio_base = servicio.precio
        descuento_aplicado = 0
        precio_final = precio_base
        
        # PRIORIDAD 1: Descuento por plan individual
        if reserva.suscripcion_utilizada and not reserva.es_reserva_empresarial:
            plan_servicio = PlanServicio.objects.filter(
                plan=reserva.suscripcion_utilizada.plan,
                servicio=servicio
            ).first()
            if plan_servicio:
                descuento_aplicado = plan_servicio.porcentaje_descuento
                precio_final = precio_base * (1 - descuento_aplicado/100)
        
        # PRIORIDAD 2: Descuento empresarial
        elif reserva.es_reserva_empresarial:
            if reserva.suscripcion_empresarial:
                # Aplicar descuentos según plan empresarial
                descuento_aplicado = reserva.suscripcion_empresarial.plan.descuento_volumen
                precio_final = precio_base * (1 - descuento_aplicado/100)
        
        precio_total += precio_final
        detalle_servicios.append({
            'servicio': servicio.nombre_servicio,
            'precio_base': precio_base,
            'descuento': descuento_aplicado,
            'precio_final': precio_final
        })
    
    return precio_total, detalle_servicios
```

---

## 📊 **BENEFICIOS DE LA IMPLEMENTACIÓN**

### **✅ Para AUTONEW:**
- **💰 Trazabilidad completa** de todos los ingresos y egresos
- **📈 Reportes financieros** automatizados y precisos  
- **🔄 Liquidaciones automáticas** que reducen trabajo manual
- **📊 Analytics** de rentabilidad por empresa y usuario
- **🛡️ Reducción de disputas** por transparencia en cálculos

### **✅ Para Usuarios:**
- **🚀 Proceso de pago simplificado** y unificado
- **💳 Múltiples opciones** de pago disponibles  
- **📱 Experiencia móvil** optimizada
- **🔒 Seguridad bancaria** de nivel empresarial
- **📊 Historial detallado** de transacciones

### **✅ Para Empresas:**
- **💼 Wallet empresarial** para gestión de flujo de caja
- **📅 Liquidaciones predecibles** y automáticas
- **📈 Reportes de rentabilidad** en tiempo real
- **🏦 Múltiples métodos** de liquidación
- **🤝 Transparencia total** en comisiones y descuentos

---

## 🚀 **PLAN DE IMPLEMENTACIÓN (4 FASES)**

### **📅 FASE 1 (Semana 1-2): Modelos Base**
1. Crear modelo `TransaccionPago` unificado
2. Implementar modelo `WalletEmpresarial`
3. Migrar datos existentes al nuevo sistema
4. Crear interfaces admin para gestión

### **📅 FASE 2 (Semana 3-4): Pagos de Usuarios**  
1. Integrar pasarelas de pago (Stripe/Wompi)
2. Crear flujo unificado de checkout
3. Implementar webhooks de confirmación
4. Testing exhaustivo de transacciones

### **📅 FASE 3 (Semana 5-6): Sistema Empresarial**
1. Implementar wallet empresarial
2. Crear sistema de liquidaciones automáticas
3. Desarrollar dashboard financiero empresarial
4. Configurar notificaciones automáticas

### **📅 FASE 4 (Semana 7-8): Optimización y Analytics**
1. Implementar reportes avanzados
2. Crear sistema de alertas financieras  
3. Optimizar rendimiento de consultas
4. Documentación y capacitación

---

## 💡 **CONSIDERACIONES TÉCNICAS IMPORTANTES**

### **🔐 Seguridad:**
- Tokenización de datos de tarjetas (PCI DSS)
- Encriptación de información bancaria
- Logs de auditoría para todas las transacciones
- Rate limiting en APIs de pago

### **⚡ Rendimiento:**
- Índices de base de datos optimizados
- Cache de cálculos de precios frecuentes
- Procesamiento asíncrono de liquidaciones
- Backup automático de datos financieros

### **🔄 Escalabilidad:**
- Arquitectura preparada para múltiples países/monedas
- Sistema de webhooks para integraciones futuras
- API REST para aplicaciones móviles
- Microservicios para módulos financieros

---

## 📞 **PRÓXIMOS PASOS RECOMENDADOS**

1. **📋 Revisar propuesta** y definir prioridades
2. **💰 Seleccionar pasarelas** de pago principales  
3. **🏗️ Comenzar implementación** por fases
4. **🧪 Ambiente de testing** con transacciones reales
5. **📱 Optimizar UX** del flujo de pagos
6. **📊 Configurar analytics** financieros desde el inicio

¿Te gustaría que profundice en algún aspecto específico de esta propuesta o que comience con la implementación de alguna de las fases?