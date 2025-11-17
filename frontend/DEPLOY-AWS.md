# AWS Deployment Guide - BNPL Platform

This document provides an overview of deploying the BNPL platform frontend to AWS. Choose between **AWS Amplify Hosting** or **AWS Elastic Beanstalk** based on your needs.

## Quick Comparison

| Feature | AWS Amplify | Elastic Beanstalk |
|---------|-------------|-------------------|
| **Best For** | Next.js apps with SSR | Traditional Node.js apps |
| **Setup Complexity** | Low | Medium |
| **CI/CD** | Automatic (Git-based) | Manual or via EB CLI |
| **Scaling** | Automatic | Configurable auto-scaling |
| **Cost** | Pay for usage | Pay for EC2 instances |
| **SSL/HTTPS** | Automatic | Manual configuration |
| **Custom Domain** | Easy | Requires load balancer setup |

## Prerequisites

Before deploying, ensure you have:

1. ✅ **AWS Account** with appropriate permissions
2. ✅ **Backend API deployed** and accessible (separate from frontend)
3. ✅ **Environment variables** ready (see `.env.example`)
4. ✅ **Git repository** with your code (for Amplify)

## Pre-Deployment Checklist

### 1. Verify Build Scripts

The `package.json` already has the correct scripts:
- ✅ `build`: `next build`
- ✅ `start`: `next start -p ${PORT:-3000}`

### 2. Environment Variables

All required environment variables are documented in `.env.example`:

**Required:**
- `NEXT_PUBLIC_API_BASE_URL` - Your backend API URL

**Optional:**
- `NEXT_PUBLIC_S3_BUCKET_URL` - For S3 document uploads
- `NEXT_PUBLIC_CDN_URL` - For CDN assets

### 3. No Hard-Coded URLs

✅ The codebase has been updated to:
- Use `process.env.NEXT_PUBLIC_API_BASE_URL` for all API calls
- Remove hard-coded `localhost` URLs in production
- Fall back to localhost only in development mode

### 4. Local Testing

Before deploying, verify locally:

```bash
cd frontend
npm install
npm run build
npm run start
```

The app should build and start successfully.

## Deployment Options

### Option 1: AWS Amplify Hosting

**Best for:** Next.js apps with SSR, automatic deployments, easy setup

**Quick Start:**
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Connect your Git repository
3. Set environment variables
4. Deploy

**Detailed Guide:** See [DEPLOY-AWS-AMPLIFY.md](./DEPLOY-AWS-AMPLIFY.md)

**Key Steps:**
- Connect repository (GitHub/GitLab/Bitbucket)
- Configure build settings (auto-detected for Next.js)
- Set `NEXT_PUBLIC_API_BASE_URL` environment variable
- Deploy

### Option 2: AWS Elastic Beanstalk

**Best for:** More control, custom configurations, traditional PaaS

**Quick Start:**
1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Create environment: `eb create`
4. Set environment variables: `eb setenv NEXT_PUBLIC_API_BASE_URL=https://your-api.com`
5. Deploy: `eb deploy`

**Detailed Guide:** See [DEPLOY-AWS-EB.md](./DEPLOY-AWS-EB.md)

**Key Steps:**
- Install EB CLI
- Initialize EB in your project
- Create environment
- Set environment variables
- Deploy using `eb deploy` or via console

## Environment Variables Setup

### For AWS Amplify

1. Go to your app in Amplify Console
2. Navigate to **"Environment variables"**
3. Add:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend-api.com`
4. Save and redeploy

### For Elastic Beanstalk

**Using EB CLI:**
```bash
eb setenv NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com
```

**Using AWS Console:**
1. Go to Elastic Beanstalk Console
2. Select your environment
3. **"Configuration"** → **"Software"**
4. Add environment variables under **"Environment properties"**
5. Click **"Apply"**

## Backend API Configuration

Your backend API must be:
1. **Deployed and accessible** from the internet
2. **CORS configured** to allow requests from your frontend domain
3. **HTTPS enabled** (recommended for production)

**Example CORS configuration for FastAPI backend:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-amplify-domain.amplifyapp.com",
        "https://your-eb-domain.elasticbeanstalk.com",
        # Add your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Post-Deployment

### 1. Verify Deployment

- ✅ Application loads without errors
- ✅ API calls work (check browser console)
- ✅ Authentication works (login/register)
- ✅ All user roles function correctly

### 2. Test Functionality

- **Customer:** Browse products, request BNPL loans
- **Retailer:** Manage products
- **Lender:** View loans

### 3. Monitor

- **Amplify:** Check build logs and deployment history
- **Elastic Beanstalk:** Monitor health dashboard and logs
- **Application:** Check browser console for errors

### 4. Set Up Custom Domain

- **Amplify:** Domain management in console (automatic SSL)
- **Elastic Beanstalk:** Configure load balancer with SSL certificate

## Troubleshooting

### Build Fails

1. Check build logs in AWS Console
2. Verify Node.js version (18.x or 20.x recommended)
3. Ensure `npm run build` works locally
4. Check for missing environment variables

### API Connection Issues

1. Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
2. Check CORS configuration on backend
3. Verify backend is accessible from internet
4. Check browser console for network errors

### Application Won't Start

1. Check application logs
2. Verify `npm run start` works locally
3. Check environment variables are set
4. Verify PORT is configured correctly

## Additional Resources

- **AWS Amplify:** [DEPLOY-AWS-AMPLIFY.md](./DEPLOY-AWS-AMPLIFY.md)
- **Elastic Beanstalk:** [DEPLOY-AWS-EB.md](./DEPLOY-AWS-EB.md)
- **Environment Variables:** See `.env.example`
- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)

## Support

For issues specific to:
- **Amplify:** See [DEPLOY-AWS-AMPLIFY.md](./DEPLOY-AWS-AMPLIFY.md) troubleshooting section
- **Elastic Beanstalk:** See [DEPLOY-AWS-EB.md](./DEPLOY-AWS-EB.md) troubleshooting section
- **Local Development:** See [README.md](./README.md) or [QUICKSTART.md](../QUICKSTART.md)

