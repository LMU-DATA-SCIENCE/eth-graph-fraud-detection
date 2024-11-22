"use client";  // Add this line at the top of the file

import { useState } from "react";
import Image from "next/image";
import axios from "axios";

export default function Home() {
  const [walletAddress, setWalletAddress] = useState("");
  const [classificationResult, setClassificationResult] = useState<{
    fraud_probability: number;
    visualization_html: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const classifyWallet = async () => {
    setError(null);
    setClassificationResult(null);
    try {
      const response = await axios.post("/api/py/classify", {
        wallet_address: walletAddress,
      });
      setClassificationResult(response.data);
    } catch (err) {
      console.error("Error classifying wallet:", err);
      setError("Failed to classify the wallet. Please try again.");
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <p className="text-center mb-6">
          Enter a wallet address below to classify its fraud probability and view the graph visualization.
        </p>

        <div className="mb-8">
          <input
            type="text"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            placeholder="Enter wallet address"
            className="border border-gray-300 p-2 rounded-lg w-80"
          />
          <button
            onClick={classifyWallet}
            className="ml-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          >
            Classify
          </button>
        </div>

        {error && (
          <div className="text-red-500 mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}

        {classificationResult && (
          <div className="w-full">
            <h2 className="text-2xl font-semibold mb-4">Classification Result</h2>
            <p className="mb-4">
              <strong>Fraud Probability:</strong> {classificationResult.fraud_probability.toFixed(2)}
            </p>
            <div dangerouslySetInnerHTML={{ __html: classificationResult.visualization_html }} />
          </div>
        )}
      </div>

      <div className="relative flex place-items-center">
        <Image
          className="relative dark:drop-shadow-[0_0_0.3rem_#ffffff70] dark:invert"
          src="/next.svg"
          alt="Next.js Logo"
          width={180}
          height={37}
          priority
        />
      </div>
    </main>
  );
}
