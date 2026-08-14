# Patrón de Store

## Propósito y alcance

Este documento registra el patrón observado de adapters de store LocalFS y
MongoDB en `aspynotifications` al 2026-08-14. Cubre los diez adapters concretos
indicados a continuación, con énfasis especial en el manejo de excepciones y
los logs estructurados.

Es un registro de patrón basado en evidencia: el comportamiento común se
identifica como tal y las diferencias entre implementaciones se conservan de
forma explícita. Un comportamiento marcado como diferencia no es un estándar
global del proyecto hasta que se adopte deliberadamente.

## Inventario y autoría Git

| Entidad | Adapter LocalFS | Adapter MongoDB | Autoría Git de las líneas actuales |
| --- | --- | --- | --- |
| CloudEvent | `cloud_event/cloud_event_file_adapter.py` | `cloud_event/cloud_event_mongo_adapter.py` | Jose Navarro: ambos archivos |
| Template | `template/template_file_adapter.py` | `template/template_mongo_adapter.py` | Jose Navarro: ambos archivos |
| Destination | `destinations_file_adapter.py` | `destinations_mongo_adapter.py` | LocalFS: Afranio Solano, excepto 4 líneas posteriores de Abidis Solano; MongoDB: Afranio Solano |
| NotificationPolicy | `policy_file_store.py` | `policy_mongo_store.py` | Abidis Solano: ambos archivos |
| NotificationProvider | `provider_file_store.py` | `provider_mongo_store.py` | Abidis Solano: ambos archivos |

La atribución de las líneas actuales es: Abidis Solano 696 líneas, Afranio
Solano 227 líneas y Jose Navarro 295 líneas en este conjunto de adapters.

## Patrón estructural compartido

Todos los adapters siguen estas reglas estructurales comunes:

1. Heredan el puerto de store específico de su entidad y exactamente un adapter
   genérico de almacenamiento: `GenericLocalFSAdapter` o
   `GenericMongoAdapter`.
2. Se registran en el grupo de plugins específico de la entidad con `LOCALFS`
   o `MONGODB` mediante `@register_plugin`.
3. `get_model_class()` retorna el modelo Pydantic de la entidad.
4. Los stores LocalFS persisten `<entity-id>.json` cuando la entidad tiene
   `id`; Templates usa `name` como clave de persistencia.
5. Los stores MongoDB definen `get_collection_name()` y pasan la clave canónica
   a las operaciones genéricas `save`, `load` y `delete`.
6. Los stores contienen únicamente traducción de persistencia. No implementan
   reglas de dominio, coordinan otras entidades ni llaman servicios.
7. `ping()` delega en `ping_resource()` en todos los adapters, aunque el
   comportamiento cuando esa operación lanza una excepción aún no es uniforme.

## Patrón de manejo de excepciones

### Significado de ausencia

La ausencia se trata como resultado normal de consulta, no como error
operacional:

| Backend | Excepción al leer por ID | Valor retornado |
| --- | --- | --- |
| LocalFS | `FileNotFoundError` | `None` |
| MongoDB | `NotFoundError` | `None` |

La misma idea se usa en los adapters MongoDB de policy y provider al consultar
por nombre. Los adapters LocalFS de policy y provider obtienen el índice de
nombre y retornan `None` cuando la lista de resultados está vacía.

### Datos persistidos corruptos

El comportamiento repetido más sólido, usado por los adapters de Destination,
NotificationPolicy y NotificationProvider, es:

1. Capturar `pydantic.ValidationError` de `load`, `find` o `find_one`.
2. Emitir un log estructurado que identifique corrupción e incluya la clave de
   consulta cuando exista.
3. Lanzar `ValueError` encadenado a la falla de validación.

Esto diferencia datos persistidos inválidos de un backend de almacenamiento no
disponible. Los adapters CloudEvent y Template, en cambio, registran la falla
de validación y usan un `raise` sin argumentos, por lo que el llamador recibe
`ValidationError`. Es una diferencia documentada, no el patrón repetido de
traducción.

### Fallas inesperadas de persistencia

Cuando un adapter captura un `Exception` inesperado, registra la operación, la
identidad de la entidad cuando está disponible y `error=str(error)`. La
cobertura de `catch-all` no es uniforme: CloudEvent y Template no agregan una
rama de error inesperado alrededor de la lectura por ID, por lo que esas fallas
se propagan sin un log local.

Los adapters Destination, NotificationPolicy y NotificationProvider traducen
la falla a un `Exception` contextual nuevo mediante `raise ... from error`.
Esto conserva la excepción original como causa y agrega la operación fallida y
la clave de la entidad. Los adapters CloudEvent y Template relanzan el error
original al guardar y eliminar, pero envuelven las fallas de listado con un
`Exception` contextual genérico.

### Delete y ping aún no son uniformes

Las implementaciones actuales difieren en dos contratos importantes:

| Operación | Comportamiento observado |
| --- | --- |
| Eliminar un registro LocalFS inexistente | Destination retorna exitosamente; NotificationPolicy y NotificationProvider registran y lanzan porque no capturan `FileNotFoundError`; CloudEvent y Template lo relanzan. |
| Eliminar un registro MongoDB inexistente | NotificationPolicy y NotificationProvider retornan exitosamente después de `NotFoundError`; Destination, CloudEvent y Template no lo manejan explícitamente. |
| `ping_resource()` lanza una excepción | CloudEvent y Template registran `PING error` y retornan `False`; Destination, NotificationPolicy y NotificationProvider propagan la excepción. |

El código actual no establece una sola política de idempotencia de delete ni de
falla de ping. Un estándar futuro debe elegir un comportamiento y aplicarlo a
los diez adapters antes de considerarlo uniforme.

## Patrón de logs estructurados

Todos los stores usan `structlog`, pero el nivel y el payload de traceback
difieren por familia de autor.

| Familia | Nivel para fallas de persistencia | Contexto | Payload de traceback |
| --- | --- | --- | --- |
| Jose Navarro: CloudEvent y Template | `logger.error` | Operación, clave o nombre de entidad, `error=str(e)` | `exc_info=e` |
| Afranio Solano: Destination | `logger.error` | Operación, `destination_id` o `destination_name`, `error=str(error)` | No se suministra |
| Abidis Solano: LocalFS de NotificationPolicy y NotificationProvider | `logger.debug` | Operación, `policy_id`/`provider_id` o nombre, `error=str(e)` | `exc_info=e` |
| Abidis Solano: MongoDB de NotificationPolicy y NotificationProvider | `logger.error` | Operación, identificador o nombre, `error=str(e)` | No se suministra |

El mínimo común observable es, por lo tanto: un mensaje estable de operación,
`error=str(exception)` y la clave de entidad o nombre de consulta siempre que
esté disponible. El nivel de log y el uso de `exc_info` aún no son uniformes.

## Diferencias de implementación por autor

### Jose Navarro — CloudEvent y Template

- Usa adapters concisos sin docstrings de clase o método.
- Usa `logger.error(..., exc_info=e)` para cada falla capturada.
- Trata `FileNotFoundError` y `NotFoundError` al leer como `None`.
- Relanza los errores originales al guardar, validar y eliminar.
- Envuelve únicamente las fallas de listado con un `Exception` contextual
  genérico.
- Convierte una falla de `ping_resource()` en `False` después de registrarla.

### Afranio Solano — Destination

- Usa firmas tipadas de colecciones y docstrings concisos de clase.
- Usa `logger.error` con un identificador/nombre específico de destination y
  sin `exc_info`.
- Traduce `ValidationError` a `ValueError` y errores inesperados a un
  `Exception` contextual encadenado.
- Maneja un registro LocalFS inexistente en delete como no-op exitoso.
- Delega `ping_resource()` sin manejador local de excepciones.

### Abidis Solano — NotificationPolicy y NotificationProvider

- Usa docstrings extensos de clase y método, y nombres de operación
  específicos de entidad.
- Los adapters LocalFS usan `logger.debug(..., exc_info=e)` para fallas de
  persistencia; los adapters MongoDB usan `logger.error` sin `exc_info`.
- Traduce `ValidationError` a `ValueError` y las demás fallas a `Exception`
  contextuales encadenados.
- Los adapters MongoDB tratan `NotFoundError` como `None` al leer y como no-op
  al eliminar.
- Los delete LocalFS no capturan `FileNotFoundError`.
- Delega `ping_resource()` y propaga cualquier falla.

## Lista de revisión para un store nuevo

Usa esta lista para comparar un adapter nuevo con el patrón observado y hacer
visible cualquier decisión deliberada de contrato:

- [ ] El adapter implementa únicamente el puerto específico de su entidad y un
  adapter genérico de backend.
- [ ] El grupo de plugins y la etiqueta `LOCALFS`/`MONGODB` coinciden con la
  factory correspondiente.
- [ ] `get_model_class()` y, para MongoDB, `get_collection_name()` identifican
  la entidad y colección correctas.
- [ ] Un registro inexistente tiene una política explícita de resultado normal
  tanto para lectura como para delete.
- [ ] `ValidationError` tiene una política explícita de corrupción y no se
  vuelve indistinguible de una falla de infraestructura.
- [ ] Toda falla inesperada de persistencia registra la operación, la clave de
  entidad o consulta y `error=str(error)` antes de propagarse o traducirse.
- [ ] El nivel de log y el comportamiento de `exc_info` escogidos son
  consistentes con el contrato de store adoptado.
- [ ] La excepción original permanece disponible mediante encadenamiento si se
  lanza una nueva excepción contextual.
- [ ] `ping()` tiene un contrato explícito: propagar la falla de almacenamiento
  o retornar `False`; no dejarlo accidental.
