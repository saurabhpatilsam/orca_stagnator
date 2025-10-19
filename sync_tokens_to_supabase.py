#!/usr/bin/env python3
"""
🔄 SYNC TOKENS TO SUPABASE EDGE FUNCTION
========================================

This script syncs all Redis tokens to Supabase using the Edge Function.
It provides a complete token management solution with Supabase storage.

Usage:
    python3 sync_tokens_to_supabase.py [action]
    
Actions:
    sync     - Sync all tokens from Redis to Supabase (default)
    status   - Get token status from both Redis and Supabase
    get      - Get a specific token from Supabase
    cleanup  - Clean up expired tokens in Supabase
"""

import requests
import json
import sys
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseTokenManager:
    def __init__(self):
        # Supabase configuration - update these with your actual values
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
        
        # Edge Function URL
        self.edge_function_url = f"{self.supabase_url}/functions/v1/token-manager"
        
        # Headers for requests
        self.headers = {
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'Content-Type': 'application/json',
            'apikey': self.supabase_anon_key
        }
    
    def sync_tokens_from_redis(self) -> Dict[str, Any]:
        """Sync all tokens from Redis to Supabase"""
        print("🔄 Syncing tokens from Redis to Supabase...")
        
        try:
            response = requests.get(
                f"{self.edge_function_url}?action=sync",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sync successful: {result.get('message', 'Done')}")
                print(f"📊 Tokens synced: {result.get('tokens_synced', 0)}")
                print(f"🔑 Key mappings: {result.get('key_mappings_created', 0)}")
                
                if result.get('accounts'):
                    print(f"🏦 Accounts synced:")
                    for account in result['accounts']:
                        print(f"   • {account}")
                
                return result
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Sync failed: {response.status_code}")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return {'success': False, 'error': error_data}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during sync: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Unexpected error during sync: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_token_status(self) -> Dict[str, Any]:
        """Get token status from both Redis and Supabase"""
        print("📊 Getting token status...")
        
        try:
            response = requests.get(
                f"{self.edge_function_url}?action=status",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status', {})
                
                print(f"📊 TOKEN STATUS:")
                print(f"   Supabase tokens: {status.get('supabase_tokens', 0)}")
                print(f"   Redis tokens: {status.get('redis_tokens', 0)}")
                print(f"   Sync needed: {status.get('sync_needed', False)}")
                print(f"   Last updated: {status.get('last_updated', 'Unknown')}")
                
                recent_tokens = result.get('recent_tokens', [])
                if recent_tokens:
                    print(f"\n🕐 Recent tokens:")
                    for token in recent_tokens[:5]:
                        print(f"   • {token.get('account_name')} (expires: {token.get('expires_at', 'Unknown')[:19]})")
                
                return result
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Status check failed: {response.status_code}")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return {'success': False, 'error': error_data}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during status check: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Unexpected error during status check: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_token(self, account_name: str) -> Dict[str, Any]:
        """Get a specific token from Supabase"""
        print(f"🔑 Getting token for account: {account_name}")
        
        try:
            response = requests.get(
                f"{self.edge_function_url}?action=get&account={account_name}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Token retrieved for {account_name}")
                print(f"   Token length: {result.get('token_length', 0)} characters")
                print(f"   Expires at: {result.get('expires_at', 'Unknown')}")
                print(f"   Token preview: {result.get('token', '')[:50]}...")
                return result
            elif response.status_code == 404:
                print(f"❌ Token not found for account: {account_name}")
                return {'success': False, 'error': 'Token not found'}
            elif response.status_code == 410:
                error_data = response.json()
                print(f"⚠️ Token expired for account: {account_name}")
                print(f"   Expired at: {error_data.get('expires_at', 'Unknown')}")
                return {'success': False, 'error': 'Token expired', 'expired': True}
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Get token failed: {response.status_code}")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return {'success': False, 'error': error_data}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during token retrieval: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Unexpected error during token retrieval: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_expired_tokens(self) -> Dict[str, Any]:
        """Clean up expired tokens in Supabase"""
        print("🧹 Cleaning up expired tokens...")
        
        try:
            response = requests.get(
                f"{self.edge_function_url}?action=cleanup",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Cleanup successful: {result.get('message', 'Done')}")
                print(f"🗑️ Tokens cleaned up: {result.get('cleaned_up', 0)}")
                return result
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Cleanup failed: {response.status_code}")
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                return {'success': False, 'error': error_data}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during cleanup: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"❌ Unexpected error during cleanup: {e}")
            return {'success': False, 'error': str(e)}

def main():
    print("\n" + "="*60)
    print("🔄 SUPABASE TOKEN MANAGER")
    print("="*60)
    
    # Get action from command line argument
    action = sys.argv[1] if len(sys.argv) > 1 else 'sync'
    
    # Initialize token manager
    manager = SupabaseTokenManager()
    
    # Check configuration
    if 'your-project' in manager.supabase_url or 'your-anon-key' in manager.supabase_anon_key:
        print("⚠️ WARNING: Please update your Supabase configuration in the script or .env file")
        print("   Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        print("   Or update the values directly in the script")
        print()
    
    # Execute action
    if action == 'sync':
        result = manager.sync_tokens_from_redis()
    elif action == 'status':
        result = manager.get_token_status()
    elif action == 'get':
        account = sys.argv[2] if len(sys.argv) > 2 else 'APEX_136189'
        result = manager.get_token(account)
    elif action == 'cleanup':
        result = manager.cleanup_expired_tokens()
    else:
        print(f"❌ Unknown action: {action}")
        print("Available actions: sync, status, get, cleanup")
        return
    
    print("\n" + "="*60)
    print("🏁 OPERATION COMPLETE")
    print("="*60)
    
    if result.get('success', False):
        print("✅ Operation completed successfully!")
    else:
        print("❌ Operation failed. Check the error messages above.")

if __name__ == "__main__":
    main()
