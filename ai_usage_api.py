"""
AI Usage Tracking API
Tracks token usage for OpenAI and DeepSeek API calls
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/admin/ai-usage", tags=["ai-usage"])

class AIUsageRecord(BaseModel):
    id: str
    provider: str  # 'openai' or 'deepseek'
    model: str
    tokens_used: int
    cost_usd: float
    request_type: str  # 'quiz_generation', 'content_analysis', etc.
    user_id: Optional[str] = None
    created_at: datetime

class AIUsageStats(BaseModel):
    total_tokens: int
    total_cost: float
    openai_tokens: int
    openai_cost: float
    deepseek_tokens: int
    deepseek_cost: float
    requests_count: int
    avg_tokens_per_request: float

class AIUsageSummary(BaseModel):
    today: AIUsageStats
    this_week: AIUsageStats
    this_month: AIUsageStats
    total: AIUsageStats

@router.get("/stats", response_model=AIUsageSummary)
async def get_ai_usage_stats():
    """Get comprehensive AI usage statistics"""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        # Get all usage records
        all_records_response = supabase.table('ai_usage_logs').select('*').execute()
        all_records = all_records_response.data or []

        # Calculate stats for different periods
        def calculate_stats(records: List[Dict]) -> AIUsageStats:
            if not records:
                return AIUsageStats(
                    total_tokens=0, total_cost=0.0, openai_tokens=0, openai_cost=0.0,
                    deepseek_tokens=0, deepseek_cost=0.0, requests_count=0, avg_tokens_per_request=0.0
                )
            
            total_tokens = sum(r.get('tokens_used', 0) for r in records)
            total_cost = sum(r.get('cost_usd', 0.0) for r in records)
            openai_records = [r for r in records if r.get('provider') == 'openai']
            deepseek_records = [r for r in records if r.get('provider') == 'deepseek']
            
            return AIUsageStats(
                total_tokens=total_tokens,
                total_cost=round(total_cost, 4),
                openai_tokens=sum(r.get('tokens_used', 0) for r in openai_records),
                openai_cost=round(sum(r.get('cost_usd', 0.0) for r in openai_records), 4),
                deepseek_tokens=sum(r.get('tokens_used', 0) for r in deepseek_records),
                deepseek_cost=round(sum(r.get('cost_usd', 0.0) for r in deepseek_records), 4),
                requests_count=len(records),
                avg_tokens_per_request=round(total_tokens / len(records), 2) if records else 0.0
            )

        # Filter records by time periods
        today_records = [r for r in all_records if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= today_start]
        week_records = [r for r in all_records if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= week_start]
        month_records = [r for r in all_records if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= month_start]

        return AIUsageSummary(
            today=calculate_stats(today_records),
            this_week=calculate_stats(week_records),
            this_month=calculate_stats(month_records),
            total=calculate_stats(all_records)
        )

    except Exception as e:
        print(f"Error fetching AI usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent", response_model=List[AIUsageRecord])
async def get_recent_ai_usage(limit: int = Query(20, ge=1, le=100)):
    """Get recent AI usage records"""
    try:
        response = supabase.table('ai_usage_logs').select('*').order('created_at', desc=True).limit(limit).execute()
        
        records = []
        for record in response.data or []:
            records.append(AIUsageRecord(
                id=record['id'],
                provider=record['provider'],
                model=record['model'],
                tokens_used=record['tokens_used'],
                cost_usd=record['cost_usd'],
                request_type=record['request_type'],
                user_id=record.get('user_id'),
                created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
            ))
        
        return records

    except Exception as e:
        print(f"Error fetching recent AI usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log")
async def log_ai_usage(
    provider: str,
    model: str,
    tokens_used: int,
    cost_usd: float,
    request_type: str,
    user_id: Optional[str] = None
):
    """Log AI usage for tracking"""
    try:
        usage_record = {
            'provider': provider,
            'model': model,
            'tokens_used': tokens_used,
            'cost_usd': cost_usd,
            'request_type': request_type,
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        response = supabase.table('ai_usage_logs').insert(usage_record).execute()
        
        if response.data:
            return {"success": True, "message": "AI usage logged successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to log AI usage")

    except Exception as e:
        print(f"Error logging AI usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_provider_breakdown():
    """Get breakdown by AI provider"""
    try:
        response = supabase.table('ai_usage_logs').select('provider, tokens_used, cost_usd').execute()
        
        breakdown = {}
        for record in response.data or []:
            provider = record['provider']
            if provider not in breakdown:
                breakdown[provider] = {'tokens': 0, 'cost': 0.0, 'requests': 0}
            
            breakdown[provider]['tokens'] += record.get('tokens_used', 0)
            breakdown[provider]['cost'] += record.get('cost_usd', 0.0)
            breakdown[provider]['requests'] += 1

        # Round costs
        for provider in breakdown:
            breakdown[provider]['cost'] = round(breakdown[provider]['cost'], 4)

        return breakdown

    except Exception as e:
        print(f"Error getting provider breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))
