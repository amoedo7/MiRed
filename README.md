<div align="center">

# MiRed

**Un diagnóstico rápido de tu conexión y red, sin escanear dispositivos ajenos.**

[![CI](https://github.com/amoedo7/MiRed/actions/workflows/ci.yml/badge.svg)](https://github.com/amoedo7/MiRed/actions/workflows/ci.yml)

`Android / Termux` · `Windows` · `macOS` · `Linux` · `Python 3` · `JSON` · `HTML local`
</div>

---

## Qué mide

MiRed genera un reporte portable con:

- IP local;
- gateway por defecto;
- servidores DNS detectados;
- resolución DNS;
- conexión TCP de salida;
- acceso HTTPS;
- latencias observadas;
- IP pública opcional;
- un score simple de salud.

No hace descubrimiento de vecinos, no escanea puertos de la LAN y no intenta acceder a otros equipos.

## Ejecutar

```bash
python mired.py
```

En Termux:

```bash
pkg install python
python mired.py
```

Agregar IP pública:

```bash
python mired.py --online
```

Guardar JSON:

```bash
python mired.py --output red.json
```

Modo sin pruebas externas, útil para CI o inventario local:

```bash
python mired.py --no-probe
```

## Dashboard local

[`viewer.html`](viewer.html) abre el JSON en un panel visual con el estilo de DesarrollAMO. El archivo se procesa localmente en el navegador.

1. generá `red.json`;
2. abrí `viewer.html`;
3. elegí el reporte;
4. revisá score, DNS, TCP, HTTPS, gateway e IPs.

## Contrato

```json
{
  "schema": "desarrollamo.mired.v1",
  "network": {
    "local_ip": "192.168.1.20",
    "default_gateway": "192.168.1.1",
    "dns_servers": ["1.1.1.1"]
  },
  "checks": {
    "dns": {"ok": true},
    "tcp": {"ok": true},
    "https": {"ok": true}
  },
  "summary": {"score": 100}
}
```

## Privacidad

El reporte no incluye MAC, SSID, contraseñas Wi-Fi ni credenciales. La IP pública sólo se consulta con `--online`.

---

**DesarrollAMO** · diagnóstico multiplataforma · [`MiDispositivo`](https://github.com/amoedo7/MiDispositivo) · [`MiSistema`](https://github.com/amoedo7/MiSistema)
