/**
 * useTradeMarkers Hook
 * Custom hook for fetching and managing trade markers with loading/error states
 */

import { useState, useEffect, useCallback } from 'react';
import { backtestApiService } from '../services/backtestApiService';
import { tradeMarkerService } from '../services/tradeMarkerService';

/**
 * Hook for managing trade markers
 * @param {Object} options - Hook options
 * @param {string} [options.backtestRunId] - Backtest run ID
 * @param {string} [options.contract] - Contract/instrument
 * @param {Date|string} [options.dateFrom] - Start date
 * @param {Date|string} [options.dateTo] - End date
 * @param {string} [options.positionFilter] - Position filter
 * @param {string} [options.resultFilter] - Result filter
 * @param {boolean} [options.autoFetch=false] - Auto-fetch on mount
 * @returns {Object} Hook state and methods
 */
const useTradeMarkers = (options = {}) => {
  const {
    backtestRunId,
    contract,
    dateFrom,
    dateTo,
    positionFilter,
    resultFilter,
    autoFetch = false
  } = options;

  const [markers, setMarkers] = useState([]);
  const [rawData, setRawData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fetchedAt, setFetchedAt] = useState(null);

  /**
   * Fetch trade markers from API
   */
  const fetchMarkers = useCallback(async (customOptions = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Merge custom options with hook options
      const fetchOptions = {
        backtestRunId: customOptions.backtestRunId || backtestRunId,
        contract: customOptions.contract || contract,
        dateFrom: customOptions.dateFrom || dateFrom,
        dateTo: customOptions.dateTo || dateTo,
        positionFilter: customOptions.positionFilter || positionFilter,
        resultFilter: customOptions.resultFilter || resultFilter
      };

      // Fetch raw data from API
      const response = await backtestApiService.getTradeMarkers(fetchOptions);
      setRawData(response);

      // Transform the response into marker format
      const transformed = tradeMarkerService.transformTradesResponse(response);
      setMarkers(transformed.allMarkers);
      setFetchedAt(new Date());

      return {
        success: true,
        markers: transformed.allMarkers,
        longMarkers: transformed.longMarkers,
        shortMarkers: transformed.shortMarkers
      };
    } catch (err) {
      console.error('Error fetching trade markers:', err);
      setError(err.message || 'Failed to fetch trade markers');
      setMarkers([]);
      setRawData(null);
      
      return {
        success: false,
        error: err.message
      };
    } finally {
      setLoading(false);
    }
  }, [backtestRunId, contract, dateFrom, dateTo, positionFilter, resultFilter]);

  /**
   * Refetch markers (alias for fetchMarkers)
   */
  const refetch = useCallback((customOptions = {}) => {
    return fetchMarkers(customOptions);
  }, [fetchMarkers]);

  /**
   * Clear markers and reset state
   */
  const clearMarkers = useCallback(() => {
    setMarkers([]);
    setRawData(null);
    setError(null);
    setFetchedAt(null);
  }, []);

  /**
   * Update markers (for local filtering/sorting)
   */
  const updateMarkers = useCallback((newMarkers) => {
    if (Array.isArray(newMarkers)) {
      setMarkers(newMarkers);
    }
  }, []);

  /**
   * Get markers by position type
   */
  const getMarkersByPosition = useCallback((positionType) => {
    if (!markers || markers.length === 0) return [];
    if (positionType === 'All') return markers;
    return markers.filter(m => m.position_type === positionType);
  }, [markers]);

  /**
   * Get markers by result
   */
  const getMarkersByResult = useCallback((resultType) => {
    if (!markers || markers.length === 0) return [];
    if (resultType === 'All') return markers;
    return markers.filter(m => m.result === resultType);
  }, [markers]);

  // Auto-fetch on mount if enabled
  useEffect(() => {
    if (autoFetch && (backtestRunId || (contract && dateFrom && dateTo))) {
      fetchMarkers();
    }
  }, [autoFetch, backtestRunId, contract, dateFrom, dateTo, fetchMarkers]);

  return {
    // State
    markers,
    rawData,
    loading,
    error,
    fetchedAt,
    hasMarkers: markers.length > 0,
    
    // Methods
    fetchMarkers,
    refetch,
    clearMarkers,
    updateMarkers,
    getMarkersByPosition,
    getMarkersByResult
  };
};

export default useTradeMarkers;
