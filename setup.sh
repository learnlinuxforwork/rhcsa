#!/usr/bin/env bash
# Create the GitHub repo and push. Requires the GitHub CLI: https://cli.github.com
set -uo pipefail
ORG="learnlinuxforwork"; REPO="rhcsa"; DOMAIN="rhcsa.learnlinuxforwork.com"
command -v gh >/dev/null || { echo "gh is not installed."; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Run 'gh auth login' first."; exit 1; }

git init -b main
git add -A
git commit -m "Free RHCSA Course: initial release

12-week course for the Red Hat Certified System Administrator exam (EX200, RHEL 10).
Ten sections, twelve standalone lab guides, home lab setup for VirtualBox / VMware
Workstation / KVM / Proxmox / UTM, and every published exam objective mapped to a week.
All content original. Licensed AGPL-3.0-or-later."

gh repo create "$ORG/$REPO" --public --source=. --remote=origin \
  --description "Free 12-week RHCSA course (EX200, RHEL 10). Twelve hands-on lab guides, home lab setup, and every exam objective covered." \
  --homepage "https://$DOMAIN" --push

gh repo edit "$ORG/$REPO" --add-topic rhcsa,redhat,rhel,linux,certification,ex200,sysadmin,homelab,free,selinux

cat <<EOF

Pushed. Two manual steps remain:
  1. Settings -> Pages -> Source: GitHub Actions
  2. Settings -> Pages -> Custom domain: $DOMAIN, then tick Enforce HTTPS
DNS is already configured for $DOMAIN.
EOF
