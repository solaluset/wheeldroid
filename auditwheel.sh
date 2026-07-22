#!/bin/bash

output=$(auditwheel repair --ldpaths "$LDPATHS" -w "$DEST_DIR" "$WHEEL" 2>&1)
exit_code=$?
cat <<< "$output"

if grep -q "This does not look like a platform wheel" <<< "$output"; then
  cp "$WHEEL" "$DEST_DIR"
  # stfu
  exit 0
fi
exit $exit_code
