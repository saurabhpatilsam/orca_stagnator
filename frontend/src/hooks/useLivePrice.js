import { useState, useEffect } from 'react';
import { priceWebSocket } from '../services/priceWebSocket';

export function useLivePrice(symbol) {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Ensure the connection is initiated
    priceWebSocket.connect().catch(err => {
      console.warn('Failed to start priceWebSocket:', err);
    });

    const handler = (msgSymbol, msgData) => {
      // Handle symbol matching dynamically, e.g. "MNQ" mapping to "MNQZ5" or vice versa
      if (!symbol) return;
      if (msgSymbol === symbol || msgSymbol.startsWith(symbol) || symbol.startsWith(msgSymbol)) {
        setData(msgData);
      }
    };

    const unsubscribe = priceWebSocket.addMessageHandler(handler);

    return () => {
      unsubscribe();
    };
  }, [symbol]);

  return data;
}
