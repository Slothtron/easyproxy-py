# EasyProxy Docker 部署指南

## 快速开始

### 方式一: 使用 Docker Compose (推荐)

1. **准备配置文件**

```bash
cd scripts/docker
cp ../../config/config.example.yaml config.yaml
# 编辑配置文件
nano config.yaml
```

2. **启动服务**

```bash
docker-compose up -d
```

3. **查看日志**

```bash
docker-compose logs -f
```

4. **停止服务**

```bash
docker-compose down
```

---

### 方式二: 使用 Docker 命令

1. **构建镜像**

```bash
cd /home/lolioy/workspace/projects/easyproxy-py
docker build -f scripts/docker/Dockerfile -t easyproxy:latest .
```

2. **运行容器**

```bash
docker run -d \
  --name easyproxy \
  --restart unless-stopped \
  -p 7899:7899 \
  -v $(pwd)/config/config.example.yaml:/etc/easyproxy/config.yaml:ro \
  -v $(pwd)/logs:/var/log/easyproxy \
  easyproxy:latest
```

3. **查看日志**

```bash
docker logs -f easyproxy
```

4. **停止容器**

```bash
docker stop easyproxy
docker rm easyproxy
```

---

## 配置说明

### 端口映射

默认映射 `7899:7899`,可以修改为其他端口:

```yaml
ports:
  - "8080:7899"  # 主机端口:容器端口
```

### 资源限制

在 `docker-compose.yml` 中调整:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU 限制
      memory: 2G       # 内存限制
```

### 日志配置

日志自动轮转配置:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"   # 单个日志文件最大 10MB
    max-file: "3"     # 保留最近 3 个日志文件
```

---

## 高级用法

### 使用主机网络模式

性能更好,但安全性较低:

```yaml
network_mode: "host"
```

然后移除 `ports` 配置。

### 多实例部署

复制 `docker-compose.yml` 并修改:

```yaml
services:
  easyproxy-1:
    # ...
    ports:
      - "7899:7899"
  
  easyproxy-2:
    # ...
    ports:
      - "7900:7899"
```

### 使用外部配置

```bash
docker run -d \
  --name easyproxy \
  -p 7899:7899 \
  -v /path/to/your/config.yaml:/etc/easyproxy/config.yaml:ro \
  easyproxy:latest
```

---

## 健康检查

容器内置健康检查,每 30 秒检查一次:

```bash
# 查看健康状态
docker inspect --format='{{.State.Health.Status}}' easyproxy
```

---

## 故障排查

### 查看容器日志

```bash
docker logs easyproxy
```

### 进入容器调试

```bash
docker exec -it easyproxy /bin/bash
```

### 检查端口监听

```bash
docker exec easyproxy netstat -tlnp
```

---

## 生产环境建议

1. **使用具体版本标签**
   ```yaml
   image: slothtron/easyproxy:0.1.0  # 而不是 :latest
   ```

2. **配置日志驱动**
   ```yaml
   logging:
     driver: "syslog"
     options:
       syslog-address: "tcp://192.168.0.1:514"
   ```

3. **启用只读根文件系统**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp
   ```

4. **使用 Docker Secrets 管理敏感信息**
   ```yaml
   secrets:
     - easyproxy_config
   ```

---

## 性能优化

### 调整 ulimit

```yaml
ulimits:
  nofile:
    soft: 65536
    hard: 65536
```

### 使用 host 网络

```yaml
network_mode: "host"
```

### 禁用不必要的安全特性

```yaml
security_opt:
  - apparmor=unconfined
```

---

## 监控集成

### Prometheus 监控

TODO: 添加 Prometheus exporter

### 日志收集

与 ELK/Loki 集成:

```yaml
logging:
  driver: "fluentd"
  options:
    fluentd-address: "localhost:24224"
    tag: "easyproxy"
```
