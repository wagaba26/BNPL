# Lender Platform Separation Strategy

## Overview
This document outlines the strategy for separating the lender platform into a completely independent application while maintaining shared backend services.

## Current Architecture

### Shared Components
- **Backend API**: FastAPI application with shared endpoints
- **Database**: Shared PostgreSQL database
- **Authentication**: JWT-based authentication shared across all platforms

### Platform-Specific Components
- **Customer/Retailer Platform**: Main marketplace and shopping experience
- **Lender Platform**: Loan management and approval system

## Separation Strategy

### Option 1: Subdomain-Based Separation (Recommended)
- **Customer Platform**: `app.bnpl.com` or `marketplace.bnpl.com`
- **Lender Platform**: `lenders.bnpl.com` or `portal.bnpl.com`
- **Shared API**: `api.bnpl.com`

**Pros:**
- Clear separation of concerns
- Independent deployments
- Different branding/styling possible
- Easier to scale independently

**Cons:**
- Requires subdomain configuration
- CORS configuration needed

### Option 2: Path-Based Separation
- **Customer Platform**: `/` (root)
- **Lender Platform**: `/lender-portal/*`
- **Shared API**: `/api/v1/*`

**Pros:**
- Simpler deployment
- No subdomain configuration needed
- Shared authentication cookies

**Cons:**
- Less clear separation
- Harder to scale independently

### Option 3: Completely Separate Applications
- **Customer Platform**: Separate Next.js app
- **Lender Platform**: Separate Next.js app (or different framework)
- **Shared API**: Separate FastAPI service

**Pros:**
- Complete independence
- Can use different tech stacks
- Independent versioning

**Cons:**
- More complex deployment
- Code duplication potential
- More infrastructure to manage

## Recommended Approach: Option 1 (Subdomain)

### Implementation Steps

1. **Create Separate Next.js App for Lenders**
   ```
   lender-platform/
   ├── app/
   │   ├── layout.tsx
   │   ├── page.tsx
   │   ├── dashboard/
   │   ├── loans/
   │   └── profile/
   ├── components/
   ├── lib/
   └── package.json
   ```

2. **Shared API Configuration**
   - Both platforms connect to the same API
   - API endpoints remain unchanged
   - Authentication tokens work across platforms

3. **Deployment**
   - Deploy customer platform to one domain/subdomain
   - Deploy lender platform to separate subdomain
   - Both point to same API backend

4. **Environment Variables**
   ```env
   # Customer Platform
   NEXT_PUBLIC_API_URL=https://api.bnpl.com
   
   # Lender Platform
   NEXT_PUBLIC_API_URL=https://api.bnpl.com
   NEXT_PUBLIC_PLATFORM_TYPE=lender
   ```

## Current Implementation

The lender platform is currently integrated into the main application but structured to be easily separated:

- **Location**: `frontend/app/lender/*`
- **Layout**: `frontend/app/lender/layout.tsx` (separate layout)
- **Components**: Can be moved to separate app
- **API Calls**: Use shared API client

## Migration Path

1. **Phase 1** (Current): Integrated but separated routes
2. **Phase 2**: Create separate Next.js app structure
3. **Phase 3**: Deploy to separate subdomain
4. **Phase 4**: Remove lender routes from main app

## Benefits of Separation

1. **Security**: Lenders don't need access to customer marketplace
2. **Performance**: Smaller bundle sizes for each platform
3. **Maintenance**: Easier to update lender features independently
4. **Scaling**: Can scale platforms based on usage patterns
5. **Branding**: Different UI/UX for different user types

## Next Steps

1. Create separate `lender-platform` directory structure
2. Copy lender-specific components and pages
3. Set up separate build and deployment pipeline
4. Configure subdomain routing
5. Update documentation

