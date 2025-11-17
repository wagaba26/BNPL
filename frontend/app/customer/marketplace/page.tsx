"use client";

import { useQuery } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/products";
import Link from "next/link";
import Image from "next/image";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

export default function MarketplacePage() {
  const { data: products = [], isLoading } = useQuery({
    queryKey: ["products"],
    queryFn: () => productsApi.getProducts(),
  });

  // Filter only BNPL eligible products
  const bnplProducts = products.filter((p) => p.bnpl_eligible);

  return (
    <div className="max-w-7xl mx-auto w-full">
      <PageHeader
        title="Marketplace"
        description="Browse products available for BNPL"
      />

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i}>
              <Skeleton className="h-48 w-full rounded-t-xl" />
              <CardContent className="p-4">
                <Skeleton className="h-6 w-3/4 mb-2" />
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-2/3 mb-4" />
                <Skeleton className="h-10 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : !bnplProducts || bnplProducts.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
            <p className="text-gray-500 text-lg font-medium">
              No products available at the moment.
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Check back later for new products.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {bnplProducts.map((product) => {
            const deposit = product.deposit || product.price * 0.1; // Default 10% deposit
            const remaining = product.price - deposit;
            const installments = product.installments || 3;
            const monthlyPayment = remaining / installments;

            return (
              <Card key={product.id} hover className="flex flex-col overflow-hidden">
                {/* Product Image */}
                <div className="relative h-48 w-full bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center overflow-hidden">
                  {product.image_url ? (
                    <Image
                      src={product.image_url}
                      alt={product.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <div className="text-center p-4">
                      <svg
                        className="w-16 h-16 text-gray-400 mx-auto"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                        />
                      </svg>
                      <p className="text-xs text-gray-500 mt-2">No Image</p>
                    </div>
                  )}
                </div>

                <CardContent className="p-5 flex-1 flex flex-col">
                  {/* Product Name */}
                  <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                    {product.name}
                  </h3>

                  {/* Description */}
                  {product.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2 flex-shrink-0">
                      {product.description}
                    </p>
                  )}

                  {/* Price Section */}
                  <div className="space-y-2 mb-4 flex-shrink-0">
                    <div className="flex items-baseline justify-between">
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        Price
                      </span>
                      <span className="text-xl font-bold text-gray-900">
                        UGX {product.price.toLocaleString()}
                      </span>
                    </div>

                    {/* BNPL Breakdown */}
                    <div className="bg-gray-50 rounded-lg p-3 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">Deposit</span>
                        <span className="font-semibold text-indigo-600">
                          UGX {deposit.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600">
                          {installments}x Monthly
                        </span>
                        <span className="font-semibold text-gray-900">
                          UGX {Math.ceil(monthlyPayment).toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* Stock */}
                    {product.stock !== undefined && (
                      <div className="flex items-center justify-between text-xs pt-1">
                        <span className="text-gray-500">Stock</span>
                        <span
                          className={`font-semibold ${
                            product.stock > 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}
                        >
                          {product.stock} available
                        </span>
                      </div>
                    )}
                  </div>

                  {/* CTA Button */}
                  <Link
                    href={`/customer/checkout/${product.id}`}
                    className="mt-auto"
                  >
                    <Button
                      variant="primary"
                      className="w-full"
                      disabled={product.stock === 0}
                    >
                      Buy with BNPL
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
