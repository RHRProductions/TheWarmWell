from cloud_sync import CloudSync
import os
import threading
import time

class SyncManager:
    def __init__(self):
        self.cloud_sync = CloudSync()
        self.tracked_files = [
            "warm_t65_leads.csv",
            "issued_t65_leads.csv",
            "dead_t65_leads.csv",
            "warm_life_leads.csv",
            "issued_life_leads.csv",
            "dead_life_leads.csv",
            "no_shows.csv",
            "converted_no_shows.csv",
            "dead_no_shows.csv",
            "deals_at_risk.csv",
            "saved_deals.csv",
            "dead_deals.csv",
            "community_connectors.csv",
            "inactive_connectors.csv",
            "removed_connectors.csv",
            "referrals.csv",
            "converted_referrals.csv",
            "dead_referrals.csv"
        ]
        self.sync_thread = None
        self.is_syncing = False
        
        # Try to authenticate on startup
        try:
            self.cloud_sync.authenticate()
        except Exception as e:
            print(f"Could not authenticate with Google Drive: {str(e)}")
            print("Working in offline mode")

    def start_sync(self):
        """Start the background sync process"""
        if not self.sync_thread or not self.sync_thread.is_alive():
            self.is_syncing = True
            self.sync_thread = threading.Thread(target=self._sync_loop)
            self.sync_thread.daemon = True
            self.sync_thread.start()

    def stop_sync(self):
        """Stop the background sync process"""
        self.is_syncing = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join()

    def _sync_loop(self):
        """Background sync loop"""
        while self.is_syncing:
            try:
                for file_name in self.tracked_files:
                    if os.path.exists(file_name):
                        self.cloud_sync.sync_file(file_name, file_name)
            except Exception as e:
                print(f"Sync error: {str(e)}")
            
            # Wait before next sync
            time.sleep(30)  # Sync every 30 seconds

    def force_sync(self):
        """Force an immediate sync of all files"""
        try:
            for file_name in self.tracked_files:
                if os.path.exists(file_name):
                    self.cloud_sync.sync_file(file_name, file_name)
        except Exception as e:
            print(f"Force sync error: {str(e)}")
