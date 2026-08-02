#!/usr/bin/env python3
"""
Generate the standalone lab guide pages under lab/ from LABS below.

Run from the repo root:   python3 tools/build_labs.py
The generated pages are committed; the published site has no build step.

Free RHCSA Course - rhcsa.learnlinuxforwork.com
Copyright (C) 2026 Shea's Tech. Licensed under the GNU AGPL v3.0 or later.
"""
import html
import json
import io
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every lab uses the same two hosts and the same working user, so the course
# reads as one continuous build rather than twelve unrelated exercises.
HOST_A = "servera"
HOST_B = "serverb"
USER = "shea"

LABS = [
 {
  "n": 1, "id": "week-01", "title": "Essential Tools and the Shell",
  "goal": "Get fast at the commands you will use in every other week, and learn to answer your own questions from the man pages instead of a search engine.",
  "time": "2-3 hours",
  "prereqs": ["Both lab machines installed and reachable", "You are logged in as " + USER + " with sudo rights"],
  "sections": [
   {"h": "1. Find your way around",
    "p": "Start by proving to yourself where things live. The exam assumes you can navigate without thinking about it.",
    "code": [
      ("Where am I, and what is here?",
       "pwd\nls -la /etc | head\nls -ld /var/log /usr/share/doc /home"),
      ("Follow a file back to the package that owns it",
       "which sshd || command -v sshd\nls -l /usr/sbin/sshd\nrpm -qf /usr/sbin/sshd"),
    ]},
   {"h": "2. Redirection and pipes",
    "p": "Every one of these appears in the objectives by name. Run each and read the result before moving on.",
    "code": [
      ("Standard output, append, and standard error",
       "ls /etc > ~/etc-list.txt\nls /nope 2> ~/errors.txt\nls /etc /nope > ~/both.txt 2>&1\necho 'appended line' >> ~/etc-list.txt\nwc -l ~/etc-list.txt ~/errors.txt ~/both.txt"),
      ("Pipe into a filter, and tee to a file while still seeing output",
       "ps aux | wc -l\nps aux | tee ~/procs.txt | grep -c sshd"),
      ("Throw output away when you only care about the exit status",
       "grep -q root /etc/passwd 2>/dev/null && echo 'root exists'"),
    ]},
   {"h": "3. grep and regular expressions",
    "p": "Anchors, character classes, and quantifiers cover almost everything the exam asks of you.",
    "code": [
      ("Anchors and case",
       "grep '^" + USER + "' /etc/passwd\ngrep 'bash$' /etc/passwd\ngrep -i 'ROOT' /etc/passwd"),
      ("Character classes and quantifiers",
       "grep -E '^[a-z]+:x:[0-9]{4,}:' /etc/passwd\ngrep -E 'nologin|false' /etc/passwd | wc -l"),
      ("Recursive search, with the filename and line number",
       "sudo grep -rn 'PermitRootLogin' /etc/ssh/ 2>/dev/null"),
    ]},
   {"h": "4. Files, directories, and links",
    "p": "Note carefully what happens to each link type when the target disappears. That difference is testable.",
    "code": [
      ("Create a working tree",
       "mkdir -p ~/lab01/{src,dst}\necho 'original content' > ~/lab01/src/original.txt\ncp ~/lab01/src/original.txt ~/lab01/dst/copy.txt\nmv ~/lab01/dst/copy.txt ~/lab01/dst/renamed.txt"),
      ("Hard link versus symbolic link",
       "ln ~/lab01/src/original.txt ~/lab01/src/hardlink.txt\nln -s ~/lab01/src/original.txt ~/lab01/src/symlink.txt\nls -li ~/lab01/src/"),
      ("Break the target and see which link survives",
       "rm ~/lab01/src/original.txt\ncat ~/lab01/src/hardlink.txt\ncat ~/lab01/src/symlink.txt"),
    ],
    "note": "The hard link still prints the content because it points at the same inode. The symlink is now dangling and fails. Being able to explain that out loud is the point."},
   {"h": "5. Permissions",
    "p": "Set the same permission set both ways so the octal and symbolic forms become interchangeable in your head.",
    "code": [
      ("Symbolic and octal, same result",
       "touch ~/lab01/perms.txt\nchmod u=rw,g=r,o= ~/lab01/perms.txt\nls -l ~/lab01/perms.txt\nchmod 640 ~/lab01/perms.txt\nls -l ~/lab01/perms.txt"),
      ("Directory permissions behave differently",
       "mkdir ~/lab01/dir\nchmod 700 ~/lab01/dir\nls -ld ~/lab01/dir\nchmod 755 ~/lab01/dir"),
    ]},
   {"h": "6. Archives",
    "p": "All three compression tools are named in the objectives. Create and extract with each.",
    "code": [
      ("tar with gzip and with bzip2",
       "tar -czf ~/lab01-gzip.tar.gz -C ~ lab01\ntar -cjf ~/lab01-bzip2.tar.bz2 -C ~ lab01\nls -lh ~/lab01-*"),
      ("Inspect before extracting, then extract elsewhere",
       "tar -tzf ~/lab01-gzip.tar.gz | head\nmkdir -p ~/restore\ntar -xzf ~/lab01-gzip.tar.gz -C ~/restore\nls -R ~/restore | head"),
    ]},
   {"h": "7. Remote access and switching users",
    "p": "You will use this connection in most later labs, so confirm it works now.",
    "code": [
      ("Connect to the second machine and come back",
       "ssh " + USER + "@" + HOST_B + " 'hostname; uptime'\nssh " + USER + "@" + HOST_B),
      ("Switch users properly",
       "su - " + USER + "\nsudo -i\nwhoami\nexit"),
    ]},
   {"h": "8. Answer your own questions",
    "p": "This is the habit that matters most. In the exam there is no internet, only these.",
    "code": [
      ("Search by keyword, then read the right section",
       "man -k passwd | head\nman 5 passwd\nman 1 passwd"),
      ("The documentation that ships with packages",
       "ls /usr/share/doc | head -20\nls /usr/share/doc/bash* 2>/dev/null | head"),
    ]},
  ],
  "verify": [
    "grep -c '' ~/etc-list.txt   # the file exists and has lines",
    "ls -li ~/lab01/src/         # hardlink shares an inode with nothing now; symlink is red/broken",
    "tar -tzf ~/lab01-gzip.tar.gz >/dev/null && echo 'archive readable'",
    "ssh " + USER + "@" + HOST_B + " 'echo remote ok'",
  ],
  "breakfix": {
    "break": "chmod 000 ~/lab01/dir",
    "symptom": "You can no longer list or enter the directory, even though you own it.",
    "fix": "chmod 755 ~/lab01/dir",
    "lesson": "Owning a file does not grant access; the permission bits still apply to you. On the exam, a 'diagnose and correct file permission problems' task usually looks exactly like this.",
  },
 },

 {
  "n": 2, "id": "week-02", "title": "Users, Groups, and Privileged Access",
  "goal": "Create and manage local accounts and groups, age passwords, and grant sudo access the way the exam expects - in a drop-in file, not by editing the main sudoers.",
  "time": "2-3 hours",
  "prereqs": ["Week 1 complete", "Root or sudo access on " + HOST_A],
  "sections": [
   {"h": "1. Read the account databases first",
    "p": "You cannot manage what you cannot read. Every field here has a meaning worth knowing.",
    "code": [
      ("The three files that define an account",
       "getent passwd " + USER + "\nsudo getent shadow " + USER + "\ngetent group " + USER),
      ("What the fields mean",
       "man 5 passwd\nman 5 shadow\nman 5 group"),
    ]},
   {"h": "2. Create accounts",
    "p": "Create three accounts with different characteristics so you have something to manage.",
    "code": [
      ("A standard account, a system account, and one with a custom home",
       "sudo useradd -c 'Standard account' analyst1\nsudo useradd -r -s /sbin/nologin svc_backup\nsudo useradd -d /opt/analyst2 -m -c 'Custom home' analyst2\ngetent passwd analyst1 svc_backup analyst2"),
      ("Set passwords",
       "echo 'ChangeMe123' | sudo passwd --stdin analyst1\nsudo passwd -l svc_backup"),
    ],
    "note": "passwd --stdin is convenient in a lab. In the exam, plain interactive passwd is fine and less error-prone."},
   {"h": "3. Password aging",
    "p": "Aging shows up in the objectives explicitly. Set it, then read it back.",
    "code": [
      ("Force a change at first login",
       "sudo chage -d 0 analyst1\nsudo chage -l analyst1"),
      ("Maximum age, minimum age, and warning period",
       "sudo chage -M 60 -m 7 -W 7 analyst1\nsudo chage -l analyst1"),
      ("Expire an account on a fixed date",
       "sudo chage -E 2027-01-01 analyst2\nsudo chage -l analyst2"),
    ]},
   {"h": "4. Groups and membership",
    "p": "Know the difference between primary and supplementary membership, and never use usermod -G without -a.",
    "code": [
      ("Create groups and assign membership",
       "sudo groupadd engineering\nsudo groupadd -g 5000 contractors\nsudo usermod -aG engineering analyst1\nsudo usermod -aG engineering,contractors analyst2\nid analyst1\nid analyst2"),
      ("Change a primary group",
       "sudo usermod -g engineering analyst1\nid analyst1"),
    ],
    "note": "usermod -G without -a replaces every supplementary group the user has. That single missing letter has failed real exams."},
   {"h": "5. A shared group directory",
    "p": "This combines permissions, group ownership, and the set-GID bit - a very common exam-style task.",
    "code": [
      ("Create it and set group ownership",
       "sudo mkdir -p /srv/engineering\nsudo chgrp engineering /srv/engineering\nsudo chmod 2770 /srv/engineering\nls -ld /srv/engineering"),
      ("Prove the set-GID bit works",
       "sudo -u analyst1 touch /srv/engineering/from-analyst1\nls -l /srv/engineering"),
    ],
    "note": "The 2 in 2770 is set-GID: new files inherit the directory's group instead of the creator's primary group. That is what makes a shared directory actually shared."},
   {"h": "6. Privileged access",
    "p": "Always use a drop-in file. Editing /etc/sudoers directly is riskier and harder to undo.",
    "code": [
      ("Grant sudo to a group, safely",
       "echo '%engineering ALL=(ALL) ALL' | sudo tee /etc/sudoers.d/engineering\nsudo chmod 0440 /etc/sudoers.d/engineering\nsudo visudo -c"),
      ("Grant a single command without a password",
       "echo 'analyst2 ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart sshd' | sudo tee /etc/sudoers.d/analyst2\nsudo chmod 0440 /etc/sudoers.d/analyst2\nsudo visudo -c"),
      ("Test as the user",
       "sudo -u analyst2 sudo -l"),
    ]},
  ],
  "verify": [
    "id analyst1 analyst2",
    "sudo chage -l analyst1 | head -5",
    "ls -ld /srv/engineering   # expect drwxrws--- and group engineering",
    "sudo visudo -c            # must report 'parsed OK'",
  ],
  "breakfix": {
    "break": "echo 'this is not valid sudoers syntax' | sudo tee /etc/sudoers.d/broken",
    "symptom": "sudo may start refusing to run at all, which can lock you out of privilege escalation.",
    "fix": "Recover from an existing root shell, or boot to the emergency shell as taught in Week 5, then: rm /etc/sudoers.d/broken",
    "lesson": "Always run 'visudo -c' after touching anything under /etc/sudoers.d, and keep a root shell open in another terminal while you work. This is the one place where a typo can lock you out of your own machine.",
  },
 },

 {
  "n": 3, "id": "week-03", "title": "Software: RPM, Repositories, and Flatpak",
  "goal": "Install and remove software from every source the objectives name, including Flatpak, which is new to the RHEL 10 exam and missing from most older study material.",
  "time": "2-3 hours",
  "prereqs": ["Week 2 complete", "Network access from " + HOST_A],
  "sections": [
   {"h": "1. Query before you install",
    "p": "Half the software objectives are really about knowing what is already there.",
    "code": [
      ("What is installed, and what owns a file",
       "rpm -qa | wc -l\nrpm -qa | grep -i openssh\nrpm -qf /etc/ssh/sshd_config\nrpm -ql openssh-server | head"),
      ("Search the repositories",
       "dnf search nmap\ndnf info nmap\ndnf provides */htop"),
    ]},
   {"h": "2. Install and remove RPM packages",
    "p": "From a repository, then from a downloaded file, so both paths are familiar.",
    "code": [
      ("From a configured repository",
       "sudo dnf install -y nmap\nrpm -q nmap\nsudo dnf remove -y nmap"),
      ("Groups and updates",
       "dnf group list\nsudo dnf check-update | head\nsudo dnf update -y"),
      ("From a local file",
       "sudo dnf download nmap 2>/dev/null || sudo dnf install -y --downloadonly --downloaddir=/tmp nmap\nsudo dnf install -y /tmp/nmap-*.rpm"),
    ]},
   {"h": "3. Configure repository access",
    "p": "Writing a .repo file by hand is explicitly in the objectives. Do it manually rather than with a helper.",
    "code": [
      ("Write the repo definition",
       "sudo tee /etc/yum.repos.d/local-lab.repo >/dev/null <<'EOF'\n[local-lab]\nname=Local Lab Repository\nbaseurl=file:///mnt/repo\nenabled=1\ngpgcheck=0\nEOF\ncat /etc/yum.repos.d/local-lab.repo"),
      ("List, enable, and disable",
       "dnf repolist\ndnf repolist --all | head\nsudo dnf config-manager --set-disabled local-lab\ndnf repolist\nsudo dnf config-manager --set-enabled local-lab"),
      ("Use a repository once without enabling it",
       "sudo dnf --disablerepo='*' --enablerepo='local-lab' list available 2>/dev/null | head"),
    ],
    "note": "gpgcheck=0 is acceptable for a local lab repo you created. For a real remote repository, point gpgkey at the key and leave gpgcheck=1."},
   {"h": "4. Flatpak",
    "p": "New in the RHEL 10 objectives. Configure a remote, then install, run, and remove an application.",
    "code": [
      ("Install the tooling and add a remote",
       "sudo dnf install -y flatpak\nflatpak remotes\nflatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo\nflatpak remotes"),
      ("Search, install, list, and run",
       "flatpak search text-editor | head\nflatpak install -y flathub org.gnome.TextEditor\nflatpak list\nflatpak run org.gnome.TextEditor --help 2>/dev/null | head -3"),
      ("Remove it and clean up",
       "flatpak uninstall -y org.gnome.TextEditor\nflatpak uninstall --unused -y\nflatpak list"),
      ("Remove a remote",
       "flatpak remote-delete flathub\nflatpak remotes"),
    ],
    "note": "An RPM installs into the system as root and integrates with system libraries. A Flatpak is a sandboxed, self-contained application bundle that can be installed per-user. Being able to state that difference is fair game."},
  ],
  "verify": [
    "dnf repolist | grep -i local-lab",
    "flatpak remotes",
    "rpm -q nmap || echo 'nmap correctly removed'",
    "sudo dnf history | head -5",
  ],
  "breakfix": {
    "break": "sudo sed -i 's|^baseurl=.*|baseurl=file:///mnt/does-not-exist|' /etc/yum.repos.d/local-lab.repo",
    "symptom": "dnf commands fail or hang with a repository error referencing local-lab.",
    "fix": "sudo sed -i 's|^baseurl=.*|baseurl=file:///mnt/repo|' /etc/yum.repos.d/local-lab.repo && sudo dnf clean all && dnf repolist",
    "lesson": "A broken repo file breaks every dnf operation, not just the one that uses it. Read the error text - it names the offending repository. 'dnf clean all' after fixing a repo is almost always necessary.",
  },
 },

 {
  "n": 4, "id": "week-04", "title": "Processes, Tuning, and Scheduled Tasks",
  "goal": "Find and control running processes, adjust their priority, manage tuned profiles, and schedule work three different ways.",
  "time": "2-3 hours",
  "prereqs": ["Week 3 complete"],
  "sections": [
   {"h": "1. See what is running",
    "p": "Learn one process listing well rather than three badly.",
    "code": [
      ("Snapshot and live views",
       "ps aux | head\nps -ef --forest | head -20\ntop -b -n 1 | head -15\nuptime"),
      ("Sort by what actually matters",
       "ps aux --sort=-%cpu | head -6\nps aux --sort=-%mem | head -6"),
    ]},
   {"h": "2. Create load, then kill it",
    "p": "Make a process you can safely identify and terminate.",
    "code": [
      ("Start something noisy in the background",
       "sha256sum /dev/zero &\nsleep 300 &\njobs\nps -ef | grep -E 'sha256sum|sleep' | grep -v grep"),
      ("Terminate it politely, then forcefully",
       "pkill sha256sum\npgrep -a sleep\nkill %2 2>/dev/null || pkill sleep\nps -ef | grep -c sleep"),
      ("Signals worth knowing",
       "kill -l | head -3\n# SIGTERM (15) asks a process to exit; SIGKILL (9) cannot be caught or ignored"),
    ]},
   {"h": "3. Scheduling priority",
    "p": "Lower nice values mean higher priority. Only root can lower a value below zero.",
    "code": [
      ("Start a process at a specific niceness",
       "nice -n 10 sha256sum /dev/zero &\nps -o pid,ni,comm -C sha256sum"),
      ("Change it while running",
       "sudo renice -n -5 -p $(pgrep -n sha256sum)\nps -o pid,ni,comm -C sha256sum\npkill sha256sum"),
    ]},
   {"h": "4. Tuning profiles",
    "p": "Named directly in the objectives, and quick marks if you know the three commands.",
    "code": [
      ("List, check, and switch",
       "sudo dnf install -y tuned\nsudo systemctl enable --now tuned\ntuned-adm list\ntuned-adm active\nsudo tuned-adm profile throughput-performance\ntuned-adm active"),
      ("Let tuned choose for the hardware",
       "sudo tuned-adm recommend\nsudo tuned-adm profile $(sudo tuned-adm recommend)\ntuned-adm active"),
    ]},
   {"h": "5. One-off jobs with at",
    "p": "",
    "code": [
      ("Schedule and inspect",
       "sudo dnf install -y at\nsudo systemctl enable --now atd\necho 'date >> /tmp/at-test.log' | at now + 1 minute\natq\nat -c $(atq | awk '{print $1}' | head -1) | tail -5"),
      ("Wait, then confirm it ran",
       "sleep 70\ncat /tmp/at-test.log\natq"),
    ]},
   {"h": "6. Recurring jobs with cron",
    "p": "Both a user crontab and a system-wide job, because the exam may ask for either.",
    "code": [
      ("A user crontab",
       "crontab -l 2>/dev/null\n(crontab -l 2>/dev/null; echo '*/2 * * * * /usr/bin/date >> /home/" + USER + "/cron-test.log') | crontab -\ncrontab -l"),
      ("A system-wide job that runs as a specific user",
       "sudo tee /etc/cron.d/lab-report >/dev/null <<'EOF'\n*/5 * * * * " + USER + " /usr/bin/uptime >> /tmp/uptime-report.log\nEOF\nsudo systemctl status crond --no-pager | head -5"),
    ]},
   {"h": "7. systemd timers",
    "p": "A timer needs two units: the service that does the work, and the timer that triggers it.",
    "code": [
      ("The service unit",
       "sudo tee /etc/systemd/system/labreport.service >/dev/null <<'EOF'\n[Unit]\nDescription=Write a short system report\n\n[Service]\nType=oneshot\nExecStart=/bin/bash -c '/usr/bin/date; /usr/bin/uptime' \nEOF"),
      ("The timer unit",
       "sudo tee /etc/systemd/system/labreport.timer >/dev/null <<'EOF'\n[Unit]\nDescription=Run labreport every 10 minutes\n\n[Timer]\nOnBootSec=2min\nOnUnitActiveSec=10min\nUnit=labreport.service\n\n[Install]\nWantedBy=timers.target\nEOF"),
      ("Enable and inspect",
       "sudo systemctl daemon-reload\nsudo systemctl enable --now labreport.timer\nsystemctl list-timers --all | grep labreport\nsudo systemctl start labreport.service\nsudo journalctl -u labreport.service --no-pager | tail -5"),
    ],
    "note": "Reach for a timer over cron when you need the job tied to boot, dependent on another unit, or logged in the journal. Cron is still fine for simple recurring work."},
  ],
  "verify": [
    "tuned-adm active",
    "crontab -l",
    "systemctl list-timers --all | grep labreport",
    "systemctl is-enabled labreport.timer   # expect: enabled",
  ],
  "breakfix": {
    "break": "sudo sed -i 's/OnUnitActiveSec=10min/OnUnitActiveSec=nonsense/' /etc/systemd/system/labreport.timer && sudo systemctl daemon-reload",
    "symptom": "The timer refuses to start and systemctl reports the unit as failed or not loaded.",
    "fix": "sudo sed -i 's/OnUnitActiveSec=nonsense/OnUnitActiveSec=10min/' /etc/systemd/system/labreport.timer && sudo systemctl daemon-reload && sudo systemctl restart labreport.timer",
    "lesson": "systemd will not guess what you meant. 'systemctl status' plus 'journalctl -xe' names the bad directive and the line number. Always run daemon-reload after editing a unit file - forgetting it is the single most common systemd mistake.",
  },
 },

 {
  "n": 5, "id": "week-05", "title": "Boot, Targets, Services, and Recovery",
  "goal": "Control services and boot targets, and - most importantly - recover a system you have locked yourself out of. This is the lab that saves you in the exam.",
  "time": "3-4 hours",
  "prereqs": ["Week 4 complete", "Console access to the VM, not just SSH"],
  "sections": [
   {"h": "1. Services: started versus enabled",
    "p": "These are two separate things, and confusing them is the classic way to lose marks after a reboot.",
    "code": [
      ("The full lifecycle",
       "sudo systemctl status sshd --no-pager\nsudo systemctl stop sshd\nsudo systemctl start sshd\nsudo systemctl restart sshd\nsudo systemctl reload sshd"),
      ("Enable is about boot, start is about now",
       "systemctl is-active sshd\nsystemctl is-enabled sshd\nsudo systemctl disable sshd\nsystemctl is-enabled sshd\nsudo systemctl enable --now sshd"),
      ("What is running, and what failed",
       "systemctl list-units --type=service --state=running | head\nsystemctl --failed"),
    ],
    "note": "'enable --now' does both in one command. If a task says a service must be running and must come back after reboot, that is the command you want."},
   {"h": "2. Boot targets",
    "p": "",
    "code": [
      ("See and switch at runtime",
       "systemctl get-default\nsystemctl list-units --type=target\nsudo systemctl isolate multi-user.target"),
      ("Set the default permanently",
       "sudo systemctl set-default multi-user.target\nsystemctl get-default\nls -l /etc/systemd/system/default.target"),
    ]},
   {"h": "3. Interrupt the boot process",
    "p": "Do this from the VM console, not over SSH. Take a snapshot first.",
    "code": [
      ("At the GRUB menu",
       "# 1. Reboot the machine and press ESC or an arrow key at the GRUB menu\n# 2. Highlight the kernel entry and press 'e' to edit it\n# 3. Find the line starting with 'linux'\n# 4. Append this to the end of that line:\n#      rd.break\n# 5. Press Ctrl-X to boot"),
      ("In the emergency shell, remount and enter the real root",
       "mount -o remount,rw /sysroot\nchroot /sysroot"),
      ("Reset the root password and force an SELinux relabel",
       "passwd root\ntouch /.autorelabel\nexit\nexit"),
    ],
    "note": "The /.autorelabel file is the step people forget. Without it, SELinux has the wrong context on /etc/shadow after you changed it, and the system may not let you log in. The relabel happens on the next boot and takes a few minutes."},
   {"h": "4. Boot into a different target manually",
    "p": "A one-time change at the GRUB menu, useful when a service is preventing a normal boot.",
    "code": [
      ("Append a target to the kernel line",
       "# At the GRUB menu, press 'e' and append one of these to the 'linux' line:\n#   systemd.unit=rescue.target\n#   systemd.unit=emergency.target\n#   systemd.unit=multi-user.target\n# Then Ctrl-X to boot. The change applies to this boot only."),
    ]},
   {"h": "5. Modify the bootloader",
    "p": "Change a kernel parameter permanently and regenerate the configuration.",
    "code": [
      ("Edit the defaults and rebuild",
       "sudo cp /etc/default/grub /root/grub.backup\nsudo grep GRUB_TIMEOUT /etc/default/grub\nsudo sed -i 's/^GRUB_TIMEOUT=.*/GRUB_TIMEOUT=10/' /etc/default/grub\nsudo grub2-mkconfig -o /boot/grub2/grub.cfg"),
      ("Confirm the change landed",
       "sudo grep -m1 timeout /boot/grub2/grub.cfg\nsudo grubby --info=ALL | head -20"),
    ]},
  ],
  "verify": [
    "systemctl get-default",
    "systemctl is-enabled sshd && systemctl is-active sshd",
    "grep GRUB_TIMEOUT /etc/default/grub",
    "reboot, then re-run all three and confirm nothing changed",
  ],
  "breakfix": {
    "break": "sudo systemctl disable sshd && sudo reboot",
    "symptom": "After the reboot you cannot SSH in at all. The service exists and works, but nothing started it.",
    "fix": "From the VM console: sudo systemctl enable --now sshd",
    "lesson": "This is the reboot-persistence rule made concrete. In the exam a task like 'ensure the web service is running' almost always means running now AND enabled at boot. Get in the habit of typing 'enable --now' rather than 'start'.",
  },
 },

 {
  "n": 6, "id": "week-06", "title": "Logs, Journals, and Time",
  "goal": "Find out what a system has been doing, make that record survive a reboot, and keep the clock correct.",
  "time": "2-3 hours",
  "prereqs": ["Week 5 complete", "Both machines reachable"],
  "sections": [
   {"h": "1. Read the journal",
    "p": "journalctl is the primary tool. Learn the filters rather than scrolling.",
    "code": [
      ("Filter by unit, priority, and time",
       "sudo journalctl -u sshd --no-pager | tail -20\nsudo journalctl -p err --no-pager | tail -20\nsudo journalctl --since '1 hour ago' --no-pager | tail\nsudo journalctl --since '2026-08-01 09:00' --until '2026-08-01 17:00' --no-pager | tail"),
      ("Follow live, and look at a specific boot",
       "sudo journalctl -f    # Ctrl-C to stop\nsudo journalctl --list-boots\nsudo journalctl -b -1 --no-pager | head"),
      ("Kernel messages and a specific executable",
       "sudo journalctl -k --no-pager | tail\nsudo journalctl /usr/sbin/sshd --no-pager | tail -5"),
    ]},
   {"h": "2. Make the journal persistent",
    "p": "By default the journal may live only in memory and vanish at reboot. Preserving it is an explicit objective.",
    "code": [
      ("Create the directory and configure it",
       "sudo mkdir -p /var/log/journal\nsudo systemd-tmpfiles --create --prefix /var/log/journal\nsudo sed -i 's/^#\\?Storage=.*/Storage=persistent/' /etc/systemd/journald.conf\ngrep -i storage /etc/systemd/journald.conf"),
      ("Restart and confirm",
       "sudo systemctl restart systemd-journald\nsudo journalctl --list-boots\nls -ld /var/log/journal/*"),
    ],
    "note": "After a reboot, 'journalctl --list-boots' should show more than one entry. If it only ever shows the current boot, persistence is not working."},
   {"h": "3. Traditional log files",
    "p": "rsyslog still writes plain text files that some tasks reference by name.",
    "code": [
      ("What is there",
       "sudo ls -l /var/log/\nsudo tail -20 /var/log/messages\nsudo tail -20 /var/log/secure\nsudo grep -i 'authentication failure' /var/log/secure | tail"),
      ("Generate an entry and find it in both places",
       "logger -p user.notice 'RHCSA lab test message from " + USER + "'\nsudo grep 'RHCSA lab test' /var/log/messages\nsudo journalctl --no-pager | grep 'RHCSA lab test'"),
    ]},
   {"h": "4. Time services",
    "p": "chrony is the client. Configure it, then prove synchronisation.",
    "code": [
      ("Install, enable, and inspect",
       "sudo dnf install -y chrony\nsudo systemctl enable --now chronyd\nchronyc sources -v\nchronyc tracking"),
      ("Point at a specific server",
       "sudo cp /etc/chrony.conf /root/chrony.conf.backup\nsudo sed -i '/^pool /d' /etc/chrony.conf\necho 'server time.cloudflare.com iburst' | sudo tee -a /etc/chrony.conf\nsudo systemctl restart chronyd\nsleep 5\nchronyc sources"),
      ("Timezone and clocks",
       "timedatectl\ntimedatectl list-timezones | grep -i new_york\nsudo timedatectl set-timezone America/New_York\nsudo timedatectl set-ntp true\ntimedatectl"),
    ]},
   {"h": "5. Secure file transfer",
    "p": "Named in the objectives, and you will use it constantly anyway.",
    "code": [
      ("Three ways to move a file to the second machine",
       "echo 'transfer test' > ~/transfer.txt\nscp ~/transfer.txt " + USER + "@" + HOST_B + ":~/\nrsync -av ~/lab01/ " + USER + "@" + HOST_B + ":~/lab01-copy/\nsftp " + USER + "@" + HOST_B + " <<'EOF'\nput ~/transfer.txt remote-via-sftp.txt\nls\nbye\nEOF"),
      ("Confirm from the far end",
       "ssh " + USER + "@" + HOST_B + " 'ls -l ~/transfer.txt ~/remote-via-sftp.txt; ls ~/lab01-copy | head'"),
    ]},
  ],
  "verify": [
    "sudo journalctl --list-boots      # more than one line after a reboot",
    "ls -d /var/log/journal/*",
    "chronyc tracking | head -3",
    "timedatectl | grep -E 'Time zone|synchronized'",
  ],
  "breakfix": {
    "break": "sudo sed -i 's/^Storage=persistent/Storage=volatile/' /etc/systemd/journald.conf && sudo systemctl restart systemd-journald && sudo reboot",
    "symptom": "After the reboot, 'journalctl --list-boots' shows only the current boot. Yesterday's evidence is gone.",
    "fix": "sudo sed -i 's/^Storage=volatile/Storage=persistent/' /etc/systemd/journald.conf && sudo systemctl restart systemd-journald",
    "lesson": "'Preserve system journals' is a real objective, and volatile storage silently discards everything at shutdown. The verification is always the same: reboot, then list boots.",
  },
 },

 {
  "n": 7, "id": "week-07", "title": "Networking and firewalld",
  "goal": "Configure addressing, name resolution, and a firewall that all survive a reboot without you touching anything.",
  "time": "3-4 hours",
  "prereqs": ["Week 6 complete", "Console access in case you cut off your own SSH session"],
  "sections": [
   {"h": "1. Look before you change",
    "p": "Record the current state so you can get back if something goes wrong.",
    "code": [
      ("Current addressing and routing",
       "ip addr show\nip route show\nip -6 addr show\nnmcli device status\nnmcli connection show"),
      ("Save a copy of what works",
       "nmcli connection show --active | tee ~/net-before.txt\nip addr show | tee -a ~/net-before.txt"),
    ]},
   {"h": "2. Configure a static IPv4 address",
    "p": "Use nmcli. Changes made with 'ip' alone disappear at reboot and score nothing.",
    "code": [
      ("Identify the connection, then modify it",
       "CONN=$(nmcli -g NAME connection show --active | head -1)\necho \"$CONN\"\nsudo nmcli connection modify \"$CONN\" ipv4.method manual ipv4.addresses 192.168.56.10/24 ipv4.gateway 192.168.56.1 ipv4.dns '1.1.1.1 9.9.9.9'"),
      ("Apply and confirm",
       "sudo nmcli connection down \"$CONN\" && sudo nmcli connection up \"$CONN\"\nip addr show\nip route show\ncat /etc/resolv.conf"),
    ],
    "note": "Adjust the addresses to match your own lab network. The method matters more than the numbers: ipv4.method manual plus an explicit address is what makes it persistent."},
   {"h": "3. Add IPv6",
    "p": "The objectives name IPv6 explicitly, and it is often skipped in practice.",
    "code": [
      ("A static IPv6 address on the same connection",
       "sudo nmcli connection modify \"$CONN\" ipv6.method manual ipv6.addresses 2001:db8:56::10/64\nsudo nmcli connection up \"$CONN\"\nip -6 addr show\nping6 -c 2 ::1"),
    ]},
   {"h": "4. Hostname and name resolution",
    "p": "",
    "code": [
      ("Set the hostname permanently",
       "hostnamectl\nsudo hostnamectl set-hostname " + HOST_A + ".lab.example.com\nhostnamectl\nhostname -f"),
      ("Static resolution and testing",
       "echo '192.168.56.11  " + HOST_B + " " + HOST_B + ".lab.example.com' | sudo tee -a /etc/hosts\ngetent hosts " + HOST_B + "\nping -c 2 " + HOST_B + "\ndig +short redhat.com\nnslookup " + HOST_B),
    ]},
   {"h": "5. Networking at boot",
    "p": "",
    "code": [
      ("Make sure it comes up by itself",
       "sudo systemctl enable --now NetworkManager\nsudo nmcli connection modify \"$CONN\" connection.autoconnect yes\nnmcli -f connection.autoconnect connection show \"$CONN\""),
    ]},
   {"h": "6. firewalld",
    "p": "Everything permanent needs --permanent followed by --reload. Forgetting that is the classic mistake.",
    "code": [
      ("Inspect the current state",
       "sudo systemctl enable --now firewalld\nsudo firewall-cmd --state\nsudo firewall-cmd --get-active-zones\nsudo firewall-cmd --list-all"),
      ("Open a named service permanently",
       "sudo firewall-cmd --permanent --add-service=http\nsudo firewall-cmd --permanent --add-service=https\nsudo firewall-cmd --reload\nsudo firewall-cmd --list-services"),
      ("Open a specific port, and a port range",
       "sudo firewall-cmd --permanent --add-port=8080/tcp\nsudo firewall-cmd --permanent --add-port=9000-9010/udp\nsudo firewall-cmd --reload\nsudo firewall-cmd --list-ports"),
      ("Remove something, and change the default zone",
       "sudo firewall-cmd --permanent --remove-port=9000-9010/udp\nsudo firewall-cmd --reload\nsudo firewall-cmd --get-default-zone\nsudo firewall-cmd --list-all --zone=public"),
    ],
    "note": "'firewall-cmd --list-all' shows the RUNTIME configuration. To check what will survive a reload, add --permanent. If the two disagree, you forgot --reload."},
  ],
  "verify": [
    "ip addr show | grep -E 'inet |inet6 '",
    "sudo firewall-cmd --permanent --list-all",
    "getent hosts " + HOST_B,
    "reboot, then re-run every command above and confirm nothing was lost",
  ],
  "breakfix": {
    "break": "sudo firewall-cmd --add-service=http   # note: no --permanent",
    "symptom": "The service is reachable right now. After 'firewall-cmd --reload' or a reboot, it is blocked again.",
    "fix": "sudo firewall-cmd --permanent --add-service=http && sudo firewall-cmd --reload",
    "lesson": "firewalld keeps runtime and permanent configuration separately. A rule without --permanent is a rule that scores zero on a performance-based exam. Make '--permanent then --reload' a single muscle memory.",
  },
 },

 {
  "n": 8, "id": "week-08", "title": "Partitions, Filesystems, and Swap",
  "goal": "Carve up the spare disk, format it three ways, mount it persistently by UUID, and add swap - all without destroying the system.",
  "time": "3-4 hours",
  "prereqs": ["Week 7 complete", "A second, empty disk attached to " + HOST_A, "A snapshot taken immediately before you start"],
  "sections": [
   {"h": "1. Identify the right disk",
    "p": "Get this wrong and you will reinstall. Confirm the device before every destructive command.",
    "code": [
      ("Which disk is spare?",
       "lsblk\nsudo fdisk -l\nsudo blkid\ndf -h"),
      ("Set a variable so you cannot mistype it later",
       "DISK=/dev/sdb        # change this to match YOUR spare disk\nlsblk $DISK\nsudo blkid $DISK || echo 'no filesystem signature - good, it is empty'"),
    ],
    "note": "If lsblk shows a mountpoint or existing data on your candidate disk, stop and pick a different one."},
   {"h": "2. Create GPT partitions",
    "p": "",
    "code": [
      ("Write a GPT label and two partitions",
       "sudo parted -s $DISK mklabel gpt\nsudo parted -s $DISK mkpart primary 1MiB 2GiB\nsudo parted -s $DISK mkpart primary 2GiB 4GiB\nsudo parted -s $DISK print\nlsblk $DISK"),
      ("Make sure the kernel noticed",
       "sudo partprobe $DISK\nlsblk $DISK"),
    ]},
   {"h": "3. Create filesystems",
    "p": "All three named types appear in the objectives.",
    "code": [
      ("XFS and ext4",
       "sudo mkfs.xfs ${DISK}1\nsudo mkfs.ext4 ${DISK}2\nsudo blkid ${DISK}1 ${DISK}2"),
      ("Label them, which makes fstab easier to read",
       "sudo xfs_admin -L labxfs ${DISK}1\nsudo e2label ${DISK}2 labext4\nsudo blkid ${DISK}1 ${DISK}2"),
    ]},
   {"h": "4. Mount, then make it permanent",
    "p": "Mounting by device name is fragile - device names can change between boots. Use UUID or label.",
    "code": [
      ("Mount by hand first to prove it works",
       "sudo mkdir -p /mnt/xfsdata /mnt/extdata\nsudo mount ${DISK}1 /mnt/xfsdata\nsudo mount ${DISK}2 /mnt/extdata\ndf -h | grep mnt\nsudo umount /mnt/xfsdata /mnt/extdata"),
      ("Add persistent entries by UUID",
       "sudo cp /etc/fstab /root/fstab.backup\nUUID1=$(sudo blkid -s UUID -o value ${DISK}1)\nUUID2=$(sudo blkid -s UUID -o value ${DISK}2)\necho \"UUID=$UUID1  /mnt/xfsdata  xfs   defaults  0 0\" | sudo tee -a /etc/fstab\necho \"UUID=$UUID2  /mnt/extdata  ext4  defaults  0 0\" | sudo tee -a /etc/fstab\ncat /etc/fstab"),
      ("Test WITHOUT rebooting - this is the safety net",
       "sudo mount -a\ndf -h | grep mnt\nsudo systemctl daemon-reload"),
    ],
    "note": "'mount -a' is the single most important habit in this lab. A typo in fstab can stop the system booting; mount -a catches it while you can still fix it."},
   {"h": "5. A VFAT filesystem",
    "p": "Named in the objectives, and quick to do with a small third partition.",
    "code": [
      ("Add and format it",
       "sudo parted -s $DISK mkpart primary fat32 4GiB 5GiB\nsudo partprobe $DISK\nsudo mkfs.vfat -n LABVFAT ${DISK}3\nsudo mkdir -p /mnt/vfatdata\nUUID3=$(sudo blkid -s UUID -o value ${DISK}3)\necho \"UUID=$UUID3  /mnt/vfatdata  vfat  defaults  0 0\" | sudo tee -a /etc/fstab\nsudo mount -a\ndf -h | grep vfat"),
    ]},
   {"h": "6. Add swap non-destructively",
    "p": "The objectives say 'non-destructively' - meaning without disturbing what is already there.",
    "code": [
      ("A swap partition",
       "sudo parted -s $DISK mkpart primary linux-swap 5GiB 6GiB\nsudo partprobe $DISK\nsudo mkswap ${DISK}4\nsudo swapon ${DISK}4\nswapon --show\nfree -h"),
      ("Make it permanent",
       "UUID4=$(sudo blkid -s UUID -o value ${DISK}4)\necho \"UUID=$UUID4  none  swap  defaults  0 0\" | sudo tee -a /etc/fstab\nsudo swapoff ${DISK}4 && sudo swapon -a\nswapon --show"),
    ]},
  ],
  "verify": [
    "sudo mount -a && echo 'fstab is valid'",
    "df -h | grep /mnt",
    "swapon --show",
    "reboot, then: df -h | grep /mnt && swapon --show",
  ],
  "breakfix": {
    "break": "echo 'UUID=00000000-dead-beef-0000-000000000000  /mnt/ghost  xfs  defaults  0 0' | sudo tee -a /etc/fstab",
    "symptom": "'mount -a' fails. Had you rebooted instead, the system would have dropped to an emergency shell asking for the root password.",
    "fix": "sudo sed -i '/dead-beef/d' /etc/fstab && sudo mount -a",
    "lesson": "A bad fstab entry can stop a machine booting entirely. Two rules follow: back up fstab before editing it, and run 'mount -a' after every change. If a real system does drop to emergency mode, log in as root, remount / read-write, fix fstab, and reboot.",
  },
 },

 {
  "n": 9, "id": "week-09", "title": "LVM, NFS, and autofs",
  "goal": "Build logical volumes you can grow on demand, share a directory over the network, and mount it automatically only when it is needed.",
  "time": "4-5 hours",
  "prereqs": ["Week 8 complete", "Free space or a third disk on " + HOST_A, HOST_B + " reachable and able to run an NFS server"],
  "sections": [
   {"h": "1. Build the LVM stack",
    "p": "Physical volume, then volume group, then logical volume. Always in that order.",
    "code": [
      ("Create physical volumes",
       "sudo parted -s $DISK mkpart primary 6GiB 8GiB\nsudo parted -s $DISK mkpart primary 8GiB 10GiB\nsudo partprobe $DISK\nsudo pvcreate ${DISK}5 ${DISK}6\nsudo pvs\nsudo pvdisplay ${DISK}5 | head"),
      ("Create a volume group",
       "sudo vgcreate labvg ${DISK}5\nsudo vgs\nsudo vgdisplay labvg | head"),
      ("Create logical volumes - by size and by extents",
       "sudo lvcreate -L 500M -n labdata labvg\nsudo lvcreate -l 50%FREE -n labarchive labvg\nsudo lvs\nlsblk"),
    ]},
   {"h": "2. Format and mount a logical volume",
    "p": "",
    "code": [
      ("Filesystem and persistent mount",
       "sudo mkfs.xfs /dev/labvg/labdata\nsudo mkdir -p /mnt/labdata\nLVUUID=$(sudo blkid -s UUID -o value /dev/labvg/labdata)\necho \"UUID=$LVUUID  /mnt/labdata  xfs  defaults  0 0\" | sudo tee -a /etc/fstab\nsudo mount -a\ndf -h /mnt/labdata"),
      ("Put something in it so you can prove it survives",
       "echo 'written before the extend' | sudo tee /mnt/labdata/before.txt\nsudo cat /mnt/labdata/before.txt"),
    ]},
   {"h": "3. Extend a volume group and a logical volume",
    "p": "Growing storage online without losing data is a headline objective.",
    "code": [
      ("Add capacity to the volume group",
       "sudo vgextend labvg ${DISK}6\nsudo vgs\nsudo pvs"),
      ("Grow the logical volume and the filesystem together",
       "df -h /mnt/labdata\nsudo lvextend -L +800M -r /dev/labvg/labdata\nsudo lvs\ndf -h /mnt/labdata\nsudo cat /mnt/labdata/before.txt"),
      ("The two-step form, for when -r is not available",
       "# sudo lvextend -L +200M /dev/labvg/labdata\n# XFS grows with:   sudo xfs_growfs /mnt/labdata\n# ext4 grows with:  sudo resize2fs /dev/labvg/labdata"),
    ],
    "note": "The -r flag resizes the filesystem at the same time as the volume, which is why it is worth remembering. Note also that XFS can grow but cannot shrink - if a task asks you to shrink, the filesystem must be ext4."},
   {"h": "4. Remove volumes cleanly",
    "p": "",
    "code": [
      ("Tear down in reverse order",
       "sudo lvremove -y labvg/labarchive\nsudo lvs\n# to remove the whole stack later:\n#   sudo umount /mnt/labdata\n#   sudo lvremove -y labvg/labdata\n#   sudo vgremove -y labvg\n#   sudo pvremove ${DISK}5 ${DISK}6"),
    ]},
   {"h": "5. Export a directory over NFS",
    "p": "Run this section on " + HOST_B + ".",
    "code": [
      ("On " + HOST_B + " - install, export, and open the firewall",
       "sudo dnf install -y nfs-utils\nsudo mkdir -p /srv/nfsshare\nsudo chmod 777 /srv/nfsshare\necho 'exported from " + HOST_B + "' | sudo tee /srv/nfsshare/hello.txt\necho '/srv/nfsshare  *(rw,sync,no_root_squash)' | sudo tee /etc/exports\nsudo exportfs -rav\nsudo systemctl enable --now nfs-server\nsudo firewall-cmd --permanent --add-service=nfs\nsudo firewall-cmd --permanent --add-service=mountd\nsudo firewall-cmd --permanent --add-service=rpc-bind\nsudo firewall-cmd --reload"),
    ]},
   {"h": "6. Mount the NFS share",
    "p": "Back on " + HOST_A + ".",
    "code": [
      ("Discover and mount by hand",
       "sudo dnf install -y nfs-utils\nshowmount -e " + HOST_B + "\nsudo mkdir -p /mnt/nfsshare\nsudo mount -t nfs " + HOST_B + ":/srv/nfsshare /mnt/nfsshare\ndf -h | grep nfs\ncat /mnt/nfsshare/hello.txt"),
      ("Make it persistent",
       "sudo umount /mnt/nfsshare\necho '" + HOST_B + ":/srv/nfsshare  /mnt/nfsshare  nfs  defaults,_netdev  0 0' | sudo tee -a /etc/fstab\nsudo mount -a\ndf -h | grep nfs"),
    ],
    "note": "_netdev tells systemd this mount needs the network up first. Without it, the boot can hang waiting for a share that is not reachable yet."},
   {"h": "7. autofs",
    "p": "Mount on access, unmount when idle. Named explicitly in the objectives.",
    "code": [
      ("Remove the static mount first",
       "sudo umount /mnt/nfsshare\nsudo sed -i '\\|" + HOST_B + ":/srv/nfsshare|d' /etc/fstab\ngrep nfs /etc/fstab || echo 'static NFS entry removed'"),
      ("Configure the maps",
       "sudo dnf install -y autofs\necho '/-  /etc/auto.direct' | sudo tee -a /etc/auto.master\necho '/mnt/nfsshare  -rw,sync  " + HOST_B + ":/srv/nfsshare' | sudo tee /etc/auto.direct\nsudo systemctl enable --now autofs\nsudo systemctl restart autofs"),
      ("Prove on-demand behaviour",
       "df -h | grep nfsshare || echo 'not mounted yet - correct'\nls /mnt/nfsshare\ndf -h | grep nfsshare\n# wait for the idle timeout, then it unmounts itself again"),
    ]},
   {"h": "8. Diagnose a permission problem",
    "p": "An explicit objective, and the diagnosis method matters more than the fix.",
    "code": [
      ("Create the problem, then work it out",
       "sudo mkdir -p /srv/shared-data\nsudo chown root:root /srv/shared-data\nsudo chmod 700 /srv/shared-data\nsudo -u analyst1 ls /srv/shared-data   # fails\nls -ld /srv/shared-data\nid analyst1"),
      ("Fix it properly with a group, not with 777",
       "sudo chgrp engineering /srv/shared-data\nsudo chmod 2775 /srv/shared-data\nsudo -u analyst1 touch /srv/shared-data/works.txt\nls -l /srv/shared-data"),
    ]},
  ],
  "verify": [
    "sudo lvs && sudo vgs && sudo pvs",
    "df -h /mnt/labdata   # should show the extended size",
    "ls /mnt/nfsshare     # triggers the autofs mount",
    "reboot, then confirm /mnt/labdata is mounted and 'ls /mnt/nfsshare' still works",
  ],
  "breakfix": {
    "break": "sudo lvextend -L +5G /dev/labvg/labdata",
    "symptom": "The command fails with 'Insufficient free space' because the volume group has no room left.",
    "fix": "Add capacity first: create another PV, then 'sudo vgextend labvg <new-pv>', then retry the lvextend.",
    "lesson": "LVM is a stack, and you can only grow a layer if the one beneath it has room. When an lvextend fails, check 'vgs' before anything else - the answer is almost always there in the VFree column.",
  },
 },

 {
  "n": 10, "id": "week-10", "title": "SELinux, SSH Keys, and Default Permissions",
  "goal": "Work with SELinux rather than around it, set up key-based authentication, and control default permissions. This domain fails more candidates than any other.",
  "time": "4-5 hours",
  "prereqs": ["Week 9 complete", "Both machines reachable", "A snapshot before you start"],
  "sections": [
   {"h": "1. Modes",
    "p": "Enforcing blocks and logs. Permissive only logs. Disabled does neither - and is never the right answer on the exam.",
    "code": [
      ("Check and switch at runtime",
       "getenforce\nsestatus\nsudo setenforce 0\ngetenforce\nsudo setenforce 1\ngetenforce"),
      ("Make the mode persistent",
       "sudo cat /etc/selinux/config | grep -v '^#'\nsudo sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config\ngrep '^SELINUX=' /etc/selinux/config"),
    ],
    "note": "setenforce changes the current mode only. The file is what applies at boot. A task that says 'SELinux must be enforcing' means both."},
   {"h": "2. Read contexts",
    "p": "Every file and process carries a context. The fourth field - the type - is what usually matters.",
    "code": [
      ("Files, processes, ports, and users",
       "ls -Z /var/www/html 2>/dev/null || sudo mkdir -p /var/www/html && ls -Zd /var/www/html\nps -eZ | grep sshd | head -3\nid -Z\nsudo semanage port -l | grep -w http_port_t"),
    ]},
   {"h": "3. Fix a context the right way",
    "p": "This is the classic exam scenario: content served from a non-default location.",
    "code": [
      ("Set up a web server with content in the wrong place",
       "sudo dnf install -y httpd\nsudo systemctl enable --now httpd\nsudo firewall-cmd --permanent --add-service=http && sudo firewall-cmd --reload\nsudo mkdir -p /srv/mysite\necho '<h1>Lab site</h1>' | sudo tee /srv/mysite/index.html\nls -Zd /srv/mysite"),
      ("Point httpd at it and watch it fail",
       "sudo sed -i 's|^DocumentRoot .*|DocumentRoot \"/srv/mysite\"|' /etc/httpd/conf/httpd.conf\nsudo systemctl restart httpd\ncurl -s -o /dev/null -w '%{http_code}\\n' http://localhost/\nsudo journalctl -t setroubleshoot --no-pager | tail -5\nsudo ausearch -m AVC -ts recent 2>/dev/null | tail -20"),
      ("Fix it permanently with semanage plus restorecon",
       "sudo dnf install -y policycoreutils-python-utils\nsudo semanage fcontext -a -t httpd_sys_content_t '/srv/mysite(/.*)?'\nsudo restorecon -Rv /srv/mysite\nls -Zd /srv/mysite\nls -Z /srv/mysite\ncurl -s http://localhost/"),
    ],
    "note": "chcon would also have worked right now - and would be wiped by the next relabel. semanage fcontext writes the rule into policy; restorecon applies it. That pairing is the correct, persistent answer."},
   {"h": "4. Port labels",
    "p": "Running a service on a non-standard port needs the port labelled, or SELinux blocks the bind.",
    "code": [
      ("Move httpd to port 8888",
       "sudo sed -i 's/^Listen 80$/Listen 8888/' /etc/httpd/conf/httpd.conf\nsudo systemctl restart httpd   # this fails\nsudo systemctl status httpd --no-pager | tail -5"),
      ("Label the port, then it starts",
       "sudo semanage port -a -t http_port_t -p tcp 8888\nsudo semanage port -l | grep -w http_port_t\nsudo systemctl restart httpd\nsudo firewall-cmd --permanent --add-port=8888/tcp && sudo firewall-cmd --reload\ncurl -s http://localhost:8888/"),
    ]},
   {"h": "5. Booleans",
    "p": "Booleans switch predefined policy behaviour on and off. -P makes the change survive a reboot.",
    "code": [
      ("Find and set one",
       "getsebool -a | head\ngetsebool -a | grep httpd | head -10\ngetsebool httpd_enable_homedirs\nsudo setsebool -P httpd_enable_homedirs on\ngetsebool httpd_enable_homedirs"),
      ("See what a boolean actually does",
       "sudo semanage boolean -l | grep httpd_enable_homedirs"),
    ],
    "note": "Without -P the change is lost at reboot. Given the persistence rule, a boolean set without -P scores nothing."},
   {"h": "6. Read a denial",
    "p": "Being able to interpret the log is the skill; the fix follows from it.",
    "code": [
      ("Find and translate",
       "sudo ausearch -m AVC -ts today 2>/dev/null | tail -20\nsudo journalctl -t setroubleshoot --no-pager | tail\n# sealert gives a plain-English explanation when setroubleshoot is installed:\nsudo dnf install -y setroubleshoot-server 2>/dev/null\nsudo sealert -a /var/log/audit/audit.log 2>/dev/null | head -30"),
    ]},
   {"h": "7. Key-based SSH authentication",
    "p": "",
    "code": [
      ("Generate a key and install it",
       "ssh-keygen -t ed25519 -C '" + USER + "@" + HOST_A + "' -f ~/.ssh/id_ed25519 -N ''\nls -l ~/.ssh/\nssh-copy-id " + USER + "@" + HOST_B + "\nssh " + USER + "@" + HOST_B + " 'echo key auth works; hostname'"),
      ("Confirm the permissions SSH insists on",
       "ssh " + USER + "@" + HOST_B + " 'ls -ld ~/.ssh; ls -l ~/.ssh/authorized_keys'\n# ~/.ssh must be 700 and authorized_keys 600, or sshd ignores them"),
      ("Optionally disable password authentication",
       "ssh " + USER + "@" + HOST_B + " \"sudo sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart sshd\""),
    ]},
   {"h": "8. Default permissions with umask",
    "p": "",
    "code": [
      ("See the effect",
       "umask\ntouch ~/umask-default.txt\nmkdir ~/umask-default-dir\nls -l ~/umask-default.txt\nls -ld ~/umask-default-dir"),
      ("Change it for this shell, then persistently",
       "umask 0077\ntouch ~/umask-private.txt\nls -l ~/umask-private.txt\necho 'umask 0077' >> ~/.bashrc"),
      ("System-wide default",
       "grep -rn umask /etc/profile /etc/bashrc | head"),
    ],
    "note": "umask subtracts from 666 for files and 777 for directories. 0077 gives 600 files and 700 directories - private to the owner."},
  ],
  "verify": [
    "getenforce   # must say Enforcing",
    "grep '^SELINUX=' /etc/selinux/config",
    "ls -Zd /srv/mysite | grep httpd_sys_content_t",
    "sudo semanage port -l | grep -w http_port_t | grep 8888",
    "getsebool httpd_enable_homedirs",
    "reboot, then re-run all of the above",
  ],
  "breakfix": {
    "break": "sudo chcon -t user_home_t /srv/mysite/index.html && sudo restorecon -Rv /srv/mysite",
    "symptom": "You set a context with chcon, then restorecon immediately reverted it - because policy disagreed with you.",
    "fix": "That IS the correct behaviour. Use: sudo semanage fcontext -a -t httpd_sys_content_t '/srv/mysite(/.*)?' && sudo restorecon -Rv /srv/mysite",
    "lesson": "chcon is a temporary label; semanage fcontext is a policy rule. If a fix disappears after a relabel or reboot, you used chcon where you needed semanage. Never solve an SELinux problem by setting permissive - the exam grades the security domain, and permissive fails it.",
  },
 },

 {
  "n": 11, "id": "week-11", "title": "Shell Scripting",
  "goal": "Write the small, practical scripts the exam asks for: conditionals, loops, arguments, and command substitution. Nothing exotic is tested.",
  "time": "3-4 hours",
  "prereqs": ["Weeks 1-10 complete"],
  "sections": [
   {"h": "1. The skeleton",
    "p": "Every script starts the same way.",
    "code": [
      ("Create, make executable, run",
       "mkdir -p ~/bin && cd ~/bin\ncat > hello.sh <<'EOF'\n#!/bin/bash\necho \"Hello from $(hostname), running as $(whoami)\"\nEOF\nchmod +x hello.sh\n./hello.sh"),
    ]},
   {"h": "2. Conditionals",
    "p": "if with test or [ ]. Know the file, string, and numeric operators.",
    "code": [
      ("Branch on a condition",
       "cat > check.sh <<'EOF'\n#!/bin/bash\nTARGET=\"/etc/passwd\"\n\nif [ -f \"$TARGET\" ]; then\n    echo \"$TARGET is a regular file\"\nelif [ -d \"$TARGET\" ]; then\n    echo \"$TARGET is a directory\"\nelse\n    echo \"$TARGET does not exist\"\nfi\nEOF\nchmod +x check.sh && ./check.sh"),
      ("The operators worth memorising",
       "# Files:    -f (file)  -d (directory)  -e (exists)  -r -w -x (readable/writable/executable)\n# Strings:  = (equal)  != (not equal)  -z (empty)  -n (not empty)\n# Numbers:  -eq -ne -lt -le -gt -ge\nman test | head -40"),
      ("Numeric and string comparison side by side",
       "cat > compare.sh <<'EOF'\n#!/bin/bash\nCOUNT=$(who | wc -l)\n\nif [ \"$COUNT\" -gt 1 ]; then\n    echo \"$COUNT users are logged in\"\nelse\n    echo \"Only one session\"\nfi\n\nif [ \"$(whoami)\" = \"root\" ]; then\n    echo \"Running as root\"\nelse\n    echo \"Not root\"\nfi\nEOF\nchmod +x compare.sh && ./compare.sh"),
    ]},
   {"h": "3. Loops",
    "p": "for over a list, a glob, and command output; while for reading input.",
    "code": [
      ("for, three ways",
       "cat > loops.sh <<'EOF'\n#!/bin/bash\n\nfor SERVICE in sshd chronyd firewalld; do\n    printf '%-12s %s\\n' \"$SERVICE\" \"$(systemctl is-active $SERVICE)\"\ndone\n\nfor FILE in /etc/*.conf; do\n    echo \"$(basename $FILE) has $(wc -l < $FILE) lines\"\ndone\n\nfor USERNAME in $(getent passwd | awk -F: '$3 >= 1000 && $3 < 65534 {print $1}'); do\n    echo \"Regular user: $USERNAME\"\ndone\nEOF\nchmod +x loops.sh && ./loops.sh"),
      ("while, reading a file line by line",
       "cat > readfile.sh <<'EOF'\n#!/bin/bash\nwhile read -r LINE; do\n    case \"$LINE\" in\n        \\#*|\"\") continue ;;\n    esac\n    echo \"config line: $LINE\"\ndone < /etc/chrony.conf\nEOF\nchmod +x readfile.sh && ./readfile.sh | head"),
    ]},
   {"h": "4. Script arguments",
    "p": "Explicitly in the objectives. Handle them, and fail cleanly when they are missing.",
    "code": [
      ("Positional parameters with validation",
       "cat > args.sh <<'EOF'\n#!/bin/bash\n\nif [ \"$#\" -lt 2 ]; then\n    echo \"Usage: $(basename $0) <name> <count>\" >&2\n    exit 1\nfi\n\nNAME=\"$1\"\nCOUNT=\"$2\"\n\necho \"Script:    $0\"\necho \"Arg count: $#\"\necho \"All args:  $@\"\n\nfor i in $(seq 1 \"$COUNT\"); do\n    echo \"$i. Hello, $NAME\"\ndone\nEOF\nchmod +x args.sh\n./args.sh\n./args.sh " + USER + " 3\necho \"exit status: $?\""),
    ]},
   {"h": "5. Using command output",
    "p": "Command substitution with $( ). Backticks work too but nest badly - use the modern form.",
    "code": [
      ("Capture and act on output",
       "cat > report.sh <<'EOF'\n#!/bin/bash\n\nHOST=$(hostname -s)\nWHEN=$(date '+%Y-%m-%d %H:%M')\nUSED=$(df -h / | awk 'NR==2 {print $5}')\nLOAD=$(uptime | awk -F'load average:' '{print $2}')\nUSERS=$(getent passwd | awk -F: '$3 >= 1000 && $3 < 65534' | wc -l)\n\necho \"===== $HOST at $WHEN =====\"\necho \"Root filesystem used: $USED\"\necho \"Load average:        $LOAD\"\necho \"Regular users:       $USERS\"\n\nif [ \"${USED%\\%}\" -gt 80 ]; then\n    echo \"WARNING: root filesystem above 80 percent\"\n    exit 2\nfi\n\nexit 0\nEOF\nchmod +x report.sh && ./report.sh\necho \"exit status: $?\""),
    ]},
   {"h": "6. Exit statuses",
    "p": "Zero means success. Anything else means failure. Your scripts should follow that convention.",
    "code": [
      ("Check and return meaningfully",
       "grep -q '^root:' /etc/passwd\necho \"grep found it, status: $?\"\ngrep -q '^nosuchuser:' /etc/passwd\necho \"grep did not find it, status: $?\"\n\nsystemctl is-active --quiet sshd && echo 'sshd is up' || echo 'sshd is down'"),
    ]},
   {"h": "7. Final objective sweep",
    "p": "Before Week 12, go back to the source.",
    "code": [
      ("Re-read the official list and be honest",
       "# Open the EX200 objectives and read every bullet.\n# For each one, ask: could I do this right now, on a fresh machine, with no notes?\n# Write down every 'no' or 'probably'. That list drives Week 12."),
    ]},
  ],
  "verify": [
    "cd ~/bin && for s in *.sh; do bash -n \"$s\" && echo \"$s: syntax ok\"; done",
    "./args.sh " + USER + " 2",
    "./report.sh; echo \"exit: $?\"",
  ],
  "breakfix": {
    "break": "sed -i 's/if \\[ \"$#\" -lt 2 \\]; then/if [ $# -lt 2 ] then/' ~/bin/args.sh",
    "symptom": "The script fails with a syntax error near an unexpected token.",
    "fix": "Restore the missing semicolon before then: 'if [ $# -lt 2 ]; then'. Check with: bash -n ~/bin/args.sh",
    "lesson": "'bash -n script.sh' parses without executing and is the fastest way to find a syntax error. Also note the quoting: \"$#\" and \"$1\" in quotes protects you from empty or space-containing values - a habit worth having before the exam.",
  },
 },

 {
  "n": 12, "id": "week-12", "title": "Mock Exam, Remediation, and Exam Day",
  "goal": "Find out whether you are actually ready, fix what the mock exposes, and walk into the real exam having already sat it once.",
  "time": "6-8 hours across the week",
  "prereqs": ["Weeks 1-11 complete", "Both lab machines rolled back to a clean snapshot"],
  "sections": [
   {"h": "1. Set the conditions honestly",
    "p": "A mock you cheat on tells you nothing. Reproduce the real constraints exactly.",
    "code": [
      ("Before you start the timer",
       "# 1. Roll both machines back to the 'clean' snapshot\n# 2. Close every browser tab except a clock\n# 3. No notes, no lab guides, no search engine\n# 4. Allowed: man, info, /usr/share/doc - nothing else\n# 5. Set a timer. Do not pause it for any reason."),
    ]},
   {"h": "2. A self-built mock",
    "p": "Work these from a cold machine, in any order, in under three hours. They are written the way exam tasks are written - the outcome is specified, the method is not.",
    "code": [
      ("Users, groups, and access",
       "# 1. Create user 'auditor' with UID 3200 and a shell of /bin/bash.\n# 2. Create group 'audit' with GID 3300; make auditor a supplementary member.\n# 3. auditor's password must expire every 30 days with a 5-day warning.\n# 4. Members of 'audit' may run any command with sudo."),
      ("Storage",
       "# 5. Create a 1 GiB partition on the spare disk, format it XFS,\n#    and mount it permanently at /data/reports using its UUID.\n# 6. Create a volume group 'appvg' and a 400 MiB logical volume 'applv'.\n# 7. Format applv ext4, mount it at /data/app, then grow it to 700 MiB\n#    without losing its contents.\n# 8. Add 512 MiB of swap that activates automatically at boot."),
      ("Services, networking, and security",
       "# 9.  Install and enable httpd. Serve content from /srv/reports\n#     instead of the default location. It must work with SELinux enforcing.\n# 10. httpd must listen on port 8404 and be reachable through the firewall.\n# 11. Set a static IPv4 address that survives a reboot.\n# 12. Configure key-based SSH from " + HOST_A + " to " + HOST_B + " for user " + USER + "."),
      ("Automation and recovery",
       "# 13. Write /usr/local/bin/diskcheck.sh that takes a mount point as $1,\n#     prints its usage percentage, and exits 2 if usage exceeds 80 percent.\n# 14. Run that script every 15 minutes via a systemd timer.\n# 15. Make the journal persistent across reboots.\n# 16. Set the system to boot into multi-user.target by default."),
      ("Then, and only then",
       "sudo reboot\n# When it comes back, re-check every single task.\n# Score only what survived. Anything that needed a manual fix scores zero."),
    ]},
   {"h": "3. Score and remediate",
    "p": "The score matters far less than the list it produces.",
    "code": [
      ("Turn failures into a study plan",
       "# For every task you missed or had to look up:\n#   - Which objective domain does it belong to?\n#   - Rebuild that lab from scratch, untimed, from the Week guide.\n#   - Then do it again from memory, timed.\n# Anything in the security or storage domains gets double attention -\n# they carry the most weight and the most partial-failure risk."),
    ]},
   {"h": "4. The second mock",
    "p": "Later in the week, on a clean snapshot again.",
    "code": [
      ("Use a source you have not seen",
       "# Sit a timed, hands-on mock you did not write yourself, so you\n# cannot unconsciously remember the answers:\n#   https://linuxcert.guru/\n# Same rules: clean machines, timer running, man pages only, reboot at the end."),
    ]},
   {"h": "5. Book it",
    "p": "",
    "code": [
      ("While the second mock is still fresh",
       "# Book EX200 within two weeks of a clean mock pass:\n#   https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam\n# Check your ID matches your Red Hat account name exactly.\n# Test your machine against the proctoring requirements the day before."),
    ]},
  ],
  "verify": [
    "Every mock task re-checked AFTER a reboot",
    "A written list of every objective you had to look up",
    "A second timed mock passed cleanly",
    "Exam booked, ID checked, environment tested",
  ],
  "breakfix": {
    "break": "Skip the reboot at the end of the mock.",
    "symptom": "You score yourself 15/16 and feel ready. On the real exam you score far lower, because several configurations never persisted.",
    "fix": "Always reboot before scoring. Always.",
    "lesson": "This is the whole course in one sentence: the exam grades the state of the machine after a reboot, not the commands you typed. If you have internalised that by now, you are in good shape.",
  },
 },
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab {n}: {title} — Free RHCSA Course</title>
<meta name="description" content="{goal_attr}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/css/style.css">
<style>
  .lab-wrap {{ max-width: 860px; margin: 0 auto; padding: 30px 22px 90px; }}
  .lab-back {{ font-size: 13px; color: var(--text-3); display: inline-block; margin-bottom: 18px; }}
  .lab-h {{ margin-bottom: 22px; }}
  .lab-h h1 {{ font-size: 27px; letter-spacing: -.02em; margin-bottom: 6px; }}
  .lab-meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 0; }}
  .step {{ margin: 30px 0 0; }}
  .step h2 {{ font-size: 17px; margin-bottom: 6px; }}
  .step > p {{ color: var(--text-2); font-size: 14px; max-width: 72ch; }}
  .cmd {{ margin: 14px 0; border: 1px solid var(--border); border-radius: var(--radius);
          overflow: hidden; background: var(--bg-elev); box-shadow: var(--shadow); }}
  .cmd__t {{ font-size: 12.5px; font-weight: 600; color: var(--text-2);
             padding: 9px 14px; background: var(--bg-sunken); border-bottom: 1px solid var(--border); }}
  .cmd pre {{ margin: 0; padding: 14px; overflow-x: auto; font-family: var(--mono);
              font-size: 12.8px; line-height: 1.65; color: var(--text); }}
  .lab-nav {{ display: flex; justify-content: space-between; gap: 12px;
              margin-top: 44px; padding-top: 20px; border-top: 1px solid var(--border); }}
  ol.verify {{ font-family: var(--mono); font-size: 12.8px; }}
  ol.verify li {{ margin-bottom: 6px; color: var(--text-2); }}
  @media print {{ .lab-back, .lab-nav, .header {{ display: none !important; }} }}
</style>
<script>
  (function () {{
    try {{
      var t = localStorage.getItem("rhcsa.theme.v1");
      if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
    }} catch (e) {{}}
  }})();
</script>
</head>
<body>
<header class="header">
  <a class="brand" href="../index.html">
    <span class="brand__mark">ST</span>
    <span class="brand__text">
      <span class="brand__title">Free RHCSA Course</span>
      <span class="brand__sub">Lab {n} of 12</span>
    </span>
  </a>
  <span class="header__spacer"></span>
  <button class="btn btn--icon" data-theme-toggle title="Toggle dark / light mode" aria-label="Toggle dark or light mode">
    <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4.5"/><line x1="12" y1="1.5" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22.5"/><line x1="4.2" y1="4.2" x2="6" y2="6"/><line x1="18" y1="18" x2="19.8" y2="19.8"/><line x1="1.5" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="22.5" y2="12"/><line x1="4.2" y1="19.8" x2="6" y2="18"/><line x1="18" y1="6" x2="19.8" y2="4.2"/></svg>
    <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
</header>

<div class="lab-wrap">
  <a class="lab-back" href="../index.html#{id}">&larr; Back to Week {n}</a>

  <div class="lab-h">
    <div class="section__eyebrow">Lab guide {n}</div>
    <h1>{title}</h1>
    <p style="color:var(--text-2);font-size:14.5px;max-width:74ch">{goal}</p>
    <div class="lab-meta">
      <span class="chip chip--accent">{time}</span>
      {prereq_chips}
    </div>
  </div>

  <div class="callout"><div class="callout__title">Before you start</div>
    <ul>{prereqs}<li>Take a snapshot of both machines. You will break things on purpose.</li></ul>
  </div>

  {sections}

  <div class="step">
    <h2>Verify your work</h2>
    <p>Run these before you consider the lab finished.</p>
    <ol class="verify">{verify}</ol>
  </div>

  <div class="callout callout--warn">
    <div class="callout__title">Break it, then fix it</div>
    <p><strong>Break:</strong></p>
    <div class="cmd"><pre>{bf_break}</pre></div>
    <p><strong>What you'll see:</strong> {bf_symptom}</p>
    <p><strong>Fix:</strong></p>
    <div class="cmd"><pre>{bf_fix}</pre></div>
    <p><strong>Why it matters:</strong> {bf_lesson}</p>
  </div>

  <div class="callout callout--danger">
    <div class="callout__title">Now reboot</div>
    <p>Run <code>sudo reboot</code>, then re-run every command in the verify list above. Anything that
    did not come back on its own would have scored zero on the exam. Fix it now, while you can still
    see what you did.</p>
  </div>

  <div class="lab-nav">
    <span>{prev}</span>
    <span>{next}</span>
  </div>
</div>

<footer class="footer">
  <div class="footer__inner">
    <div><strong>Free RHCSA Course</strong> — rhcsa.learnlinuxforwork.com<br>
    Written by Shea. Licensed under the
    <a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank" rel="noopener noreferrer">GNU AGPL v3.0 or later</a>.</div>
    <div class="footer__links">
      <a href="../index.html">Course home</a>
      <a href="https://www.learnlinuxforwork.com" target="_blank" rel="noopener noreferrer">Linux training</a>
      <a href="https://linuxcert.guru/" target="_blank" rel="noopener noreferrer">RHCSA mocks</a>
    </div>
  </div>
</footer>

<script src="../assets/js/lab.js"></script>
</body>
</html>
"""


def e(s):
    return html.escape(str(s), quote=False)


def build():
    outdir = os.path.join(HERE, "lab")
    os.makedirs(outdir, exist_ok=True)
    for i, lab in enumerate(LABS):
        secs = []
        for s in lab["sections"]:
            blocks = ""
            for title, code in s["code"]:
                blocks += ('<div class="cmd"><div class="cmd__t">' + e(title) +
                           "</div><pre>" + e(code) + "</pre></div>")
            note = ""
            if s.get("note"):
                note = ('<div class="callout"><div class="callout__title">Worth knowing</div><p>' +
                        s["note"] + "</p></div>")
            secs.append('<div class="step"><h2>' + e(s["h"]) + "</h2>" +
                        ("<p>" + e(s["p"]) + "</p>" if s.get("p") else "") +
                        blocks + note + "</div>")

        prev_l = ('<a class="btn" href="' + LABS[i - 1]["id"] + '.html">&larr; Lab ' +
                  str(LABS[i - 1]["n"]) + "</a>") if i > 0 else ""
        next_l = ('<a class="btn btn--primary" href="' + LABS[i + 1]["id"] + '.html">Lab ' +
                  str(LABS[i + 1]["n"]) + " &rarr;</a>") if i < len(LABS) - 1 else \
                 '<a class="btn btn--primary" href="../index.html#exam-day">Exam day &rarr;</a>'

        page = PAGE.format(
            n=lab["n"], id=lab["id"], title=e(lab["title"]),
            goal=e(lab["goal"]), goal_attr=html.escape(lab["goal"], quote=True),
            time=e(lab["time"]),
            prereq_chips="".join('<span class="chip">' + e(p) + "</span>" for p in lab["prereqs"][:1]),
            prereqs="".join("<li>" + e(p) + "</li>" for p in lab["prereqs"]),
            sections="".join(secs),
            verify="".join("<li>" + e(v) + "</li>" for v in lab["verify"]),
            bf_break=e(lab["breakfix"]["break"]),
            bf_symptom=e(lab["breakfix"]["symptom"]),
            bf_fix=e(lab["breakfix"]["fix"]),
            bf_lesson=e(lab["breakfix"]["lesson"]),
            prev=prev_l, next=next_l,
        )
        io.open(os.path.join(outdir, lab["id"] + ".html"), "w", encoding="utf-8").write(page)
        print("wrote lab/%s.html  (%d sections)" % (lab["id"], len(lab["sections"])))

    print("\n%d lab guides generated." % len(LABS))


if __name__ == "__main__":
    build()
