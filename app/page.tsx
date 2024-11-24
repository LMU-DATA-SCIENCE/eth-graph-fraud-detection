"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import * as d3 from "d3";

export default function Home() {
  const [walletAddress, setWalletAddress] = useState("");
  const [classificationResult, setClassificationResult] = useState<{
    fraud_probability: number;
    graph: {
      nodes: Array<{ id: string; label: string }>;
      edges: Array<{
        source: string;
        target: string;
        value: number;
        timestamp: string;
      }>;
    };
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const classifyWallet = async () => {
    setError(null);
    setClassificationResult(null);
    try {
      const response = await axios.post("/api/py/classify", {
        wallet_address: walletAddress,
        model_name: "first_Graph2Vec_RF.joblib",
      });
      setClassificationResult(response.data);
    } catch (err) {
      console.error("Error classifying wallet:", err);
      setError("Failed to classify the wallet. Please try again.");
    }
  };

  useEffect(() => {
    if (!classificationResult) return;

    const svg = d3.select("#graph");
    const width = 800;
    const height = 600;

    svg.selectAll("*").remove();

    const simulation = d3
      .forceSimulation(classificationResult.graph.nodes)
      .force("link", d3.forceLink(classificationResult.graph.edges).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .selectAll("line")
      .data(classificationResult.graph.edges)
      .enter()
      .append("line")
      .attr("stroke", "#555")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2);


          // Add link labels
    const linkLabels = svg
      .append("g")
      .selectAll("text")
      .data(classificationResult.graph.edges)
      .enter()
      .append("text")
      .attr("font-size", "10px")
      .attr("fill", "#555")
      .text((d) => `Value: ${d.value}, Timestamp: ${d.timestamp}`);

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(classificationResult.graph.nodes)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("fill", "#4caf50")
      .attr("stroke", "#1b5e20")
      .attr("stroke-width", 1.5)
      .call(
        d3.drag()
          .on("start", (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("drag", (event, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d: any) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    const nodeLabels = svg
      .append("g")
      .selectAll("text")
      .data(classificationResult.graph.nodes)
      .enter()
      .append("text")
      .attr("font-size", "12px")
      .attr("fill", "#cfd8dc")
      .attr("text-anchor", "middle")
      .attr("dy", -15)
      .text((d) => d.label);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as any).x)
        .attr("y1", (d) => (d.source as any).y)
        .attr("x2", (d) => (d.target as any).x)
        .attr("y2", (d) => (d.target as any).y);


      linkLabels
        .attr("x", (d) => ((d.source as any).x + (d.target as any).x) / 2)
        .attr("y", (d) => ((d.source as any).y + (d.target as any).y) / 2);

      node.attr("cx", (d) => d.x as number).attr("cy", (d) => d.y as number);
      nodeLabels.attr("x", (d) => d.x as number).attr("y", (d) => d.y as number);
    });
  }, [classificationResult]);

  return (
    <div className="bg-gray-900 text-white min-h-screen flex flex-col items-center">
      {/* Header */}
      <header className="w-full py-4 bg-gray-800 shadow-md text-center">
        <h1 className="text-2xl font-bold">Ethereum Fraud Checker</h1>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center px-4 space-y-6">
        {/* Instruction */}
        <p className="text-center text-gray-300 text-lg">
          Enter a wallet address below to classify its fraud probability and view the graph visualization.
        </p>

        {/* Search Bar */}
        <div className="flex items-center space-x-4">
          <input
            type="text"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            placeholder="Enter wallet address"
            className="w-80 p-3 rounded-lg bg-gray-800 text-gray-300 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <button
            onClick={classifyWallet}
            className="flex items-center px-4 py-2 bg-green-500 text-white rounded-lg shadow-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400"
          >
            Check Wallet
          </button>
        </div>

        {/* Fraud Probability */}
        {classificationResult && (
          <p className="text-xl font-semibold text-green-400">
            Fraud Probability: {classificationResult.fraud_probability.toFixed(2)*100}%
          </p>
        )}

        {/* Error Message */}
        {error && <p className="text-red-500">{error}</p>}

        {/* Graph Visualization */}
        <svg id="graph" className="mt-8" width="800" height="600" />
      </main>
    </div>
  );
}
