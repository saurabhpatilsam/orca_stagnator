/**
 * API service for backtest-related endpoints.
 * Handles tick data, trade markers, and backtest execution.
 */

import { apiClient } from '../config/api';

const backtestApiService = {
  /**
   * Fetch tick data for charting.
   * @param {Object} params - Request parameters
   * @param {string} params.instrument - Instrument symbol (NQ, ES, MNQ, MES)
   * @param {string} params.dateFrom - Start date (ISO string or Date)
   * @param {string} params.dateTo - End date (ISO string or Date)
   * @param {string} params.resolution - Tick resolution (1T, 10T, 100T, 1000T)
   * @returns {Promise<Object>} Response with bars and metadata
   */
  async getTickData(params) {
    try {
      // Convert Date objects to ISO strings if needed
      const dateFrom = params.dateFrom instanceof Date 
        ? params.dateFrom.toISOString() 
        : params.dateFrom;
      const dateTo = params.dateTo instanceof Date 
        ? params.dateTo.toISOString() 
        : params.dateTo;

      const response = await apiClient.get('/api/v1/backtest/tick-data', {
        params: {
          instrument: params.instrument,
          date_from: dateFrom,
          date_to: dateTo,
          resolution: params.resolution
        }
      });

      return response;
    } catch (error) {
      console.error('Error fetching tick data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tick data');
    }
  },

  /**
   * Fetch trade markers for visualization.
   * @param {Object} options - Request parameters
   * @param {string} [options.backtestRunId] - Specific backtest run ID
   * @param {string} [options.contract] - Contract/instrument (required if backtestRunId not provided)
   * @param {string} [options.dateFrom] - Start date (required if backtestRunId not provided)
   * @param {string} [options.dateTo] - End date (required if backtestRunId not provided)
   * @param {string} [options.positionFilter] - Filter by position type (Long/Short/All)
   * @param {string} [options.resultFilter] - Filter by result (Filled/NotFilled/All)
   * @returns {Promise<Object>} Response with trade markers
   */
  async getTradeMarkers(options = {}) {
    try {
      // Validate parameters - either backtestRunId OR (contract + dateFrom + dateTo) required
      const { backtestRunId, contract, dateFrom, dateTo, positionFilter, resultFilter } = options;
      
      if (!backtestRunId && (!contract || !dateFrom || !dateTo)) {
        throw new Error(
          'Either backtestRunId or all of (contract, dateFrom, dateTo) must be provided'
        );
      }

      // Build query params
      const params = {};
      
      if (backtestRunId) {
        params.backtest_run_id = backtestRunId;
      } else {
        params.contract = contract;
        // Convert Date objects to ISO strings if needed
        params.date_from = dateFrom instanceof Date ? dateFrom.toISOString() : dateFrom;
        params.date_to = dateTo instanceof Date ? dateTo.toISOString() : dateTo;
      }
      
      // Add optional filters
      if (positionFilter && positionFilter !== 'All') {
        params.position_filter = positionFilter;
      }
      if (resultFilter && resultFilter !== 'All') {
        params.result_filter = resultFilter;
      }

      const response = await apiClient.get('/api/v1/backtest/trade-markers', {
        params
      });

      return response;
    } catch (error) {
      console.error('Error fetching trade markers:', error);
      if (error.response?.status === 404) {
        throw new Error('No backtest results found for the specified criteria');
      }
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch trade markers');
    }
  },

  /**
   * Run a backtest with the specified configuration.
   * @param {Object} config - Backtest configuration
   * @param {string} config.run_id - Unique run ID
   * @param {string} config.contract - Contract/Instrument
   * @param {string} config.strategy_name - Combined strategy name
   * @param {string} config.exit_strategy_key - Exit strategy key
   * @param {string} config.point_key - Point strategy key
   * @param {string} config.team_way - Team way (BreakThrough or Reverse)
   * @param {string} config.date_from - Start date ISO string
   * @param {string} config.date_to - End date ISO string
   * @param {Object} [config.metadata] - Optional metadata
   * @returns {Promise<Object>} Backtest results
   */
  async runBacktest(config) {
    try {
      // Create FormData for multipart/form-data submission
      const formData = new FormData();
      
      // Default values for testing
      formData.append('accountName', 'APEX_136189');
      formData.append('mode', 'Ticks');
      formData.append('contract', config.contract || 'NQ');
      formData.append('maxMode', config.team_way || 'BreakThrough');
      formData.append('point_key', config.point_key || '15_7_5');
      formData.append('exit_strategy_key', config.exit_strategy_key || '20_7');
      
      if (config.metadata?.notes) {
        formData.append('notes', config.metadata.notes);
      }
      
      // Always use date range
      formData.append('dateFrom', config.date_from);
      formData.append('dateTo', config.date_to);

      const response = await apiClient.post('/run-bot/max-backtest', formData, {
        headers: {
          // Don't set Content-Type - let browser set it with boundary for FormData
        }
      });

      // Store the run to Supabase if successful
      if (response.data && config.run_id) {
        // Call endpoint to store run info
        try {
          await apiClient.post('/run-bot/backtest/store-run', {
            run_id: config.run_id,
            contract: config.contract,
            strategy_name: config.strategy_name,
            exit_strategy_key: config.exit_strategy_key,
            point_key: config.point_key,
            team_way: config.team_way,
            date_from: config.date_from,
            date_to: config.date_to,
            metadata: config.metadata,
            results: response.data
          });
        } catch (storeError) {
          console.error('Failed to store backtest run:', storeError);
        }
      }

      return {
        success: true,
        results: response.data,
        run_id: config.run_id
      };
    } catch (error) {
      console.error('Error running backtest:', error);
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || 'Invalid backtest configuration');
      }
      throw new Error(error.response?.data?.detail || 'Backtest execution failed. Please try again.');
    }
  }
};

export { backtestApiService };
