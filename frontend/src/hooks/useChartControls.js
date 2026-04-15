/**
 * useChartControls Hook
 * Manages chart control state and operations
 */

import { useState, useCallback, useMemo } from 'react';
import toast from 'react-hot-toast';
import {
  getVisibleMarkerTimeRange,
  calculateChartZoomPadding,
  exportChartAsImage,
  formatChartExportFilename,
  validateChartWidget,
  filterMarkers,
  calculateTradeStats
} from '../utils/chartControlHelpers';
import { TOAST_MESSAGES } from '../constants/chartControlConstants';

const useChartControls = (tradeMarkers = [], symbol = '', chartWidgetRef = null) => {
  const [showMarkers, setShowMarkers] = useState(true);
  const [positionFilter, setPositionFilter] = useState('All');
  const [resultFilter, setResultFilter] = useState('All');
  const [isExporting, setIsExporting] = useState(false);

  // Filtered markers based on current filters
  const filteredMarkers = useMemo(() => {
    return filterMarkers(tradeMarkers, {
      positionType: positionFilter,
      resultType: resultFilter
    });
  }, [tradeMarkers, positionFilter, resultFilter]);

  // Trade statistics
  const tradeStats = useMemo(() => {
    return calculateTradeStats(filteredMarkers);
  }, [filteredMarkers]);

  /**
   * Toggle marker visibility
   */
  const toggleMarkers = useCallback(() => {
    setShowMarkers(prev => !prev);
  }, []);

  /**
   * Zoom chart to visible trade markers
   */
  const zoomToTrades = useCallback(() => {
    if (!chartWidgetRef) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    if (!validateChartWidget(chartWidgetRef)) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    const timeRange = getVisibleMarkerTimeRange(tradeMarkers, {
      positionType: positionFilter,
      resultType: resultFilter
    });

    if (!timeRange.hasMarkers || !timeRange.from || !timeRange.to) {
      toast.error(TOAST_MESSAGES.NO_MARKERS);
      return;
    }

    try {
      chartWidgetRef.activeChart().setVisibleRange(
        calculateChartZoomPadding(timeRange.from, timeRange.to),
        { percentRightMargin: 10 }
      );
      toast.success(TOAST_MESSAGES.ZOOM_APPLIED);
    } catch (error) {
      console.error('Zoom error:', error);
      toast.error('Failed to zoom to trades');
    }
  }, [chartWidgetRef, tradeMarkers, positionFilter, resultFilter]);

  /**
   * Reset chart zoom to default view
   */
  const resetZoom = useCallback(() => {
    if (!chartWidgetRef) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    if (!validateChartWidget(chartWidgetRef)) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    try {
      chartWidgetRef.activeChart().resetData();
      toast.success(TOAST_MESSAGES.ZOOM_RESET);
    } catch (error) {
      console.error('Reset zoom error:', error);
      toast.error('Failed to reset zoom');
    }
  }, [chartWidgetRef]);

  /**
   * Export chart as image
   */
  const exportChart = useCallback(async () => {
    if (!chartWidgetRef) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    if (!validateChartWidget(chartWidgetRef)) {
      toast.error(TOAST_MESSAGES.CHART_NOT_READY);
      return;
    }

    setIsExporting(true);

    try {
      const filename = formatChartExportFilename(symbol);
      await exportChartAsImage(chartWidgetRef, filename);
      toast.success(TOAST_MESSAGES.EXPORT_SUCCESS);
    } catch (error) {
      console.error('Export error:', error);
      toast.error(TOAST_MESSAGES.EXPORT_ERROR);
    } finally {
      setIsExporting(false);
    }
  }, [chartWidgetRef, symbol]);

  return {
    // State
    showMarkers,
    positionFilter,
    resultFilter,
    isExporting,
    filteredMarkers,
    tradeStats,
    
    // Actions
    toggleMarkers,
    setPositionFilter,
    setResultFilter,
    zoomToTrades,
    resetZoom,
    exportChart
  };
};

export default useChartControls;
