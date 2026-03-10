#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Running MBP v2.0 Tests..."
echo ""

echo "1. Unit Tests - Extractors"
python tests/unit/test_extractors.py
echo ""

echo "2. Unit Tests - Hypothesis Generators"
python tests/unit/test_hypothesis.py
echo ""

echo "3. Integration Tests"
python tests/integration/test_flow.py
echo ""

echo "✅ All tests complete!"