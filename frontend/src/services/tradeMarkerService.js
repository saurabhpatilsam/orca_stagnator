/**
 * Service for transforming trade data into TradingView marker format.
 * Handles conversion of backend trade results into chart visualization markers.
 */

class TradeMarkerService {
  /**
   * Normalize timestamp string to ensure UTC handling.
   * Appends 'Z' if no timezone specified (treat as UTC).
   * @param {string} timeString - Timestamp string
   * @returns {string} Normalized timestamp string
   */
  normalizeTimestamp(timeString) {
    if (!timeString) return timeString;
    
    // Check if timestamp already has timezone info
    const hasTimezone = timeString.endsWith('Z') || 
                       timeString.includes('+') || 
                       timeString.includes('T') && timeString.lastIndexOf('-') > 10;
    
    if (!hasTimezone) {
      // Timestamp has no timezone - treat as UTC by appending 'Z'
      // Handle formats like '2025-01-15 10:30:00' or '2025-01-15T10:30:00'
      let normalized = timeString.trim();
      
      // Replace space with 'T' if needed for ISO format
      if (normalized.includes(' ') && !normalized.includes('T')) {
        normalized = normalized.replace(' ', 'T');
      }
      
      normalized = normalized + 'Z';
      console.log(`Normalized timestamp (assuming UTC): ${timeString} → ${normalized}`);
      return normalized;
    }
    
    return timeString;
  }

  /**
   * Parse trade timestamp string to Unix milliseconds.
   * @param {string} timeString - Timestamp string (format '%Y-%m-%d %H:%M:%S')
   * @returns {number} Unix timestamp in milliseconds
   */
  parseTradeTimestamp(timeString) {
    if (!timeString) return null;
    
    try {
      // Normalize timestamp to ensure proper UTC handling
      const normalizedTime = this.normalizeTimestamp(timeString);
      
      // Parse the timestamp string
      const date = new Date(normalizedTime);
      
      // Check if valid date
      if (isNaN(date.getTime())) {
        console.warn(`Invalid timestamp: ${timeString} (normalized: ${normalizedTime})`);
        return null;
      }
      
      return Math.floor(date.getTime());
    } catch (error) {
      console.error(`Error parsing timestamp ${timeString}:`, error);
      return null;
    }
  }

  /**
   * Transform a marker from backend response.
   * @param {Object} marker - Marker object from backend API
   * @returns {Object|null} Transformed marker or null if invalid
   */
  transformMarker(marker) {
    try {
      // Return the marker with added color based on P&L
      const pnl = parseFloat(marker.pnl || 0);
      const color = pnl >= 0 ? '#00ff00' : '#ff0000';
      
      // Normalize timestamps for proper UTC handling
      const normalizedEntryTime = this.normalizeTimestamp(marker.entry_time);
      const normalizedExitTime = this.normalizeTimestamp(marker.exit_time);
      
      return {
        color,
        entry_price: parseFloat(marker.entry_price),
        exit_price: parseFloat(marker.exit_price),
        pnl: parseFloat(marker.pnl),
        entryCoordinates: {
          time: Math.floor(new Date(marker.entry_time).getTime() / 1000), // Convert to seconds for TradingView
          price: parseFloat(marker.entry_price)
        },
        exitCoordinates: {
          time: Math.floor(new Date(marker.exit_time).getTime() / 1000), // Convert to seconds for TradingView
          price: parseFloat(marker.exit_price)
        }
      };
    } catch (error) {
      console.error('Error transforming marker:', error);
    }
  }

  /**
   * Transform a single trade object into marker data.
   * @param {Object} trade - Trade object from backend
   * @param {string} positionType - 'Long' or 'Short'
   * @returns {Object|null} Marker object or null if invalid
   */
  transformTradeToMarkers(trade, positionType) {
    try {
      // Skip not triggered trades
      if (trade.Result === 'NotTriggered') {
        return null;
      }

      // Extract prices
      const entryPrice = parseFloat(trade.Order_point || trade.entry_price || 0);
      const exitPrice = parseFloat(trade.ClosedPrice || trade.exit_price || 0);
      
      if (!entryPrice || !exitPrice) {
        console.warn('Invalid prices in trade:', trade);
        return null;
      }

      // Parse timestamps
      const entryTime = this.parseTradeTimestamp(trade.Triggered || trade.entry_time);
      const exitTime = this.parseTradeTimestamp(trade.Closed || trade.exit_time);
      
      if (!entryTime || !exitTime) {
        console.warn('Invalid timestamps in trade:', trade);
        return null;
      }

      // Calculate duration in seconds
      const durationSeconds = Math.floor((exitTime - entryTime) / 1000);
      
      // Determine color based on result
      const color = trade.Result === 'Filled' ? '#00FF00' : '#FF0000'; // Green for profit, Red for loss
      
      // Calculate P&L as a number (keep as number, don't convert to string)
      const pnl = parseFloat(trade.TradeResult || trade.pnl || 0);
      
      // Generate unique marker ID
      const markerId = `${positionType}_${entryTime}_${entryPrice}`;

      return {
        id: markerId,
        position_type: positionType,
        entryPrice,
        exitPrice,
        entry_time: entryTime,
        exit_time: exitTime,
        result: trade.Result,
        pnl: pnl, // Keep as number for formatting at render time
        duration: durationSeconds,
        color,
        marker_type: 'entry_dot',
        entryCoordinates: {
          time: entryTime / 1000, // TradingView uses seconds
          price: entryPrice
        },
        exitCoordinates: {
          time: exitTime / 1000, // TradingView uses seconds
          price: exitPrice
        }
      };
    } catch (error) {
      console.error('Error transforming trade to marker:', error);
      return null;
    }
  }

  /**
   * Transform the complete backend response into marker arrays.
   * @param {Object} tradesData - Object with structure {Long: [...], Short: [...]}
   * @returns {Object} Transformed marker groups
   */
  transformTradesResponse(tradesData) {
    try {
      const longMarkers = [];
      const shortMarkers = [];

      // Process Long trades
      if (tradesData.Long && Array.isArray(tradesData.Long)) {
        tradesData.Long.forEach(trade => {
          const marker = this.transformTradeToMarkers(trade, 'Long');
          if (marker) {
            longMarkers.push(marker);
          }
        });
      }

      // Process Short trades
      if (tradesData.Short && Array.isArray(tradesData.Short)) {
        tradesData.Short.forEach(trade => {
          const marker = this.transformTradeToMarkers(trade, 'Short');
          if (marker) {
            shortMarkers.push(marker);
          }
        });
      }

      const allMarkers = [...longMarkers, ...shortMarkers];

      return {
        longMarkers,
        shortMarkers,
        allMarkers
      };
    } catch (error) {
      console.error('Error transforming trades response:', error);
      return {
        longMarkers: [],
        shortMarkers: [],
        allMarkers: []
      };
    }
  }

  /**
   * Format duration in seconds to human-readable string.
   * @param {number} seconds - Duration in seconds
   * @returns {string} Formatted string like '2h 15m 30s'
   */
  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    const parts = [];
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);
    
    return parts.join(' ');
  }

  /**
   * Generate tooltip text for a trade marker.
   * @param {Object} marker - Trade marker object
   * @returns {string} Formatted tooltip text
   */
  formatTooltipText(marker) {
    try {
      const duration = this.formatDuration(marker.duration || 0);
      
      return `${marker.position_type} Trade\n` +
             `Entry: ${marker.entryPrice.toFixed(2)}\n` +
             `Exit: ${marker.exitPrice.toFixed(2)}\n` +
             `P&L: $${Number(marker.pnl).toFixed(2)}\n` +
             `Duration: ${duration}\n` +
             `Result: ${marker.result}`;
    } catch (error) {
      console.error('Error formatting tooltip:', error);
      return 'Trade details unavailable';
    }
  }
}

// Export singleton instance
export const tradeMarkerService = new TradeMarkerService();
