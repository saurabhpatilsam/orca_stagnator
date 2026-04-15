/**
 * Lightweight Chart Component
 * Uses TradingView's free Lightweight Charts library
 * Supports candlestick charts with trade markers
 */

import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import { backtestApiService } from '../services/backtestApiService';
import { tradeMarkerService } from '../services/tradeMarkerService';
import { priceWebSocket } from '../services/priceWebSocket';
import { apiClient } from '../config/api';

const LightweightChart = ({
  symbol = 'NQ',
  interval = '10T',
  containerId = 'lw_chart_container',
  height = 600,
  autosize = true,
  theme = 'dark',
  tradeMarkers = [],
  showMarkers = true,
  markerFilters = {},
  onMarkerClick,
  dateFrom,
  dateTo,
  enableWebSocket = true, // New prop to enable/disable WebSocket
  tradovateSymbol = 'MNQZ5' // Tradovate symbol for WebSocket
}) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const candleSeriesRef = useRef();
  const markerSeriesRef = useRef([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [mdToken, setMdToken] = useState(null);

  // Dark theme configuration
  const darkTheme = {
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a1a' },
      textColor: '#9ca3af',
    },
    grid: {
      vertLines: { color: '#2a2a2a' },
      horzLines: { color: '#2a2a2a' },
    },
    crosshair: {
      mode: CrosshairMode.Normal,
      vertLine: {
        color: '#6366f1',
        width: 1,
        style: 2,
        visible: true,
      },
      horzLine: {
        color: '#6366f1',
        width: 1,
        style: 2,
        visible: true,
      },
    },
    rightPriceScale: {
      borderColor: '#3a3a3a',
    },
    timeScale: {
      borderColor: '#3a3a3a',
      timeVisible: true,
      secondsVisible: false,
    },
  };

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      ...(theme === 'dark' ? darkTheme : {}),
      rightPriceScale: {
        borderColor: '#3a3a3a',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: '#3a3a3a',
        timeVisible: true,
        rightOffset: 12,
        barSpacing: 3,
        fixLeftEdge: false,
        lockVisibleTimeRangeOnResize: true,
      },
    });

    // Create candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#00ff00',
      downColor: '#ff0000',
      borderUpColor: '#00ff00',
      borderDownColor: '#ff0000',
      wickUpColor: '#00ff00',
      wickDownColor: '#ff0000',
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ 
          width: chartContainerRef.current.clientWidth 
        });
      }
    };

    if (autosize) {
      window.addEventListener('resize', handleResize);
    }

    return () => {
      if (autosize) {
        window.removeEventListener('resize', handleResize);
      }
      chart.remove();
    };
  }, [theme, height, autosize]);

  // Fetch and display data
  useEffect(() => {
    const fetchData = async () => {
      if (!candleSeriesRef.current) return;

      setIsLoading(true);
      setError(null);

      try {
        // Calculate date range if not provided
        const now = new Date();
        const defaultDateTo = dateTo || now.toISOString();
        const defaultDateFrom = dateFrom || new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString(); // 7 days ago

        // Fetch tick data
        const response = await backtestApiService.getTickData({
          instrument: symbol,
          dateFrom: defaultDateFrom,
          dateTo: defaultDateTo,
          resolution: interval
        });

        if (response.bars && response.bars.length > 0) {
          // Convert bars to Lightweight Charts format
          const lwBars = response.bars.map(bar => ({
            time: bar.time / 1000, // Convert to seconds
            open: bar.open,
            high: bar.high,
            low: bar.low,
            close: bar.close,
          }));

          // Sort bars by time
          lwBars.sort((a, b) => a.time - b.time);

          // Set data on candlestick series
          candleSeriesRef.current.setData(lwBars);

          // Fit content
          chartRef.current.timeScale().fitContent();
        } else {
          setError('No data available for the selected period');
        }
      } catch (err) {
        console.error('Error fetching chart data:', err);
        setError('Failed to load chart data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [symbol, interval, dateFrom, dateTo]);

  // Fetch Tradovate MD token and connect WebSocket
  useEffect(() => {
    if (!enableWebSocket) return;

    const fetchTokenAndConnect = async () => {
      try {
        await priceWebSocket.connect();
        setWsConnected(true);
        console.log('✅ WebSocket connected using Redis local price service');
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        // Fall back to polling if WebSocket fails
        setWsConnected(false);
      }
    };

    fetchTokenAndConnect();

    // Cleanup on unmount
    return () => {
      if (wsConnected) {
        priceWebSocket.disconnect();
        setWsConnected(false);
      }
    };
  }, [enableWebSocket]);

  // Subscribe to real-time candle updates
  useEffect(() => {
    if (!wsConnected || !candleSeriesRef.current) return;

    // Convert interval to minutes (10T -> 10, 1000T -> need to calculate)
    const intervalMinutes = parseInt(interval.replace('T', '')) / 100; // 10T = 10min, 1000T = 10min
    
    // Subscribe to real-time candles
    const handleCandleUpdate = (candles) => {
      if (candles && candles.length > 0) {
        // Update chart with new candles
        candles.forEach(candle => {
          candleSeriesRef.current.update(candle);
        });
        console.log(`📊 Updated ${candles.length} candles via WebSocket`);
      }
    };

    priceWebSocket.subscribeToCandles(tradovateSymbol, intervalMinutes, handleCandleUpdate);

    // Cleanup
    return () => {
      priceWebSocket.unsubscribeFromCandles(tradovateSymbol, intervalMinutes);
    };
  }, [wsConnected, tradovateSymbol, interval]);

  // Render trade markers
  useEffect(() => {
    if (!candleSeriesRef.current || !showMarkers) return;

    // Clear existing markers
    markerSeriesRef.current.forEach(series => {
      chartRef.current.removeSeries(series);
    });
    markerSeriesRef.current = [];

    if (!tradeMarkers || tradeMarkers.length === 0) return;

    // Filter markers
    let filteredMarkers = tradeMarkers;
    if (markerFilters.positionType && markerFilters.positionType !== 'All') {
      filteredMarkers = filteredMarkers.filter(m => m.position_type === markerFilters.positionType);
    }
    if (markerFilters.resultType && markerFilters.resultType !== 'All') {
      filteredMarkers = filteredMarkers.filter(m => m.result === markerFilters.resultType);
    }

    // Create markers on the candlestick series
    const markers = [];
    
    filteredMarkers.forEach(marker => {
      // Entry marker
      markers.push({
        time: marker.entryCoordinates.time / 1000, // Convert to seconds
        position: marker.position_type === 'Long' ? 'belowBar' : 'aboveBar',
        color: marker.color,
        shape: marker.position_type === 'Long' ? 'arrowUp' : 'arrowDown',
        text: `Entry: ${marker.entry_price.toFixed(2)}`,
      });

      // Exit marker  
      markers.push({
        time: marker.exitCoordinates.time / 1000,
        position: marker.position_type === 'Long' ? 'aboveBar' : 'belowBar',
        color: marker.color,
        shape: 'circle',
        text: `Exit: ${marker.exit_price.toFixed(2)} | P&L: ${marker.pnl.toFixed(2)}`,
      });
    });

    // Sort markers by time
    markers.sort((a, b) => a.time - b.time);

    // Set markers on candlestick series
    candleSeriesRef.current.setMarkers(markers);

    // Optional: Add line series for trade connections
    filteredMarkers.forEach(marker => {
      const lineSeries = chartRef.current.addLineSeries({
        color: marker.color,
        lineWidth: 1,
        lineStyle: 2, // Dashed
        crosshairMarkerVisible: false,
        priceLineVisible: false,
      });

      lineSeries.setData([
        {
          time: marker.entryCoordinates.time / 1000,
          value: marker.entry_price,
        },
        {
          time: marker.exitCoordinates.time / 1000,
          value: marker.exit_price,
        },
      ]);

      markerSeriesRef.current.push(lineSeries);

      // Handle click events
      if (onMarkerClick) {
        chartRef.current.subscribeClick((param) => {
          if (param.time >= marker.entryCoordinates.time / 1000 && 
              param.time <= marker.exitCoordinates.time / 1000) {
            onMarkerClick(marker);
          }
        });
      }
    });
  }, [tradeMarkers, showMarkers, markerFilters, onMarkerClick]);

  // Real-time updates (polling)
  useEffect(() => {
    if (!candleSeriesRef.current) return;

    const updateInterval = setInterval(async () => {
      try {
        const now = new Date();
        const from = new Date(now.getTime() - 60000); // Last minute

        const response = await backtestApiService.getTickData({
          instrument: symbol,
          dateFrom: from.toISOString(),
          dateTo: now.toISOString(),
          resolution: interval
        });

        if (response.bars && response.bars.length > 0) {
          const latestBar = response.bars[response.bars.length - 1];
          const lwBar = {
            time: latestBar.time / 1000,
            open: latestBar.open,
            high: latestBar.high,
            low: latestBar.low,
            close: latestBar.close,
          };

          // Update the latest bar
          candleSeriesRef.current.update(lwBar);
        }
      } catch (error) {
        console.error('Error updating real-time data:', error);
      }
    }, 5000); // Update every 5 seconds

    return () => clearInterval(updateInterval);
  }, [symbol, interval]);

  return (
    <div className="relative w-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400">Loading chart...</p>
          </div>
        </div>
      )}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="text-center">
            <p className="text-red-400">{error}</p>
            <button 
              onClick={() => window.location.reload()} 
              className="mt-4 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              Reload
            </button>
          </div>
        </div>
      )}
      <div 
        ref={chartContainerRef} 
        id={containerId}
        style={{ position: 'relative', width: '100%', height: `${height}px` }}
      />
    </div>
  );
};

export default LightweightChart;
