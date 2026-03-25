import React, { useState, useMemo } from 'react';

export default function CommandCenter() {
  // Currently using static logs to test the UI. You will swap this with your Supabase fetch later.
  const [logs, setLogs] = useState([
    { id: 1, timestamp: "11:24:18 PM", message: "[BTC/USD] SELL - Live Order Executed: Sold 0.001 BTC/USD. PnL: $2.50" },
    { id: 2, timestamp: "11:23:26 PM", message: "[BTC/USD] BUY - Live Order Executed: Bought 0.001 BTC/USD at $70456.20" },
    { id: 3, timestamp: "11:23:11 PM", message: "[BTC/USD] HOLD - Populating state matrix: 15/15" }
  ]);

  // --- THE QUANT HUD LOGIC ---
  const stats = useMemo(() => {
    let totalPnl = 0;
    let currentPosition = "FLAT";
    let lastTradePrice = "0.00";

    logs.forEach(log => {
      const msg = log.message;
      if (msg.includes("PnL: $")) {
        const pnlMatch = msg.match(/PnL:\s*\$([-\d.]+)/);
        if (pnlMatch) totalPnl += parseFloat(pnlMatch[1]);
      }
      if (msg.includes("BUY") && currentPosition === "FLAT") {
        currentPosition = "LONG (0.001 BTC)";
        const priceMatch = msg.match(/at\s*\$([\d.]+)/);
        if (priceMatch) lastTradePrice = priceMatch[1];
      } else if (msg.includes("SELL")) {
        currentPosition = "FLAT";
      }
    });

    return { totalPnl: totalPnl.toFixed(2), currentPosition, lastTradePrice };
  }, [logs]);

  // --- THE HACKER COLORS LOGIC ---
  const getLogColor = (message) => {
    if (message.includes("BUY")) return "text-green-400 font-bold";
    if (message.includes("SELL")) return "text-red-400 font-bold";
    if (message.includes("HOLD") && message.includes("Agent Action: 1")) return "text-green-200/50";
    if (message.includes("HOLD") && message.includes("Agent Action: 2")) return "text-red-200/50";
    return "text-blue-300";
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 p-8 font-mono selection:bg-blue-500/30">
      
      {/* HEADER */}
      <div className="max-w-5xl mx-auto mb-8">
        <h1 className="text-3xl font-black text-white tracking-widest flex items-center gap-3">
          <span>🚀</span> ZAMJAM COMMAND CENTER
        </h1>
        <p className="text-slate-500 mt-2 text-sm uppercase tracking-widest">Autonomous Quantitative Fund • Vercel Edge Node</p>
      </div>

      {/* THE QUANT HUD */}
      <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 shadow-xl">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Session PnL</p>
          <p className={`text-3xl font-light ${stats.totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${stats.totalPnl}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 shadow-xl">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Active Position</p>
          <p className={`text-3xl font-light ${stats.currentPosition === 'FLAT' ? 'text-slate-500' : 'text-blue-400'}`}>
            {stats.currentPosition}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 shadow-xl">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wider">Last Entry Price</p>
          <p className="text-3xl font-light text-white">${stats.lastTradePrice}</p>
        </div>
      </div>

      {/* THE LIVE MATRIX TERMINAL */}
      <div className="max-w-5xl mx-auto bg-slate-900/50 border border-slate-800 rounded-lg p-6 shadow-2xl overflow-hidden backdrop-blur-sm">
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
          <h2 className="text-sm font-bold text-slate-400 tracking-widest uppercase">Live System Logs</h2>
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-xs text-green-500 tracking-widest">DATA STREAM ACTIVE</span>
          </div>
        </div>

        <div className="h-[500px] overflow-y-auto space-y-2 pr-4 custom-scrollbar">
          {logs.map((log) => (
            <div key={log.id} className="flex flex-col sm:flex-row gap-2 sm:gap-4 py-1 hover:bg-slate-800/50 rounded px-2 transition-colors">
              <span className="text-slate-500 shrink-0 opacity-70">[{log.timestamp}]</span>
              <span className={`${getLogColor(log.message)} break-words`}>
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}