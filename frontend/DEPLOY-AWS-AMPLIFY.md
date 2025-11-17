# Deploying to AWS Amplify Hosting

This guide explains how to deploy the BNPL platform frontend to AWS Amplify Hosting.

## Prerequisites

- AWS Account
- GitHub, GitLab, or Bitbucket repository with your code
- Node.js 18.x or higher (for local testing)

## Overview

AWS Amplify Hosting is ideal for Next.js applications with API routes. It provides:
- Automatic builds and deployments
- Server-side rendering (SSR) support
- Environment variable management
- Custom domain support
- SSL/TLS certificates

## Step-by-Step Deployment

### 1. Connect Your Repository

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Choose your Git provider (GitHub, GitLab, or Bitbucket)
4. Authorize AWS Amplify to access your repository
5. Select your repository and branch (typically `main` or `master`)

### 2. Configure Build Settings

Amplify will auto-detect Next.js, but verify these settings:

**App root directory:** `frontend` (if your frontend is in a subdirectory)

**Build settings:**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/.next
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
      - frontend/.next/cache/**/*
```

**Or if frontend is at root:**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
```

### 3. Set Environment Variables

In the Amplify console, go to **"Environment variables"** and add:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-backend-api.com` | Your backend API URL (required) |
| `NODE_ENV` | `production` | Set automatically by Amplify |
| `PORT` | `3000` | Port (Amplify handles this automatically) |

**Important:** 
- Replace `https://your-backend-api.com` with your actual backend API URL
- If your backend is also on AWS (e.g., Elastic Beanstalk, ECS, API Gateway), use that URL
- Make sure your backend allows CORS requests from your Amplify domain

### 4. Configure Next.js for Amplify

The project is already configured for Amplify:
- ✅ `package.json` has correct `build` and `start` scripts
- ✅ Environment variables are properly used
- ✅ No hard-coded localhost URLs

### 5. Deploy

1. Click **"Save and deploy"**
2. Amplify will:
   - Install dependencies
   - Run the build
   - Deploy to a preview URL
3. Wait for the build to complete (usually 3-5 minutes)

### 6. Custom Domain (Optional)

1. In Amplify console, go to **"Domain management"**
2. Click **"Add domain"**
3. Enter your domain name
4. Follow the DNS configuration instructions
5. Amplify will automatically provision SSL certificates

## Build Configuration Details

### Build Command
```bash
npm run build
```

### Start Command (for SSR)
Amplify handles this automatically for Next.js apps. The `start` script in `package.json` is:
```bash
next start -p ${PORT:-3000}
```

### Node Version
- **Recommended:** Node.js 18.x or 20.x
- Set in Amplify console under **"Build settings"** → **"Node version"**

## Environment Variables Reference

All required environment variables are listed in `.env.example`. Set these in Amplify:

- `NEXT_PUBLIC_API_BASE_URL` - **Required** - Backend API URL

Optional variables (if needed):
- `NEXT_PUBLIC_S3_BUCKET_URL` - For document uploads to S3
- `NEXT_PUBLIC_CDN_URL` - For CDN assets

## Troubleshooting

### Build Fails

1. **Check build logs** in Amplify console
2. **Verify Node version** matches your local (18.x or 20.x)
3. **Check environment variables** are set correctly
4. **Verify build command** is `npm run build`

### API Connection Issues

1. **Verify `NEXT_PUBLIC_API_BASE_URL`** is set correctly
2. **Check CORS settings** on your backend API
3. **Verify backend is accessible** from the internet
4. **Check browser console** for network errors

### SSR Issues

- Amplify automatically handles Next.js SSR
- If you have API routes, ensure they're in the `app/api` directory
- Check that your backend API is accessible from Amplify's servers

## Post-Deployment

1. **Test all functionality:**
   - User registration and login
   - API calls to backend
   - All user roles (Customer, Retailer, Lender)

2. **Monitor:**
   - Amplify console for build status
   - AWS CloudWatch for logs (if enabled)
   - Application performance

3. **Set up CI/CD:**
   - Amplify automatically deploys on every push to your main branch
   - Configure branch previews for pull requests

## Additional Resources

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [Next.js on Amplify](https://docs.aws.amazon.com/amplify/latest/userguide/deploy-nextjs-app.html)
- [Environment Variables in Amplify](https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html)

