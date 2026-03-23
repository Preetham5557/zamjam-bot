import React, { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';

function App() {
  // Initialize as an empty array [] instead of null to prevent .map() errors
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Get existing logs from the DB
    const getLogs = async () => {
      try {
        const { data, error } = await supabase
          .from('logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(10);
        
        if (error) throw error;
        setLogs(data || []); // Ensure we always set an array
      } catch (err) {
        console.error("Error fetching logs:", err.message);
      } finally {
        setLoading(false);
      }
    };
    
    getLogs();

    // 2. LISTEN LIVE: Update UI the moment Python sends a new log
    const subscription = supabase
      .channel('public:logs')
      .on('postgres_changes', { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'logs' 
      }, (payload) => {
        // Functional update to ensure we have the latest state
        setLogs((current) => [payload.new, ...(current || [])].slice(0, 10));
      })
      .subscribe();

    return () => {
      supabase.removeChannel(subscription);
    };
  }, []);

  // Helper function for text colors based on sentiment
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'BULLISH': return '#4ade80'; // Green
      case 'BEARISH': return '#f87171'; // Red
      case 'SUCCESS': return '#fbbf24'; // Amber
      default: return '#38bdf8';        // Blue
    }
  };

  return (
    <div style={{ 
      backgroundColor: '#0f172a', 
      color: '#38bdf8', 
      minHeight: '100vh', 
      padding: '40px', 
      fontFamily: 'monospace' 
    }}>
      <h1>🚀 ZAMJAM COMMAND CENTER</h1>
      <p style={{ color: '#64748b' }}>Real-time Trading Intelligence</p>
      <hr style={{ borderColor: '#1e293b', marginBottom: '20px' }} />
      
      <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '8px', border: '1px solid #334155' }}>
        <h3 style={{ color: '#94a3b8', marginBottom: '15px' }}>LIVE SYSTEM LOGS</h3>
        
        {loading ? (
          <p>Connecting to Supabase...</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {/* Defensive check: only map if logs exists and has items */}
            {logs && logs.length > 0 ? (
              logs.map((log) => (
                <div key={log.id} style={{ fontSize: '14px', display: 'flex', gap: '12px' }}>
                  <span style={{ color: '#64748b', minWidth: '85px' }}>
                    [{new Date(log.created_at).toLocaleTimeString()}]
                  </span>
                  <span style={{ color: getSentimentColor(log.sentiment) }}>
                    {log.message}
                  </span>
                </div>
              ))
            ) : (
              <p style={{ color: '#64748b' }}>No logs yet. Run your Python bot to see data!</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;