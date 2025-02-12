"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import * as d3 from "d3";

interface NodeDatum extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx?: number | null;
  fy?: number | null;
}

interface EdgeDatum {
  source: string | NodeDatum;
  target: string | NodeDatum;
  value: number;
  timestamp: string;
}

export default function Home() {
  const [walletAddress, setWalletAddress] = useState("");
  const [classificationResult, setClassificationResult] = useState<{
    fraud_probability: number;
    graph: {
      nodes: NodeDatum[];
      edges: EdgeDatum[];
    };
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGraphVisible, setIsGraphVisible] = useState(false);

  const classifyWallet = async () => {
    setError(null);
    setClassificationResult(null);
    setIsGraphVisible(false);
    try {
      const response = await axios.post("/api/py/classify", {
        wallet_address: walletAddress,
        model_name: "first_Feather-G_RF.joblib",
      });
      setClassificationResult(response.data);
      setIsGraphVisible(true);
    } catch (err) {
      console.error("Error classifying wallet:", err);
      setError("Failed to classify the wallet. Please try again.");
    }
  };

  const isValidEthereumAddress = (address: string) => {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  };

  useEffect(() => {
    if (!classificationResult || !isGraphVisible) return;

    const svg = d3.select("#graph");
    const width = 800;
    const height = 600;

    svg.selectAll("*").remove();

    const nodesWithSimulationData = classificationResult.graph.nodes.map(node => ({
      ...node,
      x: Math.random() * width,
      y: Math.random() * height,
      vx: 0,
      vy: 0,
    }));

    const simulation = d3
      .forceSimulation<NodeDatum>(nodesWithSimulationData)
      .force(
        "link",
        d3
          .forceLink<NodeDatum, EdgeDatum>(classificationResult.graph.edges)
          .id((d: NodeDatum) => d.id)
          .distance(100)
      )
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
      .data(nodesWithSimulationData)
      .enter()
      .append("circle")
      .attr("r", 10)
      .attr("fill", "#4caf50")
      .attr("stroke", "#1b5e20")
      .attr("stroke-width", 1.5)
      .call(
        d3
          .drag<SVGCircleElement, NodeDatum>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    const nodeLabels = svg
      .append("g")
      .selectAll("text")
      .data(nodesWithSimulationData)
      .enter()
      .append("text")
      .attr("font-size", "12px")
      .attr("fill", "#cfd8dc")
      .attr("text-anchor", "middle")
      .attr("dy", -15)
      .text((d) => d.label);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => ((d.source as unknown) as NodeDatum).x!)
        .attr("y1", (d) => ((d.source as unknown) as NodeDatum).y!)
        .attr("x2", (d) => ((d.target as unknown) as NodeDatum).x!)
        .attr("y2", (d) => ((d.target as unknown) as NodeDatum).y!);

      linkLabels
        .attr("x", (d) =>
          ((((d.source as unknown) as NodeDatum).x! +
            ((d.target as unknown) as NodeDatum).x!) /
            2)
        )
        .attr("y", (d) =>
          ((((d.source as unknown) as NodeDatum).y! +
            ((d.target as unknown) as NodeDatum).y!) /
            2)
        );

      node.attr("cx", (d) => d.x as number).attr("cy", (d) => d.y as number);

      nodeLabels.attr("x", (d) => d.x as number).attr("y", (d) => d.y as number);
    });
  }, [classificationResult, isGraphVisible]);

  return (
    <div className="bg-gray-900 text-white min-h-screen flex flex-col">
      <header className="w-full py-4 px-6 bg-gray-800 shadow-md relative flex justify-between items-center">
        <div className="flex items-start space-x-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 256 417"
            className="w-10 h-10"
          >
            <path fill="#343434" d="M127.6 0L127.6 279.4 0 208.3z" />
            <path fill="#8C8C8C" d="M127.6 0L256 208.3 127.6 279.4z" />
            <path fill="#3C3C3B" d="M127.6 320.5L127.6 417 0 261.2z" />
            <path fill="#8C8C8C" d="M127.6 417L256 261.2 127.6 320.5z" />
            <path fill="#141414" d="M127.6 279.4L0 208.3 127.6 160.8z" />
            <path fill="#393939" d="M127.6 160.8L256 208.3 127.6 279.4z" />
          </svg>
          <div>
            <h1 className="text-3xl font-bold">EthXpose</h1>
            <p className="text-xs text-gray-400">Detect Fraudulent Ethereum wallets</p>
          </div>
        </div>
        <div className="absolute left-1/2 top-0 transform -translate-x-1/2 flex items-center h-full">
          <h2 className="text-3xl font-bold">
            Ethereum Wallet Fraud Detection
          </h2>
        </div>
      </header>

      <main className="flex-grow flex flex-col items-center justify-start px-4 space-y-6">
        {classificationResult && (
          <p className="text-xl font-semibold text-green-400 mt-6">
            Fraud Probability:{" "}
            {(classificationResult.fraud_probability * 100).toFixed(2)}%
          </p>
        )}
        {isGraphVisible && (
          <svg
            id="graph"
            className="mt-8 w-full"
            height="600"
            viewBox="0 0 800 600"
            preserveAspectRatio="xMidYMid meet"
          />
        )}
      </main>

      <footer className="w-full py-6 bg-gray-800 shadow-md text-center">
        <div className="flex flex-col items-center space-y-4 w-full max-w-4xl mx-auto px-4">
          <div className="flex items-center space-x-4 w-full max-w-4xl justify-center">
            <input
              type="text"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              placeholder="Enter wallet address"
              className="w-[calc(42ch)] py-3 px-4 rounded-lg bg-gray-800 text-gray-300 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={classifyWallet}
              disabled={!walletAddress || !isValidEthereumAddress(walletAddress)}
              className="w-[calc(13ch)] py-3 px-4 bg-green-500 text-white rounded-lg shadow-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 disabled:bg-gray-500 disabled:cursor-not-allowed"
            >
              Check Wallet
            </button>
          </div>
          <p className="text-center text-gray-300 text-sm w-full max-w-4xl">
            Enter a wallet address to classify its fraud probability and view the
            transaction graph.
          </p>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      </footer>
    </div>
  );
}