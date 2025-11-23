# Self-Hosting Thesidia Guide

**Domain**: thesidia.com (Namecheap)  
**Purpose**: Complete guide for self-hosting vs cloud platforms

---

## Quick Answer

**Self-hosting is BETTER if**:
- ✅ You want full control
- ✅ You have technical skills (or time to learn)
- ✅ You want to use your domain (thesidia.com)
- ✅ You want to avoid monthly fees (after initial setup)
- ✅ You want to customize everything

**Cloud platforms are BETTER if**:
- ✅ You want zero maintenance
- ✅ You want automatic updates/backups
- ✅ You want to deploy in 10 minutes
- ✅ You don't want to manage servers
- ✅ You want to test first (free tiers)

---

## Self-Hosting vs Cloud Platforms

### Self-Hosting (VPS)

**Pros**:
- ✅ **Full Control**: Complete server access
- ✅ **Custom Domain**: Use thesidia.com directly
- ✅ **No Monthly Fees**: Pay once for VPS (or low monthly)
- ✅ **Privacy**: Your data stays on your server
- ✅ **Customization**: Install anything you want
- ✅ **Learning**: Great for understanding deployment

**Cons**:
- ⚠️ **Setup Time**: 2-4 hours initial setup
- ⚠️ **Maintenance**: You manage updates, security, backups
- ⚠️ **Technical Skills**: Need Linux/server knowledge
- ⚠️ **Security**: You're responsible for securing it
- ⚠️ **Uptime**: You handle server issues
- ⚠️ **Scaling**: Manual scaling if traffic grows

### Cloud Platforms (Railway/Render/Fly.io)

**Pros**:
- ✅ **Zero Maintenance**: Platform handles everything
- ✅ **Fast Deployment**: 10 minutes to deploy
- ✅ **Automatic Updates**: Platform manages infrastructure
- ✅ **Easy Scaling**: Click to scale up/down
- ✅ **Built-in Security**: Platform handles security
- ✅ **Free Tiers**: Test for free

**Cons**:
- ⚠️ **Monthly Fees**: $5-20/month (after free tier)
- ⚠️ **Less Control**: Limited customization
- ⚠️ **Domain Setup**: Need to point domain to platform
- ⚠️ **Vendor Lock-in**: Tied to platform

---

## Self-Hosting Setup Guide

### Step 1: Choose VPS Provider

**Recommended VPS Providers**:

1. **DigitalOcean** (Recommended)
   - $6/month (1GB RAM, 1 vCPU)
   - $12/month (2GB RAM, 1 vCPU) - Better for Ollama
   - Easy setup, good docs
   - **Best for beginners**

2. **Linode**
   - $5/month (1GB RAM)
   - $12/month (2GB RAM)
   - Good performance

3. **Vultr**
   - $6/month (1GB RAM)
   - $12/month (2GB RAM)
   - Global locations

4. **Hetzner** (Europe)
   - €4.15/month (2GB RAM)
   - Best value
   - Europe only

5. **Namecheap VPS** (Since you're already there)
   - $6.88/month (1GB RAM)
   - Convenient (same account)
   - Good for beginners

**Recommendation**: **DigitalOcean** ($12/month for 2GB RAM) - Best balance of price, performance, and ease of use.

---

### Step 2: Server Requirements

**Minimum**:
- 2GB RAM (Ollama needs ~1.5GB)
- 1 vCPU
- 20GB SSD storage
- Ubuntu 22.04 LTS

**Recommended**:
- 4GB RAM (for better Ollama performance)
- 2 vCPU
- 40GB SSD storage
- Ubuntu 22.04 LTS

**Cost**: $12-24/month

---

### Step 3: Point Namecheap Domain to VPS

**In Namecheap DNS Settings**:

1. **Get VPS IP Address** (from your VPS provider)
   - Example: `123.45.67.89`

2. **Update DNS Records**:
   - Go to Namecheap → Domain List → thesidia.com → Manage
   - Go to "Advanced DNS"
   - Add/Edit A Record:
     ```
     Type: A Record
     Host: @
     Value: 123.45.67.89 (your VPS IP)
     TTL: Automatic
     ```
   - Add/Edit A Record for www:
     ```
     Type: A Record
     Host: www
     Value: 123.45.67.89 (your VPS IP)
     TTL: Automatic
     ```

3. **Wait for DNS Propagation** (5 minutes to 48 hours, usually ~30 minutes)

4. **Verify**:
   ```bash
   dig thesidia.com
   # Should show your VPS IP
   ```

---

### Step 4: Server Setup (Ubuntu 22.04)

**SSH into your VPS**:
```bash
ssh root@your-vps-ip
```

**1. Update System**:
```bash
apt update && apt upgrade -y
```

**2. Install Python & Dependencies**:
```bash
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

**3. Install Ollama**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull clean-mistral:latest
```

**4. Clone Thesidia**:
```bash
cd /var/www
git clone https://github.com/zeriouslyzen/Thesidia-V.1.git thesidia
cd thesidia
```

**5. Set Up Python Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r webapp/requirements.txt
pip install gunicorn  # Production WSGI server
```

**6. Test Thesidia**:
```bash
cd webapp
python3 server.py
# Should start on port 5000
# Test: curl http://localhost:5000/api/status
```

---

### Step 5: Production Setup (Gunicorn + Nginx)

**1. Create Gunicorn Service**:

Create `/etc/systemd/system/thesidia.service`:
```ini
[Unit]
Description=Thesidia Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/thesidia/webapp
Environment="PATH=/var/www/thesidia/venv/bin"
ExecStart=/var/www/thesidia/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    server:app

[Install]
WantedBy=multi-user.target
```

**2. Start Service**:
```bash
systemctl daemon-reload
systemctl enable thesidia
systemctl start thesidia
systemctl status thesidia
```

**3. Configure Nginx**:

Create `/etc/nginx/sites-available/thesidia`:
```nginx
server {
    listen 80;
    server_name thesidia.com www.thesidia.com;

    # Frontend static files
    location / {
        root /var/www/thesidia/webapp;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

**4. Enable Site**:
```bash
ln -s /etc/nginx/sites-available/thesidia /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

**5. Set Up SSL (HTTPS)**:
```bash
certbot --nginx -d thesidia.com -d www.thesidia.com
# Follow prompts, enter email
```

**6. Auto-Renew SSL**:
```bash
certbot renew --dry-run  # Test
# Certbot auto-renews, but verify with cron:
# 0 0 * * * certbot renew --quiet
```

---

### Step 6: Security Hardening

**1. Firewall (UFW)**:
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

**2. SSH Key Authentication** (disable password):
```bash
# On your local machine:
ssh-copy-id root@your-vps-ip

# On server:
nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
systemctl restart sshd
```

**3. Fail2Ban** (prevent brute force):
```bash
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

**4. Automatic Updates**:
```bash
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

### Step 7: Monitoring & Backups

**1. Set Up Monitoring**:
```bash
# Install monitoring tools
apt install htop iotop
# Or use external service (UptimeRobot, Pingdom)
```

**2. Set Up Backups**:
```bash
# Create backup script
nano /usr/local/bin/backup-thesidia.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/thesidia"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup code
tar -czf $BACKUP_DIR/thesidia-code-$DATE.tar.gz /var/www/thesidia

# Backup state files
tar -czf $BACKUP_DIR/thesidia-state-$DATE.tar.gz /var/www/thesidia/data

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /usr/local/bin/backup-thesidia.sh

# Add to cron (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-thesidia.sh
```

---

## Cost Comparison

### Self-Hosting (VPS)

**One-Time Setup**: ~4 hours of your time

**Monthly Costs**:
- VPS (2GB RAM): $12/month (DigitalOcean)
- Domain (thesidia.com): Already paid
- SSL Certificate: Free (Let's Encrypt)
- **Total**: $12/month

**Annual**: $144/year

---

### Cloud Platform (Railway)

**Setup Time**: 10 minutes

**Monthly Costs**:
- Railway: $5/month credit (free tier) or $20/month (paid)
- Domain: Already paid
- SSL: Included
- **Total**: $0-20/month

**Annual**: $0-240/year

---

## Recommendation

### Choose Self-Hosting If:

1. ✅ You want to use **thesidia.com** directly
2. ✅ You have **4 hours** for initial setup
3. ✅ You're comfortable with **Linux/server management**
4. ✅ You want **full control** and customization
5. ✅ You want to **learn** deployment
6. ✅ You want **privacy** (your data on your server)

### Choose Cloud Platform If:

1. ✅ You want **zero maintenance**
2. ✅ You want to **deploy in 10 minutes**
3. ✅ You want **automatic updates/backups**
4. ✅ You want to **test first** (free tier)
5. ✅ You don't want to manage servers
6. ✅ You want **easy scaling**

---

## Hybrid Approach (Best of Both Worlds)

**Option**: Use cloud platform for testing, self-host for production

1. **Test on Railway** (free tier)
   - Deploy quickly
   - Test functionality
   - Verify everything works

2. **Move to Self-Hosted VPS** (when ready)
   - Use thesidia.com domain
   - Full control
   - Lower long-term cost

**Migration Path**:
- Test on Railway → Verify → Move to VPS → Point thesidia.com

---

## Quick Start: Self-Hosting

**Fastest Path** (if you choose self-hosting):

1. **Sign up for DigitalOcean** ($12/month, 2GB RAM)
2. **Create Ubuntu 22.04 droplet**
3. **SSH into server**
4. **Run setup script** (I can create this)
5. **Point thesidia.com** (Namecheap DNS)
6. **Set up SSL** (certbot)
7. **Done!**

**Total Time**: 2-4 hours  
**Cost**: $12/month

---

## Next Steps

**If you choose self-hosting**:
1. I can create a **setup script** to automate everything
2. I can create a **deployment guide** with exact commands
3. I can help with **troubleshooting**

**If you choose cloud platform**:
1. Use **Railway** (free tier for testing)
2. Point **thesidia.com** to Railway (CNAME record)
3. Deploy in 10 minutes

---

## Conclusion

**Self-hosting is BETTER for**:
- Using your domain (thesidia.com)
- Full control and customization
- Learning and understanding deployment
- Long-term cost savings (if you keep it running)

**Cloud platforms are BETTER for**:
- Quick deployment and testing
- Zero maintenance
- Automatic scaling and updates

**My Recommendation**: 
- **Start with Railway** (free tier) to test
- **Move to self-hosted VPS** when ready for production
- **Use thesidia.com** domain on VPS

This gives you the best of both worlds: quick testing + full control.

