#!/usr/bin/env bash
#
# build-cloud-lab.sh — stand the same two-machine RHCSA lab up in the cloud,
#                      for when your laptop can't spare the RAM.
#
# RHCSA Course — rhcsa.learnlinuxforwork.com
# Copyright (C) 2026 Shea's Tech. Licensed under the GNU AGPL v3.0 or later.
#
# SUPPORTED
#   gcp     Google Cloud Platform   https://console.cloud.google.com/
#   do      DigitalOcean            https://cloud.digitalocean.com/
#   aws     Amazon Web Services     https://console.aws.amazon.com/
#   vultr   Vultr                   https://my.vultr.com/
#
# USAGE
#   ./build-cloud-lab.sh gcp
#   ./build-cloud-lab.sh do
#   ./build-cloud-lab.sh aws
#   ./build-cloud-lab.sh vultr
#   ./build-cloud-lab.sh <provider> --destroy
#
# COST WARNING
#   These are billable. Two small instances run roughly $10-25/month if you
#   leave them on. DESTROY THEM when you are not labbing:
#       ./build-cloud-lab.sh <provider> --destroy
#   Set a billing alert on day one. Every provider offers one, free.
#
set -uo pipefail

VM_A="servera"; VM_B="serverb"
LAB_TAG="rhcsa-lab"
SSH_KEY="${HOME}/.ssh/id_ed25519.pub"

c()  { printf '\033[1;31m%s\033[0m\n' "$*"; }
ok() { printf '  \033[0;32mok\033[0m  %s\n' "$*"; }
die(){ printf '\n\033[1;31mSTOPPED:\033[0m %s\n' "$*"; exit 1; }

PROVIDER="${1:-}"; shift || true
DESTROY=0
[ "${1:-}" = "--destroy" ] && DESTROY=1

[ -f "$SSH_KEY" ] || die "No SSH public key at $SSH_KEY.
Create one first:  ssh-keygen -t ed25519 -C 'shea@rhcsa-lab'"

# ==================================================================== GCP ===
gcp() {
  command -v gcloud >/dev/null || die "gcloud not installed.
Install the SDK: https://cloud.google.com/sdk/docs/install
Then:  gcloud init && gcloud auth login"

  local ZONE="${GCP_ZONE:-us-east1-b}"
  local TYPE="${GCP_TYPE:-e2-medium}"
  # Rocky Linux 10 is published in the rocky-linux-cloud project.
  local IMAGE_FAMILY="rocky-linux-10"
  local IMAGE_PROJECT="rocky-linux-cloud"

  if [ "$DESTROY" = "1" ]; then
    gcloud compute instances delete "$VM_A" "$VM_B" --zone "$ZONE" --quiet && ok "instances deleted"
    gcloud compute firewall-rules delete "${LAB_TAG}-internal" --quiet 2>/dev/null
    return
  fi

  c "Creating the lab network rules"
  gcloud compute firewall-rules create "${LAB_TAG}-internal" \
    --allow tcp,udp,icmp --source-tags "$LAB_TAG" --target-tags "$LAB_TAG" \
    --description "RHCSA lab: allow servera <-> serverb" 2>/dev/null || ok "firewall rule already exists"

  c "Creating $VM_A (with the spare disk for the storage labs)"
  gcloud compute instances create "$VM_A" \
    --zone "$ZONE" --machine-type "$TYPE" \
    --image-family "$IMAGE_FAMILY" --image-project "$IMAGE_PROJECT" \
    --boot-disk-size 20GB --boot-disk-type pd-balanced \
    --create-disk=name=${VM_A}-extra,size=10GB,type=pd-balanced,auto-delete=yes \
    --tags "$LAB_TAG" \
    --metadata ssh-keys="shea:$(cat "$SSH_KEY")"

  c "Creating $VM_B"
  gcloud compute instances create "$VM_B" \
    --zone "$ZONE" --machine-type e2-small \
    --image-family "$IMAGE_FAMILY" --image-project "$IMAGE_PROJECT" \
    --boot-disk-size 20GB --tags "$LAB_TAG" \
    --metadata ssh-keys="shea:$(cat "$SSH_KEY")"

  gcloud compute instances list --filter="name~'server'"
  cat <<EOF

Connect:   gcloud compute ssh shea@$VM_A --zone $ZONE
           gcloud compute ssh shea@$VM_B --zone $ZONE

Console:   https://console.cloud.google.com/compute/instances

STOP THEM when you finish for the day (you still pay for disks):
           gcloud compute instances stop $VM_A $VM_B --zone $ZONE
DESTROY:   $0 gcp --destroy
EOF
}

# =========================================================== DIGITALOCEAN ===
digitalocean() {
  command -v doctl >/dev/null || die "doctl not installed.
Install: https://docs.digitalocean.com/reference/doctl/how-to/install/
Then:  doctl auth init"

  local REGION="${DO_REGION:-nyc3}"
  local SIZE="${DO_SIZE:-s-2vcpu-4gb}"
  local IMAGE="rockylinux-10-x64"

  if [ "$DESTROY" = "1" ]; then
    doctl compute droplet delete "$VM_A" "$VM_B" --force && ok "droplets deleted"
    return
  fi

  local KEYID
  KEYID=$(doctl compute ssh-key list --format ID --no-header | head -1)
  [ -n "$KEYID" ] || die "No SSH key registered with DigitalOcean.
Add it:  doctl compute ssh-key import rhcsa --public-key-file $SSH_KEY"

  c "Creating $VM_A"
  doctl compute droplet create "$VM_A" --region "$REGION" --size "$SIZE" \
    --image "$IMAGE" --ssh-keys "$KEYID" --tag-name "$LAB_TAG" --wait

  c "Creating $VM_B"
  doctl compute droplet create "$VM_B" --region "$REGION" --size s-1vcpu-2gb \
    --image "$IMAGE" --ssh-keys "$KEYID" --tag-name "$LAB_TAG" --wait

  c "Adding a 10 GB volume to $VM_A for the storage labs"
  doctl compute volume create "${VM_A}-extra" --region "$REGION" --size 10GiB --fs-type "" 2>/dev/null
  local VOLID DROPID
  VOLID=$(doctl compute volume list --format ID,Name --no-header | awk '/'"${VM_A}"'-extra/{print $1}')
  DROPID=$(doctl compute droplet list --format ID,Name --no-header | awk '/'"$VM_A"'/{print $1}')
  [ -n "$VOLID" ] && doctl compute volume-action attach "$VOLID" "$DROPID" --wait && ok "volume attached"

  doctl compute droplet list --format Name,PublicIPv4,PrivateIPv4,Status
  cat <<EOF

Connect:   ssh root@<public-ip>
Console:   https://cloud.digitalocean.com/droplets

DESTROY:   $0 do --destroy
EOF
}

# ==================================================================== AWS ===
aws_ec2() {
  command -v aws >/dev/null || die "AWS CLI not installed.
Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
Then:  aws configure"

  local REGION="${AWS_REGION:-us-east-1}"
  local TYPE="${AWS_TYPE:-t3.medium}"

  if [ "$DESTROY" = "1" ]; then
    local IDS
    IDS=$(aws ec2 describe-instances --region "$REGION" \
      --filters "Name=tag:Project,Values=$LAB_TAG" "Name=instance-state-name,Values=running,stopped" \
      --query 'Reservations[].Instances[].InstanceId' --output text)
    [ -n "$IDS" ] && aws ec2 terminate-instances --region "$REGION" --instance-ids $IDS && ok "instances terminated"
    return
  fi

  c "Finding the latest Rocky Linux 10 AMI"
  local AMI
  AMI=$(aws ec2 describe-images --region "$REGION" --owners 792107900819 \
    --filters "Name=name,Values=Rocky-10-EC2-Base*x86_64*" "Name=state,Values=available" \
    --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
  [ "$AMI" != "None" ] && [ -n "$AMI" ] || die "Could not find a Rocky 10 AMI in $REGION.
Browse manually: https://console.aws.amazon.com/ec2/home#Images"
  ok "AMI: $AMI"

  aws ec2 import-key-pair --region "$REGION" --key-name rhcsa-lab \
    --public-key-material "fileb://$SSH_KEY" 2>/dev/null || ok "key pair already imported"

  aws ec2 create-security-group --region "$REGION" --group-name "$LAB_TAG" \
    --description "RHCSA lab" 2>/dev/null
  local SG
  SG=$(aws ec2 describe-security-groups --region "$REGION" --group-names "$LAB_TAG" \
    --query 'SecurityGroups[0].GroupId' --output text)
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG" \
    --protocol tcp --port 22 --cidr "$(curl -s ifconfig.me)/32" 2>/dev/null
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG" \
    --protocol -1 --source-group "$SG" 2>/dev/null
  ok "security group $SG — SSH from your IP only, plus full traffic between lab hosts"

  c "Launching $VM_A with a 10 GB spare volume"
  aws ec2 run-instances --region "$REGION" --image-id "$AMI" --instance-type "$TYPE" \
    --key-name rhcsa-lab --security-group-ids "$SG" --count 1 \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20}},{"DeviceName":"/dev/sdb","Ebs":{"VolumeSize":10}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$VM_A},{Key=Project,Value=$LAB_TAG}]" \
    --query 'Instances[0].InstanceId' --output text

  c "Launching $VM_B"
  aws ec2 run-instances --region "$REGION" --image-id "$AMI" --instance-type t3.small \
    --key-name rhcsa-lab --security-group-ids "$SG" --count 1 \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$VM_B},{Key=Project,Value=$LAB_TAG}]" \
    --query 'Instances[0].InstanceId' --output text

  cat <<EOF

List:      aws ec2 describe-instances --region $REGION \\
             --filters "Name=tag:Project,Values=$LAB_TAG" \\
             --query 'Reservations[].Instances[].[Tags[?Key==\`Name\`].Value|[0],PublicIpAddress,State.Name]' --output table
Connect:   ssh rocky@<public-ip>
Console:   https://console.aws.amazon.com/ec2/

STOP (cheaper than running, still pays for storage):
           aws ec2 stop-instances --region $REGION --instance-ids <ids>
DESTROY:   $0 aws --destroy
EOF
}

# ================================================================== VULTR ===
vultr() {
  command -v vultr-cli >/dev/null || die "vultr-cli not installed.
Install: https://github.com/vultr/vultr-cli#installation
Then export your API key:  export VULTR_API_KEY=...
Get one at: https://my.vultr.com/settings/#settingsapi"

  local REGION="${VULTR_REGION:-ewr}"
  local PLAN="${VULTR_PLAN:-vc2-2c-4gb}"

  if [ "$DESTROY" = "1" ]; then
    for n in "$VM_A" "$VM_B"; do
      local ID; ID=$(vultr-cli instance list | awk -v n="$n" '$0 ~ n {print $1}')
      [ -n "$ID" ] && vultr-cli instance delete "$ID" && ok "$n deleted"
    done
    return
  fi

  c "Finding the Rocky Linux 10 OS id"
  vultr-cli os list | grep -i "rocky" || true
  local OSID="${VULTR_OS_ID:-}"
  [ -n "$OSID" ] || die "Set the OS id from the list above, then re-run:
  export VULTR_OS_ID=<id> && $0 vultr"

  local KEYID; KEYID=$(vultr-cli ssh-key list | awk 'NR==2{print $1}')
  [ -n "$KEYID" ] || die "No SSH key on Vultr. Add it:
  vultr-cli ssh-key create --name rhcsa --key \"\$(cat $SSH_KEY)\""

  c "Creating $VM_A"
  vultr-cli instance create --region "$REGION" --plan "$PLAN" --os "$OSID" \
    --label "$VM_A" --host "$VM_A" --ssh-keys "$KEYID" --tags "$LAB_TAG"
  c "Creating $VM_B"
  vultr-cli instance create --region "$REGION" --plan vc2-1c-2gb --os "$OSID" \
    --label "$VM_B" --host "$VM_B" --ssh-keys "$KEYID" --tags "$LAB_TAG"

  vultr-cli instance list
  cat <<EOF

Add a 10 GB block volume to $VM_A for the storage labs:
  vultr-cli block-storage create --region $REGION --size 10 --label ${VM_A}-extra
  vultr-cli block-storage attach <block-id> --instance <instance-id>

Connect:   ssh root@<ip>
Console:   https://my.vultr.com/
DESTROY:   $0 vultr --destroy
EOF
}

case "$PROVIDER" in
  gcp)   gcp ;;
  do|digitalocean) digitalocean ;;
  aws)   aws_ec2 ;;
  vultr) vultr ;;
  *) sed -n '2,30p' "$0"; exit 1 ;;
esac

cat <<'EOF'

REMEMBER: cloud instances bill by the hour. Destroy them when you are done for
the week, and rebuild with this script when you come back. Rebuilding from
scratch is itself good RHCSA practice.
EOF
