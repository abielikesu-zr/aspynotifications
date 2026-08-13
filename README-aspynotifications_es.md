# aspynotifications

Versión oficial en inglés: [README-aspynotifications.md](README-aspynotifications.md)

`aspynotifications` es el paquete de dominio del Notification Service.
Actualmente implementa la persistencia de destinations y su servicio CRUD.

## Información del paquete

| Propiedad | Valor |
| --- | --- |
| Paquete | `aspynotifications` |
| Versión | `0.1.0` |
| Python | `>=3.12,<3.13` |
| Código fuente | `packages/aspynotifications/src/aspynotifications` |

Los metadatos y dependencias del paquete se gestionan con `aspymgr`. Los
archivos generados `pyproject.toml` y de requirements no deben editarse
manualmente.

## Arquitectura

El flujo actual de destinations sigue la separación HexaAs de servicio,
puerto, factory y adapter:

```text
DestinationsService
        |
        v
IDestinationStorePort
        |
        v
DestinationStoreFactory
        |
        v
Adapter LOCALFS | MONGODB
```

| Capa | Ubicación | Responsabilidad |
| --- | --- | --- |
| Entidad | `entities/destination.py` | Define la destination persistida. |
| Configuración tipada del endpoint | `config/destination_config.py` | Define la configuración específica de cada endpoint. |
| Servicio | `services/destinations_service.py` | Crea, consulta, lista, actualiza y elimina destinations. |
| Puerto | `ports/destinations_store_port.py` | Define el contrato de persistencia. |
| Adapters | `adapters/` | Persisten destinations en archivos locales o MongoDB. |
| Factory | `factories/destinations_store_factory.py` | Selecciona el adapter de almacenamiento configurado. |

## Modelo Destination

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | `str` | UUID generado por `DestinationsService` durante la creación. |
| `name` | `str` | Nombre único y legible de la destination. |
| `provider` | `str` | Nombre del proveedor de entrega configurado. |
| `type` | `email`, `slack_channel` o `teams_conversation` | Tipo de endpoint. |
| `template` | `str` | Nombre lógico del template. |
| `routable` | `bool` | Indica si la destination acepta receptores proporcionados por el evento. |
| `config` | modelo tipado | Configuración específica del endpoint. |

`Destination` rechaza campos adicionales mediante `ConfigDict(extra="forbid")`.

Los modelos de configuración de endpoint son:

| Tipo | Modelo de configuración | Campos |
| --- | --- | --- |
| `email` | `EmailDestinationConfig` | `type`, `to`, `cc`, `bcc` |
| `slack_channel` | `SlackChannelDestinationConfig` | `type`, `channel_id` |
| `teams_conversation` | `TeamsConversationDestinationConfig` | `type`, `service_url`, `conversation_id` |

## Operaciones de aplicación

`DestinationsService` expone estas operaciones asíncronas:

| Operación | Descripción |
| --- | --- |
| `create_destination` | Genera el UUID, verifica que el ID y el nombre sean únicos y persiste la destination. |
| `get_destination_by_id` | Obtiene una destination por ID. |
| `get_destination_by_name` | Obtiene una destination por nombre. |
| `list_destinations` | Lista todas las destinations. |
| `update_destination` | Persiste los cambios de una destination existente. |
| `delete_destination` | Elimina una destination por ID. |
| `ping` | Verifica el store configurado. |

## Configuración

La configuración se carga con `aspyconfig` desde estos directorios:

```text
monoconfig/default/aspynotifications/
monoconfig/<os-user>/aspynotifications/
```

El directorio específico del usuario tiene mayor precedencia. La clave raíz de
configuración es `aspynotifications`.

Ejemplo de configuración para archivos locales:

```yaml
aspynotifications:
  destinations_store:
    adapter:
      type: LOCALFS
      config:
        data_dir: ./var/aspynotifications/destinations_store
  destinations_service: {}
```

### Adapters de almacenamiento

El adapter activo se selecciona mediante
`aspynotifications.destinations_store.adapter.type`:

| Tipo | Implementación | Configuración principal |
| --- | --- | --- |
| `LOCALFS` | `DestinationsStoreAdapter` | `data_dir` |
| `MONGODB` | `DestinationsMongoStoreAdapter` | Configuración del adapter de MongoDB |

Los adapters se registran de forma perezosa en
`resources/config/aspynotifications_plugins.yaml`, dentro del grupo de plugins
`destinations_store`.

## Prueba temporal de destination

Hasta que exista un adapter oficial de entrada, usa el runner temporal de prueba:

```bash
python tests/create_destination.py \
  --name email-alerts \
  --provider email \
  --type email \
  --template incident-template \
  --destination-config '{"type":"email","to":["alerts@example.com"],"cc":[],"bcc":[]}'
```

El comando imprime la `Destination` persistida como JSON, incluido el UUID
generado por el servicio.

## Cobertura con Pytest

Las suites usan `pytest` con `@pytest.mark.asyncio` y esperan directamente las
operaciones de servicio. Esto sigue el patrón de pruebas del workspace.

### Pruebas unitarias de `DestinationsService`

La suite del servicio usa un mock de `IDestinationStorePort`; de esta forma
prueba el comportamiento de negocio de forma independiente del almacenamiento.

| Escenario | Verificación esperada |
| --- | --- |
| Crear una destination de email | Se genera un UUID y se invoca `save_destination`. |
| Crear una destination de Slack | `config.type: slack_channel` se resuelve como `SlackChannelDestinationConfig`. |
| Crear una destination de Teams | `config.type: teams_conversation` se resuelve como `TeamsConversationDestinationConfig`. |
| Discriminador de configuración desconocido | Pydantic rechaza un `config.type` no declarado. |
| Configuración de endpoint inválida | Pydantic rechaza la configuración sin campos requeridos, por ejemplo Slack sin `channel_id`. |
| ID duplicado | Se rechaza la creación. |
| Nombre duplicado | Se rechaza la creación. |
| Consultar por ID y nombre | El servicio retorna el resultado del store. |
| Listar destinations | El servicio retorna la lista del store. |
| Actualizar una destination existente | La destination actualizada se persiste. |
| Actualizar una destination inexistente | El servicio lanza `ValueError`. |
| Actualizar con un nombre ocupado | El servicio lanza `ValueError`. |
| Eliminar una destination existente | El servicio invoca `delete_destination`. |
| Eliminar una destination inexistente | El servicio lanza `ValueError`. |
| Ping | El servicio retorna el estado de salud del store. |

### Pruebas de integración LOCALFS

La suite de integración instancia `DestinationsStoreAdapter` con `tmp_path` de
pytest. Cada prueba usa un directorio aislado y no escribe en el directorio
configurado `var/` ni en datos del desarrollador.

| Secuencia | Verificación esperada |
| --- | --- |
| Crear → consultar por ID | La destination se persiste y se reconstruye. |
| Crear → consultar por nombre | El índice `by_name` resuelve la destination. |
| Crear dos → listar | Se retornan ambas destinations persistidas. |
| Crear → actualizar → consultar | El ID se conserva y la actualización se almacena. |
| Crear → eliminar → consultar | La destination deja de encontrarse. |
| Persistir cada variante de configuración de endpoint | Email, Slack y Teams conservan su `config.type` discriminado después de leer. |
| Ping a almacenamiento local | El directorio temporal de almacenamiento se reporta saludable. |

Las pruebas de integración con MongoDB quedan aplazadas hasta que exista un
entorno de pruebas MongoDB definido en el workspace. Repetirán los mismos
escenarios de persistencia cuando exista ese entorno.

Desde la raíz del repositorio, activa el entorno virtual:

```bash
source .venv/bin/activate
```

Ejecuta todas las suites disponibles:

```bash
python -m pytest packages/aspynotifications/tests -q
```

Ejecuta solo las pruebas unitarias del servicio:

```bash
python -m pytest packages/aspynotifications/tests/aspynotifications/services -q
```

Ejecuta solo las pruebas de integración LOCALFS:

```bash
python -m pytest packages/aspynotifications/tests/aspynotifications/adapters -q
```

Usa `-v` en lugar de `-q` para ver el nombre y el resultado de cada prueba.

## Estructura del paquete

```text
packages/aspynotifications/src/aspynotifications/
├── adapters/
├── config/
├── containers/
├── entities/
├── factories/
├── ports/
├── resources/
└── services/
```
