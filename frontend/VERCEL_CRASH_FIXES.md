# Vercel Serverless Function Crash Fixes

## Summary

This document details the root causes of the "Serverless Function has crashed. 500" error on Vercel and the fixes applied.

## Root Causes Identified

### 1. **CRITICAL: Instant DB Module-Level Initialization** ⚠️
**File:** `frontend/lib/instant.ts`

**Problem:**
- Instant DB was being initialized at the module level (line 93: `export const db = init({ appId: APP_ID, schema })`)
- This initialization executes when the module is imported, even during SSR or build time
- Instant DB's `init()` function requires browser-only APIs (WebSocket, localStorage, etc.) that don't exist in Node.js serverless environments
- When Next.js tries to render pages on the server or during build, it imports this module, causing the serverless function to crash

**Fix Applied:**
- Implemented lazy initialization using a Proxy pattern
- Added `getDb()` function that only initializes Instant DB on the client side
- Added guard: `if (typeof window === 'undefined')` to prevent server-side execution
- Updated all helper functions to use `getDb()` instead of direct `db` reference
- Maintained backward compatibility by exporting `db` as a Proxy that delegates to the lazy-initialized instance

**Why This Fixes the Crash:**
- The module can now be imported safely during SSR/build without executing browser-only code
- Initialization only happens when actually used on the client side
- Clear error message if someone tries to use it on the server

### 2. **Environment Variable Validation** ⚠️
**File:** `frontend/lib/apiClient.ts`

**Problem:**
- `NEXT_PUBLIC_API_BASE_URL` was defaulting to `http://localhost:8000` in all environments
- In production on Vercel, this would try to connect to localhost, which doesn't exist
- Missing environment variable would cause silent failures or incorrect API calls

**Fix Applied:**
- Added validation to check if `NEXT_PUBLIC_API_BASE_URL` is set
- In production, throws a clear error if the variable is missing (fails fast)
- In development, allows localhost fallback
- Improved error messages to guide users to configure Vercel environment variables

**Why This Fixes the Crash:**
- Prevents runtime errors from undefined environment variables
- Fails at build time in production if misconfigured (better than runtime failure)
- Clear error messages help with debugging

## Files Changed

1. **`frontend/lib/instant.ts`**
   - Changed from module-level initialization to lazy initialization
   - Added client-side guards
   - Updated all helper functions

2. **`frontend/lib/apiClient.ts`**
   - Added environment variable validation
   - Improved error handling for missing configuration
   - Better error messages

## Required Vercel Environment Variables

Make sure these are set in your Vercel project settings:

1. **`NEXT_PUBLIC_API_BASE_URL`** (REQUIRED)
   - Set to your backend API URL (e.g., `https://your-backend.vercel.app` or `https://api.yourdomain.com`)
   - This is used by the frontend to make API calls

2. **`NEXT_PUBLIC_INSTANT_APP_ID`** (OPTIONAL - only if using Instant DB)
   - Your Instant DB App ID
   - If not set, will use a default value (not recommended for production)

## How to Configure in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following:
   - **Key:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** Your backend API URL (e.g., `https://your-backend.vercel.app`)
   - **Environment:** Production, Preview, Development (as needed)
4. Click **Save**
5. Redeploy your application

## Testing the Fixes

After deploying:

1. **Check Build Logs:**
   - The build should complete without errors
   - If `NEXT_PUBLIC_API_BASE_URL` is missing, you'll see a clear error message

2. **Test Client-Side Functionality:**
   - Navigate to pages that use Instant DB (e.g., `/customer/marketplace`)
   - These should work correctly on the client side

3. **Test API Calls:**
   - Try logging in or making API requests
   - Should connect to your backend correctly

## Additional Notes

- All pages using Instant DB must have `"use client"` directive (already present in your code)
- The lazy initialization ensures Instant DB is only used on the client side
- Server-side rendering will work correctly without trying to initialize browser-only libraries

## Prevention Tips

1. **Always check for `typeof window !== 'undefined'`** before using browser-only APIs
2. **Use lazy initialization** for libraries that require browser APIs
3. **Validate environment variables** at build time, not just runtime
4. **Test builds locally** with `NODE_ENV=production` to catch issues early

## If Issues Persist

If you still see crashes after these fixes:

1. Check Vercel function logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure your backend API is accessible from Vercel's servers
4. Check for any other module-level initializations of browser-only libraries

