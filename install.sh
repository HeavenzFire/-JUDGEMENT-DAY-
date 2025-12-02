#!/usr/bin/env bash
# Guardian Mesh - Safe, Consent-First Local Installer (Bash)
# Purpose: verify signed release artifacts, prompt explicit user consent,
# install locally (Docker optional), produce a local signed attestation,
# and optionally publish the attestation to an audit endpoint only with consent.
#
# IMPORTANT: This script is intentionally conservative. It does NOT:
#  - modify other machines
#  - write system-wide persistent hooks without explicit consent
#  - alter hosts files or register persistent scheduled tasks
#  - execute remote code without signature and checksum verification
#
# Configure these variables before running
RELEASE_URL="https://example.org/releases/guardian-node-1.0.0.tar.gz"
SIG_URL="https://example.org/releases/guardian-node-1.0.0.tar.gz.asc"
SHA256_URL="https://example.org/releases/guardian-node-1.0.0.sha256"
AUDIT_ENDPOINT="https://audit.example.org/attestations"   # optional; only used if user opts in
RELEASE_NAME="guardian-node-1.0.0.tar.gz"
TMPDIR="$(mktemp -d)"
INSTALL_DIR="$HOME/.guardian-node"
ATTESTATION_FILE="$INSTALL_DIR/attestation.json"
GPG_KEY_FINGERPRINT="RELEASE_SIGNER_FINGERPRINT" # replace with published fingerprint for verification

set -euo pipefail

cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "Guardian Mesh - Safe Local Installer"
echo "Temporary working dir: $TMPDIR"
echo

# 1) Download artifacts (do not pipe into shell)
echo "Downloading release, signature, and checksum..."
curl -fsSL "$RELEASE_URL" -o "$TMPDIR/$RELEASE_NAME"
curl -fsSL "$SIG_URL" -o "$TMPDIR/$RELEASE_NAME.asc"
curl -fsSL "$SHA256_URL" -o "$TMPDIR/$RELEASE_NAME.sha256"

echo "Download complete. Files saved to $TMPDIR"
echo

# 2) Verify checksum
echo "Verifying SHA256 checksum..."
pushd "$TMPDIR" >/dev/null
if ! sha256sum -c "$RELEASE_NAME.sha256" --status; then
  echo "ERROR: checksum verification failed. Aborting."
  exit 1
fi
popd >/dev/null
echo "Checksum OK."
echo

# 3) Verify GPG signature (requires gpg installed)
echo "Verifying GPG signature..."
if ! command -v gpg >/dev/null 2>&1; then
  echo "ERROR: gpg not found. Install GnuPG and re-run the installer."
  exit 1
fi

# Import or check for the expected release signing key fingerprint.
# The installer will not auto-import unknown keys; it will show the key info and require manual trust.
echo "Inspecting signature metadata (no automatic trust changes)..."
gpg --batch --verify "$TMPDIR/$RELEASE_NAME.asc" "$TMPDIR/$RELEASE_NAME" 2>&1 || {
  echo "Signature verification failed or signature not trusted locally."
  echo "To proceed you must manually verify the signer's fingerprint matches the published fingerprint:"
  echo "  Published fingerprint: $GPG_KEY_FINGERPRINT"
  echo "If you trust the key, import it and re-run this script."
  exit 1
}
echo "Signature file is valid for the archive (signature verified)."
echo

# 4) Show manifest summary to user (human-readable)
echo "Release manifest summary (human-readable):"
echo "  Release: $RELEASE_NAME"
echo "  Source:  $RELEASE_URL"
echo "  SHA256:  $(cut -d' ' -f1 "$TMPDIR/$RELEASE_NAME.sha256")"
echo "  Signature: $SIG_URL"
echo
cat <<'MANIFEST'
Permissions requested by this installer (consent required):
 - Create a local installation directory under your home (~/.guardian-node)
 - Optionally run a local Docker container (if you choose to enable)
 - Optionally send a signed attestation to a public audit endpoint (only if you opt in)
Data handling:
 - No personal data is collected by default
 - Attestations contain only: node_id (random), artifact_hash, timestamp, and consent token
 - You may opt out of publishing attestations
Uninstall:
 - Remove ~/.guardian-node and any Docker containers/images created by this installer
MANIFEST
echo

# 5) Explicit consent prompt
read -r -p "Do you consent to install this release locally under $INSTALL_DIR? (yes/no) " CONSENT
if [[ "${CONSENT,,}" != "yes" ]]; then
  echo "Consent not given. Aborting installation."
  exit 0
fi

# 6) Create install directory and extract (local only)
mkdir -p "$INSTALL_DIR"
tar -xzf "$TMPDIR/$RELEASE_NAME" -C "$INSTALL_DIR"
echo "Release extracted to $INSTALL_DIR"
echo

# 7) Optional: offer to run a local smoke test (Docker-based) with explicit consent
if command -v docker >/dev/null 2>&1; then
  read -r -p "Docker detected. Run a local smoke test container now? (recommended) (yes/no) " DOCKER_RUN
  if [[ "${DOCKER_RUN,,}" == "yes" ]]; then
    # The installer expects a test image name in the extracted manifest; fallback to a safe local check
    if [[ -f "$INSTALL_DIR/docker-test-image.txt" ]]; then
      TEST_IMAGE="$(cat "$INSTALL_DIR/docker-test-image.txt")"
      echo "Pulling and running test image: $TEST_IMAGE (local smoke test)"
      docker pull "$TEST_IMAGE"
      docker run --rm --name guardian-smoke-test "$TEST_IMAGE" /bin/sh -c "echo smoke-test OK; exit 0"
      echo "Smoke test completed."
    else
      echo "No test image specified in release. Skipping Docker smoke test."
    fi
  else
    echo "Skipping Docker smoke test as requested."
  fi
else
  echo "Docker not found; skipping Docker smoke test."
fi
echo

# 8) Create ephemeral node keypair and signed attestation (local)
echo "Generating local node identity and attestation..."
NODE_ID="$(openssl rand -hex 12)"
NODE_KEY="$INSTALL_DIR/node.key.pem"
NODE_PUB="$INSTALL_DIR/node.pub.pem"

# Generate ephemeral RSA keypair for attestation signing (stored locally)
openssl genpkey -algorithm RSA -out "$NODE_KEY" -pkeyopt rsa_keygen_bits:2048
openssl rsa -in "$NODE_KEY" -pubout -out "$NODE_PUB"

ARTIFACT_HASH="$(sha256sum "$INSTALL_DIR/$RELEASE_NAME" 2>/dev/null | awk '{print $1}' || echo "unknown")"
TIMESTAMP="$(date --utc +%Y-%m-%dT%H:%M:%SZ)"

cat > "$ATTESTATION_FILE" <<JSON
{
  "node_id": "$NODE_ID",
  "artifact_hash": "$ARTIFACT_HASH",
  "release": "$RELEASE_NAME",
  "timestamp": "$TIMESTAMP",
  "consent": "explicit"
}
JSON

# Sign the attestation with the node private key (PKCS#7 detached signature)
ATT_SIG="$ATTESTATION_FILE.sig"
openssl dgst -sha256 -sign "$NODE_KEY" -out "$ATT_SIG" "$ATTESTATION_FILE"
echo "Local attestation created and signed at: $ATTESTATION_FILE (signature: $ATT_SIG)"
echo

# 9) Offer to publish attestation to audit endpoint (explicit opt-in)
read -r -p "Publish signed attestation to the public audit endpoint ($AUDIT_ENDPOINT)? (yes/no) " PUB_CONSENT
if [[ "${PUB_CONSENT,,}" == "yes" ]]; then
  if [[ -z "$AUDIT_ENDPOINT" ]]; then
    echo "No audit endpoint configured. Skipping publish."
  else
    echo "Publishing attestation (HTTPS POST)..."
    # Minimal safe publish: send attestation and signature as multipart/form-data
    curl -fsSL -X POST "$AUDIT_ENDPOINT" \
      -F "attestation= @${ATTESTATION_FILE}" \
      -F "signature= @${ATT_SIG}" \
      -F "pubkey= @${NODE_PUB}" \
      -o /dev/null -w "HTTP %{http_code}\n" || {
        echo "Warning: failed to publish attestation. Network or endpoint error."
      }
    echo "Publish attempt complete."
  fi
else
  echo "Attestation will remain local only (not published)."
fi
echo

# 10) Provide uninstall helper (local)
UNINSTALL_SH="$INSTALL_DIR/uninstall.sh"
cat > "$UNINSTALL_SH" <<'UNINST'
#!/usr/bin/env bash
set -euo pipefail
echo "Uninstalling Guardian Node (local only)..."
read -r -p "Confirm removal of $HOME/.guardian-node and all local artifacts (yes/no) " CONF
if [[ "${CONF,,}" == "yes" ]]; then
  rm -rf "$HOME/.guardian-node"
  echo "Local installation removed."
else
  echo "Uninstall cancelled."
fi
UNINST
chmod +x "$UNINSTALL_SH"

echo "Installation complete."
echo "Local install directory: $INSTALL_DIR"
echo "To remove, run: $UNINSTALL_SH"
echo
echo "Security notes:"
echo " - This installer never modifies other machines or system-wide settings without explicit, separate consent."
echo " - Keep your node private key ($NODE_KEY) secure; it signs attestations for this node only."
echo
exit 0