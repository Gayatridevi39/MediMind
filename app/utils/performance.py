"""
Performance optimization utilities for MediMind application
"""
import asyncio
import time
import functools
import streamlit as st
from typing import List, Dict, Any
import gc
import sys


class MemoryOptimizer:
    """Memory optimization utilities"""
    
    @staticmethod
    def force_garbage_collection():
        """Force garbage collection to free memory"""
        gc.collect()
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB"""
        return sys.getsizeof(sys.modules) / (1024 * 1024)
    
    @staticmethod
    @st.cache_data(show_spinner=False, max_entries=3)
    def process_large_file_chunked(file_content: str, chunk_size: int = 1000):
        """Process large files in chunks to optimize memory usage"""
        chunks = []
        for i in range(0, len(file_content), chunk_size):
            chunks.append(file_content[i:i + chunk_size])
        return chunks


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def timer(func):
        """Decorator to time function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Store in session state for monitoring
            if 'performance_metrics' not in st.session_state:
                st.session_state['performance_metrics'] = {}
            
            st.session_state['performance_metrics'][func.__name__] = {
                'execution_time': execution_time,
                'timestamp': time.time()
            }
            
            return result
        return wrapper
    
    @staticmethod
    def get_performance_summary():
        """Get performance summary from session state"""
        if 'performance_metrics' in st.session_state:
            return st.session_state['performance_metrics']
        return {}


class AsyncOperations:
    """Async operations for improved responsiveness"""
    
    @staticmethod
    async def async_api_call(url: str, params: Dict[str, Any], timeout: int = 10):
        """Make async API calls"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
            except Exception as e:
                st.error(f"Async API call failed: {e}")
                return None
    
    @staticmethod
    @st.cache_data(show_spinner=False, ttl=3600)
    def batch_pubmed_search(queries: List[str], max_results: int = 5):
        """Batch multiple PubMed searches for better performance"""
        import requests
        results = {}
        
        for query in queries:
            try:
                url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json"
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results[query] = data.get("esearchresult", {}).get("idlist", [])
                else:
                    results[query] = []
            except Exception:
                results[query] = []
        
        return results


class CacheOptimizer:
    """Cache optimization utilities"""
    
    @staticmethod
    def clear_old_cache_entries():
        """Clear old cache entries to prevent memory buildup"""
        try:
            st.cache_data.clear()
            st.cache_resource.clear()
        except Exception:
            pass
    
    @staticmethod
    @st.cache_data(show_spinner=False, max_entries=5, ttl=1800)  # 30 minutes
    def optimized_text_extraction(file_bytes: bytes, file_type: str):
        """Optimized text extraction with better caching"""
        if file_type == "pdf":
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_chunks = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text_chunks.append(page.get_text())
                
                # Free page memory immediately
                page = None
            
            doc.close()
            return "\n".join(text_chunks)
        
        elif file_type in ["txt", "data"]:
            return file_bytes.decode("utf-8")
        
        elif file_type == "csv":
            import pandas as pd
            import io
            df = pd.read_csv(io.BytesIO(file_bytes))
            return df.to_string(index=False)
        
        return ""


# Performance monitoring decorator for Streamlit components
def monitor_performance(component_name: str):
    """Decorator to monitor Streamlit component performance"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Calculate and store performance metrics
            execution_time = time.time() - start_time
            
            if 'component_performance' not in st.session_state:
                st.session_state['component_performance'] = {}
            
            st.session_state['component_performance'][component_name] = {
                'last_execution_time': execution_time,
                'total_calls': st.session_state['component_performance'].get(component_name, {}).get('total_calls', 0) + 1,
                'average_time': execution_time  # Can be enhanced to calculate real average
            }
            
            return result
        return wrapper
    return decorator