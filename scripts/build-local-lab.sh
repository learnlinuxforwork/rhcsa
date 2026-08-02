#!/usr/bin/env bash
#
# build-local-lab.sh — create the two-machine RHCSA lab on a Linux laptop
#                      using Oracle VirtualBox or VMware Workstation Pro.
#
# RHCSA Course — rhcsa.learnlinuxforwork.com
# Copyright (C) 2026 Shea's Tech. Licensed under the GNU AGPL v3.0 or later.
#
# WHAT IT DOES
#   1. Creates /rhcsa-labs and tells you exactly which ISO to drop in it
#   2. Creates two VMs — servera (primary) and serverb (secondary)
#   3. Gives servera a second 10 GB disk for the Week 8 and 9 storage labs
#   4. Puts both on a private host-only network plus NAT for package installs
#   5. Boots them from the ISO so you can run the installer
#
# USAGE
#   ./build-local-lab.sh                    # VirtualBox, auto-detect ISO
#   ./build-local-lab.sh --provider vmware  # VMware Workstation Pro
#   ./build-local-lab.sh --iso /rhcsa-labs/rhel-10.1-x86_64-dvd.iso
#   ./build-local-lab.sh --destroy          # remove the VMs and start over
#
# WHERE TO GET THE ISO  (download it yourself, then put it in /rhcsa-labs)
#   RHEL 10   https://developers.redhat.com/products/rhel/download
#   Rocky 10  https://rockylinux.org/download
#
set -uo pipefail

LAB_DIR="/rhcsa-labs"
PROVIDER="virtualbox"
ISO=""
NET="rhcsalab"
NET_CIDR="192.168.56"
VM_A="servera"; VM_B="serverb"
RAM_A=4096; CPU_A=2; DISK_A=20480; DISK_EXTRA=10240
RAM_B=2048; CPU_B=1; DISK_B=20480

c()  { printf '\033[1;31m%s\033[0m\n' "$*"; }
ok() { printf '  \033[0;32mok\033[0m  %s\n' "$*"; }
die(){ printf '\n\033[1;31mSTOPPED:\033[0m %s\n' "$*"; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --provider) PROVIDER="${2:-}"; shift 2 ;;
    --iso)      ISO="${2:-}"; shift 2 ;;
    --destroy)  DESTROY=1; shift ;;
    -h|--help)  sed -n '2,30p' "$0"; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

# ---------------------------------------------------------------- lab dir --
if [ ! -d "$LAB_DIR" ]; then
  c "Creating $LAB_DIR"
  sudo mkdir -p "$LAB_DIR" || die "Could not create $LAB_DIR"
  sudo chown "$USER":"$USER" "$LAB_DIR"
  ok "$LAB_DIR created and owned by $USER"
fi

if [ -z "$ISO" ]; then
  ISO=$(find "$LAB_DIR" -maxdepth 1 -iname '*.iso' | head -1)
fi

if [ -z "$ISO" ] || [ ! -f "$ISO" ]; then
  cat <<EOF

No ISO found in $LAB_DIR.

Download one of these, save it into $LAB_DIR, then run this script again:

  RHEL 10   https://developers.redhat.com/products/rhel/download
            (free Developer Subscription — covers 16 systems)
  Rocky 10  https://rockylinux.org/download

From a Linux laptop you can pull Rocky straight down with:

  cd $LAB_DIR
  curl -LO https://download.rockylinux.org/pub/rocky/10/isos/x86_64/Rocky-10-latest-x86_64-dvd.iso

EOF
  exit 1
fi
ok "Using ISO: $ISO"

# ============================================================== VIRTUALBOX ==
build_virtualbox() {
  command -v VBoxManage >/dev/null || die "VBoxManage not found. Install VirtualBox: https://www.virtualbox.org/"

  if [ "${DESTROY:-0}" = "1" ]; then
    for vm in "$VM_A" "$VM_B"; do
      VBoxManage unregistervm "$vm" --delete 2>/dev/null && ok "removed $vm"
    done
    exit 0
  fi

  # private network for servera <-> serverb
  if ! VBoxManage list hostonlyifs | grep -q "$NET_CIDR"; then
    c "Creating host-only network"
    IF=$(VBoxManage hostonlyif create 2>/dev/null | sed -n "s/.*'\(.*\)'.*/\1/p")
    VBoxManage hostonlyif ipconfig "$IF" --ip "${NET_CIDR}.1" --netmask 255.255.255.0
    ok "host-only network $IF at ${NET_CIDR}.1"
  fi
  HOSTIF=$(VBoxManage list hostonlyifs | awk '/^Name:/{n=$2} /IPAddress:/{if($2 ~ /'"$NET_CIDR"'/) print n}' | head -1)

  make_vm() {
    local NAME=$1 RAM=$2 CPU=$3 DISK=$4 EXTRA=${5:-0} IP4=$6
    VBoxManage showvminfo "$NAME" >/dev/null 2>&1 && { ok "$NAME already exists — skipping"; return; }
    c "Creating $NAME"
    VBoxManage createvm --name "$NAME" --ostype RedHat_64 --register >/dev/null
    VBoxManage modifyvm "$NAME" --memory "$RAM" --cpus "$CPU" --firmware efi \
      --nic1 nat --nic2 hostonly --hostonlyadapter2 "$HOSTIF" \
      --graphicscontroller vmsvga --vram 16 --audio-driver none >/dev/null
    VBoxManage storagectl "$NAME" --name SATA --add sata --controller IntelAhci --portcount 4 >/dev/null
    local DIR; DIR=$(VBoxManage showvminfo "$NAME" --machinereadable | sed -n 's/^CfgFile="\(.*\)\/.*/\1/p')
    VBoxManage createmedium disk --filename "$DIR/${NAME}.vdi" --size "$DISK" --format VDI >/dev/null
    VBoxManage storageattach "$NAME" --storagectl SATA --port 0 --device 0 --type hdd \
      --medium "$DIR/${NAME}.vdi" >/dev/null
    if [ "$EXTRA" -gt 0 ]; then
      VBoxManage createmedium disk --filename "$DIR/${NAME}-extra.vdi" --size "$EXTRA" --format VDI >/dev/null
      VBoxManage storageattach "$NAME" --storagectl SATA --port 1 --device 0 --type hdd \
        --medium "$DIR/${NAME}-extra.vdi" >/dev/null
      ok "$NAME: added ${EXTRA}MB spare disk for the Week 8 and 9 storage labs"
    fi
    VBoxManage storageattach "$NAME" --storagectl SATA --port 3 --device 0 --type dvddrive --medium "$ISO" >/dev/null
    VBoxManage modifyvm "$NAME" --boot1 dvd --boot2 disk >/dev/null
    ok "$NAME created — ${RAM}MB RAM, ${CPU} vCPU, static IP to set: ${IP4}"
  }

  make_vm "$VM_A" "$RAM_A" "$CPU_A" "$DISK_A" "$DISK_EXTRA" "${NET_CIDR}.10"
  make_vm "$VM_B" "$RAM_B" "$CPU_B" "$DISK_B" 0            "${NET_CIDR}.11"

  c "Starting both VMs so you can run the installer"
  VBoxManage startvm "$VM_A" --type gui >/dev/null 2>&1 || true
  VBoxManage startvm "$VM_B" --type gui >/dev/null 2>&1 || true
}

# ================================================================= VMWARE ===
build_vmware() {
  command -v vmrun >/dev/null || die "vmrun not found. Install VMware Workstation Pro (free for personal use): https://www.vmware.com/products/desktop-hypervisor/workstation-and-fusion"
  mkdir -p "$LAB_DIR/vmware"

  write_vmx() {
    local NAME=$1 RAM=$2 CPU=$3 DISK_GB=$4 EXTRA_GB=${5:-0}
    local D="$LAB_DIR/vmware/$NAME"; mkdir -p "$D"
    vmware-vdiskmanager -c -s "${DISK_GB}GB" -a lsilogic -t 1 "$D/${NAME}.vmdk" >/dev/null 2>&1
    [ "$EXTRA_GB" -gt 0 ] && vmware-vdiskmanager -c -s "${EXTRA_GB}GB" -a lsilogic -t 1 "$D/${NAME}-extra.vmdk" >/dev/null 2>&1
    cat > "$D/${NAME}.vmx" <<VMX
.encoding = "UTF-8"
config.version = "8"
virtualHW.version = "19"
displayName = "$NAME"
guestOS = "rhel9-64"
firmware = "efi"
memsize = "$RAM"
numvcpus = "$CPU"
scsi0.present = "TRUE"
scsi0.virtualDev = "lsilogic"
scsi0:0.present = "TRUE"
scsi0:0.fileName = "${NAME}.vmdk"
$( [ "$EXTRA_GB" -gt 0 ] && printf 'scsi0:1.present = "TRUE"\nscsi0:1.fileName = "%s-extra.vmdk"\n' "$NAME" )
ide1:0.present = "TRUE"
ide1:0.deviceType = "cdrom-image"
ide1:0.fileName = "$ISO"
ethernet0.present = "TRUE"
ethernet0.connectionType = "nat"
ethernet0.virtualDev = "e1000e"
ethernet1.present = "TRUE"
ethernet1.connectionType = "hostonly"
ethernet1.virtualDev = "e1000e"
usb.present = "TRUE"
sound.present = "FALSE"
VMX
    ok "$NAME.vmx written to $D"
    vmrun -T ws start "$D/${NAME}.vmx" nogui >/dev/null 2>&1 || \
      echo "     start it from the Workstation UI: $D/${NAME}.vmx"
  }

  write_vmx "$VM_A" "$RAM_A" "$CPU_A" 20 10
  write_vmx "$VM_B" "$RAM_B" "$CPU_B" 20 0
}

case "$PROVIDER" in
  virtualbox|vbox) build_virtualbox ;;
  vmware|ws)       build_vmware ;;
  *) die "Unknown provider '$PROVIDER'. Use: virtualbox | vmware" ;;
esac

cat <<EOF

$(c "Lab created. Now finish the install by hand:")

  1. In each VM's installer choose Server or Minimal Install — never Workstation.
  2. Set hostnames: $VM_A  and  $VM_B
  3. Create a user called 'shea' and give it administrator/sudo rights.
  4. After first boot, set the private addresses on the second adapter:

       servera:  sudo nmcli con mod <conn> ipv4.method manual \\
                   ipv4.addresses ${NET_CIDR}.10/24 && sudo nmcli con up <conn>
       serverb:  sudo nmcli con mod <conn> ipv4.method manual \\
                   ipv4.addresses ${NET_CIDR}.11/24 && sudo nmcli con up <conn>

  5. Add each host to the other's /etc/hosts, then confirm: ssh shea@serverb
  6. Snapshot BOTH machines and name the snapshot 'clean'.

Then start Lab Guide 1: https://rhcsa.learnlinuxforwork.com/lab/week-01.html
EOF
