FROM nginx:1.25-alpine

# Mevcut konfigürasyonu temizle
RUN rm /etc/nginx/conf.d/default.conf

# Kendi konfigürasyonunu kopyala
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx'in ön planda çalışmasını sağla (Kapanmaması için)
CMD ["nginx", "-g", "daemon off;"]
