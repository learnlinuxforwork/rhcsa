#!/usr/bin/env bash
#
# build-podman-lab.sh — a two-"machine" RHCSA practice lab in Rocky Linux
#                       containers, for when you have no spare RAM at all.
#
# Free RHCSA Course — rhcsa.learnlinuxforwork.com
# Copyright (C) 2026 Shea's Tech. Licensed under the GNU AGPL v3.0 or later.
#
# HONEST LIMITATIONS — read this first
#   Containers share the host kernel. That means these are perfect for roughly
#   two thirds of the exam and useless for the rest:
#
#     Works well    users and groups, permissions, ACLs, sudo, dnf/RPM, Flatpak
#                   basics, processes, scripting, text tools, SELinux contexts
#                   and booleans, cron syntax, archives, SSH between the two
#     Does NOT work partitioning, LVM, filesystems, swap, fstab, the bootloader,
#                   boot targets, rd.break recovery, kernel tuning, real
#                   firewalld, NetworkManager
#
#   Use this to drill Weeks 1-4, 10 (partly), and 11 on a low-spec machine.
#   You still need real VMs for Weeks 5-9. There is no way around that, and
#   anyone who tells you otherwise has not sat the exam.
#
# USAGE
#   ./build-podman-lab.sh           # create servera + serverb containers
#   ./build-podman-lab.sh --shell   # drop into servera
#   ./build-podman-lab.sh --destroy
#
set -uo pipefail

NET="rhcsa-net"
A="servera"; B="serverb"
IMAGE="${RHCSA_IMAGE:-docker.io/rockylinux/rockylinux:10}"
USER_NAME="shea"

c()  { printf '\033[1;31m%s\033[0m\n' "$*"; }
ok() { printf '  \033[0;32mok\033[0m  %s\n' "$*"; }
die(){ printf '\n\033[1;31mSTOPPED:\033[0m %s\n' "$*"; exit 1; }

command -v podman >/dev/null || die "podman not installed.
  Fedora/RHEL/Rocky:  sudo dnf install -y podman
  Debian/Ubuntu:      sudo apt install -y podman
  macOS:              brew install podman && podman machine init && podman machine start"

case "${1:-}" in
  --destroy)
    podman rm -f "$A" "$B" 2>/dev/null && ok "containers removed"
    podman network rm "$NET" 2>/dev/null && ok "network removed"
    exit 0 ;;
  --shell)
    exec podman exec -it "$A" /bin/bash ;;
esac

c "Creating the lab network"
podman network exists "$NET" 2>/dev/null || podman network create "$NET" >/dev/null
ok "$NET"

c "Pulling $IMAGE"
podman pull "$IMAGE" >/dev/null || die "Could not pull $IMAGE"
ok "image ready"

make_node() {
  local NAME=$1
  podman rm -f "$NAME" >/dev/null 2>&1
  c "Creating $NAME"
  # --systemd=always gives us a working systemctl inside the container, which
  # is what makes the service-management practice meaningful.
  podman run -d --name "$NAME" --hostname "$NAME" --network "$NET" \
    --systemd=always --cap-add SYS_ADMIN \
    "$IMAGE" /sbin/init >/dev/null || die "Could not start $NAME"

  # Give it the tools the early weeks need.
  podman exec "$NAME" bash -lc '
    dnf -y install --setopt=install_weak_deps=False \
      passwd sudo openssh-server openssh-clients procps-ng iproute \
      cronie tar gzip bzip2 findutils grep sed gawk vim-minimal \
      policycoreutils policycoreutils-python-utils man-db man-pages \
      >/dev/null 2>&1
    ssh-keygen -A >/dev/null 2>&1
    systemctl enable sshd crond >/dev/null 2>&1
  ' || true

  # Create the working user used throughout the course.
  podman exec "$NAME" bash -lc "
    useradd -m -s /bin/bash $USER_NAME 2>/dev/null
    echo '$USER_NAME:rhcsa' | chpasswd
    echo '$USER_NAME ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/$USER_NAME
    chmod 0440 /etc/sudoers.d/$USER_NAME
  " || true
  ok "$NAME up — user '$USER_NAME', password 'rhcsa'"
}

make_node "$A"
make_node "$B"

c "Checking the two nodes can reach each other"
podman exec "$A" bash -lc "getent hosts $B >/dev/null && echo reachable" || \
  echo "  (they resolve each other by container name on the $NET network)"

cat <<EOF

$(c "Container lab ready.")

  Enter servera:     podman exec -it $A /bin/bash
  Enter serverb:     podman exec -it $B /bin/bash
  As the course user: podman exec -it -u $USER_NAME $A /bin/bash
  Stop for now:      podman stop $A $B
  Start again:       podman start $A $B
  Remove entirely:   $0 --destroy

$(c "What to practise here")

  Week 1   shell, redirection, grep, links, permissions, archives
  Week 2   users, groups, password aging, sudo drop-in files
  Week 3   dnf, rpm queries, repository files
  Week 4   processes, signals, nice/renice, cron
  Week 10  SELinux contexts and booleans, umask, SSH keys between the nodes
  Week 11  all of the shell scripting

$(c "What you still need real VMs for")

  Weeks 5-9: boot targets, rd.break recovery, the bootloader, partitioning,
  LVM, filesystems, swap, fstab, NFS, autofs, firewalld, NetworkManager.

  Build those with:   ./build-local-lab.sh
  Or in the cloud:    ./build-cloud-lab.sh gcp

  Or use the browser-based hands-on labs, which need no setup at all:
      https://www.learnlinuxforwork.com
      https://www.redhat.com/en/interactive-labs
EOF
