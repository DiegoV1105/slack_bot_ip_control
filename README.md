# Bot de Slack para Actualizar IP en DigitalOcean

Este es un bot de Slack que permite actualizar la IP de acceso a una base de datos PostgreSQL alojada en DigitalOcean. El bot escucha comandos en un canal de Slack y actualiza las reglas de firewall en DigitalOcean automáticamente.

---

## Funcionalidades

1. **Actualizar IP en DigitalOcean**:
   - El bot recibe un comando con una IP y actualiza las reglas de firewall en DigitalOcean para permitir el acceso desde esa IP.

2. **Obtener la IP pública actual**:
   - El bot puede responder con la IP pública actual del usuario que ejecuta el comando.

---

## Comandos Disponibles

### Actualizar IP
Actualiza la IP en las reglas de firewall de DigitalOcean.

- **Formato**: ```!actualizar_ip <IP>```
- **Ejemplo**: ```!actualizar_ip 192.168.1.100```

**Respuesta**:

Si la actualización es exitosa:
  ```
  IP actualizada correctamente a: 192.168.1.100
  ```
Si hay un error:
  ```
  Error al actualizar la IP: 192.168.1.100
  ```

---

## Requisitos

1. **Python 3.8 o superior**.
2. **Cuenta en DigitalOcean** con un firewall configurado.
3. **Espacio de trabajo en Slack** con permisos para crear aplicaciones y bots.
---



## Configurar el Proyecto

1. **Clonar el repositorio**:
 ```bash
     git clone https://github.com/tuusuario/bot-slack-digitalocean.git
     cd bot-slack-digitalocean
```
2. **Instalar dependencias**:
 ```bash
    pip install -r requirements.txt
```
3. **Crear el archivo .env**:
Crea un archivo .env en la raíz del proyecto con el siguiente contenido:
 ```
    SLACK_TOKEN=xoxb-tu-token-de-slack
    SLACK_CHANNEL=nombre-del-canal
    DIGITALOCEAN_TOKEN=tu-token-de-digitalocean
    FIREWALL_ID=id-de-tu-firewall
    DATABASE_ID=id-de-la-bd
```