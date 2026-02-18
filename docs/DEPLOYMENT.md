# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

### Steps

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   createdb mytomorrows_db
   psql -d mytomorrows_db -f schema.sql
   python init_db.py
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your POSTGRES_* variables
   ```

4. **Run application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Deployment

### Quick Start

```bash
docker-compose up -d
```

### Production Docker

1. **Update environment**
   - Set `POSTGRES_*` variables to production database
   - Set `DEBUG=False`
   - Remove database service from `docker-compose.yml`

2. **Build and run**
   ```bash
   docker build -t mytomorrows-api:latest .
   docker run -d \
     --name mytomorrows-api \
     -p 8000:8000 \
     --env-file .env \
     mytomorrows-api:latest
   ```

## Cloud Deployment

### AWS (ECS/Fargate + RDS)

1. **Create RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier mytomorrows-db \
     --engine postgres \
     --master-username admin \
     --master-user-password <password>
   ```

2. **Build and push image**
   ```bash
   docker build -t mytomorrows-api .
   docker tag mytomorrows-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/mytomorrows-api:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/mytomorrows-api:latest
   ```

3. **Create ECS Task Definition** (JSON)
   ```json
   {
     "family": "mytomorrows-api",
     "containerDefinitions": [{
       "name": "mytomorrows-api",
       "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/mytomorrows-api:latest",
       "portMappings": [{"containerPort": 8000}],
       "environment": [
         {"name": "POSTGRES_USER", "value": "admin"},
         {"name": "POSTGRES_PASSWORD", "value": "<password>"},
         {"name": "POSTGRES_DB", "value": "mytomorrows_db"},
         {"name": "POSTGRES_HOST", "value": "<rds-endpoint>"},
         {"name": "POSTGRES_PORT", "value": "5432"},
         {"name": "DEBUG", "value": "False"}
       ]
     }]
   }
   ```

4. **Create ECS Service** with Fargate launch type

### Google Cloud Platform (Cloud Run + Cloud SQL)

1. **Create Cloud SQL**
   ```bash
   gcloud sql instances create mytomorrows-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro
   ```

2. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/<project-id>/mytomorrows-api
   gcloud run deploy mytomorrows-api \
     --image gcr.io/<project-id>/mytomorrows-api \
     --add-cloudsql-instances <project-id>:us-central1:mytomorrows-db \
     --set-env-vars POSTGRES_USER="admin",POSTGRES_PASSWORD="<password>",POSTGRES_DB="mytomorrows_db",POSTGRES_HOST="/cloudsql/<project-id>:us-central1:mytomorrows-db",POSTGRES_PORT="5432"
   ```

### Azure (Container Instances + Azure Database)

1. **Create Azure Database**
   ```bash
   az postgres server create \
     --resource-group mytomorrows-rg \
     --name mytomorrows-db \
     --admin-user admin \
     --admin-password <password>
   ```

2. **Build and deploy**
   ```bash
   az acr build --registry <registry-name> --image mytomorrows-api:latest .
   az container create \
     --resource-group mytomorrows-rg \
     --name mytomorrows-api \
     --image <registry-name>.azurecr.io/mytomorrows-api:latest \
     --environment-variables POSTGRES_USER="admin" POSTGRES_PASSWORD="<password>" POSTGRES_DB="mytomorrows_db" POSTGRES_HOST="<azure-db-host>" POSTGRES_PORT="5432"
   ```

## Infrastructure as Code

### Terraform Example (AWS)

```hcl
resource "aws_db_instance" "mytomorrows_db" {
  identifier     = "mytomorrows-db"
  engine         = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  db_name  = "mytomorrows_db"
  username = "admin"
  password = var.db_password
}

resource "aws_ecs_service" "api" {
  name            = "mytomorrows-api"
  cluster         = aws_ecs_cluster.mytomorrows.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
}
```

### Kubernetes Manifests

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mytomorrows-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: mytomorrows-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: database
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
        - name: POSTGRES_PORT
          value: "5432"
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        run: |
          docker build -t mytomorrows-api:${{ github.sha }} .
          docker push mytomorrows-api:${{ github.sha }}
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster mytomorrows-cluster --service mytomorrows-api --force-new-deployment
```

## Monitoring

### Recommended Tools
- **Application**: Datadog, New Relic, CloudWatch
- **Logging**: ELK Stack, CloudWatch Logs
- **Error Tracking**: Sentry, Rollbar
- **Metrics**: Prometheus + Grafana

## Security Checklist

- [ ] Use HTTPS/TLS
- [ ] Implement authentication (JWT)
- [ ] Use secrets management
- [ ] Enable database encryption
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Enable logging and monitoring

## Backup and Recovery

### Database Backups

**Automated**:
- RDS: Enable automated backups
- Cloud SQL: Enable automated backups
- Azure Database: Point-in-time restore

**Manual**:
```bash
pg_dump -h <host> -U <user> -d mytomorrows_db > backup.sql
psql -h <host> -U <user> -d mytomorrows_db < backup.sql
```

## Scaling

### Horizontal Scaling
- Use load balancer
- Multiple container instances
- Auto-scaling based on CPU/memory

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Query optimization
