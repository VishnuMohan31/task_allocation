#!/usr/bin/env bash
# Reads testresults_dir from pytest.ini and saves each test file's output there.

RESULTS_DIR=$(grep 'testresults_dir' pytest.ini | awk '{print $3}')
RESULTS_DIR=$(echo "$RESULTS_DIR" | tr -d '\r')
mkdir -p "$RESULTS_DIR"

for TEST_FILE in tests/test_*.py; do
    BASENAME=$(basename "$TEST_FILE" .py)
    OUTPUT_FILE="${RESULTS_DIR}/${BASENAME}.txt"
    echo "Running $TEST_FILE -> $OUTPUT_FILE"
    python -m pytest "$TEST_FILE" -v --tb=short 2>&1 | tee "$OUTPUT_FILE"
done

echo ""
echo "All results saved to: $RESULTS_DIR"
