# Missing APIs Audit Report

This document lists all APIs that are expected by the frontend but are missing or have path mismatches in the backend.

## 🔴 Missing Endpoints

### 1. **GET /products/{product_id}**
- **Frontend**: `frontend/lib/api/products.ts` - `getProduct(id)`
- **Frontend Usage**: `frontend/app/customer/checkout/[productId]/page.tsx`
- **Status**: ❌ **MISSING**
- **Expected Response**: `Product` object
- **Required**: Yes - Used in checkout flow

### 2. **GET /lender/stats**
- **Frontend**: `frontend/lib/api/lender.ts` - `getStats()`
- **Frontend Usage**: `frontend/app/lender/dashboard/page.tsx`
- **Status**: ❌ **MISSING**
- **Expected Response**: 
  ```typescript
  {
    active_loans_count: number;
    total_principal_outstanding: number;
    total_interest_earned: number;
  }
  ```
- **Required**: Yes - Used in lender dashboard

### 3. **GET /retailer/stats**
- **Frontend**: `frontend/lib/api/retailer.ts` - `getStats()`
- **Frontend Usage**: `frontend/app/retailer/dashboard/page.tsx`
- **Status**: ❌ **MISSING**
- **Expected Response**: 
  ```typescript
  {
    total_bnpl_sales: number;
    bnpl_transactions_30d: number;
    best_selling_products: Array<{
      product_id: string;
      product_name: string;
      sales_count: number;
    }>;
  }
  ```
- **Required**: Yes - Used in retailer dashboard

## ⚠️ Path Mismatches

### 4. **GET /lender/loans**
- **Frontend Expects**: `/lender/loans`
- **Backend Has**: `/loans/lender/loans`
- **Frontend**: `frontend/lib/api/lender.ts` - `getLoans(status?)`
- **Backend**: `backend/app/routers/loans.py` - `get_lender_loans()`
- **Status**: ⚠️ **PATH MISMATCH**
- **Fix Options**:
  1. Add new router at `/lender/loans` in backend
  2. Update frontend to use `/loans/lender/loans`

### 5. **GET /retailer/products**
- **Frontend Expects**: `/retailer/products`
- **Backend Has**: `/products/retailer/products`
- **Frontend**: `frontend/lib/api/retailer.ts` - `getProducts()`
- **Backend**: `backend/app/routers/products.py` - `get_retailer_products()`
- **Status**: ⚠️ **PATH MISMATCH**
- **Fix Options**:
  1. Add new router at `/retailer/products` in backend
  2. Update frontend to use `/products/retailer/products`

### 6. **POST /retailer/products**
- **Frontend Expects**: `/retailer/products`
- **Backend Has**: `/products/retailer/products`
- **Frontend**: `frontend/lib/api/retailer.ts` - `createProduct()`
- **Backend**: `backend/app/routers/products.py` - `create_product()`
- **Status**: ⚠️ **PATH MISMATCH**
- **Fix Options**:
  1. Add new router at `/retailer/products` in backend
  2. Update frontend to use `/products/retailer/products`

### 7. **PUT /retailer/products/{id}**
- **Frontend Expects**: `/retailer/products/{id}`
- **Backend Has**: `/products/retailer/products/{id}`
- **Frontend**: `frontend/lib/api/retailer.ts` - `updateProduct(id, data)`
- **Backend**: `backend/app/routers/products.py` - `update_product()`
- **Status**: ⚠️ **PATH MISMATCH**
- **Fix Options**:
  1. Add new router at `/retailer/products/{id}` in backend
  2. Update frontend to use `/products/retailer/products/{id}`

### 8. **DELETE /retailer/products/{id}**
- **Frontend Expects**: `/retailer/products/{id}`
- **Backend Has**: `/products/retailer/products/{id}`
- **Frontend**: `frontend/lib/api/retailer.ts` - `deleteProduct(id)`
- **Backend**: `backend/app/routers/products.py` - `delete_product()`
- **Status**: ⚠️ **PATH MISMATCH**
- **Fix Options**:
  1. Add new router at `/retailer/products/{id}` in backend
  2. Update frontend to use `/products/retailer/products/{id}`

## ✅ Existing APIs (Working)

### Authentication
- ✅ POST /auth/register
- ✅ POST /auth/login
- ✅ GET /auth/me

### Credit Profile
- ✅ GET /credit-profile/me
- ✅ GET /credit/profile/me
- ✅ GET /credit/events/me
- ✅ GET /credit/documents/me
- ✅ POST /credit/documents
- ✅ POST /credit/recalculate/me
- ✅ GET /credit/documents/status
- ✅ GET /credit/documents/{id}/download

### Products
- ✅ GET /products (customer view)
- ✅ GET /products/retailer/products
- ✅ POST /products/retailer/products
- ✅ PUT /products/retailer/products/{id}
- ✅ DELETE /products/retailer/products/{id}

### Loans
- ✅ POST /loans/bnpl-requests
- ✅ GET /loans/me
- ✅ GET /loans/lender/loans

## 📋 Summary

**Total Missing**: 3 endpoints
**Total Path Mismatches**: 5 endpoints
**Total Issues**: 8 endpoints

## 🎯 Recommended Action Plan

1. **Create missing endpoints**:
   - GET /products/{product_id}
   - GET /lender/stats
   - GET /retailer/stats

2. **Fix path mismatches** (choose one approach):
   - **Option A**: Add new router endpoints matching frontend expectations
   - **Option B**: Update frontend API clients to match backend paths

3. **Priority Order**:
   - High: GET /products/{product_id} (blocks checkout)
   - High: GET /lender/stats (blocks lender dashboard)
   - High: GET /retailer/stats (blocks retailer dashboard)
   - Medium: Path mismatches (can work but inconsistent)

