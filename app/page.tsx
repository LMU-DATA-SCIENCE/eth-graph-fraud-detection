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
        model_name: "first_Graph2Vec_RF.joblib", // Or pass a dynamic model name
      });
      setClassificationResult(response.data);
    } catch (err) {
      console.error("Error classifying wallet:", err);
      setError("Failed to classify the wallet. Please try again.");
    }
  };

  // D3 visualization logic
  useEffect(() => {
    if (!classificationResult) return;

    const svg = d3.select("#graph");
    const width = 800;
    const height = 600;

    // Clear existing graph
    svg.selectAll("*").remove();

    // Create simulation
    const simulation = d3
      .forceSimulation(classificationResult.graph.nodes)
      .force("link", d3.forceLink(classificationResult.graph.edges).id((d: any) => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Add links (edges)
    const link = svg
      .append("g")
      .selectAll("line")
      .data(classificationResult.graph.edges)
      .enter()
      .append("line")
      .attr("stroke", "#999")
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

    // Add nodes
    const node = svg
      .append("g")
      .selectAll("circle")
      .data(classificationResult.graph.nodes)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("fill", "#69b3a2")
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

    // Add node labels
    const nodeLabels = svg
      .append("g")
      .selectAll("text")
      .data(classificationResult.graph.nodes)
      .enter()
      .append("text")
      .attr("font-size", "12px")
      .attr("dy", -15)
      .attr("text-anchor", "middle")
      .text((d) => d.label);

    // Simulation tick
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
          </div>
        )}
      </div>

      <svg id="graph" width="800" height="600" />
    </main>
  );
}
