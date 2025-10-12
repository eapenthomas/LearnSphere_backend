#!/usr/bin/env python3
"""
LearnSphere API Performance Report Generator
Comprehensive testing and reporting of API endpoints
"""

import time
import requests
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import statistics
import json
from datetime import datetime

class APIPerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "endpoints": {},
            "summary": {},
            "recommendations": []
        }
        
    def test_endpoint(self, endpoint, method="GET", headers=None, data=None, timeout=10):
        """Test a single endpoint and measure response time"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "endpoint": endpoint,
                "method": method,
                "content_length": len(response.content) if response.content else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "response_time_ms": 0,
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "content_length": 0
            }
    
    def test_endpoint_multiple_times(self, endpoint, method="GET", count=10, headers=None, data=None):
        """Test the same endpoint multiple times to get average performance"""
        times = []
        successes = 0
        status_codes = []
        content_lengths = []
        
        for i in range(count):
            result = self.test_endpoint(endpoint, method, headers, data)
            if result["success"]:
                times.append(result["response_time_ms"])
                successes += 1
                status_codes.append(result["status_code"])
                content_lengths.append(result["content_length"])
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "success_rate": (successes / count) * 100,
                "avg_time_ms": statistics.mean(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "median_time_ms": statistics.median(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "total_requests": count,
                "successful_requests": successes,
                "status_codes": list(set(status_codes)),
                "avg_content_length": statistics.mean(content_lengths) if content_lengths else 0
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "success_rate": 0,
                "avg_time_ms": 0,
                "min_time_ms": 0,
                "max_time_ms": 0,
                "median_time_ms": 0,
                "std_dev_ms": 0,
                "total_requests": count,
                "successful_requests": 0,
                "status_codes": [],
                "avg_content_length": 0
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive API performance tests"""
        print("🚀 LearnSphere API Performance Report")
        print("=" * 80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        # Define endpoints to test
        endpoints_to_test = [
            # Core endpoints
            {"endpoint": "/", "method": "GET", "name": "Root Endpoint"},
            {"endpoint": "/health", "method": "GET", "name": "Health Check"},
            {"endpoint": "/docs", "method": "GET", "name": "API Documentation"},
            
            # Notification endpoints
            {"endpoint": "/api/notifications/types", "method": "GET", "name": "Notification Types"},
            
            # Course endpoints
            {"endpoint": "/api/courses/categories", "method": "GET", "name": "Course Categories"},
            
            # Thumbnail endpoints (will fail but test performance)
            {"endpoint": "/api/thumbnails/course/test/url", "method": "GET", "name": "Thumbnail URL"},
        ]
        
        print("📊 Testing API Endpoints")
        print("-" * 80)
        
        for test_config in endpoints_to_test:
            endpoint = test_config["endpoint"]
            method = test_config["method"]
            name = test_config["name"]
            
            print(f"Testing {name} ({method} {endpoint})...")
            result = self.test_endpoint_multiple_times(endpoint, method, 5)
            
            # Store results
            self.report_data["endpoints"][endpoint] = result
            
            if result["success_rate"] > 0:
                print(f"✅ {name}")
                print(f"   Average Response Time: {result['avg_time_ms']:.1f}ms")
                print(f"   Min/Max: {result['min_time_ms']:.1f}ms / {result['max_time_ms']:.1f}ms")
                print(f"   Success Rate: {result['success_rate']:.1f}%")
                print(f"   Status Codes: {result['status_codes']}")
                if result['avg_content_length'] > 0:
                    print(f"   Content Size: {result['avg_content_length']:.0f} bytes")
            else:
                print(f"❌ {name} - Failed")
            
            print()
        
        # Test concurrent requests
        print("🔄 Testing Concurrent Request Handling")
        print("-" * 80)
        
        concurrent_results = self.test_concurrent_requests("/health", 20)
        self.report_data["concurrent_test"] = concurrent_results
        
        # Generate performance summary
        self.generate_performance_summary()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save report to file
        self.save_report_to_file()
        
        # Display summary
        self.display_summary()
    
    def test_concurrent_requests(self, endpoint, num_requests=20):
        """Test concurrent request handling"""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(num_requests):
                future = executor.submit(self.test_endpoint, endpoint)
                futures.append(future)
            
            concurrent_times = []
            successes = 0
            for future in futures:
                result = future.result()
                if result["success"]:
                    concurrent_times.append(result["response_time_ms"])
                    successes += 1
            
            if concurrent_times:
                print(f"✅ Concurrent requests ({num_requests} simultaneous)")
                print(f"   Average: {statistics.mean(concurrent_times):.1f}ms")
                print(f"   Min: {min(concurrent_times):.1f}ms")
                print(f"   Max: {max(concurrent_times):.1f}ms")
                print(f"   Success Rate: {(successes/num_requests)*100:.1f}%")
                
                return {
                    "num_requests": num_requests,
                    "success_rate": (successes/num_requests)*100,
                    "avg_time_ms": statistics.mean(concurrent_times),
                    "min_time_ms": min(concurrent_times),
                    "max_time_ms": max(concurrent_times),
                    "successful_requests": successes
                }
            else:
                return {
                    "num_requests": num_requests,
                    "success_rate": 0,
                    "avg_time_ms": 0,
                    "min_time_ms": 0,
                    "max_time_ms": 0,
                    "successful_requests": 0
                }
    
    def generate_performance_summary(self):
        """Generate performance summary"""
        successful_endpoints = [k for k, v in self.report_data["endpoints"].items() if v["success_rate"] > 0]
        
        if successful_endpoints:
            avg_times = [self.report_data["endpoints"][ep]["avg_time_ms"] for ep in successful_endpoints]
            
            self.report_data["summary"] = {
                "total_endpoints_tested": len(self.report_data["endpoints"]),
                "successful_endpoints": len(successful_endpoints),
                "overall_avg_response_time_ms": statistics.mean(avg_times),
                "fastest_endpoint": min(successful_endpoints, key=lambda x: self.report_data["endpoints"][x]["avg_time_ms"]),
                "slowest_endpoint": max(successful_endpoints, key=lambda x: self.report_data["endpoints"][x]["avg_time_ms"]),
                "performance_rating": self.get_performance_rating(statistics.mean(avg_times))
            }
    
    def get_performance_rating(self, avg_time_ms):
        """Get performance rating based on average response time"""
        if avg_time_ms < 100:
            return "🚀 Excellent"
        elif avg_time_ms < 300:
            return "✅ Good"
        elif avg_time_ms < 500:
            return "⚠️ Fair"
        elif avg_time_ms < 1000:
            return "🐌 Slow"
        else:
            return "🐢 Very Slow"
    
    def generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []
        
        # Check response times
        successful_endpoints = [k for k, v in self.report_data["endpoints"].items() if v["success_rate"] > 0]
        if successful_endpoints:
            avg_times = [self.report_data["endpoints"][ep]["avg_time_ms"] for ep in successful_endpoints]
            overall_avg = statistics.mean(avg_times)
            
            if overall_avg > 500:
                recommendations.append("🔧 Consider implementing database connection pooling")
                recommendations.append("📦 Add caching layer for frequently accessed data")
                recommendations.append("⚡ Optimize database queries with proper indexing")
                recommendations.append("🌐 Consider using a CDN for static content")
                recommendations.append("💾 Implement Redis for session and data caching")
            
            if overall_avg > 1000:
                recommendations.append("🚀 Consider upgrading server hardware")
                recommendations.append("📊 Implement request rate limiting")
                recommendations.append("🔄 Add load balancing for high traffic")
        
        # Check concurrent performance
        if "concurrent_test" in self.report_data:
            concurrent_success_rate = self.report_data["concurrent_test"]["success_rate"]
            if concurrent_success_rate < 90:
                recommendations.append("🔄 Improve concurrent request handling")
                recommendations.append("📈 Consider horizontal scaling")
        
        self.report_data["recommendations"] = recommendations
    
    def save_report_to_file(self):
        """Save detailed report to JSON file"""
        filename = f"api_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        print(f"📄 Detailed report saved to: {filename}")
    
    def display_summary(self):
        """Display performance summary"""
        print("\n📈 Performance Summary")
        print("=" * 80)
        
        if self.report_data["summary"]:
            summary = self.report_data["summary"]
            print(f"📊 Overall Performance:")
            print(f"   Endpoints Tested: {summary['total_endpoints_tested']}")
            print(f"   Successful Endpoints: {summary['successful_endpoints']}")
            print(f"   Average Response Time: {summary['overall_avg_response_time_ms']:.1f}ms")
            print(f"   Performance Rating: {summary['performance_rating']}")
            print(f"   Fastest Endpoint: {summary['fastest_endpoint']}")
            print(f"   Slowest Endpoint: {summary['slowest_endpoint']}")
        
        print(f"\n🏆 Best Performing Endpoints:")
        successful_endpoints = [(k, v) for k, v in self.report_data["endpoints"].items() if v["success_rate"] > 0]
        sorted_endpoints = sorted(successful_endpoints, key=lambda x: x[1]["avg_time_ms"])
        
        for i, (endpoint, data) in enumerate(sorted_endpoints[:3]):
            print(f"   {i+1}. {endpoint} - {data['avg_time_ms']:.1f}ms")
        
        print(f"\n💡 Optimization Recommendations:")
        for recommendation in self.report_data["recommendations"]:
            print(f"   {recommendation}")

def main():
    """Main function"""
    print("🔍 Starting API Performance Analysis...")
    
    tester = APIPerformanceTester()
    
    try:
        tester.run_comprehensive_test()
        print("\n🎉 Performance analysis completed!")
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()
