"use client";

import { db } from "@/lib/instant";
import Link from "next/link";
import Image from "next/image";

export default function MarketplacePage() {
  const { data, isLoading } = db.useQuery({
    products: {
      $: {
        where: { isActive: true },
      },
    },
  });

  const products = data?.products ? Object.values(data.products) : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
        <p className="mt-2 text-gray-600">
          Browse products available for Shift
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading products...</p>
        </div>
      ) : !products || products.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 text-lg">No products available at the moment.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product: any) => {
            const deposit = (product.price * product.depositPercentage) / 100;
            return (
              <div
                key={product.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden"
              >
                <div className="h-48 bg-gray-200 flex items-center justify-center relative">
                  {product.imageUrl ? (
                    <Image
                      src={product.imageUrl}
                      alt={product.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <span className="text-gray-400">No Image</span>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {product.name}
                  </h3>
                  {product.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {product.description}
                    </p>
                  )}
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Price:</span>
                      <span className="text-sm font-semibold text-gray-900">
                        UGX {product.price.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Deposit:</span>
                      <span className="text-sm font-semibold text-primary-600">
                        UGX {deposit.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">Stock:</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {product.stockQuantity} available
                      </span>
                    </div>
                  </div>
                  <Link
                    href={`/customer/checkout/${product.id}`}
                    className="block w-full text-center bg-primary-600 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md"
                  >
                    Buy Now, Pay Later
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
