# 🌌 Planeta Marsiano - Biblioteca de Películas

Bienvenido a **Planeta Marsiano**: una aplicación web en **Django** para gestionar tu biblioteca personal de películas. Permite filtrar, ordenar y ver detalles de tus películas rankeadas en **Letterboxd**, enriquecidas con información de **TMDb**.

## 🎬 Funcionalidades

- Importación de películas desde CSV exportado de Letterboxd
- Enriquecimiento con TMDb: poster, sinopsis y géneros
- Listado de películas en **cards**, 3 por fila, responsive
- **Filtros**: Título, Año, Género
- **Ordenamiento**: A-Z / Z-A, Año ascendente / descendente, Mejor valoradas
- Página de detalle con toda la información de la película

## 🛠 Tecnologías

- **Python 3.11**
- **Django 3.2**
- **Bootstrap 5**
- **tmdbsimple**
- **SQLite**
- HTML / CSS / Templates Django

## 📂 Estructura del proyecto

```
planeta-marsiano/
├─ data/                                          # CSV de películas exportadas desde Letterboxd
│  └─ ratings.csv
├─ planeta-marsiano/                             # Configuración principal de Django
├─ sistema/                                      # Aplicación principal
│  ├─ templates/sistema/                         # HTML templates
│  ├─ static/                                    # CSS, JS, imágenes
│  └─ management/commands/import_watched_movies.py
└─ manage.py
```

## ⚙️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/planeta-marsiano.git
cd planeta-marsiano
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 3. Configurar tu API Key de TMDb
En `import_watched_movies.py`:
```python
tmdb.API_KEY = 'TU_API_KEY_AQUI'
```

### 4. Aplicar migraciones
```bash
python manage.py migrate
```

### 5. Importar películas desde tu CSV
```bash
python manage.py import_watched_movies
```

### 6. Ejecutar servidor local
```bash
python manage.py runserver
```

### 7. Abrir navegador
Visita: http://127.0.0.1:8000/

## 🚀 Próximas mejoras

- Autenticación de usuarios y listas personalizadas
- Guardar favoritos y valoraciones dentro de la app
- Mejor diseño y animaciones en la galería
- Búsqueda avanzada por director, actor o género

## 🔗 Referencias

- [Django Docs](https://docs.djangoproject.com/)
- [TMDb API](https://www.themoviedb.org/documentation/api)
- [Letterboxd CSV Export](https://letterboxd.com/settings/data/)

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!
