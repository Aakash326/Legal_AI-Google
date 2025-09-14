import os
import time
from typing import Optional, Dict, Any
import logging
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError, NotFound
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, project_id: Optional[str] = None, bucket_name: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.bucket_name = bucket_name or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
        
        if not self.project_id:
            logger.warning("Google Cloud Project ID not set. Storage features will be limited.")
            self.client = None
            self.bucket = None
            return
        
        try:
            # Initialize the storage client
            self.client = storage.Client(project=self.project_id)
            
            if self.bucket_name:
                try:
                    self.bucket = self.client.bucket(self.bucket_name)
                    # Test bucket access
                    self.bucket.exists()
                    logger.info(f"Connected to storage bucket: {self.bucket_name}")
                except Exception as e:
                    logger.warning(f"Could not access bucket {self.bucket_name}: {str(e)}")
                    self.bucket = None
            else:
                logger.warning("No storage bucket specified. File upload features will be limited.")
                self.bucket = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage: {str(e)}")
            self.client = None
            self.bucket = None
    
    def upload_file(self, local_file_path: str, destination_blob_name: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Upload a file to Google Cloud Storage"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return None
        
        try:
            # Check if local file exists
            if not os.path.exists(local_file_path):
                logger.error(f"Local file does not exist: {local_file_path}")
                return None
            
            # Create blob object
            blob = self.bucket.blob(destination_blob_name)
            
            # Set metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            blob.upload_from_filename(local_file_path)
            
            logger.info(f"File uploaded to {destination_blob_name}")
            
            # Return the public URL (if bucket is public) or signed URL
            return blob.public_url
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Storage upload failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return None
    
    def download_file(self, blob_name: str, local_file_path: str) -> bool:
        """Download a file from Google Cloud Storage"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return False
        
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Get blob and download
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                logger.error(f"Blob does not exist: {blob_name}")
                return False
            
            blob.download_to_filename(local_file_path)
            
            logger.info(f"File downloaded from {blob_name} to {local_file_path}")
            return True
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Storage download failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"File download failed: {str(e)}")
            return False
    
    def generate_signed_url(self, blob_name: str, expiration_hours: int = 24) -> Optional[str]:
        """Generate a signed URL for temporary access to a file"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return None
        
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                logger.error(f"Blob does not exist: {blob_name}")
                return None
            
            # Generate signed URL
            expiration = time.time() + (expiration_hours * 3600)
            
            url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            
            logger.info(f"Generated signed URL for {blob_name}")
            return url
            
        except Exception as e:
            logger.error(f"Signed URL generation failed: {str(e)}")
            return None
    
    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Google Cloud Storage"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return False
        
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                logger.warning(f"Blob does not exist: {blob_name}")
                return True  # Already deleted
            
            blob.delete()
            
            logger.info(f"File deleted: {blob_name}")
            return True
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Storage deletion failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False
    
    def list_files(self, prefix: Optional[str] = None, max_results: int = 100) -> list:
        """List files in the bucket"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return []
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, max_results=max_results)
            
            file_list = []
            for blob in blobs:
                file_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.time_created.isoformat() if blob.time_created else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "content_type": blob.content_type,
                    "metadata": blob.metadata or {}
                }
                file_list.append(file_info)
            
            logger.info(f"Listed {len(file_list)} files with prefix '{prefix}'")
            return file_list
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Storage listing failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"File listing failed: {str(e)}")
            return []
    
    def get_file_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return None
        
        try:
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                logger.error(f"Blob does not exist: {blob_name}")
                return None
            
            # Reload to get latest metadata
            blob.reload()
            
            metadata = {
                "name": blob.name,
                "size": blob.size,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "content_type": blob.content_type,
                "etag": blob.etag,
                "generation": blob.generation,
                "metageneration": blob.metageneration,
                "metadata": blob.metadata or {},
                "public_url": blob.public_url,
                "media_link": blob.media_link
            }
            
            return metadata
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud Storage metadata retrieval failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Metadata retrieval failed: {str(e)}")
            return None
    
    def create_bucket(self, bucket_name: str, location: str = "US") -> bool:
        """Create a new storage bucket"""
        if not self.client:
            logger.warning("Storage client not available")
            return False
        
        try:
            bucket = self.client.bucket(bucket_name)
            bucket.location = location
            
            bucket = self.client.create_bucket(bucket)
            
            logger.info(f"Bucket created: {bucket_name} in {location}")
            
            # Update current bucket if this is the one we want to use
            if not self.bucket_name or self.bucket_name == bucket_name:
                self.bucket = bucket
                self.bucket_name = bucket_name
            
            return True
            
        except GoogleCloudError as e:
            logger.error(f"Bucket creation failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Bucket creation failed: {str(e)}")
            return False
    
    def cleanup_old_files(self, prefix: str, days_old: int = 7) -> int:
        """Clean up files older than specified days"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return 0
        
        try:
            cutoff_time = time.time() - (days_old * 24 * 3600)
            
            blobs = self.bucket.list_blobs(prefix=prefix)
            deleted_count = 0
            
            for blob in blobs:
                if blob.time_created and blob.time_created.timestamp() < cutoff_time:
                    try:
                        blob.delete()
                        deleted_count += 1
                        logger.debug(f"Deleted old file: {blob.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {blob.name}: {str(e)}")
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return 0
    
    def get_storage_usage(self) -> Optional[Dict[str, Any]]:
        """Get storage usage information"""
        if not self.bucket:
            logger.warning("Storage bucket not available")
            return None
        
        try:
            blobs = self.bucket.list_blobs()
            
            total_size = 0
            file_count = 0
            file_types = {}
            
            for blob in blobs:
                total_size += blob.size or 0
                file_count += 1
                
                # Track file types
                content_type = blob.content_type or "unknown"
                file_types[content_type] = file_types.get(content_type, 0) + 1
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "file_types": file_types,
                "bucket_name": self.bucket_name
            }
            
        except Exception as e:
            logger.error(f"Storage usage calculation failed: {str(e)}")
            return None
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of storage service"""
        return {
            "available": self.client is not None,
            "bucket_available": self.bucket is not None,
            "project_id": self.project_id,
            "bucket_name": self.bucket_name
        }

# Global instance
storage_service = None

def get_storage_service() -> StorageService:
    """Get global storage service instance"""
    global storage_service
    if storage_service is None:
        storage_service = StorageService()
    return storage_service