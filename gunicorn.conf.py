bind = "0.0.0.0:8080"
workers = 3  # 0.5 vCPU, 2 GB
wsgi_app = "config.wsgi:application"
preload = True
timeout = 40
