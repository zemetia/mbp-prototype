#!/bin/bash
# MBP Backend QA Test Script
# Tests all API endpoints using curl

cd /mnt/d/Yoel/Projects/mbp-prototype/backend-v2/

BASE_URL="http://localhost:8000"
API_URL="http://localhost:8000/api"

PASS=0
FAIL=0

log_pass() {
    echo "✅ $1"
    ((PASS++))
}

log_fail() {
    echo "❌ $1"
    echo "   Error: $2"
    ((FAIL++))
}

echo "🧪 MBP Backend v2.0 - API QA Testing"
echo "======================================"

# Start server
echo ""
echo "🚀 Starting server..."
source venv/bin/activate
python3 -c "import uvicorn; uvicorn.run('api.main:app', host='0.0.0.0', port=8000, reload=False, log_level='error')" &
SERVER_PID=$!
sleep 6

# Verify server is running
echo ""
echo "1. HEALTH CHECKS"
echo "================"
HEALTH=$(curl -s http://localhost:8000/health)
if [ -n "$HEALTH" ]; then
    log_pass "GET /health - Server running"
else
    log_fail "GET /health" "No response"
fi

HEALTH_API=$(curl -s http://localhost:8000/api/health)
if [ -n "$HEALTH_API" ]; then
    log_pass "GET /api/health"
else
    log_fail "GET /api/health" "No response"
fi

# Test Personal Data
echo ""
echo "2. PERSONAL DATA"
echo "================"
PD_RESPONSE=$(curl -s -X POST "$API_URL/personal-data" \
    -H "Content-Type: application/json" \
    -d '{"nama":"Budi Santoso","tanggal_lahir":"15/05/1990","tempat_lahir":"Jakarta","agama":"Islam"}')
PD_ID=$(echo $PD_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('personal_data_id',''))" 2>/dev/null)

if [ -n "$PD_ID" ]; then
    log_pass "POST /api/personal-data - ID: ${PD_ID:0:8}..."
else
    log_fail "POST /api/personal-data" "$PD_RESPONSE"
fi

if [ -n "$PD_ID" ]; then
    PD_GET=$(curl -s "$API_URL/personal-data/$PD_ID")
    if echo "$PD_GET" | grep -q "Budi Santoso"; then
        log_pass "GET /api/personal-data/{id}"
    else
        log_fail "GET /api/personal-data/{id}" "$PD_GET"
    fi
    
    # Test 404
    PD_404=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/personal-data/invalid-id")
    if [ "$PD_404" = "404" ]; then
        log_pass "GET /api/personal-data/{invalid-id} - Returns 404"
    else
        log_fail "GET /api/personal-data/{invalid-id}" "Expected 404, got $PD_404"
    fi
fi

# Test Sessions
echo ""
echo "3. SESSIONS"
echo "==========="
SESSION_RESP=$(curl -s -X POST "$API_URL/sessions" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test_user","metadata":{}}')
SESSION_ID=$(echo $SESSION_RESP | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
    log_pass "POST /api/sessions - ID: ${SESSION_ID:0:8}..."
else
    log_fail "POST /api/sessions" "$SESSION_RESP"
fi

# Test session with personal data
if [ -n "$PD_ID" ]; then
    SESSION_PD=$(curl -s -X POST "$API_URL/sessions/with-personal-data" \
        -H "Content-Type: application/json" \
        -d "{\"personal_data_id\":\"$PD_ID\",\"metadata\":{}}")
    SESSION_PD_ID=$(echo $SESSION_PD | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
    
    if [ -n "$SESSION_PD_ID" ]; then
        log_pass "POST /api/sessions/with-personal-data"
    else
        log_fail "POST /api/sessions/with-personal-data" "$SESSION_PD"
    fi
    
    # Test invalid personal data
    SESSION_PD_404=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/sessions/with-personal-data" \
        -H "Content-Type: application/json" \
        -d '{"personal_data_id":"invalid-id"}')
    if [ "$SESSION_PD_404" = "404" ]; then
        log_pass "POST /api/sessions/with-personal-data (invalid) - Returns 404"
    else
        log_fail "POST /api/sessions/with-personal-data (invalid)" "Expected 404, got $SESSION_PD_404"
    fi
fi

# Get session state
if [ -n "$SESSION_ID" ]; then
    SESSION_STATE=$(curl -s "$API_URL/sessions/$SESSION_ID")
    if echo "$SESSION_STATE" | grep -q "phase"; then
        log_pass "GET /api/sessions/{id}"
    else
        log_fail "GET /api/sessions/{id}" "$SESSION_STATE"
    fi
    
    # Test 404
    SESSION_404=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/sessions/invalid-id")
    if [ "$SESSION_404" = "404" ]; then
        log_pass "GET /api/sessions/{invalid-id} - Returns 404"
    else
        log_fail "GET /api/sessions/{invalid-id}" "Expected 404, got $SESSION_404"
    fi
fi

# Test respond endpoint
if [ -n "$SESSION_ID" ]; then
    RESPOND=$(curl -s -X POST "$API_URL/sessions/$SESSION_ID/respond" \
        -H "Content-Type: application/json" \
        -d '{"message":"Saya sering merasa cemas"}')
    
    if echo "$RESPOND" | grep -q "phase"; then
        log_pass "POST /api/sessions/{id}/respond"
    elif echo "$RESPOND" | grep -q "Processing error"; then
        ERROR_MSG=$(echo "$RESPOND" | python3 -c "import sys,json; print(json.load(sys.stdin).get('detail',''))" 2>/dev/null)
        log_fail "POST /api/sessions/{id}/respond" "$ERROR_MSG"
    else
        log_fail "POST /api/sessions/{id}/respond" "$RESPOND"
    fi
    
    # Test profile (should be 400 for incomplete)
    PROFILE_400=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/sessions/$SESSION_ID/profile")
    if [ "$PROFILE_400" = "400" ]; then
        log_pass "GET /api/sessions/{id}/profile (incomplete) - Returns 400"
    else
        log_fail "GET /api/sessions/{id}/profile" "Expected 400, got $PROFILE_400"
    fi
fi

# Test Analyses
echo ""
echo "4. ANALYSES"
echo "==========="
if [ -n "$PD_ID" ] && [ -n "$SESSION_ID" ]; then
    ANALYSIS=$(curl -s -X POST "$API_URL/analyses" \
        -H "Content-Type: application/json" \
        -d "{\"personal_data_id\":\"$PD_ID\",\"session_id\":\"$SESSION_ID\",\"final_profile\":{\"test\":\"data\"},\"executive_summary\":\"Test summary\",\"core_insights\":[],\"tensions\":[]}")
    ANALYSIS_ID=$(echo $ANALYSIS | python3 -c "import sys,json; print(json.load(sys.stdin).get('analysis_id',''))" 2>/dev/null)
    
    if [ -n "$ANALYSIS_ID" ]; then
        log_pass "POST /api/analyses - ID: ${ANALYSIS_ID:0:8}..."
    else
        log_fail "POST /api/analyses" "$ANALYSIS"
    fi
    
    # Test invalid personal data
    ANALYSIS_404=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/analyses" \
        -H "Content-Type: application/json" \
        -d "{\"personal_data_id\":\"invalid\",\"session_id\":\"$SESSION_ID\",\"final_profile\":{}}")
    if [ "$ANALYSIS_404" = "404" ]; then
        log_pass "POST /api/analyses (invalid PD) - Returns 404"
    else
        log_fail "POST /api/analyses (invalid PD)" "Expected 404, got $ANALYSIS_404"
    fi
    
    # Test invalid session
    ANALYSIS_404B=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/analyses" \
        -H "Content-Type: application/json" \
        -d "{\"personal_data_id\":\"$PD_ID\",\"session_id\":\"invalid\",\"final_profile\":{}}")
    if [ "$ANALYSIS_404B" = "404" ]; then
        log_pass "POST /api/analyses (invalid session) - Returns 404"
    else
        log_fail "POST /api/analyses (invalid session)" "Expected 404, got $ANALYSIS_404B"
    fi
    
    # List analyses
    LIST=$(curl -s "$API_URL/analyses")
    if echo "$LIST" | grep -q "analyses"; then
        log_pass "GET /api/analyses"
    else
        log_fail "GET /api/analyses" "$LIST"
    fi
    
    # Filtered list
    LIST_FILTER=$(curl -s "$API_URL/analyses?personal_data_id=$PD_ID")
    if echo "$LIST_FILTER" | grep -q "analyses"; then
        log_pass "GET /api/analyses?personal_data_id=..."
    else
        log_fail "GET /api/analyses?personal_data_id=..." "$LIST_FILTER"
    fi
    
    # Get analysis detail
    if [ -n "$ANALYSIS_ID" ]; then
        DETAIL=$(curl -s "$API_URL/analyses/$ANALYSIS_ID")
        if echo "$DETAIL" | grep -q "analysis_id"; then
            log_pass "GET /api/analyses/{id}"
        else
            log_fail "GET /api/analyses/{id}" "$DETAIL"
        fi
        
        # Test 404
        DETAIL_404=$(curl -s -w "%{http_code}" -o /dev/null "$API_URL/analyses/invalid-id")
        if [ "$DETAIL_404" = "404" ]; then
            log_pass "GET /api/analyses/{invalid-id} - Returns 404"
        else
            log_fail "GET /api/analyses/{invalid-id}" "Expected 404, got $DETAIL_404"
        fi
    fi
fi

# Test validation
echo ""
echo "5. VALIDATION"
echo "============="
# Empty message
if [ -n "$SESSION_ID" ]; then
    EMPTY_MSG=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/sessions/$SESSION_ID/respond" \
        -H "Content-Type: application/json" \
        -d '{"message":""}')
    if [ "$EMPTY_MSG" = "422" ]; then
        log_pass "Validation: Empty message - Returns 422"
    else
        log_fail "Validation: Empty message" "Expected 422, got $EMPTY_MSG"
    fi
fi

# Missing fields
MISSING_FIELDS=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/personal-data" \
    -H "Content-Type: application/json" \
    -d '{"nama":"Test"}')
if [ "$MISSING_FIELDS" = "422" ]; then
    log_pass "Validation: Missing fields - Returns 422"
else
    log_fail "Validation: Missing fields" "Expected 422, got $MISSING_FIELDS"
fi

# Summary
echo ""
echo "======================================"
echo "📊 TEST SUMMARY"
echo "======================================"
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
    RATE=$(awk "BEGIN {printf \"%.1f\", ($PASS/$TOTAL)*100}")
    echo "📈 Success Rate: $RATE%"
fi

# Stop server
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
if [ $FAIL -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "⚠️ SOME TESTS FAILED"
    exit 1
fi
