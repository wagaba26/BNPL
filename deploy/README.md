# Deployment Scripts and Automation

This directory contains scripts and templates to help deploy the BNPL platform to AWS.

## Prerequisites

1. **AWS CLI** installed and configured
   ```powershell
   aws configure
   ```

2. **Docker** installed and running (for containerized deployments)

3. **EB CLI** (for Elastic Beanstalk deployment)
   ```powershell
   pip install awsebcli
   ```

4. **AWS Account** with appropriate permissions:
   - EC2 (for security groups, ECS)
   - RDS (for database)
   - S3 (for file storage)
   - ECR (for container registry)
   - IAM (for roles and policies)
   - CloudFormation (for infrastructure as code)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Set up AWS infrastructure:**
   ```powershell
   cd deploy
   .\aws-setup.ps1 -Region us-east-1 -Environment production
   ```

2. **Create RDS database** (manual step via AWS Console or CloudFormation):
   - Use the CloudFormation template: `cloudformation-infrastructure.yaml`
   - Or create manually using the configuration from `aws-setup.ps1` output

3. **Build and push Docker images:**
   ```powershell
   .\build-and-push.ps1 -Component all
   ```

4. **Deploy backend:**
   ```powershell
   .\deploy-backend-eb.ps1 -EnvironmentName bnpl-backend-prod
   ```

5. **Deploy frontend:**
   - Use AWS Amplify (see `frontend/DEPLOY-AWS-AMPLIFY.md`)
   - Or Elastic Beanstalk (see `frontend/DEPLOY-AWS-EB.md`)

### Option 2: CloudFormation (Infrastructure as Code)

1. **Deploy infrastructure:**
   ```powershell
   aws cloudformation create-stack \
     --stack-name bnpl-infrastructure \
     --template-body file://cloudformation-infrastructure.yaml \
     --parameters \
       ParameterKey=Environment,ParameterValue=production \
       ParameterKey=DatabasePassword,ParameterValue=YourSecurePassword \
       ParameterKey=DatabaseInstanceClass,ParameterValue=db.t3.micro \
     --capabilities CAPABILITY_IAM
   ```

2. **Wait for stack creation:**
   ```powershell
   aws cloudformation wait stack-create-complete --stack-name bnpl-infrastructure
   ```

3. **Get outputs:**
   ```powershell
   aws cloudformation describe-stacks --stack-name bnpl-infrastructure --query 'Stacks[0].Outputs'
   ```

4. **Update backend environment variables** with RDS endpoint from outputs

5. **Build and deploy applications** (same as Option 1, steps 3-5)

## Scripts Overview

### `aws-setup.ps1`
Sets up basic AWS resources:
- S3 bucket for documents
- ECR repositories for Docker images
- Generates configuration file

**Usage:**
```powershell
.\aws-setup.ps1 -Region us-east-1 -Environment production
```

### `build-and-push.ps1`
Builds Docker images and pushes to ECR.

**Usage:**
```powershell
# Build and push both
.\build-and-push.ps1 -Component all

# Build and push only backend
.\build-and-push.ps1 -Component backend

# Build and push only frontend
.\build-and-push.ps1 -Component frontend
```

### `deploy-backend-eb.ps1`
Deploys backend to AWS Elastic Beanstalk.

**Usage:**
```powershell
.\deploy-backend-eb.ps1 -EnvironmentName bnpl-backend-prod -Region us-east-1
```

### `update-cors.ps1`
Updates CORS configuration in backend code.

**Usage:**
```powershell
.\update-cors.ps1 -AllowedOrigins "https://app.example.com","https://www.example.com"
```

## CloudFormation Template

The `cloudformation-infrastructure.yaml` template creates:

- **RDS PostgreSQL** database instance
- **S3 bucket** for document storage
- **ECR repositories** for Docker images
- **Security groups** for RDS and backend
- **IAM role** for backend S3 access

**Deploy:**
```powershell
aws cloudformation create-stack \
  --stack-name bnpl-infrastructure \
  --template-body file://cloudformation-infrastructure.yaml \
  --parameters ParameterKey=DatabasePassword,ParameterValue=YourPassword \
  --capabilities CAPABILITY_IAM
```

**Note:** The template assumes a default VPC exists. For production, modify it to use a custom VPC with private subnets.

## Environment Variables

### Backend (.env or Elastic Beanstalk environment variables)

```env
DATABASE_URL=postgresql://bnpl_user:password@rds-endpoint:5432/bnpl_db
SECRET_KEY=your-strong-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://your-frontend-domain.com
LENDER_ADMIN_CODE=your-secure-admin-code
DEBUG=False
```

### Frontend (Amplify/Elastic Beanstalk environment variables)

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
```

## Deployment Checklist

- [ ] AWS CLI configured
- [ ] Infrastructure set up (RDS, S3, ECR)
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] CORS updated for production
- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] SSL/HTTPS enabled
- [ ] Monitoring set up (CloudWatch)
- [ ] Backups configured (RDS)

## Troubleshooting

### Build fails
- Check Docker is running
- Verify AWS credentials are configured
- Check ECR repository exists

### Deployment fails
- Check logs: `eb logs` or CloudWatch
- Verify environment variables are set
- Check security groups allow traffic

### Database connection fails
- Verify RDS security group allows backend security group
- Check `DATABASE_URL` is correct
- Verify RDS is accessible from backend

### CORS errors
- Update CORS configuration with frontend URL
- Rebuild and redeploy backend
- Check browser console for specific error

## Security Notes

1. **Never commit secrets** - Use AWS Secrets Manager or Parameter Store
2. **Use IAM roles** - Don't hardcode AWS credentials
3. **Restrict database access** - Only allow backend security group
4. **Enable HTTPS** - Always use SSL/TLS
5. **Update CORS** - Don't use `["*"]` in production
6. **Strong passwords** - Use complex passwords for RDS
7. **Enable backups** - Configure RDS automated backups

## Cost Optimization

- Use `db.t3.micro` for development/testing
- Use `db.t3.small` or larger for production
- Enable RDS automated backups (7 days minimum)
- Set up S3 lifecycle policies
- Use ECR lifecycle policies to clean old images
- Monitor CloudWatch costs

## Additional Resources

- [AWS Deployment Checklist](../AWS_DEPLOYMENT_CHECKLIST.md)
- [Frontend Deployment Guide](../frontend/DEPLOY-AWS.md)
- [Backend README](../backend/README.md)

