# Deploying to AWS Elastic Beanstalk

This guide explains how to deploy the BNPL platform frontend to AWS Elastic Beanstalk as a Node.js application.

## Prerequisites

- AWS Account
- AWS CLI installed and configured
- EB CLI installed (`pip install awsebcli`)
- Node.js 18.x or higher (for local testing)

## Overview

AWS Elastic Beanstalk is a Platform-as-a-Service (PaaS) that simplifies deploying Node.js applications. It handles:
- Load balancing
- Auto-scaling
- Health monitoring
- Environment management

## Step-by-Step Deployment

### 1. Install EB CLI

```bash
pip install awsebcli
```

Verify installation:
```bash
eb --version
```

### 2. Initialize Elastic Beanstalk

Navigate to your frontend directory:

```bash
cd frontend
eb init
```

Follow the prompts:
- **Select a region:** Choose your preferred AWS region
- **Select an application:** Create a new application or use existing
- **Application name:** `bnpl-frontend` (or your preferred name)
- **Platform:** Node.js
- **Platform version:** Node.js 18 or 20 (recommended: 18.x)
- **SSH:** Yes (optional, for debugging)
- **SSH keypair:** Select or create a new one

### 3. Create Environment

```bash
eb create bnpl-frontend-env
```

This will:
- Create an Elastic Beanstalk environment
- Launch EC2 instances
- Set up load balancer
- Deploy your application

**Note:** This takes 5-10 minutes. You can monitor progress in the AWS Console.

### 4. Configure Environment Variables

Set environment variables in Elastic Beanstalk:

**Option A: Using EB CLI**

```bash
eb setenv NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
```

**Option B: Using AWS Console**

1. Go to [Elastic Beanstalk Console](https://console.aws.amazon.com/elasticbeanstalk/)
2. Select your environment
3. Go to **"Configuration"** → **"Software"**
4. Scroll to **"Environment properties"**
5. Add:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend-api.com`
   - `NODE_ENV` = `production`
6. Click **"Apply"**

### 5. Configure Build and Start Commands

Create `.ebextensions/01_nodejs.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:nodejs:
    NodeCommand: "npm run start"
    NodeVersion: 18.18.0
  aws:elasticbeanstalk:application:environment:
    NODE_ENV: production
```

Or use the Procfile (see below).

### 6. Create Procfile

Create a `Procfile` in the `frontend` directory:

```
web: npm run start
```

This tells Elastic Beanstalk how to start your application.

### 7. Deploy

```bash
eb deploy
```

This will:
- Package your application
- Upload to S3
- Deploy to your environment
- Run health checks

### 8. Check Status

```bash
eb status
eb health
```

### 9. View Logs

```bash
eb logs
```

Or view in AWS Console:
- Go to your environment
- Click **"Logs"** → **"Request Logs"** → **"Last 100 Lines"**

## Configuration Files

### Procfile

Create `frontend/Procfile`:

```
web: npm run start
```

This is the simplest way to tell Elastic Beanstalk how to start your app.

### .ebextensions Configuration (Optional)

For more control, create `frontend/.ebextensions/nodejs.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:nodejs:
    NodeCommand: "npm run start"
    NodeVersion: 18.18.0
  aws:elasticbeanstalk:application:environment:
    NODE_ENV: production
    PORT: 8080
```

### .ebignore (Optional)

Create `frontend/.ebignore` to exclude files from deployment:

```
node_modules
.next
.env.local
.env*.local
*.log
.DS_Store
.git
.gitignore
README.md
```

## Environment Variables Reference

Set these in Elastic Beanstalk **"Configuration"** → **"Software"** → **"Environment properties"**:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-backend-api.com` | **Required** - Backend API URL |
| `NODE_ENV` | `production` | Environment mode |
| `PORT` | `8080` | Port (EB sets this automatically, but you can override) |

Optional:
- `NEXT_PUBLIC_S3_BUCKET_URL` - For S3 document uploads
- `NEXT_PUBLIC_CDN_URL` - For CDN assets

## Build Process

Elastic Beanstalk will:
1. Run `npm install` (or `npm ci` if `package-lock.json` exists)
2. Run `npm run build` (if specified in build hooks)
3. Start the app with `npm run start` (from Procfile)

The `package.json` scripts are already configured:
- `build`: `next build`
- `start`: `next start -p ${PORT:-3000}`

## Custom Domain

1. In Elastic Beanstalk console, go to **"Configuration"** → **"Load balancer"**
2. Add a listener for HTTPS (port 443)
3. Configure SSL certificate (use AWS Certificate Manager)
4. Update your DNS to point to the Elastic Beanstalk environment URL

## Scaling

Configure auto-scaling in **"Configuration"** → **"Capacity"**:
- **Environment type:** Load balanced
- **Min instances:** 1
- **Max instances:** 4 (adjust based on needs)
- **Scaling triggers:** CPU, Network, Request count

## Troubleshooting

### Deployment Fails

1. **Check logs:**
   ```bash
   eb logs
   ```

2. **Verify Node version:**
   - Ensure EB is using Node.js 18.x or 20.x
   - Check in **"Configuration"** → **"Platform"**

3. **Check build errors:**
   - Look for errors in deployment logs
   - Verify `npm run build` works locally

### Application Won't Start

1. **Check Procfile:**
   - Ensure `Procfile` exists and is correct
   - Verify `npm run start` works locally

2. **Check environment variables:**
   - Verify `NEXT_PUBLIC_API_BASE_URL` is set
   - Check in **"Configuration"** → **"Software"**

3. **Check health:**
   ```bash
   eb health
   ```

### 502 Bad Gateway

- Application is not starting correctly
- Check logs: `eb logs`
- Verify PORT is set correctly (EB uses 8080 by default)
- Ensure `next start` is listening on the correct port

### API Connection Issues

1. **Verify `NEXT_PUBLIC_API_BASE_URL`** is set correctly
2. **Check CORS** on your backend API
3. **Verify security groups** allow outbound HTTPS traffic
4. **Test API URL** from the EC2 instance (use `eb ssh` then `curl`)

## Using Docker (Alternative)

If you prefer containerized deployment, see the `Dockerfile` in the repository root. You can:

1. Build and push to Amazon ECR
2. Deploy to Elastic Beanstalk with Docker platform
3. Or use ECS/Fargate instead

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Node.js on Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_nodejs.html)

