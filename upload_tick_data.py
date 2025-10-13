"""
TXT Tick Data Upload Pipeline
==============================
Automatically uploads tick-by-tick data from TXT files to Supabase with:
- Auto-detection of date range
- Instrument selection (ES or NQ)
- Duplicate prevention
- Batch processing for large files
- Progress tracking

Author: Automated Trading System
Date: 2025-10-11
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from loguru import logger
from supabase import create_client, Client
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class UploadConfig:
    """Configuration for TXT file upload with dual Supabase support"""
    
    # Dual Supabase configuration
    DEFAULT_TARGET = os.getenv("DEFAULT_SUPABASE", "selfhosted")
    
    # Self-hosted Supabase
    SELFHOSTED_URL = os.getenv("SELFHOSTED_SUPABASE_URL")
    SELFHOSTED_KEY = os.getenv("SELFHOSTED_SUPABASE_KEY")
    SELFHOSTED_SCHEMA = os.getenv("SELFHOSTED_SCHEMA", "orca")
    
    # Cloud Supabase
    CLOUD_URL = os.getenv("CLOUD_SUPABASE_URL")
    CLOUD_KEY = os.getenv("CLOUD_SUPABASE_KEY")
    CLOUD_SCHEMA = os.getenv("CLOUD_SCHEMA", "public")
    
    # Upload settings
    BATCH_SIZE = 10000  # Number of rows per batch (increased for faster uploads)
    
    # Supported instruments
    INSTRUMENTS = {
        'ES': 'ticks_es',
        'NQ': 'ticks_nq'
    }
    
    @staticmethod
    def get_supabase_config(target: str = None):
        """Get Supabase configuration for specified target"""
        target = target or UploadConfig.DEFAULT_TARGET
        
        if target == "selfhosted":
            return {
                'url': UploadConfig.SELFHOSTED_URL,
                'key': UploadConfig.SELFHOSTED_KEY,
                'schema': UploadConfig.SELFHOSTED_SCHEMA
            }
        else:  # cloud
            return {
                'url': UploadConfig.CLOUD_URL,
                'key': UploadConfig.CLOUD_KEY,
                'schema': UploadConfig.CLOUD_SCHEMA
            }


# ============================================================================
# FILE ANALYZER
# ============================================================================

class CSVAnalyzer:
    """Analyzes TXT/CSV files to extract metadata"""
    
    @staticmethod
    def detect_date_range(csv_file: str, has_header: bool = True, separator: str = ',') -> Optional[Tuple[datetime, datetime]]:
        """
        Detect the start and end datetime from TXT file.
        
        Args:
            csv_file: Path to TXT file
            has_header: Whether file has header row
            separator: Field separator (comma, semicolon, etc.)
        
        Returns:
            Tuple of (start_datetime, end_datetime) or None
        """
        logger.info(f"Analyzing file: {csv_file}")
        
        try:
            # Detect separator if not specified
            if separator == ',':
                with open(csv_file, 'r') as f:
                    first_line = f.readline()
                    if ';' in first_line and ',' not in first_line:
                        separator = ';'
                        logger.info(f"Detected separator: semicolon (;)")
            
            # Read file with appropriate settings
            if has_header:
                df_first = pd.read_csv(csv_file, sep=separator, nrows=1)
                
                # Get total rows
                with open(csv_file, 'r') as f:
                    total_rows = sum(1 for _ in f) - 1  # Subtract header
                
                # Read last row
                df_last = pd.read_csv(csv_file, sep=separator, skiprows=range(1, total_rows))
                
                # Detect timestamp column
                timestamp_col = None
                for col in ['ts', 'timestamp', 'time', 'datetime']:
                    if col in df_first.columns:
                        timestamp_col = col
                        break
                
                if not timestamp_col:
                    logger.error("Could not find timestamp column in file")
                    return None
                
                # Parse timestamps
                start_time = pd.to_datetime(df_first[timestamp_col].iloc[0])
                end_time = pd.to_datetime(df_last[timestamp_col].iloc[0])
            else:
                # File without header - assume first column is timestamp
                df_first = pd.read_csv(csv_file, sep=separator, header=None, nrows=1)
                
                # Get total rows
                with open(csv_file, 'r') as f:
                    total_rows = sum(1 for _ in f)
                
                # Read last row
                df_last = pd.read_csv(csv_file, sep=separator, header=None, skiprows=total_rows-1)
                
                # Parse timestamp from first column
                # Format: YYYYMMDD HHMMSS microseconds
                start_time = CSVAnalyzer._parse_timestamp(df_first.iloc[0, 0])
                end_time = CSVAnalyzer._parse_timestamp(df_last.iloc[0, 0])
            
            logger.success(f"✅ Date range detected:")
            logger.info(f"   Start: {start_time}")
            logger.info(f"   End:   {end_time}")
            logger.info(f"   Total rows: {total_rows:,}")
            
            return (start_time, end_time)
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            logger.error(f"Details: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> datetime:
        """
        Parse timestamp from various formats.
        
        Args:
            timestamp_str: Timestamp string
        
        Returns:
            datetime object
        """
        # Try format: YYYYMMDD HHMMSS microseconds
        if ' ' in str(timestamp_str):
            parts = str(timestamp_str).split()
            if len(parts) >= 2:
                date_part = parts[0]  # YYYYMMDD
                time_part = parts[1]  # HHMMSS
                
                # Parse date
                year = int(date_part[0:4])
                month = int(date_part[4:6])
                day = int(date_part[6:8])
                
                # Parse time
                hour = int(time_part[0:2])
                minute = int(time_part[2:4])
                second = int(time_part[4:6])
                
                return datetime(year, month, day, hour, minute, second)
        
        # Fallback to pandas
        return pd.to_datetime(timestamp_str)
    
    @staticmethod
    def get_csv_info(csv_file: str) -> Dict:
        """
        Get comprehensive information about TXT file.
        
        Args:
            csv_file: Path to TXT file
        
        Returns:
            Dict with file information
        """
        try:
            # Get file size
            file_size = os.path.getsize(csv_file)
            file_size_mb = file_size / (1024 * 1024)
            
            # Read first few rows to check structure
            df_sample = pd.read_csv(csv_file, nrows=5)
            
            # Count total rows
            with open(csv_file, 'r') as f:
                total_rows = sum(1 for _ in f) - 1
            
            info = {
                'file_path': csv_file,
                'file_size_mb': round(file_size_mb, 2),
                'total_rows': total_rows,
                'columns': list(df_sample.columns),
                'sample_data': df_sample.to_dict('records')
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {}


# ============================================================================
# DUPLICATE DETECTOR
# ============================================================================

class DuplicateDetector:
    """Detects and prevents duplicate tick data"""
    
    def __init__(self, supabase: Client, table_name: str):
        """
        Initialize duplicate detector.
        
        Args:
            supabase: Supabase client
            table_name: Name of the table (ticks_es or ticks_nq)
        """
        self.supabase = supabase
        self.table_name = table_name
        self.existing_rows = set()  # Store complete row hashes
    
    def load_existing_timestamps(self, start_date: datetime, end_date: datetime):
        """
        Load existing tick data from Supabase for the date range.
        Creates hashes of complete rows (ts, bid, ask, last, vol) for exact duplicate detection.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        """
        logger.info(f"Loading existing tick data from {self.table_name}...")
        
        try:
            # Quick check if table is empty
            count_check = self.supabase.table(self.table_name)\
                .select('id', count='exact')\
                .limit(1)\
                .execute()
            
            total_in_table = count_check.count if hasattr(count_check, 'count') else 0
            
            if total_in_table == 0:
                logger.info("✅ Table is empty - skipping duplicate check (fast path)")
                return
            
            logger.info(f"Table has {total_in_table:,} rows - checking for duplicates...")
            logger.info("Note: This may take a while for large date ranges...")
            
            # Query existing data in the date range with pagination
            # We need all fields to detect exact duplicates
            page_size = 1000
            offset = 0
            total_loaded = 0
            
            while True:
                response = self.supabase.table(self.table_name)\
                    .select('ts, bid, ask, last, vol')\
                    .gte('ts', start_date.isoformat())\
                    .lte('ts', end_date.isoformat())\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                
                if not response.data or len(response.data) == 0:
                    break
                
                # Create hash for each complete row
                for row in response.data:
                    row_hash = f"{row['ts']}|{row.get('bid')}|{row.get('ask')}|{row.get('last')}|{row.get('vol')}"
                    self.existing_rows.add(row_hash)
                
                total_loaded += len(response.data)
                
                # Log progress every 10k rows
                if total_loaded % 10000 == 0:
                    logger.info(f"  Loaded {total_loaded:,} existing rows...")
                
                # Check if we got less than page_size (last page)
                if len(response.data) < page_size:
                    break
                
                offset += page_size
            
            if self.existing_rows:
                logger.info(f"Found {len(self.existing_rows):,} existing unique rows")
            else:
                logger.info("No existing data found in this date range")
                
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
            logger.warning("Continuing without duplicate detection...")
    
    def filter_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out exact duplicate rows based on complete row data (ts, bid, ask, last, vol).
        Multiple ticks can have the same timestamp but different prices - those are NOT duplicates!
        
        Args:
            df: DataFrame with tick data
        
        Returns:
            DataFrame with exact duplicates removed
        """
        if not self.existing_rows:
            return df
        
        # Create hash for each row in the dataframe
        df['row_hash'] = df.apply(
            lambda row: f"{row['ts']}|{row.get('bid')}|{row.get('ask')}|{row.get('last')}|{row.get('vol')}", 
            axis=1
        )
        
        # Filter out exact duplicates
        df_filtered = df[~df['row_hash'].isin(self.existing_rows)]
        
        duplicates_found = len(df) - len(df_filtered)
        if duplicates_found > 0:
            logger.warning(f"Filtered out {duplicates_found} exact duplicate rows")
        
        # Drop temporary column
        df_filtered = df_filtered.drop('row_hash', axis=1)
        
        return df_filtered


# ============================================================================
# FILE UPLOADER
# ============================================================================

class TickDataUploader:
    """Uploads tick data from TXT files to Supabase with dual target support"""
    
    def __init__(self, supabase_target: str = None):
        """Initialize the uploader
        
        Args:
            supabase_target: 'selfhosted' or 'cloud' (defaults to env DEFAULT_SUPABASE)
        """
        self.target = supabase_target or UploadConfig.DEFAULT_TARGET
        config = UploadConfig.get_supabase_config(self.target)
        
        self.supabase: Client = create_client(config['url'], config['key'])
        self.schema = config['schema']
        
        logger.info(f"Tick data uploader initialized for {self.target.upper()} Supabase")
        logger.info(f"Using schema: {self.schema}")
    
    def upload_csv(
        self,
        csv_file: str,
        instrument: str,
        skip_duplicates: bool = True,
        has_header: bool = True,
        progress_callback = None
    ) -> Dict:
        """
        Upload TXT file to Supabase.
        
        Args:
            csv_file: Path to TXT file
            instrument: Instrument code ('ES' or 'NQ')
            skip_duplicates: Whether to skip duplicate rows
            has_header: Whether file has header row
            progress_callback: Optional callback function for batch progress updates
        
        Returns:
            Dict with upload statistics
        """
        logger.info("=" * 70)
        logger.info("TXT TICK DATA UPLOAD")
        logger.info("=" * 70)
        
        # Validate instrument
        if instrument not in UploadConfig.INSTRUMENTS:
            logger.error(f"Invalid instrument: {instrument}")
            logger.error(f"Supported instruments: {list(UploadConfig.INSTRUMENTS.keys())}")
            return {'success': False, 'error': 'Invalid instrument'}
        
        table_base = UploadConfig.INSTRUMENTS[instrument]
        table_name = f"{self.schema}.{table_base}"
        logger.info(f"Target table: {table_name}")
        logger.info(f"Supabase: {self.target.upper()}")
        
        # Check if file exists
        if not os.path.exists(csv_file):
            logger.error(f"File not found: {csv_file}")
            return {'success': False, 'error': 'File not found'}
        
        # Get file info
        csv_info = CSVAnalyzer.get_csv_info(csv_file)
        logger.info(f"File size: {csv_info['file_size_mb']} MB")
        logger.info(f"Total rows: {csv_info['total_rows']:,}")
        logger.info(f"Columns: {csv_info['columns']}")
        
        # Detect date range
        date_range = CSVAnalyzer.detect_date_range(csv_file, has_header=has_header)
        if not date_range:
            logger.error("Could not detect date range from file")
            return {'success': False, 'error': 'Could not detect date range'}
        
        start_date, end_date = date_range
        
        # Initialize duplicate detector
        duplicate_detector = None
        if skip_duplicates:
            duplicate_detector = DuplicateDetector(self.supabase, table_name)
            duplicate_detector.load_existing_timestamps(start_date, end_date)
        
        # Process file in chunks
        logger.info(f"\nUploading data in batches of {UploadConfig.BATCH_SIZE}...")
        
        total_rows = 0
        uploaded_rows = 0
        skipped_rows = 0
        error_rows = 0
        
        try:
            # Detect separator
            separator = ','
            with open(csv_file, 'r') as f:
                first_line = f.readline()
                if ';' in first_line and ',' not in first_line:
                    separator = ';'
                    logger.info(f"Detected separator: semicolon (;)")
            
            # Read file in chunks
            if has_header:
                chunk_iterator = pd.read_csv(csv_file, sep=separator, chunksize=UploadConfig.BATCH_SIZE)
            else:
                # File without header - specify column names
                # Format: timestamp;bid;ask;last;vol
                chunk_iterator = pd.read_csv(
                    csv_file, 
                    sep=separator, 
                    header=None,
                    names=['timestamp', 'bid', 'ask', 'last', 'vol'],
                    chunksize=UploadConfig.BATCH_SIZE
                )
            
            for chunk_num, chunk in enumerate(chunk_iterator, 1):
                total_rows += len(chunk)
                
                # Standardize column names
                chunk = self._standardize_columns(chunk, has_header=has_header)
                
                # Filter duplicates
                if duplicate_detector:
                    original_size = len(chunk)
                    chunk = duplicate_detector.filter_duplicates(chunk)
                    skipped_rows += (original_size - len(chunk))
                
                if len(chunk) == 0:
                    logger.info(f"  Batch {chunk_num}: All rows are duplicates, skipping...")
                    continue
                
                # Convert to records
                records = chunk.to_dict('records')
                
                # Upload to Supabase with simple insert
                try:
                    # Use simple insert - much faster and more reliable
                    response = self.supabase.table(table_name)\
                        .insert(records)\
                        .execute()
                    
                    # Count inserted rows
                    inserted_count = len(response.data) if response.data else len(records)
                    uploaded_rows += inserted_count
                    
                    logger.info(f"  ✅ Batch {chunk_num}: Uploaded {inserted_count} rows (Total: {uploaded_rows:,}/{total_rows:,})")
                    
                    # Send progress update if callback provided
                    if progress_callback:
                        progress_callback({
                            'batch': chunk_num,
                            'batch_rows': inserted_count,
                            'total_uploaded': uploaded_rows,
                            'total_processed': total_rows,
                            'skipped': skipped_rows,
                            'status': 'uploading'
                        })
                    
                except Exception as e:
                    # Log error and continue
                    error_msg = str(e)
                    logger.error(f"  ❌ Batch {chunk_num}: Error uploading - {error_msg}")
                    error_rows += len(records)
            
            # Summary
            logger.info("=" * 70)
            logger.success("UPLOAD COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Total rows processed: {total_rows:,}")
            logger.info(f"Uploaded rows:        {uploaded_rows:,}")
            logger.info(f"Skipped (duplicates): {skipped_rows:,}")
            logger.info(f"Errors:               {error_rows:,}")
            logger.info("=" * 70)
            
            return {
                'success': True,
                'total_rows': total_rows,
                'uploaded_rows': uploaded_rows,
                'skipped_rows': skipped_rows,
                'error_rows': error_rows,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during upload: {e}")
            return {'success': False, 'error': str(e)}
    
    def _standardize_columns(self, df: pd.DataFrame, has_header: bool = True) -> pd.DataFrame:
        """
        Standardize column names to match Supabase schema.
        
        Args:
            df: DataFrame with tick data
            has_header: Whether the original file had headers
        
        Returns:
            DataFrame with standardized columns
        """
        # Map common column name variations
        column_mapping = {
            'timestamp': 'ts',
            'time': 'ts',
            'datetime': 'ts',
            'price': 'last',
            'last_price': 'last',
            'volume': 'vol',
            'bid_price': 'bid',
            'ask_price': 'ask'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = ['ts', 'last']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Required column '{col}' not found")
                raise ValueError(f"Missing required column: {col}")
        
        # Convert timestamp to ISO format
        if not has_header:
            # Parse custom timestamp format: YYYYMMDD HHMMSS microseconds
            def parse_custom_timestamp(ts_str):
                try:
                    parts = str(ts_str).split()
                    if len(parts) >= 2:
                        date_part = parts[0]  # YYYYMMDD
                        time_part = parts[1]  # HHMMSS
                        
                        # Parse date
                        year = int(date_part[0:4])
                        month = int(date_part[4:6])
                        day = int(date_part[6:8])
                        
                        # Parse time
                        hour = int(time_part[0:2])
                        minute = int(time_part[2:4])
                        second = int(time_part[4:6])
                        
                        dt = datetime(year, month, day, hour, minute, second)
                        return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                except:
                    pass
                return pd.to_datetime(ts_str).strftime('%Y-%m-%dT%H:%M:%S+00:00')
            
            df['ts'] = df['ts'].apply(parse_custom_timestamp)
        else:
            df['ts'] = pd.to_datetime(df['ts']).dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        
        # Select only columns that exist in Supabase schema
        available_columns = ['ts', 'bid', 'ask', 'last', 'vol']
        df = df[[col for col in available_columns if col in df.columns]]
        
        return df
    
    def verify_upload(self, instrument: str, start_date: datetime, end_date: datetime) -> Dict:
        """
        Verify uploaded data in Supabase.
        
        Args:
            instrument: Instrument code
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            Dict with verification results
        """
        table_name = UploadConfig.INSTRUMENTS[instrument]
        
        logger.info(f"\nVerifying uploaded data in {table_name}...")
        
        try:
            # Count rows in date range
            response = self.supabase.table(table_name)\
                .select('ts', count='exact')\
                .gte('ts', start_date.isoformat())\
                .lte('ts', end_date.isoformat())\
                .execute()
            
            count = response.count if hasattr(response, 'count') else len(response.data)
            
            logger.success(f"✅ Found {count:,} rows in Supabase")
            
            # Get sample data
            sample = self.supabase.table(table_name)\
                .select('*')\
                .gte('ts', start_date.isoformat())\
                .lte('ts', end_date.isoformat())\
                .order('ts', desc=False)\
                .limit(5)\
                .execute()
            
            logger.info("\nSample data:")
            for row in sample.data:
                logger.info(f"  {row}")
            
            return {
                'success': True,
                'count': count,
                'sample': sample.data
            }
            
        except Exception as e:
            logger.error(f"Error verifying upload: {e}")
            return {'success': False, 'error': str(e)}


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    
    print("\n" + "=" * 70)
    print("CSV TICK DATA UPLOAD PIPELINE")
    print("=" * 70)
    print("Upload tick-by-tick data to Supabase with automatic deduplication")
    print("=" * 70 + "\n")
    
    # Get CSV file path
    csv_file = input("Enter CSV file path (or press Enter for default): ").strip()
    if not csv_file:
        csv_file = os.path.expanduser("~/Downloads/es.csv")
    
    # Expand ~ to home directory
    csv_file = os.path.expanduser(csv_file)
    
    # Check if file exists
    if not os.path.exists(csv_file):
        logger.error(f"File not found: {csv_file}")
        return
    
    # Get instrument
    print("\nSupported instruments:")
    for inst in UploadConfig.INSTRUMENTS.keys():
        print(f"  - {inst}")
    
    instrument = input("\nEnter instrument (ES or NQ): ").strip().upper()
    if instrument not in UploadConfig.INSTRUMENTS:
        logger.error(f"Invalid instrument: {instrument}")
        return
    
    # Ask about file format
    has_header = input("\nDoes the file have a header row? (y/n) [default: y]: ").strip().lower()
    has_header = has_header != 'n'
    
    # Ask about duplicate handling
    skip_duplicates = input("\nSkip duplicate rows? (y/n) [default: y]: ").strip().lower()
    skip_duplicates = skip_duplicates != 'n'
    
    # Initialize uploader
    uploader = TickDataUploader()
    
    # Upload CSV
    result = uploader.upload_csv(
        csv_file=csv_file,
        instrument=instrument,
        skip_duplicates=skip_duplicates,
        has_header=has_header
    )
    
    if result['success']:
        # Verify upload
        if 'start_date' in result:
            start_date = datetime.fromisoformat(result['start_date'])
            end_date = datetime.fromisoformat(result['end_date'])
            uploader.verify_upload(instrument, start_date, end_date)
    else:
        logger.error(f"Upload failed: {result.get('error')}")


if __name__ == "__main__":
    main()
