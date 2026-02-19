# 📦 Sistema de Gestión de Inventario y Pedidos

Sistema completo orientado a **producción**, diseñado como proyecto de **portafolio profesional**, **freelancing** y **empleo formal**.

El proyecto implementa un **backend en Python** con arquitectura REST, una **aplicación móvil en Flutter** y un **frontend web**, simulando un entorno real de negocio para la gestión de inventario, pedidos, deudores y pagos.

---

## 🎯 Objetivo del Proyecto

Construir un sistema realista que demuestre habilidades en:

- Desarrollo backend profesional
- Diseño de APIs REST
- Manejo de bases de datos relacionales
- Autenticación y autorización por roles
- Consumo de APIs desde aplicaciones móviles y web
- Buenas prácticas de arquitectura, seguridad y escalabilidad

Este proyecto **no es un tutorial** ni un ejercicio académico: está pensado para representar un sistema que podría usarse en un negocio real.

---

## 🧠 Arquitectura General

El sistema está compuesto por:

- **Backend**: API REST central
- **Base de datos**: Relacional
- **Aplicación móvil**: Flutter
- **Frontend web**: Panel administrativo

Todos los clientes consumen la misma API, manteniendo una arquitectura desacoplada y escalable.

---

## 🛠️ Tecnologías Utilizadas

### Backend

- **Python**
- **FastAPI**
- **SQLModel** (ORM basado en SQLAlchemy + Pydantic)
- **JWT** para autenticación

### Base de Datos

- **SQLite** (desarrollo)
- Diseño preparado para **PostgreSQL** (producción)

### Mobile App

- **Flutter**
- Consumo de API REST

### Web Frontend

- HTML, CSS, JavaScript
- Comunicación con API REST

---

## 👥 Roles del Sistema

### Usuario

- Registro e inicio de sesión
- Visualización de productos
- Creación de pedidos
- Consulta del estado de pedidos

### Administrador

- Gestión de productos y categorías
- Control de inventario
- Gestión de pedidos
- Registro y seguimiento de deudas
- Registro de pagos
- Visualización de reportes

---

## 📦 Funcionalidades Principales

- Autenticación segura con JWT
- Sistema de roles y permisos
- CRUD de productos y categorías
- Control de stock en tiempo real
- Flujo completo de pedidos
- Manejo de deudores y pagos
- Reportes básicos de negocio

---

## 🔁 Flujos de Uso

- Un usuario crea un pedido desde la app Flutter o la web
- El backend valida el stock y registra el pedido
- El administrador gestiona el pedido y el inventario
- En caso de deuda, se registra y se da seguimiento
- Los pagos se registran y actualizan el estado financiero

---

## 🔐 Seguridad y Buenas Prácticas

- Validación de datos en todos los endpoints
- Protección de rutas según rol
- Uso de variables de entorno
- Manejo centralizado de errores
- Separación clara de capas (API, lógica, datos)

---

## 🚀 Despliegue

El sistema está diseñado para un despliegue económico y escalable:

- Backend desplegable en servicios cloud
- Base de datos migrable a PostgreSQL
- Configuración por variables de entorno

---

## 📄 Documentación

La API está documentada automáticamente mediante **Swagger / OpenAPI**, accesible desde el backend.

Además, el repositorio incluye:

- Diagramas conceptuales
- Explicación de la arquitectura
- Descripción de entidades y relaciones

---

## 💼 Enfoque Profesional

Este proyecto puede utilizarse para:

- Portafolio profesional
- Presentación a clientes freelancer
- Demostración técnica en entrevistas
- Base para sistemas reales de negocio

Demuestra conocimientos en backend, frontend, móvil, bases de datos y arquitectura de software.

---

## 📌 Nota

El proyecto se desarrolla inicialmente con **SQLite** por simplicidad, pero toda la arquitectura está pensada para migrar a **PostgreSQL** sin cambios estructurales.

---

⭐ Si este proyecto te resulta interesante o útil, no dudes en explorarlo y revisarlo.
