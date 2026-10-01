# Deploy CRM pe server (VPS Ubuntu/Debian)

## 1. Pregătire server
- Un VPS cu Ubuntu 22.04/24.04 (2 GB RAM e suficient pentru echipă mică)
- (Recomandat) Un domeniu sau subdomeniu, ex: `crm.firma-ta.ro`, cu DNS spre IP-ul serverului

## 2. Copiază aplicația pe server
```bash
sudo mkdir -p /opt/crm
sudo chown $USER:$USER /opt/crm
# copiază tot conținutul proiectului (fără venv) în /opt/crm
```

## 3. Instalează dependențele
```bash
cd /opt/crm
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 4. Secretul de sesiune
Generează o valoare aleatoare și pune-o în `deploy/crm.service` la `CRM_SECRET`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 5. Serviciul systemd
```bash
sudo useradd -r -s /bin/false crm || true
sudo chown -R crm:crm /opt/crm
sudo cp deploy/crm.service /etc/systemd/system/crm.service
sudo systemctl daemon-reload
sudo systemctl enable --now crm
sudo systemctl status crm   # verifică că e "active (running)"
```
Aplicația ascultă pe `127.0.0.1:8000`.

## 6. Nginx + HTTPS (recomandat)
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```
Config nginx (`/etc/nginx/sites-available/crm`):
```nginx
server {
    listen 80;
    server_name crm.firma-ta.ro;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d crm.firma-ta.ro
```

## 7. Backup
Baza de date e un singur fișier: `/opt/crm/crm.db`. Fă backup zilnic:
```bash
# exemplu cron zilnic la 03:00
0 3 * * * cp /opt/crm/crm.db /var/backups/crm/crm-$(date +\%F).db
```

## 8. Primul login
Intră pe `https://crm.firma-ta.ro`, autentifică-te cu `admin@demo.ro / admin123`,
apoi **schimbă imediat parola** și șterge/înlocuiește datele demo.
