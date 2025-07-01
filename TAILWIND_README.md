# Guía de Tailwind CSS para Autonew

## ✅ Instalación Completada

Tu proyecto Django ya tiene Tailwind CSS correctamente instalado y configurado.

## 🚀 Cómo usar

### Para Desarrollo:
1. **Iniciar el modo watch de Tailwind** (ejecutar en una terminal):
   ```powershell
   cd theme
   npm run build-dev
   ```
   Esto mantendrá Tailwind observando cambios y reconstruyendo automáticamente.

2. **Iniciar el servidor Django** (ejecutar en otra terminal):
   ```powershell
   python manage.py runserver
   ```

### Para Producción:
```powershell
cd theme
npm run build
```

## 📁 Estructura de Archivos

```
theme/
├── package.json              # Dependencias de Node.js
├── tailwind.config.js        # Configuración de Tailwind
├── static_src/
│   └── src/
│       └── input.css         # Archivo fuente de Tailwind
└── static/
    └── css/
        └── dist/
            └── styles.css    # Archivo CSS compilado
```

## 🎨 Cómo agregar Tailwind a tus templates

En tu `base.html` ya está incluido:
```html
<!-- Tailwind CSS -->
<link rel="stylesheet" href="{% static 'css/dist/styles.css' %}">
```

## 📝 Ejemplo de uso en templates

```html
<!-- Contenedor con padding y máximo ancho -->
<div class="container mx-auto px-4 py-8">
    
    <!-- Título con gradiente -->
    <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
        Mi Título
    </h1>
    
    <!-- Tarjeta con sombra -->
    <div class="bg-white p-6 rounded-lg shadow-lg">
        <p class="text-gray-600">Contenido de la tarjeta</p>
    </div>
    
    <!-- Botón con hover -->
    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-300">
        Mi Botón
    </button>
    
    <!-- Grid responsivo -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="bg-gray-100 p-4 rounded">Columna 1</div>
        <div class="bg-gray-100 p-4 rounded">Columna 2</div>
        <div class="bg-gray-100 p-4 rounded">Columna 3</div>
    </div>
</div>
```

## 🔧 Configuración

### tailwind.config.js
- Configurado para buscar clases en tus templates HTML
- Incluye plugins para formularios y tipografía

### Settings.py
- `STATICFILES_DIRS` configurado para servir archivos de Tailwind
- Apps `tailwind` y `theme` agregadas a `INSTALLED_APPS`

## 📚 Recursos Útiles

- [Documentación oficial de Tailwind CSS](https://tailwindcss.com/docs)
- [Tailwind CSS Cheat Sheet](https://tailwindcomponents.com/cheatsheet/)
- [Tailwind Play (Playground online)](https://play.tailwindcss.com/)

## 🔄 Flujo de Trabajo Recomendado

1. Mantén `npm run build-dev` ejecutándose mientras desarrollas
2. Agrega clases de Tailwind a tus templates
3. Los cambios se reflejarán automáticamente
4. Para producción, ejecuta `npm run build` para optimizar el CSS

## ⚠️ Notas Importantes

- Los estilos se compilan desde `theme/static_src/src/input.css`
- El archivo final se genera en `theme/static/css/dist/styles.css`
- Tailwind solo incluye las clases que realmente uses (purge CSS)
- Puedes usar Tailwind junto con Bootstrap (ya incluido en tu proyecto)
