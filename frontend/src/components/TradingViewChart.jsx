/**
 * TradingView Chart Component
 * Renders a TradingView chart with custom datafeed and trade marker support
 */

import React, { useState, useEffect, useRef } from 'react';
import { tradeMarkerService } from '../services/tradeMarkerService';

const TradingViewChart = ({
  symbol = 'NQ',
  interval = '10T',
  containerId = 'tv_chart_container',
  libraryPath = '/charting_library/',
  chartsStorageUrl,
  chartsStorageApiVersion = '1.1',
  clientId,
  userId,
  fullscreen = false,
  autosize = true,
  studiesOverrides,
  theme = 'dark',
  onChartReady,
  tradeMarkers = [],
  showMarkers = true,
  markerFilters = {},
  height = 600
}) => {
  const widgetRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [renderedShapes, setRenderedShapes] = useState([]);

  // Initialize TradingView widget
  useEffect(() => {
    const initWidget = () => {
      // Check if TradingView library is available
      if (!window.TradingView) {
        // Dynamically load the script
        const script = document.createElement('script');
        script.src = `${libraryPath}charting_library.js`;
        script.onload = () => {
          createWidget();
        };
        script.onerror = () => {
          console.error('Failed to load TradingView library');
          setIsLoading(false);
        };
        document.head.appendChild(script);
      } else {
        createWidget();
      }
    };

    const createWidget = () => {
      try {
        const tradingViewDatafeed = require('../services/tradingViewDatafeed').default;
        
        const widget = new window.TradingView.widget({
          symbol,
          interval,
          container: containerId,
          datafeed: tradingViewDatafeed,
          library_path: libraryPath,
          locale: 'en',
          disabled_features: [],
          enabled_features: ['study_templates', 'tick_resolution', 'seconds_resolution'],
          charts_storage_url: chartsStorageUrl,
          charts_storage_api_version: chartsStorageApiVersion,
          client_id: clientId,
          user_id: userId,
          fullscreen,
          autosize,
          studies_overrides: studiesOverrides,
          theme,
          overrides: {
            // Dark theme colors
            'paneProperties.background': '#1a1a1a',
            'paneProperties.vertGridProperties.color': '#2a2a2a',
            'paneProperties.horzGridProperties.color': '#2a2a2a',
            'scalesProperties.lineColor': '#3a3a3a',
            'scalesProperties.textColor': '#9ca3af',
            'mainSeriesProperties.candleStyle.upColor': '#00ff00',
            'mainSeriesProperties.candleStyle.downColor': '#ff0000',
            'mainSeriesProperties.candleStyle.borderUpColor': '#00ff00',
            'mainSeriesProperties.candleStyle.borderDownColor': '#ff0000',
            'mainSeriesProperties.candleStyle.wickUpColor': '#00ff00',
            'mainSeriesProperties.candleStyle.wickDownColor': '#ff0000',
          },
          loading_screen: {
            backgroundColor: '#1a1a1a',
            foregroundColor: '#6366f1'
          },
          custom_css_url: undefined
        });

        // Register onChartReady callback immediately after construction
        widget.onChartReady(() => {
          setIsLoading(false);
          if (onChartReady) {
            onChartReady(widget);
          }
        });

        widgetRef.current = widget;
      } catch (error) {
        console.error('Error initializing TradingView widget:', error);
        setIsLoading(false);
      }
    };

    initWidget();

    // Cleanup
    return () => {
      if (widgetRef.current) {
        removeAllMarkers();
        widgetRef.current.remove();
        widgetRef.current = null;
      }
    };
  }, [symbol, interval]);

  // Render trade markers
  const renderTradeMarkers = (markers) => {
    // Clear existing markers
    removeAllMarkers();

    if (!widgetRef.current || !markers || markers.length === 0) {
      return;
    }

    // Filter markers based on filters
    let filteredMarkers = markers;
    if (markerFilters.positionType && markerFilters.positionType !== 'All') {
      filteredMarkers = filteredMarkers.filter(m => m.position_type === markerFilters.positionType);
    }
    if (markerFilters.resultType && markerFilters.resultType !== 'All') {
      filteredMarkers = filteredMarkers.filter(m => m.result === markerFilters.resultType);
    }

    const newShapes = [];

    // Get the active chart
    widgetRef.current.onChartReady(() => {
      const chart = widgetRef.current.activeChart();
      
      filteredMarkers.forEach(marker => {
        try {
          // Create entry dot
          const entryShapeId = chart.createShape({
            time: marker.entryCoordinates.time,
            price: marker.entryCoordinates.price
          }, {
            shape: marker.position_type === 'Long' ? 'long_position' : 'short_position',
            lock: true,
            disableSelection: false,
            disableSave: true,
            text: tradeMarkerService.formatTooltipText(marker),
            overrides: {
              color: marker.color,
              transparency: 20
            }
          });
          
          if (entryShapeId) {
            newShapes.push(entryShapeId);
          }

          // Create exit line
          const lineShapeId = chart.createMultipointShape([
            {
              time: marker.entryCoordinates.time,
              price: marker.entryCoordinates.price
            },
            {
              time: marker.exitCoordinates.time,
              price: marker.exitCoordinates.price
            }
          ], {
            shape: 'trend_line',
            lock: true,
            disableSelection: false,
            disableSave: true,
            text: `${marker.result}: ${marker.pnl.toFixed(2)}`,
            overrides: {
              linecolor: marker.color,
              linewidth: 2,
              linestyle: 0,
              extendLeft: false,
              extendRight: false,
              showLabel: true
            }
          });
          
          if (lineShapeId) {
            newShapes.push(lineShapeId);
          }
        } catch (error) {
          console.error('Error creating marker shape:', error);
        }
      });

      setRenderedShapes(newShapes);
    });
  };

  // Remove all markers
  const removeAllMarkers = () => {
    if (!widgetRef.current || renderedShapes.length === 0) {
      return;
    }

    widgetRef.current.onChartReady(() => {
      const chart = widgetRef.current.activeChart();
      
      renderedShapes.forEach(shapeId => {
        try {
          chart.removeEntity(shapeId);
        } catch (error) {
          console.error('Error removing shape:', error);
        }
      });

      setRenderedShapes([]);
    });
  };

  // Update markers when data changes
  useEffect(() => {
    if (showMarkers && tradeMarkers) {
      renderTradeMarkers(tradeMarkers);
    } else {
      removeAllMarkers();
    }
  }, [tradeMarkers, showMarkers, markerFilters]);

  return (
    <div className="relative w-full h-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400">Loading TradingView Chart...</p>
          </div>
        </div>
      )}
      <div 
        id={containerId} 
        className="w-full"
        style={{ height: `${height}px` }}
      />
    </div>
  );
};

export default TradingViewChart;
