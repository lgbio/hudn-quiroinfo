---
inclusion: always
---

# Reglas de Código — Quiroinfo

## Alcance de las reglas de nomenclatura

Estas reglas aplican **únicamente al código de dominio** de la aplicación.
NO modificar ni traducir nombres estándar de Django, Python ni librerías externas.
Los nombres del framework (Django, Python, librerías) deben permanecer en inglés.

## Nomenclatura (código de dominio)

- Todos los identificadores de dominio deben estar en **español**.
- Esto incluye: modelos, variables, funciones, clases, URLs personalizadas y lógica de negocio.
- NO usar inglés para conceptos de dominio.

## Estilo de nomenclatura

- Clases y otros tipos: **PascalCase** con inicial mayúscula (ej. `SesionActiva`, `EstadoQuirurgico`).
- Funciones y variables: **camelCase** con inicial minúscula (ej. `siguienteEstado`, `codigoPaciente`).
- Este estilo sigue la convención Java: uppercase para tipos, lowercase para instancias y funciones.

## Apps Django

- Las apps Django deben comenzar con el prefijo `app_`.

## URLs y rutas

- Las rutas personalizadas de la aplicación deben estar en español.
- Las rutas estándar de Django pueden permanecer en inglés:
  - `/login/`
  - `/logout/`
  - `/admin/`

## Constantes y enumeraciones

- Los enums y constantes de dominio deben estar en español.
- Ejemplo:
  - `EN_PREPARACION`
  - `EN_CIRUGIA`
  - `EN_RECUPERACION`

## Estilo de sintaxis

- Dejar un espacio entre el nombre de función o variable y los paréntesis/corchetes.
  - Ejemplo: `FuncionEjemplo ()`, `variableEjemplo []`

## Diseño de funciones

- Funciones cortas: máximo ~30 líneas.
- Una sola responsabilidad por función.

## Vistas

- Usar Class-Based Views (CBV) cuando aplique.
- Usar `LoginRequiredMixin` para proteger vistas privadas.

## Frontend

- Evitar JavaScript personalizado; preferir HTMX para interacciones dinámicas.
- Alpine.js solo para comportamientos ligeros de UI (modales, dropdowns).
- Templates simples y reutilizables; evitar lógica compleja en templates.
- Tailwind CSS por CDN en el MVP.
