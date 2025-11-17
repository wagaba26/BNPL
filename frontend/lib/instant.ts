import { id, i, init, InstaQLEntity } from "@instantdb/react";

// Instant DB App ID - configured via .env.local
const APP_ID = process.env.NEXT_PUBLIC_INSTANT_APP_ID || "984221bb-26fe-4a5f-b002-bde17713f1ad";

// Schema definition
export const schema = i.schema({
  entities: {
    users: i.entity({
      email: i.string(),
      username: i.string().optional(), // Optional username for login
      phone: i.string(),
      fullName: i.string(),
      passwordHash: i.string(), // In production, use proper auth
      role: i.string(), // "customer" | "retailer" | "lender"
      isActive: i.boolean(),
      isVerified: i.boolean(),
      nin: i.string().optional(), // National ID
      createdAt: i.number(),
      updatedAt: i.number(),
    }),
    creditProfiles: i.entity({
      userId: i.string(),
      score: i.number(),
      tier: i.string(), // "bronze" | "silver" | "gold" | "platinum"
      maxBnplLimit: i.number(),
      createdAt: i.number(),
      updatedAt: i.number(),
    }),
    products: i.entity({
      retailerId: i.string(),
      name: i.string(),
      description: i.string().optional(),
      price: i.number(),
      depositPercentage: i.number(), // e.g., 10.00 for 10%
      isBnplEligible: i.boolean(),
      minRequiredScore: i.number().optional(),
      category: i.string().optional(),
      sku: i.string().optional(),
      stockQuantity: i.number(),
      isActive: i.boolean(),
      imageUrl: i.string().optional(),
      createdAt: i.number(),
      updatedAt: i.number(),
    }),
    loans: i.entity({
      customerId: i.string(),
      lenderId: i.string().optional(), // Nullable until matched
      productId: i.string(),
      loanAmount: i.number(), // Amount after deposit
      depositAmount: i.number(),
      totalAmount: i.number(), // Including interest
      interestRate: i.number(),
      numberOfInstallments: i.number(),
      status: i.string(), // "pending" | "approved" | "rejected" | "active" | "completed" | "defaulted"
      creditScore: i.number().optional(),
      approvedAt: i.number().optional(),
      rejectedAt: i.number().optional(),
      rejectionReason: i.string().optional(),
      createdAt: i.number(),
      updatedAt: i.number(),
    }),
    paymentSchedules: i.entity({
      loanId: i.string(),
      installmentNumber: i.number(),
      dueDate: i.number(), // Unix timestamp
      amount: i.number(),
      status: i.string(), // "pending" | "paid" | "overdue" | "failed"
      paidAt: i.number().optional(),
      paymentReference: i.string().optional(),
      createdAt: i.number(),
      updatedAt: i.number(),
    }),
  },
  rooms: {
    marketplace: {
      presence: i.entity({}),
    },
    loans: {
      presence: i.entity({}),
    },
  },
});

// Type exports
export type User = InstaQLEntity<typeof schema, "users">;
export type CreditProfile = InstaQLEntity<typeof schema, "creditProfiles">;
export type Product = InstaQLEntity<typeof schema, "products">;
export type Loan = InstaQLEntity<typeof schema, "loans">;
export type PaymentSchedule = InstaQLEntity<typeof schema, "paymentSchedules">;

// Lazy initialization to prevent server-side execution
// Instant DB requires browser APIs (WebSocket, localStorage, etc.) that don't exist in Node.js
let dbInstance: ReturnType<typeof init> | null = null;
let marketplaceRoomInstance: ReturnType<typeof ReturnType<typeof init>["room"]> | null = null;
let loansRoomInstance: ReturnType<typeof ReturnType<typeof init>["room"]> | null = null;

function getDb() {
  // Only initialize on the client side
  if (typeof window === 'undefined') {
    throw new Error('Instant DB can only be used on the client side. Make sure to use this in a component with "use client" directive.');
  }
  
  if (!dbInstance) {
    try {
      dbInstance = init({ appId: APP_ID, schema });
    } catch (error) {
      console.error('Failed to initialize Instant DB:', error);
      throw error;
    }
  }
  
  return dbInstance;
}

// Export a getter that ensures client-side only execution
export const db = new Proxy({} as ReturnType<typeof init>, {
  get(_target, prop) {
    const db = getDb();
    return (db as any)[prop];
  }
});

// Rooms - lazy initialized
export function getMarketplaceRoom() {
  if (!marketplaceRoomInstance) {
    marketplaceRoomInstance = getDb().room("marketplace");
  }
  return marketplaceRoomInstance;
}

export function getLoansRoom() {
  if (!loansRoomInstance) {
    loansRoomInstance = getDb().room("loans");
  }
  return loansRoomInstance;
}

// For backward compatibility, export room getters
export const marketplaceRoom = new Proxy({} as ReturnType<typeof ReturnType<typeof init>["room"]>, {
  get(_target, prop) {
    const room = getMarketplaceRoom();
    return (room as any)[prop];
  }
});

export const loansRoom = new Proxy({} as ReturnType<typeof ReturnType<typeof init>["room"]>, {
  get(_target, prop) {
    const room = getLoansRoom();
    return (room as any)[prop];
  }
});

// Helper functions
// Note: These functions require client-side execution and will throw if called on the server
export function createUser(data: {
  email: string;
  phone: string;
  fullName: string;
  passwordHash: string;
  role: "customer" | "retailer" | "lender";
}) {
  const db = getDb();
  return db.transact(
    db.tx.users[id()].update({
      email: data.email,
      phone: data.phone,
      fullName: data.fullName,
      passwordHash: data.passwordHash,
      role: data.role,
      isActive: true,
      isVerified: false,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    })
  );
}

export function createCreditProfile(userId: string, score: number = 600) {
  const db = getDb();
  const tier = score >= 800 ? "platinum" : score >= 700 ? "gold" : score >= 600 ? "silver" : "bronze";
  const maxBnplLimit = score >= 800 ? 5000000 : score >= 700 ? 3000000 : score >= 600 ? 2000000 : 1000000;
  
  return db.transact(
    db.tx.creditProfiles[id()].update({
      userId,
      score,
      tier,
      maxBnplLimit,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    })
  );
}

export function createProduct(data: {
  retailerId: string;
  name: string;
  description?: string;
  price: number;
  depositPercentage: number;
  category?: string;
  stockQuantity: number;
  imageUrl?: string;
}) {
  const db = getDb();
  return db.transact(
    db.tx.products[id()].update({
      retailerId: data.retailerId,
      name: data.name,
      description: data.description,
      price: data.price,
      depositPercentage: data.depositPercentage,
      isBnplEligible: true,
      stockQuantity: data.stockQuantity,
      category: data.category,
      imageUrl: data.imageUrl,
      isActive: true,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    })
  );
}

export function createLoan(data: {
  customerId: string;
  productId: string;
  loanAmount: number;
  depositAmount: number;
  totalAmount: number;
  interestRate: number;
  numberOfInstallments: number;
  creditScore?: number;
}) {
  const db = getDb();
  return db.transact(
    db.tx.loans[id()].update({
      customerId: data.customerId,
      productId: data.productId,
      loanAmount: data.loanAmount,
      depositAmount: data.depositAmount,
      totalAmount: data.totalAmount,
      interestRate: data.interestRate,
      numberOfInstallments: data.numberOfInstallments,
      status: "pending",
      creditScore: data.creditScore,
      createdAt: Date.now(),
      updatedAt: Date.now(),
    })
  );
}

export function createPaymentSchedules(loanId: string, loanAmount: number, numberOfInstallments: number, interestRate: number) {
  const db = getDb();
  const monthlyPayment = (loanAmount * (1 + interestRate / 100)) / numberOfInstallments;
  const now = Date.now();
  const oneMonth = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds
  
  const schedules = [];
  for (let i = 1; i <= numberOfInstallments; i++) {
    schedules.push(
      db.tx.paymentSchedules[id()].update({
        loanId,
        installmentNumber: i,
        dueDate: now + (i * oneMonth),
        amount: monthlyPayment,
        status: "pending",
        createdAt: Date.now(),
        updatedAt: Date.now(),
      })
    );
  }
  
  return db.transact(schedules);
}

export function updateLoanStatus(loanId: string, status: Loan["status"], lenderId?: string, rejectionReason?: string) {
  const db = getDb();
  const updates: any = {
    status,
    updatedAt: Date.now(),
  };
  
  if (status === "approved") {
    updates.approvedAt = Date.now();
    if (lenderId) updates.lenderId = lenderId;
  } else if (status === "rejected") {
    updates.rejectedAt = Date.now();
    if (rejectionReason) updates.rejectionReason = rejectionReason;
  } else if (status === "active") {
    updates.approvedAt = Date.now();
    if (lenderId) updates.lenderId = lenderId;
  }
  
  return db.transact(db.tx.loans[loanId].update(updates));
}

export function markPaymentAsPaid(paymentScheduleId: string, paymentReference?: string) {
  const db = getDb();
  return db.transact(
    db.tx.paymentSchedules[paymentScheduleId].update({
      status: "paid",
      paidAt: Date.now(),
      paymentReference,
      updatedAt: Date.now(),
    })
  );
}

