# 🤖 Multi-Agent AI Framework (LangGraph & Python)

Un sistema arquitectónico multi-agente robusto, resiliente y altamente optimizado construido con **LangGraph** y **Python**. El sistema está diseñado para coordinar agentes especialistas (gestión de archivos, extracción de bases de datos y generación de reportes) bajo la supervisión de un nodo central, garantizando la eficiencia de tokens, la prevención de bucles infinitos y la consistencia de estado atómico.

---

## 🏗️ Arquitectura y Características Principales

### 1. Gestión de Estado y Progreso Atómico (`AgentState`)
* **Diccionario de Control (`progress`):** Incorpora una estructura dentro del estado global para llevar métricas exactas del avance del pipeline (`path_created`, `data_extracted`, `report_generated`, etc.).
* **Reducer de Fusión (`merge_progress`):** Utiliza una función reductora limpia basada en expansión de diccionarios (`{**current, **new_data}`) para evitar condiciones de carrera, sobrescrituras destructivas y asegurar actualizaciones atómicas (marcas `SUCCESS` / `ERROR`).

### 2. Estandarización con `Command` e Inyección Limpia
* **Retorno Unificado:** Todos los agentes especialistas devuelven sus resultados de manera unificada mediante `Command(update=...)`.
* **Desacoplamiento de Esquemas:** Las herramientas emplean `Annotated[..., InjectedState]` e `Annotated[..., InjectedToolCallId]` internamente. Los esquemas Pydantic (`args_schema`) se mantienen limpios, exponiendo al LLM únicamente los parámetros de negocio necesarios.

### 3. Optimización y Aislamiento del Supervisor
* **Aislamiento de Contexto:** Se eliminó la lectura de historiales de chat pesados en el nodo supervisor para prevenir amnesia o saturación por desbordamiento de contexto.
* **Entrada Minimalista:** El supervisor procesa exclusivamente dos entradas clave: el objetivo original del usuario (**User Goal**) y el panel métrico actual (**Current Workflow Progress**).
* **Bloqueo Cognitivo:** Un *System Prompt* reforzado prohíbe explícitamente reintentar pasos que ya posean el estatus `SUCCESS`, respetando dependencias condicionales.

### 4. Capas del Flujo de Ejecución (`Graph -> Wrappers -> Agents -> Tools`)
1. **Nodo del Grafo Principal:** Invoca al wrapper del especialista, calcula los mensajes nuevos evitando duplicados y empaqueta las actualizaciones.
2. **Capa Wrapper:** Recibe el estado, ejecuta al sub-agente vía `ainvoke(state)` y encapsula la respuesta en un objeto propio (`AgentResponse`).
3. **Agentes y Herramientas Especialistas:** Ejecutan la lógica de negocio aislada y emiten su `Command(update=...)`.

### 5. Resiliencia e Idempotencia
* **Idempotencia Técnica:** Las herramientas críticas (como la creación de directorios con `exist_ok=True`) soportan ejecuciones repetidas de forma segura.
* **Autocorrección:** Capacidad nativa para adaptarse a imprevistos en tiempo de ejecución (ej. nombres dinámicos de archivos con marcas de tiempo) y completar flujos de punta a punta.

---

## 👥 Especialistas del Sistema

* **`files_manager_agent`:** Administra directorios en el sandbox y manipulación de archivos.
* **`data_extractor_agent`:** Ejecuta consultas seguras sobre bases de datos relacionales para la extracción de información estructurada.
* **`reports_manager_agent`:** Genera reportes automatizados en formatos tabulares (ej. Excel) a partir de los datos extraídos.

---

## 📊 Ejemplo de Ejecución Exitosa (Log)

```text
agent: files_manager_agent
instruction: Crea el path orders/shippeds
Agente files manager: SUCCESS: Path created successfully.

agent: data_extractor_agent
instruction: Extrae información de clientes con estatus 'Shipped' y total >= 100000...
SUCCESS: 81 rows were extracted from the database.

agent: reports_manager_agent
instruction: Genera un excel en la ruta 'orders/shippeds'...
SUCCESS: report successfully generated: orders/shippeds/20261026_ordenes_entregadas.xlsx

agent: files_manager_agent
instruction: open orders/shippeds/20261026_ordenes_entregadas.xlsx
Agente files manager: SUCCESS: file opened successfully.

agent: END
instruction: El path ha sido creado, los datos extraídos, el reporte generado y abierto exitosamente.