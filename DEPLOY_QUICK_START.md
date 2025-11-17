# Quick Start: Deploy to AWS

I've created deployment automation scripts and infrastructure templates. **I cannot deploy directly** (requires your AWS credentials), but I've prepared everything you need to deploy yourself.

## What I've Created

### ✅ Deployment Scripts (`deploy/` directory)
1. **`aws-setup.ps1`** - Sets up S3, ECR repositories
2. **`build-and-push.ps1`** - Builds and pushes Docker images to ECR
3. **`deploy-backend-eb.ps1`** - Deploys backend to Elastic Beanstalk
4. **`update-cors.ps1`** - Updates CORS configuration

### ✅ Infrastructure as Code
- **`cloudformation-infrastructure.yaml`** - Complete infrastructure template (RDS, S3, ECR, Security Groups)

### ✅ Code Updates
- Updated CORS to be environment-aware (uses `CORS_ORIGINS` environment variable)
- Backend now reads CORS origins from config

### ✅ Documentation
- **`AWS_DEPLOYMENT_CHECKLIST.md`** - Complete deployment checklist
- **`deploy/README.md`** - Script usage guide

## Quick Deployment Steps

### 1. Prerequisites
```powershell
# Install AWS CLI (if not installed)
# Download from: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure

# Install EB CLI (for Elastic Beanstalk)
pip install awsebcli

# Verify Docker is running
docker ps
```

### 2. Set Up Infrastructure

**Option A: Using Scripts (Easier)**
```powershell
cd deploy
.\aws-setup.ps1 -Region us-east-1 -Environment production
```

**Option B: Using CloudFormation (Infrastructure as Code)**
```powershell
aws cloudformation create-stack \
  --stack-name bnpl-infrastructure \
  --template-body file://deploy/cloudformation-infrastructure.yaml \
  --parameters \
    ParameterKey=DatabasePassword,ParameterValue=YourSecurePassword \
    ParameterKey=DatabaseInstanceClass,ParameterValue=db.t3.micro \
  --capabilities CAPABILITY_IAM
```

### 3. Create RDS Database

If using CloudFormation, RDS is created automatically. Otherwise:

1. Go to AWS RDS Console
2. Create PostgreSQL 15.x instance
3. Use configuration from `aws-setup.ps1` output
4. Note the endpoint URL

### 4. Run Database Migrations

```powershell
cd backend
# Set DATABASE_URL environment variable
$env:DATABASE_URL = "postgresql://bnpl_user:password@rds-endpoint:5432/bnpl_db"
alembic upgrade head
```

### 5. Build and Push Docker Images

```powershell
cd deploy
.\build-and-push.ps1 -Component all
```

### 6. Deploy Backend

```powershell
.\deploy-backend-eb.ps1 -EnvironmentName bnpl-backend-prod
```

When prompted, enter:
- `DATABASE_URL` (from RDS)
- `SECRET_KEY` (generate a strong random key)
- `LENDER_ADMIN_CODE` (your secure admin code)

### 7. Update CORS (After Frontend is Deployed)

Once you have your frontend URL:

```powershell
.\update-cors.ps1 -AllowedOrigins "https://your-frontend-domain.com"
```

Then rebuild and redeploy backend.

### 8. Deploy Frontend

**Option A: AWS Amplify (Recommended for Next.js)**
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Connect your Git repository
3. Set environment variable: `NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.com`
4. Deploy

**Option B: Elastic Beanstalk**
See `frontend/DEPLOY-AWS-EB.md`

## Environment Variables Summary

### Backend (Set in Elastic Beanstalk or .env)
```env
DATABASE_URL=postgresql://bnpl_user:password@rds-endpoint:5432/bnpl_db
SECRET_KEY=your-strong-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
LENDER_ADMIN_CODE=your-secure-code
DEBUG=False
```

### Frontend (Set in Amplify/Elastic Beanstalk)
```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
```

## What You Need to Provide

1. **AWS Account** - With appropriate permissions
2. **Database Password** - Strong password for RDS
3. **Secret Key** - For JWT tokens (generate random)
4. **Frontend URL** - For CORS configuration
5. **Lender Admin Code** - For lender registration

## Estimated Costs

- **Development/Testing**: ~$25-30/month
- **Production**: ~$110-130/month

## Troubleshooting

### Can't connect to RDS
- Check security group allows backend security group
- Verify `DATABASE_URL` is correct
- Ensure RDS is in same VPC or has public access

### CORS errors
- Update `CORS_ORIGINS` environment variable
- Rebuild and redeploy backend
- Check browser console for specific error

### Build fails
- Verify Docker is running
- Check AWS credentials: `aws sts get-caller-identity`
- Ensure ECR repositories exist

## Next Steps

1. Review `AWS_DEPLOYMENT_CHECKLIST.md` for complete checklist
2. Read `deploy/README.md` for detailed script usage
3. Check `frontend/DEPLOY-AWS.md` for frontend deployment options

## Need Help?

- **Infrastructure Issues**: Check CloudFormation stack events
- **Deployment Issues**: Check `eb logs` or CloudWatch logs
- **Application Issues**: Check backend logs and frontend console

---

**Note**: I cannot execute these scripts for you as they require:
- Your AWS credentials
- Your AWS account access
- Your approval for resource creation

All scripts are ready to run - just execute them in your environment!

