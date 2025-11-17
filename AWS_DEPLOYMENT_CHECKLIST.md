# AWS Deployment Checklist - BNPL Platform

This document outlines everything you need to deploy your BNPL platform to AWS.

## Architecture Overview

Your application consists of:
1. **Frontend** - Next.js application
2. **Backend API** - FastAPI Python application
3. **Database** - PostgreSQL (currently using SQLite in dev)
4. **File Storage** - S3 for document uploads (credit documents, etc.)

## Deployment Components

### 1. Frontend (Next.js)

**Deployment Options:**
- ✅ **AWS Amplify Hosting** (Recommended for Next.js)
- ✅ **AWS Elastic Beanstalk**
- ✅ **AWS ECS/Fargate** (with Docker)
- ✅ **AWS EC2** (with Docker or direct Node.js)

**What You Need:**
- [ ] Git repository (GitHub/GitLab/Bitbucket) connected
- [ ] Environment variable: `NEXT_PUBLIC_API_BASE_URL` (your backend API URL)
- [ ] Node.js 18.x or 20.x
- [ ] Build command: `npm run build`
- [ ] Start command: `npm run start`

**Files Already Configured:**
- ✅ `frontend/package.json` - Has correct build/start scripts
- ✅ `frontend/Dockerfile` - Docker configuration ready
- ✅ `frontend/Procfile` - For Elastic Beanstalk
- ✅ Deployment docs: `frontend/DEPLOY-AWS.md`, `frontend/DEPLOY-AWS-AMPLIFY.md`, `frontend/DEPLOY-AWS-EB.md`

**Quick Deploy:**
```bash
# Option 1: AWS Amplify (Easiest)
# 1. Go to AWS Amplify Console
# 2. Connect your Git repository
# 3. Set NEXT_PUBLIC_API_BASE_URL environment variable
# 4. Deploy

# Option 2: Elastic Beanstalk
cd frontend
eb init
eb create bnpl-frontend-env
eb setenv NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
eb deploy
```

---

### 2. Backend API (FastAPI)

**Deployment Options:**
- ✅ **AWS Elastic Beanstalk** (Python platform)
- ✅ **AWS ECS/Fargate** (with Docker) - Recommended
- ✅ **AWS EC2** (with Docker or direct Python)
- ✅ **AWS Lambda** (with API Gateway) - For serverless (requires refactoring)

**What You Need:**
- [ ] PostgreSQL database (RDS)
- [ ] Environment variables (see below)
- [ ] Python 3.11+
- [ ] CORS configuration updated for production
- [ ] SSL/HTTPS certificate

**Files Already Configured:**
- ✅ `Dockerfile` - Docker configuration ready
- ✅ `backend/requirements.txt` - All dependencies listed
- ✅ `backend/app/main.py` - FastAPI app with CORS (needs production CORS update)

**Required Environment Variables:**
```env
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/bnpl_db
SECRET_KEY=your-strong-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LENDER_ADMIN_CODE=your-secure-admin-code
DEBUG=False
```

**CORS Configuration (Update in `backend/app/main.py`):**
```python
# Replace allow_origins=["*"] with your frontend URL(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "https://your-amplify-domain.amplifyapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Quick Deploy with Docker:**
```bash
# Build Docker image
docker build -t bnpl-backend .

# Tag for ECR
docker tag bnpl-backend:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bnpl-backend:latest

# Push to ECR
aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/bnpl-backend:latest

# Deploy to ECS/Fargate or Elastic Beanstalk
```

**Quick Deploy with Elastic Beanstalk:**
```bash
cd backend
eb init -p python-3.11
eb create bnpl-backend-env
eb setenv DATABASE_URL=postgresql://... SECRET_KEY=... ALGORITHM=HS256
eb deploy
```

---

### 3. Database (PostgreSQL)

**Deployment Options:**
- ✅ **AWS RDS PostgreSQL** (Recommended)
- ✅ **AWS RDS Aurora PostgreSQL** (For high availability)
- ✅ **Self-managed on EC2** (Not recommended for production)

**What You Need:**
- [ ] RDS PostgreSQL instance (15.x recommended)
- [ ] Database name: `bnpl_db`
- [ ] Master username and password
- [ ] Security group allowing access from backend
- [ ] Automated backups enabled
- [ ] Multi-AZ deployment (for production)

**RDS Setup Steps:**
1. Create RDS PostgreSQL instance
2. Configure security group:
   - Allow inbound from backend security group (port 5432)
   - Or allow from specific IPs
3. Get endpoint URL: `your-db-instance.xxxxx.us-east-1.rds.amazonaws.com:5432`
4. Update `DATABASE_URL` in backend environment:
   ```
   DATABASE_URL=postgresql://username:password@your-db-instance.xxxxx.us-east-1.rds.amazonaws.com:5432/bnpl_db
   ```
5. Run migrations:
   ```bash
   # From backend directory
   alembic upgrade head
   ```

**RDS Configuration:**
- **Instance Class:** db.t3.micro (dev) / db.t3.small+ (production)
- **Storage:** 20GB+ (auto-scaling recommended)
- **Backup Retention:** 7 days minimum
- **Multi-AZ:** Yes for production
- **Public Access:** No (use VPC)

---

### 4. File Storage (S3)

**For Document Uploads:**
- Credit documents
- KYC documents
- Trading licenses
- Other user-uploaded files

**What You Need:**
- [ ] S3 bucket for document storage
- [ ] IAM policy for backend to upload files
- [ ] CORS configuration for frontend uploads (if direct upload)
- [ ] Bucket policy for access control

**S3 Setup Steps:**
1. Create S3 bucket: `bnpl-documents-{region}-{account-id}`
2. Enable versioning (optional but recommended)
3. Configure CORS (if frontend uploads directly):
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["PUT", "POST", "GET"],
       "AllowedOrigins": ["https://your-frontend-domain.com"],
       "ExposeHeaders": ["ETag"],
       "MaxAgeSeconds": 3000
     }
   ]
   ```
4. Create IAM policy for backend:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:PutObject",
           "s3:GetObject",
           "s3:DeleteObject"
         ],
         "Resource": "arn:aws:s3:::bnpl-documents-*/*"
       }
     ]
   }
   ```
5. Update backend environment variables (if using S3):
   ```env
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=bnpl-documents-{region}-{account-id}
   ```

---

## Complete Deployment Checklist

### Pre-Deployment

- [ ] **AWS Account** set up with appropriate permissions
- [ ] **AWS CLI** installed and configured (`aws configure`)
- [ ] **Git repository** ready (for frontend deployment)
- [ ] **Domain name** (optional, for custom domain)
- [ ] **SSL certificate** (AWS Certificate Manager)

### Infrastructure Setup

- [ ] **RDS PostgreSQL** instance created
  - [ ] Database name: `bnpl_db`
  - [ ] Security group configured
  - [ ] Backups enabled
  - [ ] Connection tested

- [ ] **S3 Bucket** created
  - [ ] Bucket name: `bnpl-documents-{region}-{account-id}`
  - [ ] CORS configured (if needed)
  - [ ] IAM policy created

- [ ] **ECR Repository** created (if using Docker)
  ```bash
  aws ecr create-repository --repository-name bnpl-backend --region us-east-1
  aws ecr create-repository --repository-name bnpl-frontend --region us-east-1
  ```

### Backend Deployment

- [ ] **Environment Variables** configured:
  - [ ] `DATABASE_URL` (RDS endpoint)
  - [ ] `SECRET_KEY` (strong random key)
  - [ ] `ALGORITHM=HS256`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=30`
  - [ ] `LENDER_ADMIN_CODE` (secure code)
  - [ ] `DEBUG=False`
  - [ ] AWS credentials (if using S3)

- [ ] **CORS** updated in `backend/app/main.py`:
  - [ ] Replace `allow_origins=["*"]` with production frontend URLs

- [ ] **Database Migrations** run:
  ```bash
  alembic upgrade head
  ```

- [ ] **Backend Deployed**:
  - [ ] ECS/Fargate service running
  - [ ] Or Elastic Beanstalk environment healthy
  - [ ] Health check endpoint working: `https://your-api.com/health`
  - [ ] API docs accessible: `https://your-api.com/docs`

### Frontend Deployment

- [ ] **Environment Variables** configured:
  - [ ] `NEXT_PUBLIC_API_BASE_URL` (backend API URL)

- [ ] **Frontend Deployed**:
  - [ ] Amplify app connected to Git repo
  - [ ] Or Elastic Beanstalk environment created
  - [ ] Build successful
  - [ ] Application accessible

### Post-Deployment

- [ ] **CORS** verified:
  - [ ] Frontend can call backend API
  - [ ] No CORS errors in browser console

- [ ] **Authentication** tested:
  - [ ] User registration works
  - [ ] User login works
  - [ ] JWT tokens working

- [ ] **Database** verified:
  - [ ] Tables created correctly
  - [ ] Data persists
  - [ ] Migrations applied

- [ ] **File Uploads** tested (if implemented):
  - [ ] Documents upload to S3
  - [ ] Files accessible

- [ ] **Monitoring** set up:
  - [ ] CloudWatch logs configured
  - [ ] Alarms set up (optional)
  - [ ] Health checks monitoring

- [ ] **Security** verified:
  - [ ] HTTPS enabled
  - [ ] CORS properly configured
  - [ ] Secrets not exposed
  - [ ] Database not publicly accessible

---

## Cost Estimation (Monthly)

### Development/Testing Environment:
- **RDS db.t3.micro**: ~$15/month
- **EC2 t3.micro** (backend): ~$7/month
- **Amplify Hosting**: ~$1/month (or free tier)
- **S3 Storage**: ~$0.023/GB/month
- **Data Transfer**: ~$0.09/GB
- **Total**: ~$25-30/month

### Production Environment:
- **RDS db.t3.small (Multi-AZ)**: ~$60/month
- **ECS Fargate** (backend): ~$30-50/month
- **Amplify Hosting**: ~$15/month
- **S3 Storage**: ~$0.023/GB/month
- **CloudWatch**: ~$5/month
- **Total**: ~$110-130/month

*Costs vary by region, usage, and traffic*

---

## Quick Start Commands

### 1. Set Up RDS
```bash
aws rds create-db-instance \
  --db-instance-identifier bnpl-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username bnpl_user \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx
```

### 2. Create S3 Bucket
```bash
aws s3 mb s3://bnpl-documents-$(aws sts get-caller-identity --query Account --output text)-$(aws configure get region)
```

### 3. Deploy Backend (ECS)
```bash
# Build and push Docker image
docker build -t bnpl-backend .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag bnpl-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bnpl-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/bnpl-backend:latest

# Create ECS service (requires task definition, cluster, etc.)
```

### 4. Deploy Frontend (Amplify)
1. Go to AWS Amplify Console
2. Connect Git repository
3. Set `NEXT_PUBLIC_API_BASE_URL`
4. Deploy

---

## Security Best Practices

1. **Never commit secrets** - Use AWS Secrets Manager or Parameter Store
2. **Use IAM roles** - Don't hardcode AWS credentials
3. **Enable HTTPS** - Always use SSL/TLS
4. **Restrict database access** - Only allow backend security group
5. **Use VPC** - Keep resources in private subnets when possible
6. **Enable WAF** - Protect against common attacks
7. **Regular backups** - Enable automated RDS backups
8. **Monitor logs** - Set up CloudWatch alarms

---

## Troubleshooting

### Backend Can't Connect to RDS
- Check security group allows inbound from backend
- Verify `DATABASE_URL` is correct
- Check RDS is in same VPC or has public access enabled

### Frontend Can't Call Backend
- Verify CORS configuration
- Check `NEXT_PUBLIC_API_BASE_URL` is set correctly
- Verify backend is accessible from internet

### Build Fails
- Check Node.js/Python version matches
- Verify all dependencies are in requirements.txt/package.json
- Check build logs in AWS Console

---

## Additional Resources

- **Frontend Deployment**: See `frontend/DEPLOY-AWS.md`
- **Backend Setup**: See `backend/README.md`
- **AWS Documentation**:
  - [RDS PostgreSQL](https://docs.aws.amazon.com/rds/latest/userguide/CHAP_PostgreSQL.html)
  - [ECS](https://docs.aws.amazon.com/ecs/)
  - [Amplify Hosting](https://docs.aws.amazon.com/amplify/)
  - [S3](https://docs.aws.amazon.com/s3/)

---

## Next Steps

1. **Choose deployment method** for each component
2. **Set up RDS** database first
3. **Deploy backend** and verify it connects to RDS
4. **Deploy frontend** and verify it connects to backend
5. **Test end-to-end** functionality
6. **Set up monitoring** and alerts
7. **Configure custom domain** (optional)

