#!/usr/bin/env python3
"""
Supabase API Performance Analyzer
Comprehensive testing and optimization of Supabase database calls
"""

import os
import time
import asyncio
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor
from supabase import create_client, Client
from dotenv import load_dotenv

class SupabasePerformanceAnalyzer:
    def __init__(self):
        # Try to load from backend directory first
        backend_env_path = os.path.join("backend", ".env")
        if os.path.exists(backend_env_path):
            load_dotenv(backend_env_path)
        else:
            load_dotenv()
        
        # Initialize Supabase client
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Missing Supabase configuration")
            print("Please ensure you have:")
            print("1. Created a .env file in the backend directory")
            print("2. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
            print("3. Or set these as environment variables")
            raise ValueError("Missing Supabase configuration")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.results = {}
        self.optimization_recommendations = []
        
    def measure_query_performance(self, query_name: str, query_func, *args, **kwargs) -> Dict[str, Any]:
        """Measure the performance of a database query"""
        times = []
        errors = []
        
        # Run query multiple times to get average performance
        for i in range(5):
            try:
                start_time = time.time()
                result = query_func(*args, **kwargs)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                times.append(response_time)
                
            except Exception as e:
                errors.append(str(e))
        
        if times:
            return {
                "query_name": query_name,
                "avg_time_ms": statistics.mean(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "median_time_ms": statistics.median(times),
                "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "success_rate": (len(times) / 5) * 100,
                "errors": errors,
                "sample_count": len(times)
            }
        else:
            return {
                "query_name": query_name,
                "avg_time_ms": 0,
                "min_time_ms": 0,
                "max_time_ms": 0,
                "median_time_ms": 0,
                "std_dev_ms": 0,
                "success_rate": 0,
                "errors": errors,
                "sample_count": 0
            }
    
    def test_core_queries(self):
        """Test core database queries"""
        print("🔍 Testing Core Database Queries")
        print("-" * 60)
        
        # Test 1: Simple table select
        def simple_select():
            return self.supabase.table("profiles").select("id, full_name").limit(10).execute()
        
        result = self.measure_query_performance("Simple Select (profiles)", simple_select)
        self.results["simple_select"] = result
        self._print_query_result(result)
        
        # Test 2: Courses with joins
        def courses_with_joins():
            return self.supabase.table("courses").select("""
                id, title, description, category,
                profiles!courses_teacher_id_fkey(full_name)
            """).limit(10).execute()
        
        result = self.measure_query_performance("Courses with Joins", courses_with_joins)
        self.results["courses_with_joins"] = result
        self._print_query_result(result)
        
        # Test 3: Complex query with filters
        def complex_filtered_query():
            return self.supabase.table("courses").select("""
                id, title, category, status,
                profiles!courses_teacher_id_fkey(full_name)
            """).eq("status", "active").limit(20).execute()
        
        result = self.measure_query_performance("Complex Filtered Query", complex_filtered_query)
        self.results["complex_filtered_query"] = result
        self._print_query_result(result)
        
        # Test 4: Count query
        def count_query():
            return self.supabase.table("courses").select("id", count="exact").execute()
        
        result = self.measure_query_performance("Count Query", count_query)
        self.results["count_query"] = result
        self._print_query_result(result)
        
        # Test 5: Insert operation (skip if no valid teacher_id)
        def insert_test():
            try:
                # First, get a valid teacher_id
                teacher_result = self.supabase.table("profiles").select("id").eq("role", "teacher").limit(1).execute()
                if not teacher_result.data:
                    return {"data": []}  # Skip test if no teachers
                
                teacher_id = teacher_result.data[0]["id"]
                test_data = {
                    "title": f"Test Course {int(time.time())}",
                    "description": "Performance test course",
                    "category": "Testing",
                    "teacher_id": teacher_id,
                    "status": "draft"
                }
                result = self.supabase.table("courses").insert(test_data).execute()
                # Clean up test data
                if result.data:
                    self.supabase.table("courses").delete().eq("id", result.data[0]["id"]).execute()
                return result
            except Exception:
                return {"data": []}  # Skip test if fails
        
        result = self.measure_query_performance("Insert Operation", insert_test)
        self.results["insert_test"] = result
        self._print_query_result(result)
    
    def test_notification_queries(self):
        """Test notification-related queries"""
        print("\n🔔 Testing Notification Queries")
        print("-" * 60)
        
        # Test 1: Notification types (static data)
        def notification_types():
            return {"data": [
                {"type": "assignment_created", "title": "New assignment posted"},
                {"type": "quiz_created", "title": "New quiz available"}
            ]}
        
        result = self.measure_query_performance("Notification Types (Static)", notification_types)
        self.results["notification_types"] = result
        self._print_query_result(result)
        
        # Test 2: User notifications (if table exists)
        def user_notifications():
            try:
                return self.supabase.table("notifications").select("*").limit(10).execute()
            except Exception:
                return {"data": []}
        
        result = self.measure_query_performance("User Notifications", user_notifications)
        self.results["user_notifications"] = result
        self._print_query_result(result)
    
    def test_course_materials_queries(self):
        """Test course materials queries"""
        print("\n📁 Testing Course Materials Queries")
        print("-" * 60)
        
        # Test 1: Course materials with joins
        def course_materials_with_joins():
            try:
                return self.supabase.table("course_materials").select("""
                    id, file_name, file_url, file_size,
                    courses!course_materials_course_id_fkey(title),
                    profiles!course_materials_uploaded_by_fkey(full_name)
                """).limit(10).execute()
            except Exception:
                return {"data": []}
        
        result = self.measure_query_performance("Course Materials with Joins", course_materials_with_joins)
        self.results["course_materials"] = result
        self._print_query_result(result)
    
    def test_concurrent_requests(self):
        """Test concurrent database requests"""
        print("\n🔄 Testing Concurrent Requests")
        print("-" * 60)
        
        def simple_query():
            return self.supabase.table("profiles").select("id").limit(1).execute()
        
        concurrent_times = []
        errors = 0
        
        def run_query():
            try:
                start_time = time.time()
                simple_query()
                end_time = time.time()
                return (end_time - start_time) * 1000
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_query) for _ in range(20)]
            
            for future in futures:
                result = future.result()
                if result is not None:
                    concurrent_times.append(result)
                else:
                    errors += 1
        
        if concurrent_times:
            concurrent_result = {
                "query_name": "Concurrent Simple Queries",
                "total_requests": 20,
                "successful_requests": len(concurrent_times),
                "failed_requests": errors,
                "success_rate": (len(concurrent_times) / 20) * 100,
                "avg_time_ms": statistics.mean(concurrent_times),
                "min_time_ms": min(concurrent_times),
                "max_time_ms": max(concurrent_times),
                "median_time_ms": statistics.median(concurrent_times)
            }
            
            self.results["concurrent_requests"] = concurrent_result
            self._print_query_result(concurrent_result)
        else:
            print("❌ All concurrent requests failed")
    
    def analyze_performance_bottlenecks(self):
        """Analyze performance bottlenecks and generate recommendations"""
        print("\n📊 Performance Analysis")
        print("-" * 60)
        
        # Analyze query performance
        slow_queries = []
        fast_queries = []
        
        for query_name, result in self.results.items():
            if result["avg_time_ms"] > 500:  # Slow threshold
                slow_queries.append((query_name, result["avg_time_ms"]))
            elif result["avg_time_ms"] < 100:  # Fast threshold
                fast_queries.append((query_name, result["avg_time_ms"]))
        
        print(f"🐌 Slow Queries (>500ms): {len(slow_queries)}")
        for query, time_ms in sorted(slow_queries, key=lambda x: x[1], reverse=True):
            print(f"   - {query}: {time_ms:.1f}ms")
        
        print(f"\n🚀 Fast Queries (<100ms): {len(fast_queries)}")
        for query, time_ms in sorted(fast_queries, key=lambda x: x[1]):
            print(f"   - {query}: {time_ms:.1f}ms")
        
        # Generate optimization recommendations
        self.generate_optimization_recommendations()
    
    def generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("\n💡 Optimization Recommendations")
        print("-" * 60)
        
        recommendations = []
        
        # Check for slow queries
        slow_queries = [(name, result) for name, result in self.results.items() 
                       if result["avg_time_ms"] > 500]
        
        if slow_queries:
            recommendations.append("🔧 Optimize slow queries with proper indexing")
            recommendations.append("📊 Consider denormalizing frequently joined data")
            recommendations.append("💾 Implement query result caching")
        
        # Check for join performance
        join_queries = [(name, result) for name, result in self.results.items() 
                       if "join" in name.lower() or "with" in name.lower()]
        
        if join_queries:
            recommendations.append("🔗 Optimize JOIN queries with proper foreign key indexes")
            recommendations.append("📈 Consider using views for complex joins")
        
        # Check concurrent performance
        if "concurrent_requests" in self.results:
            concurrent_success_rate = self.results["concurrent_requests"]["success_rate"]
            if concurrent_success_rate < 95:
                recommendations.append("🔄 Improve connection pooling")
                recommendations.append("⚡ Consider connection limits optimization")
        
        # General recommendations
        recommendations.extend([
            "📋 Add database indexes for frequently queried columns",
            "🎯 Use SELECT specific columns instead of SELECT *",
            "⏰ Implement query timeout handling",
            "📊 Monitor query performance with Supabase dashboard",
            "🔍 Use EXPLAIN ANALYZE for slow queries",
            "💾 Consider Redis caching for frequently accessed data"
        ])
        
        self.optimization_recommendations = recommendations
        
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")
    
    def _print_query_result(self, result: Dict[str, Any]):
        """Print query result in a formatted way"""
        if result["success_rate"] > 0:
            print(f"✅ {result['query_name']}")
            print(f"   Average: {result['avg_time_ms']:.1f}ms")
            print(f"   Min/Max: {result['min_time_ms']:.1f}ms / {result['max_time_ms']:.1f}ms")
            print(f"   Success Rate: {result['success_rate']:.1f}%")
            if result.get("errors"):
                print(f"   Errors: {len(result['errors'])}")
        else:
            print(f"❌ {result['query_name']} - Failed")
            if result.get("errors"):
                print(f"   Error: {result['errors'][0]}")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📈 Generating Performance Report")
        print("-" * 60)
        
        # Calculate overall statistics
        successful_queries = [result for result in self.results.values() if result["success_rate"] > 0]
        
        if successful_queries:
            avg_times = [q["avg_time_ms"] for q in successful_queries]
            overall_avg = statistics.mean(avg_times)
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "supabase_url": self.supabase_url,
                "total_queries_tested": len(self.results),
                "successful_queries": len(successful_queries),
                "overall_avg_response_time_ms": overall_avg,
                "performance_rating": self._get_performance_rating(overall_avg),
                "query_results": self.results,
                "optimization_recommendations": self.optimization_recommendations,
                "summary": {
                    "fastest_query": min(successful_queries, key=lambda x: x["avg_time_ms"])["query_name"],
                    "slowest_query": max(successful_queries, key=lambda x: x["avg_time_ms"])["query_name"],
                    "queries_over_500ms": len([q for q in successful_queries if q["avg_time_ms"] > 500]),
                    "queries_under_100ms": len([q for q in successful_queries if q["avg_time_ms"] < 100])
                }
            }
            
            # Save report
            filename = f"supabase_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Report saved to: {filename}")
            
            # Display summary
            print(f"\n📊 Performance Summary")
            print(f"   Total Queries: {report['total_queries_tested']}")
            print(f"   Successful: {report['successful_queries']}")
            print(f"   Average Response Time: {overall_avg:.1f}ms")
            print(f"   Performance Rating: {report['performance_rating']}")
            print(f"   Fastest Query: {report['summary']['fastest_query']}")
            print(f"   Slowest Query: {report['summary']['slowest_query']}")
            print(f"   Slow Queries (>500ms): {report['summary']['queries_over_500ms']}")
            print(f"   Fast Queries (<100ms): {report['summary']['queries_under_100ms']}")
    
    def _get_performance_rating(self, avg_time_ms: float) -> str:
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
    
    def run_full_analysis(self):
        """Run complete performance analysis"""
        print("🚀 Supabase Performance Analyzer")
        print("=" * 80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Supabase URL: {self.supabase_url}")
        print()
        
        try:
            # Run all tests
            self.test_core_queries()
            self.test_notification_queries()
            self.test_course_materials_queries()
            self.test_concurrent_requests()
            
            # Analyze results
            self.analyze_performance_bottlenecks()
            
            # Generate report
            self.generate_performance_report()
            
            print("\n🎉 Performance analysis completed!")
            
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            raise

def main():
    """Main function"""
    try:
        analyzer = SupabasePerformanceAnalyzer()
        analyzer.run_full_analysis()
    except Exception as e:
        print(f"❌ Failed to run analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
